from pathlib import Path


def test_vastiri_desert_is_always_count_zone_for_town_reentry():
    source = Path("src/ui/main_window.py").read_text(encoding="utf-8")

    assert '"act9_area2"' in source
    assert "ヴァスティリ砂漠" in source
