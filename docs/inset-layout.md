# Inset layout (sharper facecam)

`clipper/inset_layout.py` renders a 1080x1920 clip with the game at full width and the
facecam as a small inset over a blurred background. The stock `split` layout enlarges a
small facecam crop to the full width, which blurs it; this layout does not.

It is standalone: ffmpeg plus the Python standard library. It does not transcribe,
pick moments or touch the rest of the pipeline.

```
python -m clipper.inset_layout SOURCE.mp4 OUT.mp4 --start 17 --duration 15.5 \
    --cam 0,458,390,235 --hook "YOUR HOOK" --captions captions.json
```

- `--cam x,y,w,h`: the facecam rectangle in SOURCE pixels (look at one frame to find it).
- `--cam-scale`: default 1.5. Above about 1.5 a ~390 px crop softens. A 1080p source
  matters: a 480p source has far less facecam detail.
- `captions.json`: `[{"start": 1.0, "end": 3.2, "text": "..."}]`, seconds from the cut start.
  Check wording and timing yourself.
- `--preset`, `--crf`, `--threads`: ffmpeg settings. Defaults are veryfast, crf 24 and
  ffmpeg's own thread count. Output is capped at about 4 Mbit/s so short clips stay under
  messaging size limits (about 11 MB for 25 s).

Tested: `python tests/test_inset_layout.py` renders a synthetic fixture (no real footage)
and checks the output size is 1080x1920. A rendered frame was inspected by eye. Not tested:
other machines, other operating systems and real stream sources beyond the ones used by the author.

Caption position: captions are bottom-aligned just inside the top of the game area (`caption_y`, default 540), so they do not cover subtitles that games or streamers burn into the lower part of the clip.

Fonts: captions use DejaVu Sans; install it or change the style names in `build_ass` if
your system lacks it.

Rights: you are responsible for permission to use any footage. This repo ships no media.

## Using it inside the stock `clipper render` flow

The stock renderer also accepts the same layout as a pick layout, so live chunks and
`analyze` jobs can use it without the standalone script:

```json
"layout": {"type": "inset", "face": [0.005, 0.556, 0.196, 0.193], "cam_scale": 1.2}
```

`face` is the facecam rectangle as fractions of the source (same as `split`; find it with
`python3 -m clipper frame <id> <seconds>`). `cam_scale` defaults to 1.2. The hook sits above the
game and captions sit in the upper part of the game area, away from burned-in game subtitles.

`clipper check` failures (weak hook, dead air, missing title wording) are not cosmetic. Fix
them before treating an export as ready to post. Rendering after a failed check is only a
pipeline test, not a usable clip. Test: `python -m unittest tests.test_inset_render_layout`.

Face-crop warnings (heuristic, unofficial): `clipper render` prints a `[check]` warning when an
inset pick's `face` box extends past the source frame, is tiny, or sits on the hard edge of a
rectangle the way HUD panels and minimaps do (`face_crop_warnings` in `clipper/render.py`, one
sampled frame per pick). The edge test catches hard-edged overlays; a soft or translucent HUD
sliver fully inside the box can pass unnoticed, so measure the box on real frames
(`python3 -m clipper frame <job> <seconds>`) and look at a rendered frame either way.
Tests: `python -m unittest tests.test_face_crop` (geometry always, edge heuristic with a synthetic
ffmpeg fixture).
