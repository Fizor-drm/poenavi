"""PoEショップ用のAct別ジェム検索文字列を組み立てる。"""
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


def build_act_vendor_gem_query(
    acquisition_plan: list[dict],
    act: int,
    gem_names_ja: Mapping[str, str],
    exclude_quest_rewards: bool,
) -> str:
    """現在Actのジェムを公式日本語名のOR検索にする。"""
    terms: list[str] = []
    seen: set[str] = set()
    for entry in acquisition_plan:
        if entry.get("act") != act:
            continue
        for gem in entry.get("gems", []):
            if exclude_quest_rewards and gem.get("type") == "quest":
                continue
            name = gem.get("name", "")
            term = gem_names_ja.get(name, "")
            if term and term not in seen:
                seen.add(term)
                terms.append(term)
    return "|".join(terms)
