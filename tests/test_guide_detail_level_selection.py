import unittest
from unittest.mock import patch

try:
    from src.ui.main_window import MainWindow
except ModuleNotFoundError as exc:  # pragma: no cover - local dev without GUI deps
    MainWindow = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None

from src.utils.poe_version_data import POE1, POE2


class FakeGuideDetailLevelDialog:
    selected_level = "intermediate"
    calls = []

    def __init__(self, parent=None, current_level="beginner"):
        self.parent = parent
        self.current_level = current_level
        FakeGuideDetailLevelDialog.calls.append(current_level)

    def exec(self):
        return True


@unittest.skipIf(MainWindow is None, f"GUI dependencies unavailable: {IMPORT_ERROR}")
class GuideDetailLevelSelectionFlowTest(unittest.TestCase):
    def make_window(self, config):
        window = MainWindow.__new__(MainWindow)
        window.config = config
        return window

    def setUp(self):
        FakeGuideDetailLevelDialog.calls = []

    def test_poe1_does_not_show_guide_detail_level_selection(self):
        window = self.make_window({"poe_version": POE1, "guide_detail_level_selected": False})

        with patch("src.ui.main_window.GuideDetailLevelSelectionDialog", FakeGuideDetailLevelDialog), \
             patch("src.ui.main_window.ConfigManager.save_config") as save_config:
            self.assertTrue(window._ensure_guide_detail_level_selected_if_needed())

        self.assertEqual(FakeGuideDetailLevelDialog.calls, [])
        save_config.assert_not_called()

    def test_poe2_shows_guide_detail_level_selection_once_and_saves_choice(self):
        config = {
            "poe_version": POE2,
            "guide_detail_level": "beginner",
            "guide_detail_level_selected": False,
        }
        window = self.make_window(config)

        with patch("src.ui.main_window.GuideDetailLevelSelectionDialog", FakeGuideDetailLevelDialog), \
             patch("src.ui.main_window.ConfigManager.save_config") as save_config:
            self.assertTrue(window._ensure_guide_detail_level_selected_if_needed())

        self.assertEqual(FakeGuideDetailLevelDialog.calls, ["beginner"])
        self.assertEqual(config["guide_detail_level"], "intermediate")
        self.assertTrue(config["guide_detail_level_selected"])
        save_config.assert_called_once_with(config)

    def test_poe2_does_not_show_when_already_selected(self):
        config = {
            "poe_version": POE2,
            "guide_detail_level": "intermediate",
            "guide_detail_level_selected": True,
        }
        window = self.make_window(config)

        with patch("src.ui.main_window.GuideDetailLevelSelectionDialog", FakeGuideDetailLevelDialog), \
             patch("src.ui.main_window.ConfigManager.save_config") as save_config:
            self.assertTrue(window._ensure_guide_detail_level_selected_if_needed())

        self.assertEqual(FakeGuideDetailLevelDialog.calls, [])
        save_config.assert_not_called()


if __name__ == "__main__":
    unittest.main()
