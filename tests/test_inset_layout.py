"""Safe fixture test: builds a synthetic 1920x1080 source (no real footage) and renders it."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clipper import inset_layout


def test_ass_has_hook_and_caption():
    ass = inset_layout.build_ass("HOOK", [{"start": 1, "end": 2, "text": "hi {x}"}])
    assert "Hook,0,0,0,HOOK" in ass and "hi (x)" in ass


def test_caption_sits_in_upper_game_area():
    # Game subtitles are burned into the bottom of many clips; captions go near the top of the game area.
    ass = inset_layout.build_ass("", [{"start": 0, "end": 1, "text": "x"}])
    assert ",1,1,5,0,2,30,30,1380" in ass
    assert "Cap,0,0,0,x" in ass


def test_render_fixture():
    if not shutil.which("ffmpeg"):
        print("skip: no ffmpeg"); return
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "src.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=30",
                        "-f", "lavfi", "-i", "sine=frequency=440", "-t", "3", "-pix_fmt", "yuv420p", str(src)], check=True)
        caps = Path(d) / "c.json"
        caps.write_text(json.dumps([{"start": 0.5, "end": 2, "text": "Caption test"}]))
        out = Path(d) / "out.mp4"
        inset_layout.main([str(src), str(out), "--duration", "2", "--cam", "0,700,390,235",
                           "--hook", "HOOK TEST", "--captions", str(caps)])
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(out)],
                           capture_output=True, text=True)
        assert "1080,1920" in r.stdout


if __name__ == "__main__":
    test_ass_has_hook_and_caption(); test_caption_sits_in_upper_game_area(); test_render_fixture(); print("ok")
