import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide
from src.utils.zone_master_data import load_zone_data_by_version
from src.utils.poe_version_data import POE1


class Act6RiverwaysFlagTest(unittest.TestCase):
    def test_riverways_has_act6_wetlands_flag_frame(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

        flags = guide_data["act6_area10"]["visits"]["1"].get("flags", {})

        self.assertIn("act6_wetlands_enter", flags)
        self.assertIsInstance(flags["act6_wetlands_enter"], dict)

    def test_act2_and_act6_wetlands_have_distinct_zone_ids(self):
        act2_wetlands = [z for z in load_zone_data_by_version()[POE1]["Act 2"] if z["zone"] == "湿地"]
        act6_wetlands = [z for z in load_zone_data_by_version()[POE1]["Act 6"] if z["zone"] == "湿地"]

        self.assertEqual(act2_wetlands[0]["id"], "act2_area14")
        self.assertEqual(act6_wetlands[0]["id"], "act6_area11")

    def test_act6_wetlands_flag_selects_flag_guide_on_revisit(self):
        guide_data = {
            "act6_area10": {
                "visits": {
                    "1": {
                        "objective": "default objective",
                        "direction": "nw",
                        "flags": {
                            "act6_wetlands_enter": {
                                "objective": "act6 wetlands flag objective",
                                "mini_navi": {"text": "act6 wetlands mini", "direction": "sw"},
                            }
                        },
                    },
                    "2": {"objective": "visit2 objective", "direction": "sw"},
                }
            }
        }

        default_guide = get_zone_guide(
            guide_data,
            "act6_area10",
            visit=2,
            active_flags={"act2_wetlands_enter"},
        )
        flag_guide = get_zone_guide(
            guide_data,
            "act6_area10",
            visit=2,
            active_flags={"act6_wetlands_enter"},
        )

        self.assertEqual(default_guide["objective"], "visit2 objective")
        self.assertEqual(flag_guide["objective"], "act6 wetlands flag objective")
        self.assertEqual(flag_guide["mini_navi"], {"text": "act6 wetlands mini", "direction": "sw"})


if __name__ == "__main__":
    unittest.main()
