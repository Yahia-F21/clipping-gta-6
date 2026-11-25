"""Heuristic moment ranker. NOT a machine-learning model.
Stage 1 (audio): per-second loudness, jump over the local baseline, and speech-activity variation -> window scores.
Stage 2 (transcript): lexicon/rate heuristics on ASR words of the top windows.
Final judgment of setup/payoff is a human/LLM review step outside this file."""
import re
import subprocess
import numpy as np

REACT = re.compile(r"\b(oh my god|omg|what the (hell|fuck)|no way|bro|dude|yo|wait|holy|shit|fuck|damn|crazy|insane|"
                   r"dead|dying|lmao|lol|haha|ha ha|why|stop|help|nooo+|wow)\b", re.I)

ACTION = re.compile(r"\b(shoot|shot|shooting|gun|kill|killing|run|go go|get down|cops?|police|car|drive|chase|explod\w*|bomb|"
                    r"fire|reload|cover|behind you|move|hit)\b", re.I)
FUNNY = re.compile(r"\b(lmao|lol|haha+|ha ha|laugh\w*|funny|joke|bruh|why would|what are you doing|stop it|dead|"
                   r"i can't|cooked|bro what)\b", re.I)


def per_second(src, start=0, dur=None, sr=8000):
    cmd = ["ffmpeg", "-loglevel", "error", "-ss", str(start)] + (["-t", str(dur)] if dur else []) + \
          ["-i", str(src), "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"]
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.int16).astype(np.float32)
    n = len(a) // sr
    x = a[:n * sr].reshape(n, sr) / 32768.0
    rms = 20 * np.log10(np.sqrt((x ** 2).mean(1)) + 1e-5)
    zc = (np.diff(np.signbit(x), axis=1) != 0).mean(1)          # crude voice-vs-music/noise proxy
    return rms, zc


def window_scores(rms, zc, win=20, base=90):
    n = len(rms)
    out = np.zeros(n)
    for t in range(0, n - win):
        lo, hi = max(0, t - base), min(n, t + win + base)
        ctx = np.r_[rms[lo:t], rms[t + win:hi]]
        if len(ctx) < 20:
            continue
        w = rms[t:t + win]
        jump = np.percentile(w, 90) - np.median(ctx)             # louder than surroundings
        var = w.std()                                            # dynamics (silence -> burst)
        voice = float(((zc[t:t + win] > 0.04) & (zc[t:t + win] < 0.25) & (w > np.median(ctx))).mean())
        out[t] = jump + 0.5 * var + 6 * voice
    return out


def top_windows(scores, k=20, win=20, gap=45):
    order = np.argsort(scores)[::-1]
    picks = []
    for t in order:
        if scores[t] <= 0:
            break
        if all(abs(t - p) >= gap for p in picks):
            picks.append(int(t))
        if len(picks) >= k:
            break
    return picks


def transcript_score(words):
    """words: [{'w','s','e'}] inside one window -> (score, features).
    action_cues / funny_cues are keyword counts only; they are NOT validated predictors of action or humor."""
    if not words:
        return 0.0, {"words": 0}
    text = " ".join(w["w"] for w in words)
    dur = max(1.0, words[-1]["e"] - words[0]["s"])
    rate = len(words) / dur
    react = len(REACT.findall(text))
    excl = text.count("!") + text.count("?")
    caps = sum(1 for w in words if len(w["w"]) > 2 and w["w"].isupper())
    action = len(ACTION.findall(text))
    funny = len(FUNNY.findall(text))
    s = min(rate, 4) + 1.5 * min(react, 6) + 0.5 * min(excl, 6) + 0.5 * min(caps, 4)
    return s, {"words": len(words), "rate": round(rate, 2), "react": react, "excl": excl,
                  "action_cues": action, "funny_cues": funny}
