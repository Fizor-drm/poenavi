"""ぽえなび本体のサイドバー付きダッシュボード。"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.utils.poe_version_data import get_poe_label


SIDEBAR_EXPANDED_WIDTH = 156
SIDEBAR_COLLAPSED_WIDTH = 44
# ホームの下段を2列にするページ幅。これより狭いときは縦に積む。
HOME_WIDE_LAYOUT_WIDTH = 640

NAV_BUTTON_STYLE = """
QPushButton {{
    background: transparent;
    color: #E9FFBD;
    border: none;
    border-radius: 6px;
    text-align: {align};
    padding: 3px {pad};
    font-size: 12px;
    font-weight: 700;
}}
QPushButton:hover {{ background: rgba(176, 255, 123, 0.12); }}
QPushButton:checked {{
    background: rgba(176, 255, 123, 0.24);
    color: #ffffff;
}}
"""

SCROLL_STYLE = """
QScrollArea { background: transparent; border: none; }
QScrollBar:vertical {
    width: 12px;
    background: rgba(176, 255, 123, 0.08);
    border-radius: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    min-height: 28px;
    background: rgba(176, 255, 123, 0.45);
    border-radius: 6px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
"""


def guide_excerpt_text(html: str, limit_lines: int = 8) -> str:
    """攻略HTMLから、ホームに出すプレーンテキストの冒頭を取り出す。"""
    document = QTextDocument()
    document.setHtml(html or "")
    lines = [line.strip() for line in document.toPlainText().splitlines() if line.strip()]
    if not lines:
        return "エリアに入場すると、次の手順がここに出ます。"
    excerpt = lines[:limit_lines]
    if len(lines) > limit_lines:
        excerpt.append("…")
    return "\n".join(excerpt)


def make_section_page(description: str) -> tuple[QWidget, QVBoxLayout]:
    """既存パネルを載せるページ。見出しはサイドバー側で出す。"""
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(6, 4, 6, 4)
    layout.setSpacing(4)
    if description:
        label = QLabel(description)
        label.setWordWrap(True)
        label.setStyleSheet("color: #C9D4C2; font-size: 11px;")
        layout.addWidget(label)
    return page, layout


class FeatureLaunchPage(QWidget):
    """ダイアログやオーバーレイを、サイドバーのページから開くための案内。"""

    def __init__(self, description: str, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 6, 8, 8)
        root.setSpacing(6)
        body = QLabel(description)
        body.setWordWrap(True)
        body.setStyleSheet("color: #C9D4C2; font-size: 12px;")
        root.addWidget(body)
        self.actions_layout = QVBoxLayout()
        self.actions_layout.setSpacing(8)
        root.addLayout(self.actions_layout)
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #b0ff7b; font-size: 12px; font-weight: bold;")
        self.status_label.hide()
        root.addWidget(self.status_label)
        root.addStretch(1)

    def add_icon_action(self, button: QPushButton, caption: str):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)
        row_layout.addWidget(button)
        caption_label = QLabel(caption)
        caption_label.setStyleSheet("color: #E9FFBD; font-size: 12px; font-weight: bold;")
        row_layout.addWidget(caption_label)
        row_layout.addStretch(1)
        self.actions_layout.addWidget(row)

    def set_status(self, text: str):
        self.status_label.setText(text)
        self.status_label.setVisible(bool(text))


class DashboardShell(QWidget):
    """左サイドバーと、ページを切り替えるメイン領域。"""

    page_changed = Signal(str)
    collapsed_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboardShell")
        self.pages: dict[str, QWidget] = {}
        self.nav_buttons: dict[str, QPushButton] = {}
        self.section_labels: list[QLabel] = []
        self._nav_enabled: dict[str, bool] = {}
        self._last_section = None
        self.current_page_id = ""
        self.collapsed = False

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = QWidget()
        self.sidebar.setObjectName("dashboardSidebar")
        self.sidebar.setAttribute(Qt.WA_StyledBackground, True)
        self.sidebar.setFixedWidth(SIDEBAR_EXPANDED_WIDTH)
        self.sidebar.setStyleSheet(
            "#dashboardSidebar {"
            " background-color: #141c14;"
            " border-right: 1px solid rgba(176, 255, 123, 0.28);"
            "}"
        )
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(4, 6, 4, 4)
        sidebar_layout.setSpacing(2)

        self.brand_label = QLabel("ぽえなび")
        self.brand_label.setStyleSheet("color: #b0ff7b; font-size: 13px; font-weight: bold;")
        sidebar_layout.addWidget(self.brand_label)
        self.brand_subtitle = QLabel("ダッシュボード")
        self.brand_subtitle.setStyleSheet("color: #8ea884; font-size: 10px;")
        sidebar_layout.addWidget(self.brand_subtitle)

        self.nav_host = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_host)
        self.nav_layout.setContentsMargins(0, 4, 0, 0)
        self.nav_layout.setSpacing(1)
        self.nav_layout.addStretch(1)
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setFrameShape(QFrame.NoFrame)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setStyleSheet(SCROLL_STYLE)
        nav_scroll.setWidget(self.nav_host)
        sidebar_layout.addWidget(nav_scroll, stretch=1)

        self.collapse_button = QPushButton("◀ 狭く")
        self.collapse_button.setObjectName("dashboardCollapseButton")
        self.collapse_button.setCursor(Qt.PointingHandCursor)
        self.collapse_button.setToolTip("サイドバーを折りたたむ")
        self.collapse_button.setFixedHeight(36)
        self.collapse_button.setStyleSheet(
            "QPushButton { background: rgba(26,26,26,220); color: #b0ff7b;"
            " border: 1px solid rgba(176,255,123,0.85); border-radius: 6px;"
            " padding: 4px 2px; font-size: 11px; font-weight: bold; }"
            "QPushButton:hover { background: rgba(176,255,123,0.28); color: #ffffff;"
            " border-color: #ffffff; }"
            "QPushButton:pressed { background: rgba(176,255,123,0.45); }"
        )
        self.collapse_button.clicked.connect(self.toggle_collapsed)
        sidebar_layout.addWidget(self.collapse_button)
        root.addWidget(self.sidebar)

        self.content = QWidget()
        self.content.setObjectName("dashboardContent")
        self.content.setAttribute(Qt.WA_StyledBackground, True)
        self.content.setStyleSheet("#dashboardContent { background-color: rgba(8, 14, 8, 150); }")
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(4, 2, 4, 4)
        content_layout.setSpacing(2)

        header = QWidget()
        self.header_layout = QHBoxLayout(header)
        self.header_layout.setContentsMargins(4, 0, 2, 0)
        self.header_layout.setSpacing(4)
        self.page_title = QLabel("ホーム")
        self.page_title.setObjectName("dashboardPageTitle")
        self.page_title.setStyleSheet("color: #E9FFBD; font-size: 14px; font-weight: bold;")
        self.header_layout.addWidget(self.page_title)
        self.header_layout.addStretch(1)
        content_layout.addWidget(header)

        self.stack = QStackedWidget()
        self.stack.setObjectName("dashboardStack")
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout.addWidget(self.stack, stretch=1)
        root.addWidget(self.content, stretch=1)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

    def minimumSizeHint(self):
        """各ページの推奨サイズで、本体が 540×480 より大きくならないようにする。"""
        return QSize(0, 0)

    def add_page(self, page_id: str, label: str, icon, widget: QWidget, *, section: str | None = None):
        if section and section != self._last_section:
            section_label = QLabel(section)
            section_label.setStyleSheet(
                "color: #8ea884; font-size: 10px; font-weight: bold; padding: 6px 4px 1px 4px;"
            )
            insert_at = max(0, self.nav_layout.count() - 1)
            self.nav_layout.insertWidget(insert_at, section_label)
            self.section_labels.append(section_label)
            self._last_section = section

        button = QPushButton(label)
        button.setObjectName(f"dashboardNav_{page_id}")
        button.setProperty("fullLabel", label)
        button.setIcon(icon)
        button.setIconSize(QSize(18, 18))
        button.setFixedHeight(28)
        button.setCheckable(True)
        button.setCursor(Qt.PointingHandCursor)
        button.setToolTip(label)
        button.setStyleSheet(NAV_BUTTON_STYLE.format(align="left", pad="6px"))
        button.clicked.connect(lambda _checked=False, target=page_id: self.set_page(target))
        self.nav_group.addButton(button)
        insert_at = max(0, self.nav_layout.count() - 1)
        self.nav_layout.insertWidget(insert_at, button)
        self.nav_buttons[page_id] = button
        self.pages[page_id] = widget
        self._nav_enabled[page_id] = True
        widget.setMinimumSize(0, 0)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stack.addWidget(widget)
        if not self.current_page_id:
            self.set_page(page_id, notify=False)

    def is_nav_enabled(self, page_id: str) -> bool:
        return bool(self._nav_enabled.get(page_id, False))

    def set_nav_visible(self, page_id: str, visible: bool, *, notify: bool = True):
        self._nav_enabled[page_id] = bool(visible)
        button = self.nav_buttons.get(page_id)
        if button is not None:
            button.setVisible(bool(visible))
        if not visible and self.current_page_id == page_id:
            self.set_page("home", notify=notify)

    def set_page(self, page_id: str, *, notify: bool = True):
        if page_id not in self.pages or not self.is_nav_enabled(page_id):
            page_id = "home" if self.is_nav_enabled("home") else ""
            if not page_id:
                enabled = [key for key, value in self._nav_enabled.items() if value and key in self.pages]
                page_id = enabled[0] if enabled else ""
        if not page_id:
            return
        changed = page_id != self.current_page_id
        self.current_page_id = page_id
        self.stack.setCurrentWidget(self.pages[page_id])
        button = self.nav_buttons[page_id]
        button.blockSignals(True)
        button.setChecked(True)
        button.blockSignals(False)
        self.page_title.setText(button.property("fullLabel") or page_id)
        if notify and changed:
            self.page_changed.emit(page_id)

    def toggle_collapsed(self):
        self.set_collapsed(not self.collapsed)

    def set_collapsed(self, collapsed: bool, *, notify: bool = True):
        self.collapsed = bool(collapsed)
        self.sidebar.setFixedWidth(
            SIDEBAR_COLLAPSED_WIDTH if self.collapsed else SIDEBAR_EXPANDED_WIDTH
        )
        align = "center" if self.collapsed else "left"
        pad = "0px" if self.collapsed else "6px"
        self.sidebar.layout().setContentsMargins(2 if self.collapsed else 4, 4, 2 if self.collapsed else 4, 4)
        style = NAV_BUTTON_STYLE.format(align=align, pad=pad)
        for button in self.nav_buttons.values():
            label = button.property("fullLabel") or ""
            button.setText("" if self.collapsed else label)
            button.setToolTip(label)
            button.setStyleSheet(style)
        for label in self.section_labels:
            label.setVisible(not self.collapsed)
        self.brand_label.setText("ぽ" if self.collapsed else "ぽえなび")
        self.brand_label.setAlignment(Qt.AlignCenter if self.collapsed else Qt.AlignLeft)
        self.brand_subtitle.setVisible(not self.collapsed)
        self.collapse_button.setText("▶" if self.collapsed else "◀ 狭く")
        self.collapse_button.setToolTip(
            "サイドバーを広げる" if self.collapsed else "サイドバーを折りたたむ"
        )
        if notify:
            self.collapsed_changed.emit(self.collapsed)

    def place_restore_button(self, button: QPushButton):
        """最小化したパネルを戻すボタンを、ページに関係なく出せる位置へ移す。"""
        self.header_layout.addWidget(button)


def _card(title: str) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("dashCard")
    frame.setAttribute(Qt.WA_StyledBackground, True)
    frame.setStyleSheet(
        "QFrame#dashCard {"
        " background-color: rgba(20, 32, 20, 210);"
        " border: 1px solid rgba(176, 255, 123, 0.28);"
        " border-radius: 8px;"
        "}"
    )
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(8, 5, 8, 6)
    layout.setSpacing(2)
    heading = QLabel(title)
    heading.setStyleSheet(
        "color: #8ea884; font-size: 10px; font-weight: bold; background: transparent; border: none;"
    )
    layout.addWidget(heading)
    return frame, layout


class HomeSummaryPage(QWidget):
    """いまログとタイマーが知っている状態の要約。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homeSummaryPage")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(SCROLL_STYLE)
        inner = QWidget()
        inner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root = QVBoxLayout(inner)
        self._home_root = root
        root.setContentsMargins(4, 2, 4, 4)
        root.setSpacing(6)

        header = QHBoxLayout()
        self.version_badge = QLabel("PoE")
        self.version_badge.setObjectName("homeVersionBadge")
        self.version_badge.setStyleSheet(
            "background: rgba(176, 255, 123, 0.16); color: #b0ff7b;"
            " border: 1px solid rgba(176, 255, 123, 0.55); border-radius: 10px;"
            " padding: 1px 8px; font-size: 11px; font-weight: bold;"
        )
        header.addWidget(self.version_badge)
        header.addStretch(1)
        self.log_status = QLabel("ログ未設定")
        self.log_status.setObjectName("homeLogStatus")
        self.log_status.setStyleSheet("color: #888888; font-size: 11px; font-weight: bold;")
        header.addWidget(self.log_status)
        root.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)
        self._home_grid = grid
        self._wide_cards = None

        zone_card, zone_layout = _card("現在地")
        self.zone_card = zone_card
        self.zone_value = QLabel("📍 エリア: ---")
        self.zone_value.setObjectName("homeZoneValue")
        self.zone_value.setWordWrap(True)
        self.zone_value.setMinimumWidth(0)
        self.zone_value.setStyleSheet("color: #E9FFBD; font-size: 13px; font-weight: bold;")
        zone_layout.addWidget(self.zone_value)

        level_card, level_layout = _card("キャラクター")
        self.level_card = level_card
        self.level_value = QLabel("キャラLv. 1")
        self.level_value.setObjectName("homeLevelValue")
        self.level_value.setStyleSheet("color: #E9FFBD; font-size: 13px; font-weight: bold;")
        level_layout.addWidget(self.level_value)
        self.level_meta = QLabel("")
        self.level_meta.setWordWrap(True)
        self.level_meta.setStyleSheet("color: #C9D4C2; font-size: 11px;")
        level_layout.addWidget(self.level_meta)

        advice_card, advice_layout = _card("経験値ペナルティ")
        self.advice_card = advice_card
        self.advice_value = QLabel("ログ監視待機中...")
        self.advice_value.setObjectName("homeAdviceValue")
        self.advice_value.setWordWrap(True)
        self.advice_value.setStyleSheet("color: #888888; font-size: 12px; font-weight: bold;")
        advice_layout.addWidget(self.advice_value)

        timer_card, timer_layout = _card("タイマー")
        self.timer_card = timer_card
        clock_row = QHBoxLayout()
        clock_row.setSpacing(8)
        self.timer_value = QLabel("00:00:00.00")
        self.timer_value.setObjectName("homeTimerValue")
        self.timer_value.setStyleSheet(
            "font-family: 'Consolas', 'Courier New', monospace;"
            " font-size: 20px; font-weight: bold; color: #b0ff7b;"
        )
        clock_row.addWidget(self.timer_value)
        self.timer_state = QLabel("停止中")
        self.timer_state.setObjectName("homeTimerState")
        self.timer_state.setStyleSheet("color: #C9D4C2; font-size: 11px; font-weight: bold;")
        clock_row.addWidget(self.timer_state)
        clock_row.addStretch(1)
        timer_layout.addLayout(clock_row)
        self.segment_value = QLabel("区間: エリア移動を待機中")
        self.segment_value.setWordWrap(True)
        self.segment_value.setStyleSheet("color: #C9D4C2; font-size: 11px;")
        timer_layout.addWidget(self.segment_value)
        actions = QHBoxLayout()
        actions.setSpacing(4)
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.reset_button = QPushButton("Reset")
        self.ready_button = QPushButton("Ready")
        compact_button = (
            "QPushButton { background-color: rgba(26, 26, 26, 200); color: #b0ff7b;"
            " border: 1px solid #b0ff7b; border-radius: 3px; padding: 2px 8px;"
            " font-size: 11px; font-weight: bold; }"
            "QPushButton:hover { border-color: #ffffff; }"
            "QPushButton:disabled { color: #666666; border-color: #555555; }"
        )
        for button in (self.start_button, self.stop_button, self.reset_button, self.ready_button):
            button.setStyleSheet(compact_button)
            button.setCursor(Qt.PointingHandCursor)
            button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
            actions.addWidget(button)
        actions.addStretch(1)
        timer_layout.addLayout(actions)

        steps_card, steps_layout = _card("次の手順")
        self.steps_card = steps_card
        steps_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.next_steps = QLabel("エリアに入場すると、次の手順がここに出ます。")
        self.next_steps.setObjectName("homeNextSteps")
        self.next_steps.setWordWrap(True)
        self.next_steps.setMinimumWidth(0)
        self.next_steps.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.next_steps.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.next_steps.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.next_steps.setStyleSheet("color: #E9FFBD; font-size: 12px;")
        steps_layout.addWidget(self.next_steps, stretch=1)
        self.open_guide_button = QPushButton("ガイドを開く")
        self.open_guide_button.setStyleSheet(compact_button)
        self.open_guide_button.setCursor(Qt.PointingHandCursor)
        self.open_guide_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        steps_layout.addWidget(self.open_guide_button, alignment=Qt.AlignLeft)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        root.addLayout(grid, stretch=1)

        hint = QLabel("詳細は左のメニューから開けます。ゲーム中はみになびで同じガイドを見られます。")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #8ea884; font-size: 10px;")
        root.addWidget(hint)
        scroll.setWidget(inner)
        outer.addWidget(scroll)
        self._apply_home_card_layout(wide=False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        wide = self.width() >= HOME_WIDE_LAYOUT_WIDTH
        if wide != self._wide_cards:
            self._apply_home_card_layout(wide)

    def _apply_home_card_layout(self, wide: bool):
        """狭いときはカードを縦に積み、広いときは上段を2列にして次の手順を伸ばす。"""
        self._wide_cards = wide
        grid = self._home_grid
        for card in (
            self.zone_card,
            self.level_card,
            self.advice_card,
            self.timer_card,
            self.steps_card,
        ):
            grid.removeWidget(card)
        grid.addWidget(self.zone_card, 0, 0)
        grid.addWidget(self.level_card, 0, 1)
        for row in range(1, 4):
            grid.setRowStretch(row, 0)
        if wide:
            grid.addWidget(self.advice_card, 1, 0)
            grid.addWidget(self.timer_card, 1, 1)
            grid.addWidget(self.steps_card, 2, 0, 1, 2)
            grid.setRowStretch(2, 1)
        else:
            grid.addWidget(self.advice_card, 1, 0, 1, 2)
            grid.addWidget(self.timer_card, 2, 0, 1, 2)
            grid.addWidget(self.steps_card, 3, 0, 1, 2)
            grid.setRowStretch(3, 1)

    def bind_window(self, window):
        self.start_button.clicked.connect(window.start_timer)
        self.stop_button.clicked.connect(window.stop_timer)
        self.reset_button.clicked.connect(window.reset_timer)
        self.ready_button.clicked.connect(window.toggle_timer_ready)
        self.open_guide_button.clicked.connect(lambda: window.show_dashboard_page("guide"))

    def refresh(self, window, timer_only: bool = False):
        hours = getattr(window, "lbl_hours", None)
        mins = getattr(window, "lbl_mins", None)
        secs = getattr(window, "lbl_secs", None)
        millis = getattr(window, "lbl_ms", None)
        if hours is not None and mins is not None and secs is not None and millis is not None:
            self.timer_value.setText(f"{hours.text()}:{mins.text()}:{secs.text()}{millis.text()}")
        if getattr(window, "timer_ready", False):
            state = "Ready（入場待ち）"
        elif getattr(window, "is_running", False):
            state = "計測中"
        else:
            state = "停止中"
        self.timer_state.setText(state)
        ready = getattr(window, "ready_btn", None)
        if ready is not None:
            self.ready_button.setText(ready.text())
            self.ready_button.setEnabled(ready.isEnabled())
            self.ready_button.setToolTip(ready.toolTip())
        if timer_only:
            return

        zone = getattr(window, "zone_label", None)
        if zone is not None:
            self.zone_value.setText(zone.text())
        level = getattr(window, "level_label", None)
        if level is not None:
            self.level_value.setText(level.text())
        advice = getattr(window, "advice_label", None)
        if advice is not None:
            self.advice_value.setText(advice.text() or "ログ監視待機中...")
            color = "#888888"
            style = advice.styleSheet() or ""
            marker = "color:"
            if marker in style:
                color = style.split(marker, 1)[1].split(";", 1)[0].strip() or color
            self.advice_value.setStyleSheet(
                f"color: {color}; font-size: 12px; font-weight: bold; background: transparent;"
            )
        segment = getattr(window, "segment_summary_label", None)
        if segment is not None:
            self.segment_value.setText(segment.text())
        guide = getattr(window, "guide_text_label", None)
        if guide is not None:
            self.next_steps.setText(guide_excerpt_text(guide.text()))

        version = getattr(window, "poe_version", "poe1")
        self.version_badge.setText(get_poe_label(version))
        labels = list(getattr(window, "lap_labels", []) or [])
        index = int(getattr(window, "current_act", 1) or 1) - 1
        lap_name = labels[index] if 0 <= index < len(labels) else "—"
        if version == "poe1":
            part = "Act 6-10" if getattr(window, "part2_mode", False) else "Act 1-5"
        else:
            part = "PoE2"
        self.level_meta.setText(f"{part}  /  次のラップ: {lap_name}")

        config = getattr(window, "config", {}) or {}
        paths = config.get("client_log_paths", {}) if isinstance(config, dict) else {}
        path = paths.get(version, "") if isinstance(paths, dict) else ""
        watcher = getattr(window, "log_watcher", None)
        if not path:
            log_text, log_color = "ログ未設定", "#888888"
        elif watcher is not None and getattr(watcher, "is_active", False):
            log_text, log_color = "ログ監視中", "#b0ff7b"
        else:
            log_text, log_color = "ログ監視は停止中", "#ffcc66"
        self.log_status.setText(log_text)
        self.log_status.setStyleSheet(f"color: {log_color}; font-size: 11px; font-weight: bold;")
