from pathlib import Path
from unittest.mock import patch

from src.utils.log_watcher import LogWatcher


def test_twilight_trace_reports_log_and_detection_timestamps(capsys):
    watcher = LogWatcher()
    line = (
        "2026/07/23 20:15:30 123456 abc [INFO Client 1234] "
        ": You have entered The Twilight Strand."
    )

    with patch.dict("os.environ", {"POENAVI_TWILIGHT_TRACE": "1"}):
        watcher._parse_line(line)

    output = capsys.readouterr().out
    assert "[黄昏の岸辺・検知テスト]" in output
    assert "入場ログ（英語）" in output
    assert "2026/07/23 20:15:30" in output
    assert "PoENavi検知時刻:" in output
    assert "The Twilight Strand" in output


def test_twilight_trace_reports_set_source_separately(capsys):
    watcher = LogWatcher()
    line = (
        "2026/07/23 20:15:29 123456 abc [DEBUG Client 1234] "
        "[SCENE] Set Source [黄昏の岸辺]"
    )

    with patch.dict("os.environ", {"POENAVI_TWILIGHT_TRACE": "1"}):
        watcher._parse_line(line)

    output = capsys.readouterr().out
    assert "[黄昏の岸辺・検知テスト]" in output
    assert "検知経路     : Set Source" in output


def test_twilight_trace_is_disabled_without_development_flag(capsys):
    watcher = LogWatcher()
    line = (
        "2026/07/23 20:15:30 123456 abc [INFO Client 1234] "
        ": You have entered The Twilight Strand."
    )

    with patch.dict("os.environ", {}, clear=True):
        watcher._parse_line(line)

    output = capsys.readouterr().out
    assert "[黄昏の岸辺・検知テスト]" not in output


def test_lines_after_twilight_are_saved_with_elapsed_time(tmp_path):
    watcher = LogWatcher()
    entry = (
        "2026/07/23 20:15:30 123456 abc [INFO Client 1234] "
        ": You have entered The Twilight Strand."
    )
    later = "2026/07/23 20:15:31 123456 abc [INFO Client 1234] later event"

    with patch.dict(
        "os.environ",
        {
            "POENAVI_TWILIGHT_TRACE": "1",
            "POENAVI_TWILIGHT_CAPTURE_SECONDS": "120",
            "POENAVI_USER_DATA_DIR": str(tmp_path),
        },
    ):
        watcher._parse_line(entry)
        watcher._capture_twilight_line(entry)
        watcher._capture_twilight_line(later)

    trace_files = list((tmp_path / "diagnostics").glob("twilight-client-log-*.txt"))
    assert len(trace_files) == 1
    content = trace_files[0].read_text(encoding="utf-8")
    assert "[+00000." in content
    assert entry in content
    assert later in content


def test_twilight_capture_stops_after_configured_duration(tmp_path, capsys):
    watcher = LogWatcher()
    watcher._twilight_capture_path = Path(tmp_path) / "trace.txt"
    watcher._twilight_capture_path.write_text("", encoding="utf-8")
    watcher._twilight_capture_started_at = 10.0

    with patch.dict(
        "os.environ",
        {"POENAVI_TWILIGHT_CAPTURE_SECONDS": "2"},
    ), patch("src.utils.log_watcher.time.perf_counter", return_value=12.1):
        watcher._capture_twilight_line("too late")

    assert watcher._twilight_capture_started_at is None
    assert watcher._twilight_capture_path.read_text(encoding="utf-8") == ""
    assert "ログ保存を終了しました" in capsys.readouterr().out
