from unittest.mock import patch

from src.poetore.parser import parse_item_text
from src.poetore.trade import (
    PriceListing, PriceResult, TradeStatFilter, active_pc_league, build_search_query, physical_dps,
    resolve_trade_stat_filters, search_prices,
)


ITEM = """Item Class: Two Hand Swords
Rarity: Rare
Doom Sever
Reaver Sword
--------
Two Hand Sword
Physical Damage: 108-181 (augmented)
Attacks per Second: 1.74 (augmented)
--------
Item Level: 67
--------
74% increased Physical Damage
"""


def test_weapon_search_uses_english_base_rarity_and_comparable_pdps():
    item = parse_item_text(ITEM)
    query = build_search_query(item, "Reaver Sword")["query"]
    assert query["type"] == "Reaver Sword"
    assert query["filters"]["type_filters"]["filters"]["rarity"]["option"] == "rare"
    assert query["filters"]["weapon_filters"]["filters"]["pdps"]["min"] == 201.1
    assert round(physical_dps(item), 2) == 251.43


def test_enabled_stat_filter_is_added_with_editable_minimum():
    item = parse_item_text(ITEM)
    stat = TradeStatFilter("explicit.stat_1", "Physical", 74, "prefix", True)
    query = build_search_query(item, "Reaver Sword", (stat,))["query"]
    assert query["stats"][0]["filters"] == [
        {"id": "explicit.stat_1", "value": {"min": 74}},
    ]


def test_japanese_modifier_resolves_to_official_trade_stat_id():
    item = parse_item_text(ITEM.replace("74% increased Physical Damage", "物理ダメージが74%\u5897加する"))
    entries = ({"id": "explicit.stat_1509134228", "text": "物理ダメージが#%増加する", "type": "explicit"},)
    with patch("src.poetore.trade._trade_stat_entries", return_value=entries):
        filters = resolve_trade_stat_filters(item)
    assert filters == (TradeStatFilter(
        "explicit.stat_1509134228", "物理ダメージが74%増加する", 74, "explicit", False,
    ),)


def test_hybrid_and_duplicate_stats_resolve_with_correct_values_and_sum():
    item = parse_item_text("""アイテムクラス: 両手剣
レアリティ: レア
地獄の破滅
略奪者の剣
--------
アイテムレベル: 67
--------
{ プレフィックスモッド「引き裂く者」(ティア: 6) }
物理ダメージが30(25-34)%増加する
命中力 +55(47-72)
{ プレフィックスモッド「重い」(ティア: 8) }
物理ダメージが44(40-49)%増加する
{ サフィックスモッド「吸収の」(ティア: 6) }
倒した敵1体ごとに4(4-6)のマナを獲得する
""")
    entries = (
        {"id": "explicit.phys", "text": "物理ダメージが#%増加する", "type": "explicit"},
        {"id": "explicit.accuracy", "text": "命中力 +# (ローカル)", "type": "explicit"},
        {"id": "explicit.mana", "text": "倒した敵1体ごとに#のマナを獲得する", "type": "explicit"},
    )
    with patch("src.poetore.trade._trade_stat_entries", return_value=entries):
        filters = resolve_trade_stat_filters(item)
    assert [(row.stat_id, row.min_value) for row in filters] == [
        ("explicit.phys", 74), ("explicit.accuracy", 55), ("explicit.mana", 4),
    ]
    assert filters[0].text.endswith("(2行合計)")


def test_active_pc_league_skips_permanent_and_hard_modes():
    payload = {"result": [
        {"id": "Hardcore Mirage", "realm": "pc"},
        {"id": "Mirage", "realm": "pc"},
        {"id": "Standard", "realm": "pc"},
    ]}
    with patch("src.poetore.trade._request_json", return_value=(payload, {})):
        assert active_pc_league() == "Mirage"


def test_price_result_calculates_median_per_currency():
    result = PriceResult("Mirage", "q", 3, (
        PriceListing(3, "chaos"), PriceListing(7, "chaos"), PriceListing(1, "divine")
    ))
    assert result.median_by_currency() == {"chaos": 5, "divine": 1}


def test_search_prices_keeps_item_and_seller_for_list_display():
    search = ({"id": "query1", "result": ["item1"]}, {"X-Rate-Limit-Ip-State": "1:10:0"})
    fetch = ({"result": [{
        "listing": {"price": {"amount": 4, "currency": "chaos"}, "account": {"name": "seller"}},
        "item": {"name": "Doom Sever", "baseType": "Reaver Sword"},
    }]}, {})
    with patch("src.poetore.trade._request_json", side_effect=[search, fetch]):
        result = search_prices(parse_item_text(ITEM), "Reaver Sword", "Mirage")
    assert result.listings == (
        PriceListing(4, "chaos", "seller", "Doom Sever", "Reaver Sword"),
    )
