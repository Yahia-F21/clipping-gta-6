"""Synthetic test for clipper.moment_rank (heuristic shortlist helper). No footage needed. Run: python tests/test_moment_rank.py"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from clipper import moment_rank as m


def main():
    d = tempfile.mkdtemp()
    wav = os.path.join(d, "t.wav")
    # 60 s quiet tone with a loud burst of noise at 30-40 s
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    "sine=f=200:d=60,volume=0.02", "-f", "lavfi", "-i", "anoisesrc=d=10:a=0.6,adelay=30000|30000,apad=whole_dur=60",
                    "-filter_complex", "amix=inputs=2:duration=first:normalize=0", "-ac", "1", wav], check=True)
    rms, zc = m.per_second(wav)
    assert len(rms) >= 59, len(rms)
    sc = m.window_scores(rms, zc, win=10, base=30)
    top = m.top_windows(sc, k=1, win=10)
    assert top and 20 <= top[0] <= 40, top
    words = [{"w": w, "s": i * 0.3, "e": i * 0.3 + 0.3} for i, w in enumerate("oh my god bro shoot him lol what the hell".split())]
    s, f = m.transcript_score(words)
    assert s > 0 and f["react"] >= 3 and f["action_cues"] >= 1 and f["funny_cues"] >= 1, f
    assert m.transcript_score([])[0] == 0
    print("ok", top, round(s, 1), f)


if __name__ == "__main__":
    main()
