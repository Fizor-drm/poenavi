import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.ui.settings_dialog import MiniNaviEditorDialog


class MiniNaviEditorDirectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_inherit_option_is_available_for_second_visit_and_removes_direction_override(self):
        guide = {
            "objective": "2回目ガイド",
            "direction": "ne",
            "mini_navi": {"text": "2回目みになび", "direction": "ne"},
        }
        dialog = MiniNaviEditorDialog(
            None,
            "テスト (act8_area15)",
            [{"kind": "visit", "title": "2回目", "visit": 2, "route": "", "guide": guide}],
        )
        item = dialog.section_editors[0]
        values = {button.property("dir_value") for button in item["direction"].buttons()}
        self.assertIn("inherit", values)
        item["editor"].setPlainText("2回目みになび")
        for button in item["direction"].buttons():
            if button.property("dir_value") == "inherit":
                button.setChecked(True)
                break

        dialog.apply_to_sections()

        self.assertNotIn("direction", guide)
        self.assertEqual(guide["mini_navi"], {"text": "2回目みになび"})

    def test_inherit_option_is_not_available_for_first_visit_base_guide(self):
        guide = {
            "objective": "1回目ガイド",
            "direction": "ne",
        }
        dialog = MiniNaviEditorDialog(
            None,
            "テスト (act8_area15)",
            [{"kind": "visit", "title": "1回目", "visit": 1, "route": "", "guide": guide}],
        )
        item = dialog.section_editors[0]
        values = {button.property("dir_value") for button in item["direction"].buttons()}

        self.assertNotIn("inherit", values)

    def test_direction_only_change_updates_guide_direction_and_mini_navi(self):
        guide = {
            "objective": "右上へ進み、帝国の庭園へ",
            "direction": "ne",
        }
        dialog = MiniNaviEditorDialog(
            None,
            "黒檀の兵舎 (act3_area11)",
            [{"kind": "visit", "title": "2回目", "visit": 2, "route": "", "guide": guide}],
        )
        item = dialog.section_editors[0]
        item["editor"].setPlainText("")
        for button in item["direction"].buttons():
            if button.property("dir_value") == "e":
                button.setChecked(True)
                break

        dialog.apply_to_sections()

        self.assertEqual(guide["direction"], "e")
        self.assertEqual(guide["mini_navi"], {"text": "", "direction": "e"})


if __name__ == "__main__":
    unittest.main()
