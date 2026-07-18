from pathlib import Path
import zipfile

import pytest

from src.update.updater_engine import (
    UpdateApplyError,
    apply_update,
    wait_for_process_exit,
)


def make_release(path: Path, marker="new", guide="new guide"):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("PoENavi/PoENavi.exe", marker)
        archive.writestr("PoENavi/PoENaviUpdater.exe", "updater")
        archive.writestr("PoENavi/guide_data.json", guide)


def test_wait_for_process_exit_stops_when_process_finishes():
    states = iter([True, True, False])
    assert wait_for_process_exit(
        42,
        1,
        lambda _pid: next(states),
        sleep=lambda _seconds: None,
    )


def test_apply_update_replaces_install_and_launches_new_exe(tmp_path):
    install = tmp_path / "ぽえなび" / "PoENavi"
    install.mkdir(parents=True)
    (install / "PoENavi.exe").write_text("old", encoding="utf-8")
    archive = tmp_path / "PoENavi.zip"
    make_release(archive)
    launched = []

    backup = apply_update(
        archive,
        install,
        tmp_path / "work",
        lambda exe: launched.append(exe),
    )

    assert (install / "PoENavi.exe").read_text(encoding="utf-8") == "new"
    assert launched == [install / "PoENavi.exe"]
    assert backup.exists()


def test_apply_update_replaces_old_official_guide_with_release_guide(tmp_path):
    install = tmp_path / "PoENavi"
    install.mkdir()
    (install / "PoENavi.exe").write_text("old", encoding="utf-8")
    (install / "guide_data.json").write_text("user-edited old guide", encoding="utf-8")
    archive = tmp_path / "PoENavi.zip"
    make_release(archive, guide="latest official guide")

    apply_update(archive, install, tmp_path / "work", lambda _exe: object())

    assert (install / "guide_data.json").read_text(encoding="utf-8") == "latest official guide"


def test_apply_update_does_not_touch_external_user_data(tmp_path):
    install = tmp_path / "PoENavi"
    install.mkdir()
    (install / "PoENavi.exe").write_text("old", encoding="utf-8")
    user_data = tmp_path / "AppData" / "PoENavi"
    user_data.mkdir(parents=True)
    area_notes = user_data / "area_notes_poe1.json"
    config = user_data / "config.json"
    area_notes.write_text('{"area": {"text": "my note"}}', encoding="utf-8")
    config.write_text('{"font_size": 18}', encoding="utf-8")
    archive = tmp_path / "PoENavi.zip"
    make_release(archive)

    apply_update(archive, install, tmp_path / "work", lambda _exe: object())

    assert area_notes.read_text(encoding="utf-8") == '{"area": {"text": "my note"}}'
    assert config.read_text(encoding="utf-8") == '{"font_size": 18}'


def test_apply_update_restores_old_install_when_launch_fails(tmp_path):
    install = tmp_path / "PoENavi"
    install.mkdir()
    (install / "PoENavi.exe").write_text("old", encoding="utf-8")
    archive = tmp_path / "PoENavi.zip"
    make_release(archive)

    def fail_launch(_exe):
        raise OSError("launch failed")

    with pytest.raises(UpdateApplyError, match="旧版を復元"):
        apply_update(archive, install, tmp_path / "work", fail_launch)
    assert (install / "PoENavi.exe").read_text(encoding="utf-8") == "old"


def test_apply_update_restores_old_install_when_new_app_exits_immediately(tmp_path):
    install = tmp_path / "PoENavi"
    install.mkdir()
    (install / "PoENavi.exe").write_text("old", encoding="utf-8")
    archive = tmp_path / "PoENavi.zip"
    make_release(archive)

    with pytest.raises(UpdateApplyError, match="旧版を復元"):
        apply_update(
            archive,
            install,
            tmp_path / "work",
            lambda _exe: object(),
            startup_check=lambda _process: False,
        )
    assert (install / "PoENavi.exe").read_text(encoding="utf-8") == "old"
