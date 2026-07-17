import hashlib
import io
from pathlib import Path
import zipfile

import pytest

from src.update.artifacts import (
    DownloadCancelled,
    download_file,
    parse_checksum,
    validate_update_archive,
    verify_sha256,
)


def write_zip(path: Path, names: list[str]):
    with zipfile.ZipFile(path, "w") as archive:
        for name in names:
            archive.writestr(name, b"content")


def test_parse_checksum_and_verify_file(tmp_path):
    archive = tmp_path / "PoENavi.zip"
    archive.write_bytes(b"release")
    digest = hashlib.sha256(b"release").hexdigest()
    assert parse_checksum(f"{digest}  PoENavi.zip\n") == digest
    assert verify_sha256(archive, digest)


@pytest.mark.parametrize(
    "text",
    ["bad PoENavi.zip", "a" * 64 + "  Other.zip", ""],
)
def test_parse_checksum_rejects_invalid_content(text):
    with pytest.raises(ValueError):
        parse_checksum(text)


def test_validate_update_archive_accepts_release_layout(tmp_path):
    archive = tmp_path / "PoENavi.zip"
    write_zip(
        archive,
        [
            "PoENavi/PoENavi.exe",
            "PoENavi/PoENaviUpdater.exe",
            "PoENavi/update-manifest.json",
        ],
    )
    validate_update_archive(archive)


@pytest.mark.parametrize(
    "entry",
    ["../outside", "PoENavi/../../outside", "/absolute", "C:/absolute"],
)
def test_validate_update_archive_rejects_path_escape(tmp_path, entry):
    archive = tmp_path / "PoENavi.zip"
    write_zip(
        archive,
        [
            "PoENavi/PoENavi.exe",
            "PoENavi/PoENaviUpdater.exe",
            "PoENavi/update-manifest.json",
            entry,
        ],
    )
    with pytest.raises(ValueError):
        validate_update_archive(archive)


class Response(io.BytesIO):
    def __init__(self, data: bytes, final_url="https://github.com/file"):
        super().__init__(data)
        self.headers = {"Content-Length": str(len(data))}
        self._final_url = final_url

    def geturl(self):
        return self._final_url

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


def test_download_reports_progress_and_honors_cancel(tmp_path):
    progress = []
    target = download_file(
        "https://github.com/file",
        tmp_path / "file",
        lambda done, total: progress.append((done, total)),
        lambda: False,
        opener=lambda _request, timeout: Response(b"release"),
    )
    assert target.read_bytes() == b"release"
    assert progress[-1] == (7, 7)

    with pytest.raises(DownloadCancelled):
        download_file(
            "https://github.com/file",
            tmp_path / "cancelled",
            lambda _done, _total: None,
            lambda: True,
            opener=lambda _request, timeout: Response(b"release"),
        )
    assert not (tmp_path / "cancelled").exists()


def test_download_rejects_redirect_outside_github(tmp_path):
    with pytest.raises(ValueError, match="GitHub"):
        download_file(
            "https://github.com/file",
            tmp_path / "file",
            lambda _done, _total: None,
            lambda: False,
            opener=lambda _request, timeout: Response(
                b"release",
                final_url="https://example.com/file",
            ),
        )
