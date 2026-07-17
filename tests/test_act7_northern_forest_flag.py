import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide
from src.utils.zone_master_data import load_zone_data_by_version
from src.utils.poe_version_data import POE1


class Act7NorthernForestFlagTest(unittest.TestCase):
    def test_northern_forest_has_act7_dread_thicket_flag_frame(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

        flags = guide_data["act7_area10"]["visits"]["1"].get("flags", {})

        self.assertIn("act7_dreadthicket_enter", flags)
        self.assertIsInstance(flags["act7_dreadthicket_enter"], dict)

    def test_act2_and_act7_northern_forest_have_distinct_zone_ids(self):
        act2_northern = [z for z in load_zone_data_by_version()[POE1]["Act 2"] if z["zone"] == "北の森"]
        act7_northern = [z for z in load_zone_data_by_version()[POE1]["Act 7"] if z["zone"] == "北の森"]
        act7_dread = [z for z in load_zone_data_by_version()[POE1]["Act 7"] if z["zone"] == "恐怖の密林"]

        self.assertEqual(act2_northern[0]["id"], "act2_area16")
        self.assertEqual(act7_northern[0]["id"], "act7_area10")
        self.assertEqual(act7_dread[0]["id"], "act7_area12")

    def test_act7_dread_thicket_flag_selects_flag_guide_on_revisit(self):
        guide_data = {
            "act7_area10": {
                "visits": {
                    "1": {
                        "objective": "default objective",
                        "direction": "sw",
                        "flags": {
                            "act7_dreadthicket_enter": {
                                "objective": "act7 dread thicket flag objective",
                                "mini_navi": {"text": "act7 dread mini", "direction": "n"},
                            }
                        },
                    },
                    "2": {"objective": "visit2 objective", "direction": "n"},
                }
            }
        }

        default_guide = get_zone_guide(
            guide_data,
            "act7_area10",
            visit=2,
            active_flags={"act2_dreadthicket_enter"},
        )
        flag_guide = get_zone_guide(
            guide_data,
            "act7_area10",
            visit=2,
            active_flags={"act7_dreadthicket_enter"},
        )

        self.assertEqual(default_guide["objective"], "visit2 objective")
        self.assertEqual(flag_guide["objective"], "act7 dread thicket flag objective")
        self.assertEqual(flag_guide["mini_navi"], {"text": "act7 dread mini", "direction": "n"})


if __name__ == "__main__":
    unittest.main()

class Act7DreadThicketMasterDataTest(unittest.TestCase):
    def test_act2_and_act7_dread_thicket_have_distinct_zone_ids_in_runtime_master(self):
        zone_data = load_zone_data_by_version()[POE1]
        act2_dread = [z for z in zone_data["Act 2"] if z.get("zone") == "恐怖の密林" or z.get("zone_en") == "The Dread Thicket"]
        act7_dread = [z for z in zone_data["Act 7"] if z.get("zone") == "恐怖の密林" or z.get("zone_en") == "The Dread Thicket"]

        self.assertEqual(act2_dread[0]["id"], "act2_area19")
        self.assertEqual(act7_dread[0]["id"], "act7_area12")
