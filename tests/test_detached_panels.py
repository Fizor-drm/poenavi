import os

os.environ.setdefault("QT_QPA_PLATFORM", "minimal")

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from src.ui.main_window import DetachedPanelWindow, MainWindow
from src.utils.config_manager import ConfigManager


def _app():
    return QApplication.instance() or QApplication([])


def _window():
    _app()
    host = QWidget()
    layout = QVBoxLayout(host)
    content = QWidget()
    detach_button = QPushButton("↗ 切り離す")
    detach_button.show()
    layout.addWidget(content)
    window = MainWindow.__new__(MainWindow)
    window.config = {"detached_panels": {"timer": {"detached": False}}}
    window.panel_registry = {"timer": {"content": content, "host": host, "layout": layout, "index": 0, "title": "タイマー", "detach_button": detach_button}}
    window.detached_panel_windows = {}
    return window, content, layout


def test_detach_panel_moves_content_out_of_main_layout(monkeypatch):
    window, content, layout = _window()
    monkeypatch.setattr(ConfigManager, "save_config", lambda _config: None)

    window.detach_panel("timer")

    assert layout.indexOf(content) == -1
    assert window.detached_panel_windows["timer"].content is content
    assert not window.panel_registry["timer"]["detach_button"].isVisible()


def test_restore_panel_returns_content_to_original_layout(monkeypatch):
    window, content, layout = _window()
    monkeypatch.setattr(ConfigManager, "save_config", lambda _config: None)
    window.detach_panel("timer")

    window.restore_panel("timer")

    assert layout.indexOf(content) == 0
    assert window.detached_panel_windows == {}
    assert window.panel_registry["timer"]["detach_button"].isVisible()


def test_detached_panel_move_saves_its_geometry(monkeypatch):
    window, _content, _layout = _window()
    monkeypatch.setattr(ConfigManager, "save_config", lambda _config: None)
    window.detach_panel("timer")
    panel_window = window.detached_panel_windows["timer"]

    panel_window.move(41, 52)
    _app().processEvents()

    assert window.config["detached_panels"]["timer"]["x"] == 41
    assert window.config["detached_panels"]["timer"]["y"] == 52


def test_detached_panel_uses_a_frameless_dark_header():
    _app()
    content = QWidget()
    panel_window = DetachedPanelWindow("timer", "タイマー", content, lambda _panel_id: None, lambda _panel_id: None)

    assert panel_window.windowFlags() & Qt.FramelessWindowHint
    assert panel_window.title_label.text() == "タイマー"


def test_dragging_detached_panel_header_moves_the_window():
    _app()
    panel_window = DetachedPanelWindow("timer", "タイマー", QWidget(), lambda _panel_id: None, lambda _panel_id: None)
    panel_window._drag_offset = QPoint(8, 9)

    panel_window._move_from_global_position(QPoint(108, 209))

    assert panel_window.pos() == QPoint(100, 200)


def test_restore_detached_panels_keeps_saved_geometry(monkeypatch):
    window, _content, _layout = _window()
    monkeypatch.setattr(ConfigManager, "save_config", lambda _config: None)
    window.config["detached_panels"]["timer"] = {
        "detached": True, "x": 41, "y": 52, "width": 420, "height": 280,
    }

    window._restore_detached_panels()

    assert window.detached_panel_windows["timer"].geometry().getRect() == (41, 52, 420, 280)
