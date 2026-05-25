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


class UserDataFileMigrationTest(unittest.TestCase):
    def test_legacy_user_file_is_copied_to_user_data_without_overwriting_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            app_dir = Path(tmp) / "app"
            user_dir = (Path(tmp) / "user-data").resolve()
            app_dir.mkdir()
            user_dir.mkdir()
            legacy = app_dir / "notes_poe1.json"
            legacy.write_text(json.dumps({"content": "legacy"}), encoding="utf-8")

            with patch.dict(os.environ, {ConfigManager.ENV_USER_DATA_DIR: str(user_dir)}), \
                 patch.object(ConfigManager, "get_app_dir", return_value=app_dir):
                migrated = ConfigManager.migrate_legacy_user_file("notes_poe1.json")
                self.assertEqual(migrated, user_dir / "notes_poe1.json")
                self.assertEqual(json.loads(migrated.read_text(encoding="utf-8"))["content"], "legacy")
                self.assertFalse(legacy.exists())

                migrated.write_text(json.dumps({"content": "user"}), encoding="utf-8")
                legacy.write_text(json.dumps({"content": "changed-legacy"}), encoding="utf-8")
                migrated_again = ConfigManager.migrate_legacy_user_file("notes_poe1.json")
                self.assertEqual(json.loads(migrated_again.read_text(encoding="utf-8"))["content"], "user")
                self.assertFalse(legacy.exists())


@unittest.skipIf(MainWindow is None, f"GUI dependencies unavailable: {IMPORT_ERROR}")
class MainWindowUserDataPathTest(unittest.TestCase):
    def make_window(self, poe_version):
        window = MainWindow.__new__(MainWindow)
        window.poe_version = poe_version
        return window

    def test_vendor_presets_and_progress_flags_use_user_data_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {ConfigManager.ENV_USER_DATA_DIR: tmp}):
                window = self.make_window(POE2)
                self.assertEqual(Path(window._vendor_search_presets_path()), Path(tmp).resolve() / "vendor_search_presets.json")
                self.assertEqual(Path(window._progress_flags_path()), Path(tmp).resolve() / "progress_flags_poe2.json")

    def test_notes_paths_are_user_data_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {ConfigManager.ENV_USER_DATA_DIR: tmp}):
                self.assertEqual(ConfigManager.get_user_data_path("notes_poe1.json"), Path(tmp).resolve() / "notes_poe1.json")
                self.assertEqual(ConfigManager.get_user_data_path("notes_poe2.json"), Path(tmp).resolve() / "notes_poe2.json")


if __name__ == "__main__":
    unittest.main()
