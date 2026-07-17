from src.ui.main_window import MainWindow


class DummyWindow:
    _mini_navi_exp_guide = MainWindow._mini_navi_exp_guide


def test_mini_navi_exp_guide_is_hidden_for_excluded_zone():
    window = DummyWindow()
    window.monster_levels = {
        "act10_area8": {"lv": 0, "exclude": "non_combat"},
        "act10_area9": {"lv": 66},
    }
    window.player_level = 63

    assert window._mini_navi_exp_guide(46, zone_id="act10_area8") is None
    assert window._mini_navi_exp_guide(66, zone_id="act10_area9") is not None
