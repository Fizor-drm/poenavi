import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide


class Act5RuinedSquareFlagTest(unittest.TestCase):
    def test_ruined_square_has_reliquary_flag_frame(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

        flags = guide_data["act5_area7"]["visits"]["1"].get("flags", {})

        self.assertIn("act5_reliquary_enter", flags)
        self.assertIsInstance(flags["act5_reliquary_enter"], dict)

    def test_reliquary_flag_selects_flag_guide_on_revisit(self):
        guide_data = {
            "act5_area7": {
                "visits": {
                    "1": {
                        "objective": "default objective",
                        "direction": "sw",
                        "flags": {
                            "act5_reliquary_enter": {
                                "objective": "reliquary flag objective",
                                "mini_navi": {"text": "reliquary mini", "direction": "nw"},
                            }
                        },
                    },
                    "2": {"objective": "visit2 objective", "direction": "nw"},
                }
            }
        }

        default_guide = get_zone_guide(
            guide_data,
            "act5_area7",
            visit=2,
            active_flags=set(),
        )
        flag_guide = get_zone_guide(
            guide_data,
            "act5_area7",
            visit=2,
            active_flags={"act5_reliquary_enter"},
        )

        self.assertEqual(default_guide["objective"], "visit2 objective")
        self.assertEqual(flag_guide["objective"], "reliquary flag objective")
        self.assertEqual(flag_guide["mini_navi"], {"text": "reliquary mini", "direction": "nw"})


if __name__ == "__main__":
    unittest.main()
