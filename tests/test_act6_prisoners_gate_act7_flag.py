import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide
from src.utils.zone_master_data import load_zone_data_by_version
from src.utils.poe_version_data import POE1


class Act6PrisonersGateAct7FlagTest(unittest.TestCase):
    def test_maligaro_sanctum_zone_id(self):
        zone_data = load_zone_data_by_version()[POE1]
        sanctum = [z for z in zone_data["Act 7"] if z["zone"] == "マリガロの聖域"]

        self.assertEqual(sanctum[0]["id"], "act7_area6")
        self.assertEqual(sanctum[0]["zone_en"], "Maligaro's Sanctum")

    def test_prisoners_gate_has_act7_maligaro_flag_frame(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))
        visit1 = guide_data["act6_area8"]["visits"]["1"]
        flags = visit1.get("flags", {})

        self.assertIn("act7_maligarosanctum_enter", flags)
        self.assertIsInstance(flags["act7_maligarosanctum_enter"], dict)

    def test_act7_maligaro_flag_selects_prisoners_gate_flag_guide(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

        default_guide = get_zone_guide(
            guide_data,
            "act6_area8",
            visit=1,
            active_flags=set(),
        )
        flag_guide = get_zone_guide(
            guide_data,
            "act6_area8",
            visit=1,
            active_flags={"act7_maligarosanctum_enter"},
        )

        self.assertNotEqual(default_guide, flag_guide)
        self.assertEqual(flag_guide.get("direction"), "none")


if __name__ == "__main__":
    unittest.main()
