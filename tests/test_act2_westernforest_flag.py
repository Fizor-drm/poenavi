import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide


class Act2WesternForestFlagTest(unittest.TestCase):
    def test_riverways_has_western_forest_flag_frame(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

        flags = guide_data["act2_area7"]["visits"]["1"].get("flags", {})

        self.assertIn("act2_westernforest_enter", flags)
        self.assertIsInstance(flags["act2_westernforest_enter"], dict)

    def test_flagged_riverways_guide_overrides_default_when_edited(self):
        guide_data = {
            "act2_area7": {
                "visits": {
                    "1": {
                        "objective": "default objective",
                        "direction": "sw",
                        "mini_navi": {"text": "default mini", "direction": "sw"},
                        "flags": {
                            "act2_westernforest_enter": {
                                "objective": "flag objective",
                                "mini_navi": {"text": "flag mini", "direction": "nw"},
                            }
                        },
                    }
                }
            }
        }

        guide = get_zone_guide(
            guide_data,
            "act2_area7",
            visit=1,
            active_flags={"act2_westernforest_enter"},
        )

        self.assertEqual(guide["objective"], "flag objective")
        self.assertEqual(guide["direction"], "sw")
        self.assertEqual(guide["mini_navi"], {"text": "flag mini", "direction": "nw"})


if __name__ == "__main__":
    unittest.main()
