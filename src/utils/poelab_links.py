"""PoELabトップから当日のLabyrinthページURLだけを解決する。"""

from __future__ import annotations

import re
import urllib.request
from html import unescape
from urllib.parse import urljoin


POELAB_HOME = "https://www.poelab.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
LAB_LINK_LABELS = {
    "normal": "Normal Labyrinth Daily Notes",
    "cruel": "Cruel Labyrinth Daily Notes",
    "merciless": "Merciless Labyrinth Daily Notes",
}


def extract_daily_notes_url(page_html: str, lab_type: str) -> str:
    """PoELabトップHTMLから指定難易度のDaily Notes URLを返す。"""
    wanted = LAB_LINK_LABELS.get((lab_type or "").lower())
    if not wanted:
        raise ValueError(f"未対応のLabyrinth種別です: {lab_type}")

    link_re = re.compile(r"<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", re.I | re.S)
    for href, body in link_re.findall(page_html):
        label = re.sub(r"<[^>]+>", " ", body)
        label = " ".join(unescape(label).split())
        if label.casefold() == wanted.casefold():
            return urljoin(POELAB_HOME, unescape(href))
    raise RuntimeError(f"PoELabから {wanted} のリンクを取得できませんでした")


def find_daily_notes_url(lab_type: str, timeout: int = 10) -> str:
    """トップページだけを取得し、当日のDaily Notes URLを返す。"""
    request = urllib.request.Request(
        POELAB_HOME,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        page_html = response.read().decode("utf-8", "replace")
    return extract_daily_notes_url(page_html, lab_type)
