import json
import unittest
from pathlib import Path

from src.utils.guide_data import get_zone_guide, get_mini_navi_content


class Act8Temple2MiniNaviFallbackTest(unittest.TestCase):
    def test_underbelly_temple_level2_visit2_falls_back_to_visit1_mini_navi(self):
        guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))
        config = {"poe1_route_act8": "underbelly"}

        for zone_id in ("act8_area11", "act8_area16"):
            with self.subTest(zone_id=zone_id):
                guide = get_zone_guide(guide_data, zone_id, visit=2, config=config, active_flags=set())
                mini = get_mini_navi_content(guide)

                self.assertIsNotNone(mini)
                self.assertTrue(mini["text"].strip())


if __name__ == "__main__":
    unittest.main()
