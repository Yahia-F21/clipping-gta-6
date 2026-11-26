"""Inset-layout hooks stay above the game area (which starts at y=380), shrinking to fit."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clipper import captions, render
from PIL import Image


class InsetHookTests(unittest.TestCase):
    def _bbox(self, text, style, layout):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "h.png"
            captions.render_hook(text, p, style, layout)
            return Image.open(p).getchannel("A").getbbox()

    def test_long_hook_stays_above_the_game_area(self):
        bbox = self._bbox("DID HE JUST STEAL HER SCOOTER AT THE LIGHTS", "bold", "inset")
        self.assertIsNotNone(bbox)
        self.assertLessEqual(bbox[3], captions.INSET_GAME_TOP)

    def test_short_hook_also_stays_above(self):
        bbox = self._bbox("HE TOOK IT", "bold", "inset")
        self.assertIsNotNone(bbox)
        self.assertLessEqual(bbox[3], captions.INSET_GAME_TOP)

    def test_boxed_hook_stays_above(self):
        bbox = self._bbox("He really took granny's scooter and left", "box", "inset")
        self.assertIsNotNone(bbox)
        self.assertLessEqual(bbox[3], captions.INSET_GAME_TOP)

    def test_fit_layout_is_not_clamped(self):
        # the fit layout's hook keeps its centred position lower on the frame
        bbox = self._bbox("NO WAY", "bold", "fit")
        self.assertIsNotNone(bbox)
        self.assertGreater(bbox[3], captions.INSET_GAME_TOP)

    def test_empty_text_draws_nothing(self):
        self.assertIsNone(self._bbox("   ", "bold", "inset"))


class JoinedCaptionLayoutTests(unittest.TestCase):
    def test_inset_segments_keep_inset_positions(self):
        self.assertEqual(render.joined_caption_layout({"type": "inset"}, ["inset", "inset"]), "inset")

    def test_split_wins_when_mixed(self):  # its seam keeps the hook off the facecam on top
        self.assertEqual(render.joined_caption_layout(None, ["inset", "split"]), "split")

    def test_fit_stays_fit(self):
        self.assertEqual(render.joined_caption_layout(None, ["fit"]), "fit")

    def test_explicit_as_is_preserved(self):
        self.assertEqual(render.joined_caption_layout({"type": "inset", "as": "fit"}, ["inset"]), "fit")


if __name__ == "__main__":
    unittest.main()
