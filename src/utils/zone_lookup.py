"""ゾーン検索・レベル助言ユーティリティ。

ゾーン一覧の正本は data/zone_data.json。
このモジュールには可変/重複しやすいゾーンマスタデータを置かない。
"""


def get_zone_info(zone_data: dict, zone_name: str, part2: bool = False) -> tuple:
    """
    エリア名から適正レベルとAct情報を検索。
    part2=True の場合、Act 6-10を優先検索（同名エリア対策）。

    Returns:
        (act_name, zone_level) or (None, None) if not found
    """
    if part2:
        search_order = [k for k in zone_data if k in ("Act 6", "Act 7", "Act 8", "Act 9", "Act 10")]
        search_order += [k for k in zone_data if k not in search_order]
    else:
        search_order = [k for k in zone_data if k in ("Act 1", "Act 2", "Act 3", "Act 4", "Act 5")]
        search_order += [k for k in zone_data if k not in search_order]

    for act_name in search_order:
        for z in zone_data.get(act_name, []):
            if z["zone"] == zone_name or z.get("zone_en") == zone_name:
                return act_name, z["level"]
    return None, None


def get_level_advice(player_level: int, zone_level: int) -> tuple:
    """
    PoE公式XPペナルティ計算式に基づくレベルアドバイス。

    - ペナルティ許容範囲 = player_level // 16 + 3
    - 最適レベル範囲 = player_level // 16 + 2（キャラLv ≤ エリアLv の場合）

    Returns:
        (message, color) — 表示メッセージとカラーコード
    """
    safe_range = player_level // 16 + 3
    optimal_margin = player_level // 16 + 2
    diff = player_level - zone_level

    if abs(diff) > safe_range:
        if diff > 0:
            return f"🔴 ペナルティ (+{diff}) — レベル超過！経験値減少中", "#ff4444"
        return f"🔴 ペナルティ ({diff:+d}) — レベル不足！経験値減少中", "#ff4444"

    if diff <= 0 and abs(diff) <= optimal_margin:
        if diff == 0:
            return "🟢 最適レベル (±0)", "#b0ff7b"
        return f"🟢 最適レベル ({diff:+d})", "#b0ff7b"

    if diff > 0:
        return f"🟡 ペナルティなし (+{diff}) — ややレベル上がり気味", "#ffff66"
    return f"🟡 ペナルティなし ({diff:+d}) — ややレベル不足気味", "#ffff66"
