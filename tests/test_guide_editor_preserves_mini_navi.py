import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.ui.settings_dialog import GuideEditorDialog


class GuideEditorPreservesMiniNaviTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_normal_guide_save_preserves_existing_mini_navi(self):
        guide = {
            "objective": "old objective",
            "layout": "",
            "tips": "",
            "direction": "sw",
            "mini_navi": {"text": "mini text", "direction": "sw"},
        }
        dialog = GuideEditorDialog(None, "Test Zone", guide, zone_id="act2_area7")
        dialog.objective_edit.setPlainText("new objective")

        result = dialog.get_guide()

        self.assertEqual(result["objective"], "new objective")
        self.assertEqual(result["mini_navi"], {"text": "mini text", "direction": "sw"})

    def test_second_visit_guide_save_preserves_existing_mini_navi(self):
        guide_v2 = {
            "objective": "second objective",
            "layout": "",
            "tips": "",
            "mini_navi": {"text": "second mini", "direction": "nw"},
        }
        dialog = GuideEditorDialog(None, "Test Zone", {}, guide_v2=guide_v2, zone_id="act2_area7")

        result = dialog.get_guide_v2()

        self.assertEqual(result["mini_navi"], {"text": "second mini", "direction": "nw"})

    def test_flag_and_route_guides_save_preserve_existing_mini_navi(self):
        flag_guides = {
            "act2_flag": {
                "objective": "flag objective",
                "mini_navi": {"text": "flag mini", "direction": "n"},
            }
        }
        route_guides = {
            "~library_detour": {
                "objective": "route objective",
                "mini_navi": {"text": "route mini", "direction": "e"},
            }
        }
        dialog = GuideEditorDialog(
            None,
            "Test Zone",
            {},
            zone_id="act3_area14",
            flag_guides=flag_guides,
            route_guides=route_guides,
        )

        self.assertEqual(
            dialog.get_flag_guides()["act2_flag"]["mini_navi"],
            {"text": "flag mini", "direction": "n"},
        )
        self.assertEqual(
            dialog.get_route_guides()["~library_detour"]["mini_navi"],
            {"text": "route mini", "direction": "e"},
        )


if __name__ == "__main__":
    unittest.main()
