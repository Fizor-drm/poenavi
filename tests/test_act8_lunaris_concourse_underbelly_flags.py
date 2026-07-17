import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide


FLAG_KEY = "act8_lunaristemple2_enter+act8_solaristemple2_enter"


class Act8LunarisConcourseUnderbellyFlagsTest(unittest.TestCase):
    def test_underbelly_route_has_both_temples_flag_frames(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

        visits = guide_data["act8_area14"]["routes"]["underbelly"]["visits"]

        for visit in ("1", "2"):
            with self.subTest(visit=visit):
                flags = visits[visit].get("flags", {})
                self.assertIn(FLAG_KEY, flags)
                self.assertIsInstance(flags[FLAG_KEY], dict)

    def test_underbelly_route_uses_composite_flag_guide_only_when_both_flags_are_active(self):
        guide_data = {
            "act8_area14": {
                "visits": {
                    "1": {"objective": "standard objective", "direction": "nw"},
                },
                "routes": {
                    "underbelly": {
                        "visits": {
                            "1": {
                                "objective": "underbelly default",
                                "direction": "ne",
                                "flags": {
                                    FLAG_KEY: {
                                        "objective": "both temples objective",
                                        "mini_navi": {"text": "both temples mini", "direction": "se"},
                                    }
                                },
                            },
                            "2": {
                                "objective": "underbelly visit2",
                                "direction": "sw",
                                "flags": {
                                    FLAG_KEY: {"objective": "both temples visit2"}
                                },
                            },
                        }
                    }
                },
            }
        }
        config = {"poe1_route_act8": "underbelly"}

        one_flag_guide = get_zone_guide(
            guide_data,
            "act8_area14",
            visit=1,
            config=config,
            active_flags={"act8_lunaristemple2_enter"},
        )
        both_flags_guide = get_zone_guide(
            guide_data,
            "act8_area14",
            visit=1,
            config=config,
            active_flags={"act8_lunaristemple2_enter", "act8_solaristemple2_enter"},
        )
        both_flags_visit2_guide = get_zone_guide(
            guide_data,
            "act8_area14",
            visit=2,
            config=config,
            active_flags={"act8_lunaristemple2_enter", "act8_solaristemple2_enter"},
        )

        self.assertEqual(one_flag_guide["objective"], "underbelly default")
        self.assertEqual(both_flags_guide["objective"], "both temples objective")
        self.assertEqual(both_flags_guide["mini_navi"], {"text": "both temples mini", "direction": "se"})
        self.assertEqual(both_flags_visit2_guide["objective"], "both temples visit2")

    def test_standard_route_does_not_use_underbelly_flag_guide(self):
        guide_data = {
            "act8_area14": {
                "visits": {"1": {"objective": "standard objective", "direction": "nw"}},
                "routes": {
                    "underbelly": {
                        "visits": {
                            "1": {
                                "objective": "underbelly default",
                                "flags": {FLAG_KEY: {"objective": "both temples objective"}},
                            }
                        }
                    }
                },
            }
        }

        guide = get_zone_guide(
            guide_data,
            "act8_area14",
            visit=1,
            config={"poe1_route_act8": "standard"},
            active_flags={"act8_lunaristemple2_enter", "act8_solaristemple2_enter"},
        )

        self.assertEqual(guide["objective"], "standard objective")


if __name__ == "__main__":
    unittest.main()
