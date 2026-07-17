import json
from pathlib import Path

from src.utils.guide_data import get_zone_guide, get_mini_navi_content


def test_act10_area11_contains_integrated_clear_guide():
    guide_data = json.loads(Path("guide_data.json").read_text(encoding="utf-8"))

    guide = get_zone_guide(guide_data, "act10_area11", visit=1, config={}, active_flags=set())
    mini = get_mini_navi_content(guide)

    assert "Act10クリア" in guide["objective"]
    assert "オリアスの船着場" in guide["objective"]
    assert "カルイの海岸" in guide["objective"]
    assert "ラニ" in guide["objective"]
    assert "/passives" in guide["objective"]
    assert mini is not None
    assert "オリアスの船着場" in mini["text"]
    assert "カルイの海岸" in mini["text"]
    assert "/passives" in mini["text"]


def test_act10_clear_handler_uses_act10_area11_guide():
    source = Path("src/ui/main_window.py").read_text(encoding="utf-8")

    assert 'zone_id = "act10_area11"' in source
    assert 'zone_name = "渇望の祭壇"' in source
    assert 'get_clear_message(self.poe_version, "final")' not in source
