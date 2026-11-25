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
