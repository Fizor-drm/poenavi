import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide
from src.utils.poe_version_data import POE1
from src.utils.zone_master_data import load_zone_data_by_version


class Act9VastiriDesertFlagTest(unittest.TestCase):
    def test_vastiri_desert_has_oasis_flag_frame(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

        flags = guide_data["act9_area2"]["visits"]["1"].get("flags", {})

        self.assertIn("act9_oasis_enter", flags)
        self.assertIsInstance(flags["act9_oasis_enter"], dict)

    def test_act9_vastiri_desert_and_oasis_zone_ids(self):
        zone_data = load_zone_data_by_version()[POE1]
        vastiri = [z for z in zone_data["Act 9"] if z["zone"] == "ヴァスティリ砂漠"]
        oasis = [z for z in zone_data["Act 9"] if z["zone"] == "オアシス"]

        self.assertEqual(vastiri[0]["id"], "act9_area2")
        self.assertEqual(oasis[0]["id"], "act9_area3")

    def test_oasis_flag_selects_flag_guide_on_revisit(self):
        guide_data = {
            "act9_area2": {
                "visits": {
                    "1": {
                        "objective": "default objective",
                        "direction": "none",
                        "flags": {
                            "act9_oasis_enter": {
                                "objective": "act9 oasis flag objective",
                                "mini_navi": {"text": "act9 oasis mini", "direction": "n"},
                            }
                        },
                    },
                    "2": {"objective": "visit2 objective", "direction": "n"},
                }
            }
        }

        default_guide = get_zone_guide(
            guide_data,
            "act9_area2",
            visit=2,
            active_flags=set(),
        )
        flag_guide = get_zone_guide(
            guide_data,
            "act9_area2",
            visit=2,
            active_flags={"act9_oasis_enter"},
        )

        self.assertEqual(default_guide["objective"], "visit2 objective")
        self.assertEqual(flag_guide["objective"], "act9 oasis flag objective")
        self.assertEqual(flag_guide["mini_navi"], {"text": "act9 oasis mini", "direction": "n"})


if __name__ == "__main__":
    unittest.main()
