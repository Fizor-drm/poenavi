import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from src.ui.main_window import MainWindow
except ModuleNotFoundError as exc:  # pragma: no cover - local dev without GUI deps
    MainWindow = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None

from src.utils.config_manager import ConfigManager
from src.utils.poe_version_data import POE1, POE2


@unittest.skipIf(MainWindow is None, f"GUI dependencies unavailable: {IMPORT_ERROR}")
class TimerStateStorageTest(unittest.TestCase):
    def make_window(self, poe_version=POE1):
        window = MainWindow.__new__(MainWindow)
        window.poe_version = poe_version
        window.config = {"poe_version": poe_version}
        window.accumulated_time = 12.5
        window.lap_times = [1.0, None]
        window.lap_record_order = [1]
        window.current_act = 2
        return window

    def test_timer_state_is_saved_to_user_data_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {ConfigManager.ENV_USER_DATA_DIR: tmp}):
                window = self.make_window(POE2)

                window._save_timer_state()

                path = Path(tmp) / "timer_poe2.json"
                self.assertTrue(path.exists())
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data["accumulated_time"], 12.5)
                self.assertEqual(data["current_act"], 2)
                self.assertNotIn("saved_timer::timer_poe2.json", window.config)

    def test_legacy_config_timer_state_is_migrated_and_removed_from_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {ConfigManager.ENV_USER_DATA_DIR: tmp}):
                legacy_key = "saved_timer::timer_poe1.json"
                legacy_payload = {
                    "accumulated_time": 34.0,
                    "lap_times": [2.0],
                    "lap_record_order": [1],
                    "current_act": 1,
                }
                window = self.make_window(POE1)
                window.config = {
                    "poe_version": POE1,
                    legacy_key: legacy_payload,
                }

                migrated = window._migrate_legacy_timer_state_from_config()

                self.assertEqual(migrated, legacy_payload)
                self.assertNotIn(legacy_key, window.config)
                path = Path(tmp) / "timer_poe1.json"
                self.assertTrue(path.exists())
                self.assertEqual(json.loads(path.read_text(encoding="utf-8")), legacy_payload)
                saved_config = ConfigManager.load_config()
                self.assertNotIn(legacy_key, saved_config)


if __name__ == "__main__":
    unittest.main()
