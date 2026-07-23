"""PoEショップ用のAct別ジェム検索文字列を組み立てる。"""

import json
import os
import sys
from collections.abc import Mapping


class HoldTrigger:
    """長押しタイマーの古い発火と連続実行を防ぐ状態。"""

    def __init__(self) -> None:
        self._generation = 0
        self._held = False
        self._consumed = False

    def start(self) -> int:
        if self._held:
            return self._generation
        self._generation += 1
        self._held = True
        self._consumed = False
        return self._generation

    def release(self) -> None:
        self._held = False

    def consume_if_current(self, generation: int) -> bool:
        if generation != self._generation or not self._held or self._consumed:
            return False
        self._consumed = True
        return True


def _get_data_dir() -> str:
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        exe_data_dir = os.path.join(exe_dir, "data")
        if os.path.isdir(exe_data_dir):
            return exe_data_dir
        return os.path.join(getattr(sys, "_MEIPASS", exe_dir), "data")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


def load_gem_shop_search_terms() -> dict[str, str]:
    """ユーザーが確認したショップ検索用通称を読み込む。"""
    path = os.path.join(_get_data_dir(), "gem_shop_search_terms_ja.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_act_vendor_gem_query(
    acquisition_plan: list[dict],
    act: int,
    gem_names_ja: Mapping[str, str],
    search_terms: Mapping[str, str],
) -> str:
    """現在Actの購入ジェムだけを短縮語のOR検索にする。"""
    terms: list[str] = []
    seen: set[str] = set()
    for entry in acquisition_plan:
        if entry.get("act") != act:
            continue
        for gem in entry.get("gems", []):
            if gem.get("type") not in {"vendor", "lilly"}:
                continue
            name = gem.get("name", "")
            term = search_terms.get(name) or gem_names_ja.get(name, "")[:4]
            if term and term not in seen:
                seen.add(term)
                terms.append(term)
    return "|".join(terms)
