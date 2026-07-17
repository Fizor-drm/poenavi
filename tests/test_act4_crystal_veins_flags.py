import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide


class Act4CrystalVeinsFlagsTest(unittest.TestCase):
    def test_crystal_veins_has_grand_arena_kaom_and_composite_flag_frames(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

        flags = guide_data["act4_area6"]["visits"]["1"].get("flags", {})

        for flag_key in (
            "act4_grandarena_enter",
            "act4_kaomstronghold_enter",
            "act4_grandarena_enter+act4_kaomstronghold_enter",
        ):
            with self.subTest(flag_key=flag_key):
                self.assertIn(flag_key, flags)
                self.assertIsInstance(flags[flag_key], dict)

    def test_single_and_composite_flags_select_three_different_guides(self):
        guide_data = {
            "act4_area6": {
                "visits": {
                    "1": {
                        "objective": "default objective",
                        "direction": "none",
                        "flags": {
                            "act4_grandarena_enter": {"objective": "grand arena only"},
                            "act4_kaomstronghold_enter": {"objective": "kaom only"},
                            "act4_grandarena_enter+act4_kaomstronghold_enter": {"objective": "both flags"},
                        },
                    },
                    "2": {"objective": "visit2 objective", "direction": "none"},
                }
            }
        }

        grand_guide = get_zone_guide(
            guide_data,
            "act4_area6",
            visit=2,
            active_flags={"act4_grandarena_enter"},
        )
        kaom_guide = get_zone_guide(
            guide_data,
            "act4_area6",
            visit=2,
            active_flags={"act4_kaomstronghold_enter"},
        )
        both_guide = get_zone_guide(
            guide_data,
            "act4_area6",
            visit=2,
            active_flags={"act4_grandarena_enter", "act4_kaomstronghold_enter"},
        )

        self.assertEqual(grand_guide["objective"], "grand arena only")
        self.assertEqual(kaom_guide["objective"], "kaom only")
        self.assertEqual(both_guide["objective"], "both flags")


if __name__ == "__main__":
    unittest.main()
