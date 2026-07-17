from unittest.mock import Mock, patch

import pytest

pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.update.release_client import ReleaseInfo


@pytest.fixture(scope="module", autouse=True)
def app():
    return QApplication.instance() or QApplication([])


def release_info():
    return ReleaseInfo(
        "2.5.0",
        "notes",
        "https://github.com/page",
        "https://github.com/a.zip",
        "https://github.com/a.sha256",
    )


def test_startup_check_skips_already_notified_release():
    window = MainWindow.__new__(MainWindow)
    window.config = {"notified_update_version": "2.5.0"}
    window._show_update_available = Mock()

    window._on_update_check_finished(release_info(), False)

    window._show_update_available.assert_not_called()


def test_manual_check_shows_same_release_again():
    window = MainWindow.__new__(MainWindow)
    window.config = {"notified_update_version": "2.5.0"}
    window._show_update_available = Mock()

    window._on_update_check_finished(release_info(), True)

    window._show_update_available.assert_called_once_with(release_info())


def test_manual_check_without_release_reports_latest():
    window = MainWindow.__new__(MainWindow)
    with patch("src.ui.main_window.QMessageBox.information") as information:
        window._on_update_check_finished(None, True)
    information.assert_called_once()
