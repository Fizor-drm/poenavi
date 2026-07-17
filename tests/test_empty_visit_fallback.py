import unittest

from src.utils.guide_data import get_zone_guide, get_mini_navi_content


class EmptyVisitFallbackTest(unittest.TestCase):
    def test_direction_only_visit_falls_back_to_visit1(self):
        guide_data = {
            "act8_area15": {
                "visits": {
                    "1": {
                        "objective": "first guide",
                        "direction": "nw",
                        "mini_navi": {"text": "first mini", "direction": "nw"},
                    },
                    "2": {"direction": "none"},
                }
            }
        }

        guide = get_zone_guide(guide_data, "act8_area15", visit=2, config={}, active_flags=set())
        mini = get_mini_navi_content(guide)

        self.assertEqual(guide["objective"], "first guide")
        self.assertEqual(mini, {"text": "first mini", "direction": "nw"})

    def test_empty_route_visit_falls_back_to_route_visit1(self):
        guide_data = {
            "act8_area15": {
                "visits": {
                    "1": {"objective": "standard first", "mini_navi": {"text": "standard mini", "direction": "none"}},
                },
                "routes": {
                    "underbelly": {
                        "visits": {
                            "1": {
                                "objective": "route first",
                                "direction": "ne",
                                "mini_navi": {"text": "route mini", "direction": "ne"},
                            },
                            "2": {"objective": "", "layout": "", "tips": "", "direction": "none"},
                        }
                    }
                },
            }
        }

        guide = get_zone_guide(
            guide_data,
            "act8_area15",
            visit=2,
            config={"poe1_route_act8": "underbelly"},
            active_flags=set(),
        )
        mini = get_mini_navi_content(guide)

        self.assertEqual(guide["objective"], "route first")
        self.assertEqual(mini, {"text": "route mini", "direction": "ne"})


if __name__ == "__main__":
    unittest.main()
