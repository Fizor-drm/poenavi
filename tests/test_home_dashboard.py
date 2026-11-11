"""サイドバー付きホームダッシュボードのページ切替と要約表示。"""

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QWidget

from src.ui.home_dashboard import (
    DashboardShell,
    HomeSummaryPage,
    guide_excerpt_text,
)
from src.ui.toolbar_icons import home_icon, guide_icon, timer_icon
from src.utils.poe_version_data import POE1, POE2


def _app():
    return QApplication.instance() or QApplication([])


def _icon():
    return home_icon("#b0ff7b", "#263A20", "#142111")


def test_guide_excerpt_strips_html_and_limits_lines():
    _app()
    html = "<b>北へ進む</b><br>次の出口<br>" + "<br>".join(f"手順{i}" for i in range(10))
    text = guide_excerpt_text(html, limit_lines=3)
    assert "北へ進む" in text
    assert "<b>" not in text
    assert text.endswith("…")
    assert guide_excerpt_text("") == "エリアに入場すると、次の手順がここに出ます。"


def test_sidebar_switches_pages_collapses_and_hides_unavailable_nav():
    _app()
    shell = DashboardShell()
    home = QWidget()
    guide = QWidget()
    gem = QWidget()
    shell.add_page("home", "ホーム", _icon(), home, section="進行")
    shell.add_page("guide", "ガイド", guide_icon("#b0ff7b", "#263A20", "#142111"), guide, section="進行")
    shell.add_page("gem", "ジェム", timer_icon("#b0ff7b", "#263A20", "#142111"), gem, section="進行")

    assert shell.current_page_id == "home"
    shell.set_page("guide")
    assert shell.current_page_id == "guide"
    assert shell.stack.currentWidget() is guide
    assert shell.page_title.text() == "ガイド"
    assert shell.nav_buttons["guide"].text() == "ガイド"

    shell.set_collapsed(True, notify=False)
    assert shell.nav_buttons["guide"].text() == ""
    assert shell.nav_buttons["guide"].toolTip() == "ガイド"
    assert shell.section_labels[0].isHidden()
    assert shell.sidebar.width() < 80
    shell.set_collapsed(False, notify=False)
    assert shell.nav_buttons["guide"].text() == "ガイド"
    assert not shell.section_labels[0].isHidden()

    shell.set_nav_visible("gem", False, notify=False)
    shell.set_page("gem")
    assert shell.current_page_id == "home"
    assert not shell.nav_buttons["gem"].isVisible()
    shell.set_page("missing")
    assert shell.current_page_id == "home"
    shell.deleteLater()


def test_home_summary_mirrors_existing_labels():
    _app()
    page = HomeSummaryPage()

    class Watcher:
        is_active = True

    window = type("Window", (), {})()
    window.poe_version = POE1
    window.part2_mode = False
    window.current_act = 2
    window.lap_labels = ["Act 1", "Act 2"]
    window.is_running = True
    window.timer_ready = False
    window.config = {"client_log_paths": {POE1: "C:/PoE/logs/Client.txt"}}
    window.log_watcher = Watcher()
    window.lbl_hours = QLabel("00")
    window.lbl_mins = QLabel("12")
    window.lbl_secs = QLabel("34")
    window.lbl_ms = QLabel(".56")
    window.zone_label = QLabel("📍 Act 1 — ぬかるみの干潟 (MLv.4)")
    window.level_label = QLabel("キャラLv. 4")
    window.advice_label = QLabel("🟢 最適レベル (±0)")
    window.advice_label.setStyleSheet("color: #b0ff7b; font-size: 12px;")
    window.segment_summary_label = QLabel("直近: 海岸 00:10")
    window.guide_text_label = QLabel("<b>北の出口</b>へ進む<br>次は海岸")
    window.ready_btn = QPushButton("Ready")
    window.ready_btn.setEnabled(False)

    page.refresh(window)
    assert page.zone_value.text() == window.zone_label.text()
    assert page.level_value.text() == "キャラLv. 4"
    assert "最適レベル" in page.advice_value.text()
    assert "#b0ff7b" in page.advice_value.styleSheet()
    assert page.timer_value.text() == "00:12:34.56"
    assert page.timer_state.text() == "計測中"
    assert page.log_status.text() == "ログ監視中"
    assert "北の出口" in page.next_steps.text()
    assert "<b>" not in page.next_steps.text()
    assert "Act 1-5" in page.level_meta.text()
    assert "Act 2" in page.level_meta.text()
    assert not page.ready_button.isEnabled()

    window.lbl_secs.setText("35")
    window.zone_label.setText("別のエリア")
    page.refresh(window, timer_only=True)
    assert page.timer_value.text() == "00:12:35.56"
    assert page.zone_value.text() == "📍 Act 1 — ぬかるみの干潟 (MLv.4)"

    window.poe_version = POE2
    window.is_running = False
    window.config = {"client_log_paths": {}}
    page.refresh(window)
    assert page.version_badge.text() == "PoE2"
    assert page.log_status.text() == "ログ未設定"
    assert page.timer_state.text() == "停止中"
    page.deleteLater()


def test_main_window_source_keeps_toolbar_icons_and_lists_dashboard_pages():
    source = Path("src/ui/main_window.py").read_text(encoding="utf-8")
    assert "self.memo_btn.setIcon(memo_icon(" in source
    assert "self.vendor_search_btn.setIcon(vendor_presets_icon(" in source
    assert "self.cheat_sheets_btn.setIcon(image_manager_icon(" in source
    assert "self.settings_btn.setIcon(settings_icon(" in source
    assert "self.poetore_btn" not in source
    assert "DashboardShell(" in source
    for page_id in (
        "home",
        "guide",
        "timer",
        "map",
        "gem",
        "mini_navi",
        "cheat_sheets",
        "memo",
        "vendor",
        "poetore",
        "settings",
        "info",
    ):
        assert f'"{page_id}"' in source
    assert "dashboard_page" in source
    assert "dashboard_sidebar_collapsed" in source


def test_main_window_launches_into_sidebar_dashboard(tmp_path, monkeypatch):
    monkeypatch.setenv("POENAVI_USER_DATA_DIR", str(tmp_path))
    log_file = tmp_path / "Client.txt"
    log_file.write_text("", encoding="utf-8")
    (tmp_path / "config.json").write_text(
        json.dumps(
            {
                "poe_version": POE1,
                "poe_version_mode": POE1,
                "area_note_migration_notice_shown": True,
                "poe1_route_selected": True,
                "client_log_paths": {POE1: str(log_file), POE2: ""},
                "window_opacity": 100,
                "text_opacity": 100,
                "dashboard_page": "guide",
                "dashboard_sidebar_collapsed": True,
            }
        ),
        encoding="utf-8",
    )
    app = _app()
    previous_update = app.property("startupUpdateChecked")
    previous_version = app.property("startupPoeVersionSelected")
    app.setProperty("startupUpdateChecked", True)
    app.setProperty("startupPoeVersionSelected", True)
    from src.ui.main_window import MainWindow

    window = MainWindow()
    try:
        assert window._main_window_initialized
        assert window.dashboard_shell.current_page_id == "guide"
        assert window.dashboard_shell.collapsed
        window.show()
        app.processEvents()
        window.show_dashboard_page("home")
        app.processEvents()
        assert window.dashboard_shell.current_page_id == "home"
        assert window.home_summary_page.isVisible()
        window.show_dashboard_page("timer")
        app.processEvents()
        assert window.timer_container.isVisible()
        window.show_dashboard_page("gem")
        app.processEvents()
        assert window.gem_tracker.isVisible()
        window.show_dashboard_page("memo")
        app.processEvents()
        assert window.memo_btn.isVisible()
        for page_id in (
            "home", "guide", "timer", "map", "gem", "mini_navi",
            "cheat_sheets", "memo", "vendor", "poetore", "settings", "info",
        ):
            assert page_id in window.dashboard_shell.pages
        assert "self.poetore_btn" not in Path("src/ui/main_window.py").read_text(encoding="utf-8")
    finally:
        window.close()
        app.processEvents()
        app.setProperty("startupUpdateChecked", previous_update)
        app.setProperty("startupPoeVersionSelected", previous_version)
