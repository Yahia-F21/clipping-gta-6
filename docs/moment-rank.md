# Moment shortlist helper (heuristic)

`clipper/moment_rank.py` narrows a long stream to a short list of windows worth a human look. It is **hand-written
signal processing and keyword counting, not a machine-learning model, and not a predictor of views or engagement.**

## What it does
1. Audio stage: per-second loudness, jump over the surrounding ~90 s baseline, loudness variation and a crude
   voice-activity proxy, scored over sliding windows (`per_second`, `window_scores`, `top_windows`).
2. Transcript stage: on ASR words for the top windows only, `transcript_score` counts reaction words, `!`/`?`,
   speech rate, plus keyword counts `action_cues` and `funny_cues`.

Cutscenes are not excluded. Chat-replay signals are not used (not retrievable here).

## What it does not do
- It does not judge setup/payoff, humor or action. The `action_cues` and `funny_cues` counts are keywords only and are
  not validated.
- Audio scores can be high for music or silence artifacts (seen in testing).

## Evidence so far (small, informal)
On one 2 h VOD, one known good pick ranked in the top ~1% of windows (sanity check, not validation). Of 3 held-out
shortlisted windows reviewed with video frames, 1 was a usable clip and 2 were not: transcript scores overrated slow
dialogue. Treat output as a shortlist and review the actual footage before using a clip.

## Usage (library)
    from clipper import moment_rank as m
    rms, zc = m.per_second("audio_or_video.mp4")
    scores = m.window_scores(rms, zc)
    starts = m.top_windows(scores, k=20)   # seconds; transcribe these windows, then m.transcript_score(words)

Test: `python tests/test_moment_rank.py` (synthetic audio, no footage; needs ffmpeg and numpy).
