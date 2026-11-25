"""Vertical (9:16) layout with the game full-width and the facecam as a small inset.

Why this exists: the stock `split` layout enlarges a small facecam crop to the full
frame width, which blurs it. This layout keeps the game at 1080 wide (no upscale
from a 1080p source) and shows the facecam crop at a modest scale (default 1.5x)
under it, over a blurred copy of the game.

Standalone: uses only ffmpeg and the Python standard library. Does not touch the
rest of the clipper pipeline. Licensed AGPL-3.0 like the rest of this repository.

Usage:
  python -m clipper.inset_layout SOURCE.mp4 OUT.mp4 \
      --start 17 --duration 15.5 \
      --cam 0,458,390,235 \
      --hook "ALL I WANTED WAS A HAPPY FAMILY" \
      --captions captions.json

--cam is x,y,w,h of the facecam in SOURCE pixels. Captions file is a JSON list of
{"start": seconds, "end": seconds, "text": "..."} with times relative to the cut.
Review captions yourself; this tool does not transcribe.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

W, H = 1080, 1920


def _ts(t):
    t = max(0.0, float(t))
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _esc(text):
    return text.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def build_ass(hook, captions, hook_seconds=6.0, caption_y=1045):
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,Bold,BorderStyle,"
        "Outline,Shadow,Alignment,MarginL,MarginR,MarginV",
        "Style: Hook,DejaVu Sans,74,&H00FFFFFF,&H00000000,&H80000000,1,1,6,0,8,60,60,170",
        "Style: Cap,DejaVu Sans,54,&H0000FFFF,&H00000000,&H80000000,1,1,5,0,5,30,30,0",
        "[Events]",
        "Format: Layer,Start,End,Style,MarginL,MarginR,MarginV,Text",
    ]
    if hook:
        lines.append(f"Dialogue: 0,{_ts(0)},{_ts(hook_seconds)},Hook,0,0,0,{_esc(hook)}")
    for c in captions:
        lines.append(f"Dialogue: 0,{_ts(c['start'])},{_ts(c['end'])},Cap,0,0,{caption_y},{_esc(c['text'])}")
    return "\n".join(lines) + "\n"


def build_command(src, out, ass_path, start, duration, cam, cam_scale=1.5,
                  game_y=380, cam_y=1100, preset="veryfast", crf=24, threads=0):
    cx, cy, cw, ch = cam
    game_h = round(W * 9 / 16)
    cam_w = round(cw * cam_scale)
    cam_h = round(ch * cam_scale)
    fc = (
        "[0:v]split=3[a][b][c];"
        f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,eq=brightness=-0.15[bg];"
        f"[b]scale={W}:{game_h}[g];"
        f"[c]crop={cw}:{ch}:{cx}:{cy},scale={cam_w}:{cam_h}:flags=lanczos[cam];"
        f"[bg][g]overlay=0:{game_y}[t];[t][cam]overlay=(W-w)/2:{cam_y},ass={ass_path}"
    )
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    if threads:
        cmd += ["-threads", str(threads)]
    cmd += ["-ss", str(start), "-t", str(duration), "-i", str(src), "-filter_complex", fc,
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-maxrate", "4M", "-bufsize", "8M",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", str(out)]
    return cmd


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source")
    p.add_argument("out")
    p.add_argument("--start", type=float, default=0.0)
    p.add_argument("--duration", type=float, required=True)
    p.add_argument("--cam", required=True, help="x,y,w,h of the facecam in source pixels")
    p.add_argument("--cam-scale", type=float, default=1.5, help="facecam enlargement; above ~1.5 it softens")
    p.add_argument("--hook", default="")
    p.add_argument("--captions", help="JSON list of {start,end,text}, times relative to the cut")
    p.add_argument("--preset", default="veryfast")
    p.add_argument("--crf", type=int, default=24)
    p.add_argument("--threads", type=int, default=0, help="ffmpeg threads; 0 = ffmpeg default")
    a = p.parse_args(argv)
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found")
    cam = [int(v) for v in a.cam.split(",")]
    if len(cam) != 4:
        sys.exit("--cam needs x,y,w,h")
    caps = json.loads(Path(a.captions).read_text()) if a.captions else []
    with tempfile.TemporaryDirectory() as d:
        ass = Path(d) / "layout.ass"
        ass.write_text(build_ass(a.hook, caps))
        cmd = build_command(a.source, a.out, str(ass).replace(":", "\\:"), a.start, a.duration,
                            cam, a.cam_scale, preset=a.preset, crf=a.crf, threads=a.threads)
        subprocess.run(cmd, check=True)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
