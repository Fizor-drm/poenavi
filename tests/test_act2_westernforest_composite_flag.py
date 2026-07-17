import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide


class Act2WesternForestCompositeFlagTest(unittest.TestCase):
    def test_western_forest_has_weavers_and_wetlands_composite_flag_frame(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

        flags = guide_data["act2_area8"]["visits"]["1"].get("flags", {})

        self.assertIn("act2_weaverschambers_enter+act2_wetlands_enter", flags)
        self.assertIsInstance(flags["act2_weaverschambers_enter+act2_wetlands_enter"], dict)

    def test_composite_flag_requires_both_flags(self):
        guide_data = {
            "act2_area8": {
                "visits": {
                    "1": {
                        "objective": "default objective",
                        "direction": "none",
                        "mini_navi": {"text": "default mini", "direction": "none"},
                        "flags": {
                            "act2_weaverschambers_enter+act2_wetlands_enter": {
                                "objective": "both flags objective",
                                "mini_navi": {"text": "both flags mini", "direction": "sw"},
                            }
                        },
                    }
                }
            }
        }

        one_flag_guide = get_zone_guide(
            guide_data,
            "act2_area8",
            visit=1,
            active_flags={"act2_weaverschambers_enter"},
        )
        both_flags_guide = get_zone_guide(
            guide_data,
            "act2_area8",
            visit=1,
            active_flags={"act2_weaverschambers_enter", "act2_wetlands_enter"},
        )

        self.assertEqual(one_flag_guide["objective"], "default objective")
        self.assertEqual(both_flags_guide["objective"], "both flags objective")
        self.assertEqual(both_flags_guide["mini_navi"], {"text": "both flags mini", "direction": "sw"})


if __name__ == "__main__":
    unittest.main()
