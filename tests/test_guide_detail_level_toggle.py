import unittest
from unittest.mock import Mock, patch

try:
    from src.ui.main_window import MainWindow
except ModuleNotFoundError as exc:  # pragma: no cover - local dev without GUI deps
    MainWindow = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None

from src.utils.poe_version_data import POE2


@unittest.skipIf(MainWindow is None, f"GUI dependencies unavailable: {IMPORT_ERROR}")
class GuideDetailLevelToggleTest(unittest.TestCase):
    def make_window(self):
        window = MainWindow.__new__(MainWindow)
        window.config = {"guide_detail_level": "beginner"}
        window.poe_version = POE2
        window.current_zone = "The Grelwood"
        window.zone_visit_counts = {"poe2_act1_area04": 2}
        window.guide_expanded = True
        window.guide_detail_level_toggle_btn = Mock()
        window._get_zone_id = Mock(return_value="poe2_act1_area04")
        window._update_guide_and_map = Mock()
        return window

    def test_toggle_guide_detail_level_saves_and_refreshes_current_guide(self):
        window = self.make_window()

        with patch("src.ui.main_window.ConfigManager.save_config") as save_config:
            window.toggle_guide_detail_level()

        self.assertEqual(window.config["guide_detail_level"], "intermediate")
        self.assertTrue(window.config["guide_detail_level_selected"])
        save_config.assert_called_once_with(window.config)
        window.guide_detail_level_toggle_btn.setText.assert_called_with("要点版ガイド")
        window._update_guide_and_map.assert_called_once_with(
            "The Grelwood", "poe2_act1_area04", 2
        )


if __name__ == "__main__":
    unittest.main()
