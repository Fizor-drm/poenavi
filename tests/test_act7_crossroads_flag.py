import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide
from src.utils.zone_master_data import load_zone_data_by_version
from src.utils.poe_version_data import POE1


class Act7CrossroadsFlagTest(unittest.TestCase):
    def test_crossroads_has_act7_crypt_flag_frame(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

        flags = guide_data["act7_area2"]["visits"]["1"].get("flags", {})

        self.assertIn("act7_crypt_enter", flags)
        self.assertIsInstance(flags["act7_crypt_enter"], dict)

    def test_act2_and_act7_crypt_have_distinct_zone_ids(self):
        act2_crypt_ids = [z["id"] for z in load_zone_data_by_version()[POE1]["Act 2"] if z["zone"].startswith("地下聖堂")]
        act7_crypt = [z for z in load_zone_data_by_version()[POE1]["Act 7"] if z["zone"] == "地下聖堂"]

        self.assertEqual(act2_crypt_ids, ["act2_area12", "act2_area13"])
        self.assertEqual(act7_crypt[0]["id"], "act7_area4")

    def test_act7_crypt_flag_selects_flag_guide_on_revisit(self):
        guide_data = {
            "act7_area2": {
                "visits": {
                    "1": {
                        "objective": "default objective",
                        "direction": "none",
                        "flags": {
                            "act7_crypt_enter": {
                                "objective": "act7 crypt flag objective",
                                "mini_navi": {"text": "act7 crypt mini", "direction": "se"},
                            }
                        },
                    },
                    "2": {"objective": "visit2 objective", "direction": "se"},
                }
            }
        }

        default_guide = get_zone_guide(
            guide_data,
            "act7_area2",
            visit=2,
            active_flags={"act2_crypt_enter"},
        )
        flag_guide = get_zone_guide(
            guide_data,
            "act7_area2",
            visit=2,
            active_flags={"act7_crypt_enter"},
        )

        self.assertEqual(default_guide["objective"], "visit2 objective")
        self.assertEqual(flag_guide["objective"], "act7 crypt flag objective")
        self.assertEqual(flag_guide["mini_navi"], {"text": "act7 crypt mini", "direction": "se"})


if __name__ == "__main__":
    unittest.main()
