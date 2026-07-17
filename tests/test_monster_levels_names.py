import json
from pathlib import Path


def test_act10_aspirants_plaza_monster_level_name_matches_zone_data():
    zone_master = json.loads(Path("data/zone_data.json").read_text(encoding="utf-8"))
    zone_data = zone_master["zone_data_by_version"]["poe1"]
    monster_levels = json.loads(Path("monster_levels.json").read_text(encoding="utf-8"))

    act10_area8 = None
    for zone in zone_data["Act 10"]:
        if zone.get("id") == "act10_area8":
            act10_area8 = zone
            break

    assert act10_area8 is not None
    assert act10_area8["zone"] == "志す者の広場"
    assert monster_levels["act10_area8"]["en"] == act10_area8["zone_en"]
    assert monster_levels["act10_area8"]["exclude"] == "non_combat"
