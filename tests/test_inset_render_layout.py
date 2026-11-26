"""Offline test for the `inset` layout type in the stock renderer (synthetic source, no real footage)."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clipper import captions, render


class InsetLayoutTest(unittest.TestCase):
    def test_positions_registered(self):
        self.assertIn("inset", captions.LAYOUTS)
        self.assertEqual(render.caption_layout({"type": "inset"}), "inset")

    def test_filter_uses_face_crop_and_scale(self):
        vf = render.video_filter({"type": "inset", "face": [0.0, 0.5, 0.2, 0.2], "cam_scale": 1.2}, (1920, 1080))
        self.assertIn("crop=384:216:0:540", vf)
        self.assertIn("scale=460:258", vf)
        self.assertTrue(vf.endswith("[v1]"))

    @unittest.skipUnless(shutil.which("ffmpeg"), "no ffmpeg")
    def test_filter_renders_1080x1920(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "o.mp4"
            vf = render.video_filter({"type": "inset", "face": [0.0, 0.5, 0.2, 0.2]}, (1920, 1080))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=30",
                            "-t", "1", "-filter_complex", vf, "-map", "[v1]", "-pix_fmt", "yuv420p", str(out)], check=True)
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0",
                                str(out)], capture_output=True, text=True)
            self.assertIn("1080,1920", r.stdout)


if __name__ == "__main__":
    unittest.main()
