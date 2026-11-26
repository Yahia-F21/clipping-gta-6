"""Campaign presets and the compliance check: pure logic, no ffmpeg."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clipper import campaigns


def pick(**kw):
    base = {"hook": "Did he just steal her scooter?", "start": 0.0, "end": 13.5,
            "voiceover": None, "music": []}
    base.update(kw)
    return base


class PresetShapeTests(unittest.TestCase):
    def test_casino_and_ai_girlfriend_campaigns_are_not_built(self):
        self.assertNotIn("vavada", campaigns.CAMPAIGNS)
        self.assertNotIn("fanvue", campaigns.CAMPAIGNS)
        self.assertIn("vavada", campaigns.SKIPPED_CAMPAIGNS)
        self.assertIn("fanvue", campaigns.SKIPPED_CAMPAIGNS)

    def test_unread_external_briefs_are_marked_unknown(self):
        self.assertIn("Foltyn", campaigns.UNKNOWN_CAMPAIGNS)
        self.assertNotIn("foltyn", campaigns.CAMPAIGNS)

    def test_sounds_are_posting_time_steps_never_bundled(self):
        for key, spec in campaigns.CAMPAIGNS.items():
            if spec.get("sound"):
                self.assertIn("posting", campaigns.check(pick(), key)["posting"]["sound"])
                self.assertTrue(spec["sound"]["name"])

    def test_common_rules_ride_along_as_verify_items(self):
        r = campaigns.check(pick(), "rexxlife")
        self.assertTrue(any("GTA 6 gameplay only" in v for v in r["verify"]))
        self.assertTrue(any("watermark" in v for v in r["verify"]))


class LengthTests(unittest.TestCase):
    def test_exact_length(self):
        self.assertTrue(any("not one of" in f for f in campaigns.check(pick(), "whethan")["fails"]))
        self.assertFalse(any("not one of" in f
                             for f in campaigns.check(pick(end=15.0), "whethan")["fails"]
                             if "length" in f))

    def test_loop_lengths(self):
        self.assertFalse(any("length" in f for f in campaigns.check(pick(end=30.0), "gameover")["fails"]))
        self.assertTrue(any("length" in f for f in campaigns.check(pick(end=45.0), "gameover")["fails"]))

    def test_min_max(self):
        self.assertTrue(any("under the 10s minimum" in f
                            for f in campaigns.check(pick(end=8.0), "rexxlife")["fails"]))
        self.assertTrue(any("over the 60s maximum" in f
                            for f in campaigns.check(pick(end=61.0), "rexxlife")["fails"]))

    def test_segments_sum(self):
        p = pick(segments=[{"start": 5.0, "end": 6.8}, {"start": 9.2, "end": 13.0},
                           {"start": 15.1, "end": 23.0}])
        self.assertEqual(campaigns.pick_seconds(p), 13.5)


class RuleTests(unittest.TestCase):
    def test_missing_hook_fails_hook_campaigns(self):
        r = campaigns.check(pick(hook=None, hooks=None), "rexxlife")
        self.assertTrue(any("no hook" in f for f in r["fails"]))

    def test_voiceover_banned_for_rexxlife(self):
        r = campaigns.check(pick(voiceover="a line"), "rexxlife")
        self.assertTrue(any("voiceover" in f for f in r["fails"]))

    def test_mixed_music_fails_official_sound_campaigns(self):
        r = campaigns.check(pick(music=[{"id": "x"}]), "denial")
        self.assertTrue(any("never mixed" in f for f in r["fails"]))

    def test_whethan_one_text_line_needs_a_captions_off_path(self):
        self.assertTrue(any("captions-off" in f for f in campaigns.check(pick(end=15.0), "whethan")["fails"]))

    def test_logo_campaigns_are_blocked_until_assets_and_discord(self):
        self.assertTrue(any("blocked" in f for f in campaigns.check(pick(), "gta-clipper-logo")["fails"]))
        self.assertTrue(any("blocked" in f for f in campaigns.check(pick(), "clipup")["fails"]))

    def test_rexxlife_posting_steps(self):
        r = campaigns.check(pick(), "rexxlife")
        self.assertIn("Handful of Diamond Rings", r["posting"]["sound"])
        self.assertIn("0:09 or 0:26", r["posting"]["sound"])
        self.assertEqual(r["posting"]["caption"], "Song: Handful of Diamond Rings by @rexxliferaj")
        self.assertTrue(any("no cutscenes" in v for v in r["verify"]))
        self.assertTrue(any("radio" in v for v in r["verify"]))

    def test_compliant_rexxlife_pick_has_no_automatic_failures(self):
        self.assertEqual(campaigns.check(pick(), "rexxlife")["fails"], [])


if __name__ == "__main__":
    unittest.main()
