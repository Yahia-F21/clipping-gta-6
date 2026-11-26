"""Face-crop warnings for the inset layout. Geometry checks always run; the HUD straight-edge
heuristic needs ffmpeg and is skipped without it (the synthetic fixture carries no real footage)."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clipper import render

FFMPEG = shutil.which("ffmpeg")


class FaceCropGeometryTests(unittest.TestCase):
    def test_box_past_frame_warns(self):
        w = render.face_crop_warnings({"type": "inset", "face": [0.9, 0.9, 0.2, 0.2]}, (1920, 1080))
        self.assertTrue(any("past the source frame" in x for x in w), w)

    def test_tiny_box_warns(self):
        w = render.face_crop_warnings({"type": "inset", "face": [0.1, 0.1, 0.02, 0.02]}, (1920, 1080))
        self.assertTrue(any("tiny" in x for x in w), w)

    def test_valid_box_without_source_is_quiet(self):
        self.assertEqual(render.face_crop_warnings({"type": "inset", "face": [0.1, 0.7, 0.15, 0.28]},
                                                   (1920, 1080)), [])

    def test_box_ending_on_the_frame_edge_is_not_past_it(self):
        # facecams commonly sit flush with the bottom edge; that is not a geometry problem
        self.assertEqual(render.face_crop_warnings({"type": "inset", "face": [0.1, 0.7, 0.15, 0.3]},
                                                   (1920, 1080)), [])

    def test_non_inset_layout_is_quiet(self):
        self.assertEqual(render.face_crop_warnings({"type": "split", "face": [2, 2, 2, 2]}, (1920, 1080)), [])

    def test_missing_face_box_warns(self):
        self.assertTrue(render.face_crop_warnings({"type": "inset"}, (1920, 1080)))


@unittest.skipUnless(FFMPEG, "needs ffmpeg")
class HudEdgeHeuristicTests(unittest.TestCase):
    def _src(self, d):
        src = Path(d) / "src.mp4"
        # white rectangle on black footage: a stand-in HUD panel at the bottom left
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
                        "-i", "color=c=black:size=1920x1080:rate=10,"
                              "drawbox=x=30:y=810:w=220:h=250:color=white:t=fill",
                        "-t", "2", "-pix_fmt", "yuv420p", str(src)], check=True)
        return src

    def test_border_on_panel_edge_warns(self):
        with tempfile.TemporaryDirectory() as d:
            src = self._src(d)
            # the crop's left edge lands on the panel's right edge (x=250 of 1920)
            lay = {"type": "inset", "face": [250 / 1920, 0.75, 0.13, 0.25]}
            w = render.face_crop_warnings(lay, (1920, 1080), src, at=1.0)
            self.assertTrue(any("HUD" in x for x in w), w)

    def test_border_off_panel_is_quiet(self):
        with tempfile.TemporaryDirectory() as d:
            src = self._src(d)
            lay = {"type": "inset", "face": [0.5, 0.2, 0.13, 0.25]}
            self.assertEqual(render.face_crop_warnings(lay, (1920, 1080), src, at=1.0), [])


if __name__ == "__main__":
    unittest.main()
