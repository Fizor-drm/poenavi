$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$releaseDir = Join-Path $repoRoot "dist\PoENavi"
$archive = Join-Path $repoRoot "PoENavi.zip"
$testRoot = Join-Path $repoRoot "build\local-update-e2e"
$installDir = Join-Path $testRoot "install\PoENavi"
$userDataDir = Join-Path $testRoot "user-data"
$workDir = Join-Path $testRoot "updater-work"
$notesPath = Join-Path $userDataDir "area_notes_poe1.json"
$oldGuideMarker = "LOCAL_UPDATE_TEST_OLD_GUIDE"

if (-not (Test-Path (Join-Path $releaseDir "PoENavi.exe"))) {
    throw "dist\PoENavi\PoENavi.exe がありません。先に build_exe.bat を実行してください。"
}
if (-not (Test-Path (Join-Path $releaseDir "PoENaviUpdater.exe"))) {
    throw "dist\PoENavi\PoENaviUpdater.exe がありません。先に build_exe.bat を実行してください。"
}
if (-not (Test-Path $archive)) {
    throw "PoENavi.zip がありません。先に build_exe.bat を実行してください。"
}

Remove-Item $testRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item (Split-Path $installDir) -ItemType Directory -Force | Out-Null
New-Item $userDataDir -ItemType Directory -Force | Out-Null
New-Item $workDir -ItemType Directory -Force | Out-Null
Copy-Item $releaseDir $installDir -Recurse

# 旧版だけに存在するガイド内容を作り、更新後に公式版へ置換されたことを確認する。
[IO.File]::WriteAllText(
    (Join-Path $installDir "guide_data.json"),
    $oldGuideMarker,
    [Text.UTF8Encoding]::new($false)
)

# 実際のエリアメモ形式で隔離ユーザーデータを用意する。
$noteJson = @'
{
  "schema": 1,
  "notes": {
    "act1_area1": "ローカル更新テスト用メモ"
  }
}
'@
[IO.File]::WriteAllText($notesPath, $noteJson, [Text.UTF8Encoding]::new($false))
$notesHashBefore = (Get-FileHash $notesPath -Algorithm SHA256).Hash

$updater = Join-Path $workDir "PoENaviUpdater.exe"
$stagedArchive = Join-Path $workDir "PoENavi.zip"
Copy-Item (Join-Path $releaseDir "PoENaviUpdater.exe") $updater
Copy-Item $archive $stagedArchive

$previousUserDataDir = $env:POENAVI_USER_DATA_DIR
$env:POENAVI_USER_DATA_DIR = $userDataDir
try {
    $process = Start-Process -FilePath $updater -ArgumentList @(
        "--pid", "2147483647",
        "--archive", ('"' + $stagedArchive + '"'),
        "--install-dir", ('"' + $installDir + '"'),
        "--work-dir", ('"' + $workDir + '"')
    ) -WorkingDirectory $workDir -PassThru -Wait
}
finally {
    if ($null -eq $previousUserDataDir) {
        Remove-Item Env:POENAVI_USER_DATA_DIR -ErrorAction SilentlyContinue
    }
    else {
        $env:POENAVI_USER_DATA_DIR = $previousUserDataDir
    }
}

if ($process.ExitCode -ne 0) {
    throw "アップデーターが終了コード $($process.ExitCode) で失敗しました。"
}
if (-not (Test-Path (Join-Path $installDir "PoENavi.exe"))) {
    throw "更新後のPoENavi.exeがありません。"
}
if ((Get-Content (Join-Path $installDir "guide_data.json") -Raw) -eq $oldGuideMarker) {
    throw "旧公式ガイドが更新版へ置換されていません。"
}
if (-not (Test-Path $notesPath)) {
    throw "更新後にエリアメモが失われました。"
}
$notesHashAfter = (Get-FileHash $notesPath -Algorithm SHA256).Hash
if ($notesHashAfter -ne $notesHashBefore) {
    throw "更新中にエリアメモが変更されました。"
}

Write-Host ""
Write-Host "LOCAL UPDATE TEST SUCCESS" -ForegroundColor Green
Write-Host "- 公式ガイド: 更新版へ置換"
Write-Host "- エリアメモ: 保持"
Write-Host "- 新版PoENavi: 自動起動"
Write-Host "テスト用データ: $testRoot"

