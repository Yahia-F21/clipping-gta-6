"""Live-recorder reliability: capped HLS-resolve backoff with a hard fail limit, and stall detection
for an ffmpeg that stays alive but writes nothing. No network: subprocess/probe/sleep are faked."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clipper import live


class ResolveBackoffTests(unittest.TestCase):
    def test_doubles_then_caps(self):
        waits = [live.resolve_backoff(n) for n in range(1, 9)]
        self.assertEqual(waits, [5, 10, 20, 40, 80, 120, 120, 120])

    def test_first_wait_is_the_base(self):
        self.assertEqual(live.resolve_backoff(1), live.RESOLVE_BACKOFF_BASE_S)


class StallWatchTests(unittest.TestCase):
    def test_growth_never_flags(self):
        w = live.StallWatch(stall_s=180)
        self.assertFalse(w.update(1000, 0))
        self.assertFalse(w.update(2000, 100))

    def test_flat_bytes_flag_after_stall_seconds(self):
        w = live.StallWatch(stall_s=180)
        self.assertFalse(w.update(1000, 0))
        self.assertFalse(w.update(1000, 100))   # flatness noticed here
        self.assertFalse(w.update(1000, 279))
        self.assertTrue(w.update(1000, 280))

    def test_growth_resets_the_clock(self):
        w = live.StallWatch(stall_s=180)
        w.update(1000, 0)
        w.update(1000, 100)
        self.assertFalse(w.update(2000, 190))   # grew: reset
        self.assertFalse(w.update(2000, 300))   # flat again: the clock starts here
        self.assertFalse(w.update(2000, 479))
        self.assertTrue(w.update(2000, 480))

    def test_shrinking_bytes_count_as_stall(self):
        w = live.StallWatch(stall_s=60)
        w.update(1000, 0)
        self.assertFalse(w.update(500, 61))     # smaller than before: the clock starts here
        self.assertTrue(w.update(500, 121))


class ResolveFailCapTests(unittest.TestCase):
    @mock.patch.object(live.time, "sleep")
    @mock.patch.object(live.subprocess, "run")
    @mock.patch.object(live, "probe")
    def test_recorder_gives_up_after_the_cap(self, probe, run, sleep):
        probe.return_value = {"live": True, "title": "t", "channel": "c"}
        run.return_value = subprocess.CompletedProcess([], 1, "", "boom")
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(live, "WORK", Path(td)):
                live.record("Some Stream", "http://example.invalid/x", cfg=None)
        self.assertEqual(run.call_count, live.MAX_RESOLVE_FAILS)
        # backoff waits between attempts, no wait before the give-up break
        self.assertEqual(sleep.call_count, live.MAX_RESOLVE_FAILS - 1)
        sleep.assert_any_call(live.RESOLVE_BACKOFF_BASE_S)
        # the pid file is released so the next watch pass can start a fresh recorder
        self.assertEqual(list(Path(td).rglob("pid")), [])


if __name__ == "__main__":
    unittest.main()
