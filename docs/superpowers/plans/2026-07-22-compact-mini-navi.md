# コンパクトみになび Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ExileUI風のコンパクトみになびを選択可能にし、内容量に応じて日本語案内を見切れなく表示する。

**Architecture:** `mini_guide_overlay.display_mode` で標準とコンパクトを切り替える。既存の位置・サイズは標準プロファイルとして維持し、コンパクトのジオメトリは `compact_geometry` に独立保存する。オーバーレイは選択中のプロファイルでレイアウト・高さを計算し、コンパクト時のみ案内を省略しない。

**Tech Stack:** Python 3、PySide6、pytest、Qt offscreen platform

## Global Constraints

- 既存ユーザーの `mini_guide_overlay.position`、`width`、`height`、透過率、ロック状態を変更しない。
- 初期表示は標準モードとし、コンパクトは設定で明示的に選択する。
- コンパクトの初回位置は利用可能画面領域の下中央、初期幅は390pxとする。
- コンパクト時は案内文を省略せず、内容量に合わせて高さを増減させる。
- 画面高を超える場合のみ、利用可能な画面領域内に収める。

---

### Task 1: 表示モード設定と既存設定の移行

**Files:**
- Modify: `default_config.json:53-75`
- Modify: `src/utils/config_manager.py:17,369-397`
- Modify: `src/ui/settings_dialog.py:1938-2015,2655-2663`
- Test: `tests/test_config_manager.py:46-135`

**Interfaces:**
- Produces `mini_guide_overlay["display_mode"]`: `"standard"` or `"compact"`.
- Produces `mini_guide_overlay["compact_geometry"]`: `{"position": {"x": int, "y": int}, "width": int, "height": int}`.
- Keeps existing `position`、`width`、`height` as standard-mode geometry.

- [ ] **Step 1: Write failing migration tests**

```python
def test_schema_v3_adds_standard_mode_without_changing_existing_geometry():
    migrated = ConfigManager._migrate_config({
        "schemaVersion": 2,
        "mini_guide_overlay": {"position": {"x": 30, "y": 40}, "width": 795, "height": 126},
    })
    assert migrated["schemaVersion"] == 3
    assert migrated["mini_guide_overlay"]["display_mode"] == "standard"
    assert migrated["mini_guide_overlay"]["position"] == {"x": 30, "y": 40}
    assert migrated["mini_guide_overlay"]["width"] == 795

def test_schema_v3_preserves_compact_geometry():
    geometry = {"position": {"x": 400, "y": 700}, "width": 420, "height": 140}
    migrated = ConfigManager._migrate_config({
        "schemaVersion": 2,
        "mini_guide_overlay": {"display_mode": "compact", "compact_geometry": geometry},
    })
    assert migrated["mini_guide_overlay"]["display_mode"] == "compact"
    assert migrated["mini_guide_overlay"]["compact_geometry"] == geometry
```

- [ ] **Step 2: Verify the tests fail**

Run: `python -X faulthandler -m pytest tests/test_config_manager.py -q`

Expected: FAIL because schema version 3 and `display_mode` do not exist.

- [ ] **Step 3: Implement schema v3 and the selector**

```python
CURRENT_SCHEMA_VERSION = 3

if schema_version < 3:
    overlay = migrated.get("mini_guide_overlay")
    if isinstance(overlay, dict):
        overlay.setdefault("display_mode", "standard")
```

Add `"display_mode": "standard"` to `default_config.json`. Add a `QComboBox` with `("標準", "standard")` and `("コンパクト", "compact")` in the existing mini-navi settings group, then save `currentData()` into `mini_navi_overlay_config["display_mode"]`. Do not create `compact_geometry` during migration.

- [ ] **Step 4: Verify and commit**

Run: `python -X faulthandler -m pytest tests/test_config_manager.py -q`

Expected: PASS.

```bash
git add default_config.json src/utils/config_manager.py src/ui/settings_dialog.py tests/test_config_manager.py
git commit -m "feat: add mini navi display mode setting"
```

### Task 2: コンパクト時に案内を省略しない

**Files:**
- Modify: `src/utils/guide_data.py:196-238`
- Modify: `src/ui/main_window.py:6378-6387`
- Test: `tests/test_guide_data.py`

**Interfaces:**
- Changes `get_mini_navi_content(guide: dict | None, max_lines: int | None = 4) -> dict | None`.
- `max_lines is None` returns every non-empty line and never appends an ellipsis.
- `display_mode == "compact"` passes `max_lines=None`; standard mode keeps the existing configured limit.

- [ ] **Step 1: Write the failing guide-data test**

```python
def test_mini_navi_content_returns_all_lines_when_line_limit_is_none():
    guide = {"mini_navi": {"text": "一行目\n二行目\n三行目\n四行目\n五行目"}}
    content = get_mini_navi_content(guide, max_lines=None)
    assert content["text"].splitlines() == ["一行目", "二行目", "三行目", "四行目", "五行目"]
```

- [ ] **Step 2: Verify the test fails**

Run: `python -X faulthandler -m pytest tests/test_guide_data.py -q`

Expected: FAIL because `None` is currently coerced to a four-line limit.

- [ ] **Step 3: Implement the optional limit and mode selection**

```python
if max_lines is None:
    return {"text": "\n".join(lines), "direction": direction}

max_lines = max(4, min(int(max_lines), 6))
```

```python
display_mode = overlay_config.get("display_mode", "standard")
max_lines = None if display_mode == "compact" else overlay_config.get("max_lines", 4)
```

- [ ] **Step 4: Verify and commit**

Run: `python -X faulthandler -m pytest tests/test_guide_data.py -q`

Expected: PASS.

```bash
git add src/utils/guide_data.py src/ui/main_window.py tests/test_guide_data.py
git commit -m "feat: show full guidance in compact mini navi"
```

### Task 3: コンパクトオーバーレイのレイアウトと高さ追従

**Files:**
- Modify: `src/ui/main_window.py:121-760`
- Test: `tests/test_mini_navi_standalone.py:12-92`

**Interfaces:**
- Produces `MiniNaviOverlay.is_compact_mode() -> bool`.
- Produces `MiniNaviOverlay._geometry_config() -> dict` for the active profile.
- Updates `_fit_height_to_content()` to both grow and shrink compact height, capped to the screen's available height.

- [ ] **Step 1: Write failing overlay tests**

```python
def test_compact_mode_uses_bottom_center_geometry_when_unsaved():
    main = QWidget()
    main.config = {"mini_guide_overlay": {"enabled": True, "display_mode": "compact"}}
    overlay = MiniNaviOverlay(main)
    assert overlay.width() == 390
    assert overlay.geometry().center().x() == overlay.screen().availableGeometry().center().x()

def test_compact_mode_saves_geometry_without_overwriting_standard_geometry():
    main = QWidget()
    main.config = {"mini_guide_overlay": {"display_mode": "compact", "width": 800, "height": 130}}
    overlay = MiniNaviOverlay(main)
    overlay.setGeometry(300, 500, 420, 150)
    overlay._remember_current_geometry_to_config()
    assert main.config["mini_guide_overlay"]["width"] == 800
    assert main.config["mini_guide_overlay"]["compact_geometry"]["width"] == 420

def test_compact_height_tracks_long_japanese_text():
    main = QWidget()
    main.config = {"mini_guide_overlay": {"enabled": True, "display_mode": "compact"}}
    overlay = MiniNaviOverlay(main)
    overlay.update_content({"text": "長い日本語案内です。" * 40, "direction": "right"})
    assert overlay.height() > 100
    assert overlay.text_label.width() <= overlay.outer.layout().contentsRect().width()
```

- [ ] **Step 2: Verify the tests fail**

Run: `QT_QPA_PLATFORM=offscreen python -X faulthandler -m pytest tests/test_mini_navi_standalone.py -q`

Expected: FAIL because the overlay has no compact profile or bottom-center defaults.

- [ ] **Step 3: Implement the active profile and default geometry**

```python
COMPACT_DEFAULT_WIDTH = 390
COMPACT_DEFAULT_HEIGHT = 100

def is_compact_mode(self) -> bool:
    return self.config().get("display_mode", "standard") == "compact"

def _geometry_config(self) -> dict:
    config = self._mutable_config()
    return config.setdefault("compact_geometry", {}) if self.is_compact_mode() else config
```

When compact geometry is absent, use `self.screen().availableGeometry()` to center `COMPACT_DEFAULT_WIDTH` horizontally and place `COMPACT_DEFAULT_HEIGHT` against the bottom edge. Read and write only `_geometry_config()` from `apply_settings()` and `_remember_current_geometry_to_config()`.

- [ ] **Step 4: Implement actual-layout width and content-driven height**

For compact mode, use 6px horizontal/5px vertical margins, 4px spacing, and a 40px arrow/experience column. Calculate text width from `outer.layout().contentsRect()` minus the widths of the visible left column, visible size grip, and actual layout spacings; do not use a fixed total subtraction. Set compact height to the calculated needed height even when it is smaller than the current height. Clamp height and final geometry to `self.screen().availableGeometry()`.

- [ ] **Step 5: Verify and commit**

Run: `QT_QPA_PLATFORM=offscreen python -X faulthandler -m pytest tests/test_mini_navi_standalone.py -q`

Expected: PASS.

```bash
git add src/ui/main_window.py tests/test_mini_navi_standalone.py
git commit -m "feat: add compact mini navi layout"
```

### Task 4: 統合回帰確認

**Files:**
- Verify: `tests/test_config_manager.py`
- Verify: `tests/test_guide_data.py`
- Verify: `tests/test_mini_navi_standalone.py`
- Verify: full test suite

**Interfaces:**
- Verifies the existing `MainWindow` settings reload path applies the selected display mode.
- Verifies standard mode remains covered by the existing mini-navi tests.

- [ ] **Step 1: Run the feature-focused suite**

Run: `QT_QPA_PLATFORM=offscreen python -X faulthandler -m pytest tests/test_config_manager.py tests/test_guide_data.py tests/test_mini_navi_standalone.py -q`

Expected: PASS.

- [ ] **Step 2: Run full verification**

Run: `QT_QPA_PLATFORM=offscreen python -X faulthandler -m pytest -q && git diff --check`

Expected: all tests PASS and no whitespace errors.

- [ ] **Step 3: Review the final diff**

Run: `git diff --stat origin/main...HEAD && git status --short`

Expected: only the compact-mini-navi implementation, tests, and its approved design documents are pending publication.
