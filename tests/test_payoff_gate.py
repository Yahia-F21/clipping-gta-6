"""Offline tests: a failing check or a missing payoff note blocks a normal render; --diagnostic is the only bypass."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clipper import __main__ as cli
from clipper import hooks


class PayoffGateTest(unittest.TestCase):
    def test_payoff_note_required(self):
        self.assertIn("video 1", hooks.check_payoff([{"start": 0, "end": 20, "hook": "x"}]))
        self.assertIn("video 1", hooks.check_payoff([{"payoff": "too short"}]))
        ok = {"payoff": "car flies off the pier, streamer screams as it sinks"}
        self.assertEqual(hooks.check_payoff([ok]), {})

    def test_long_dead_air_fails(self):
        pick = {"start": 0, "end": 30}
        words = [{"s": 0.0, "e": 1.0}, {"s": 2.0, "e": 3.0}, {"s": 12.0, "e": 13.0}, {"s": 13.5, "e": 14.0}]
        self.assertEqual(len(hooks.long_dead_air(pick, words)), 2)   # 3-12 s and 14-30 s
        self.assertEqual(hooks.long_dead_air(pick, [{"s": i, "e": i + 0.8} for i in range(0, 30)]), [])
        src = [dict(w, w="word", spk=0) for w in words]
        report = hooks.check_picks([pick], None, src)
        self.assertTrue(hooks.has_fails(report))

    def _run(self, picks, extra=()):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "picks.json"
            p.write_text(json.dumps(picks))
            with mock.patch.object(cli.render_mod, "render", return_value=[]) as rend, \
                    mock.patch.object(cli.config, "job_dir", return_value=Path(d)), \
                    mock.patch.object(cli, "job_words", return_value=[]):
                try:
                    cli.main(["render", "jobx", "--picks", str(p), *extra])
                    code = 0
                except SystemExit as e:
                    code = e.code
                return code, rend

    def test_render_blocked_without_payoff(self):
        pick = {"start": 0, "end": 20, "hook": "Did he really just do that?", "title": "t"}
        code, rend = self._run([pick])
        self.assertNotEqual(code, 0)
        rend.assert_not_called()

    def test_diagnostic_renders_into_diagnostic_folder(self):
        pick = {"start": 0, "end": 20, "hook": "Did he really just do that?", "title": "t"}
        code, rend = self._run([pick], ["--diagnostic"])
        self.assertEqual(code, 0)
        rend.assert_called_once()
        self.assertTrue(str(rend.call_args[0][4]).endswith("diagnostic"))


if __name__ == "__main__":
    unittest.main()
