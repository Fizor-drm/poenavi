import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide


class Act3EbonyBarracksCompositeFlagTest(unittest.TestCase):
    def test_ebony_barracks_has_solaris_and_lunaris_composite_flag_frame(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

        flags = guide_data["act3_area11"]["visits"]["1"].get("flags", {})

        self.assertIn("act3_solaris_enter+act3_lunaris_enter", flags)
        self.assertIsInstance(flags["act3_solaris_enter+act3_lunaris_enter"], dict)

    def test_composite_flag_requires_both_flags_and_applies_on_revisit(self):
        guide_data = {
            "act3_area11": {
                "visits": {
                    "1": {
                        "objective": "default objective",
                        "direction": "nw",
                        "mini_navi": {"text": "default mini", "direction": "nw"},
                        "flags": {
                            "act3_solaris_enter+act3_lunaris_enter": {
                                "objective": "both flags objective",
                                "mini_navi": {"text": "both flags mini", "direction": "ne"},
                            }
                        },
                    },
                    "2": {
                        "objective": "visit2 objective",
                        "direction": "ne",
                        "mini_navi": {"text": "visit2 mini", "direction": "ne"},
                    },
                }
            }
        }

        one_flag_guide = get_zone_guide(
            guide_data,
            "act3_area11",
            visit=2,
            active_flags={"act3_solaris_enter"},
        )
        both_flags_guide = get_zone_guide(
            guide_data,
            "act3_area11",
            visit=2,
            active_flags={"act3_solaris_enter", "act3_lunaris_enter"},
        )

        self.assertEqual(one_flag_guide["objective"], "visit2 objective")
        self.assertEqual(both_flags_guide["objective"], "both flags objective")
        self.assertEqual(both_flags_guide["mini_navi"], {"text": "both flags mini", "direction": "ne"})


if __name__ == "__main__":
    unittest.main()
