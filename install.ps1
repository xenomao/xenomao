#Requires -Version 5.1
<#
.SYNOPSIS
    DigiLab Beauty AI組織システム - Windowsセットアップスクリプト

.DESCRIPTION
    PowerShell one-liner でプロジェクトをセットアップします:
      irm https://raw.githubusercontent.com/xenomao/xenomao/main/install.ps1 | iex

.NOTES
    前提条件: Windows 10/11, PowerShell 5.1+, インターネット接続
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ===================================
# ユーティリティ
# ===================================
function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Text)
    Write-Host "[*] $Text" -ForegroundColor Yellow
}

function Write-OK {
    param([string]$Text)
    Write-Host "[OK] $Text" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Text)
    Write-Host "[!] $Text" -ForegroundColor Magenta
}

function Write-Err {
    param([string]$Text)
    Write-Host "[ERROR] $Text" -ForegroundColor Red
}

# ===================================
# 前提条件チェック
# ===================================
function Test-Prerequisites {
    Write-Header "前提条件チェック"

    # Python
    Write-Step "Python 3.12+ を確認中..."
    $python = $null
    foreach ($cmd in @('python', 'python3', 'py')) {
        try {
            $ver = & $cmd --version 2>&1
            if ($ver -match 'Python (\d+)\.(\d+)') {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 12)) {
                    $python = $cmd
                    Write-OK "Python $major.$minor が見つかりました ($cmd)"
                    break
                }
                Write-Warn "Python $major.$minor は古いバージョンです (3.12+ 推奨)"
            }
        } catch { }
    }
    if (-not $python) {
        Write-Err "Python 3.12 以上が必要です。"
        Write-Host "  https://www.python.org/downloads/ からインストールしてください。" -ForegroundColor Gray
        exit 1
    }

    # Git
    Write-Step "Git を確認中..."
    try {
        $gitVer = & git --version 2>&1
        Write-OK "$gitVer が見つかりました"
    } catch {
        Write-Err "Git が見つかりません。"
        Write-Host "  https://git-scm.com/download/win からインストールしてください。" -ForegroundColor Gray
        exit 1
    }

    return $python
}

# ===================================
# リポジトリのクローン / 更新
# ===================================
function Install-Repository {
    param([string]$InstallDir)

    Write-Header "リポジトリのセットアップ"

    $repoUrl = 'https://github.com/xenomao/xenomao.git'

    if (Test-Path (Join-Path $InstallDir '.git')) {
        Write-Step "既存のリポジトリを更新中: $InstallDir"
        Push-Location $InstallDir
        try {
            git pull --ff-only origin main 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
            Write-OK "リポジトリを更新しました"
        } finally {
            Pop-Location
        }
    } else {
        Write-Step "リポジトリをクローン中: $InstallDir"
        git clone $repoUrl $InstallDir 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        Write-OK "クローン完了"
    }
}

# ===================================
# 環境変数 (.env) のセットアップ
# ===================================
function Install-EnvFile {
    param([string]$InstallDir)

    Write-Header "環境変数のセットアップ"

    $envPath = Join-Path $InstallDir '.env'
    $dbPath  = Join-Path $InstallDir 'db\digilab_beauty.db'

    if (Test-Path $envPath) {
        Write-OK ".env ファイルが既に存在します — スキップ"
        return
    }

    Write-Step ".env ファイルを作成中..."

    $newsapiKey = Read-Host "NewsAPI キーを入力してください (スキップは Enter)"
    if (-not $newsapiKey) { $newsapiKey = '' }

    $content = @"
# DigiLab Beauty AI組織システム - 環境変数設定
# このファイルはGitにコミットしないでください

# NewsAPI設定
NEWSAPI_KEY=$newsapiKey

# データベースパス
DB_PATH=$dbPath

# メール設定（将来使用）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=
EMAIL_PASSWORD=

# SerpAPI設定（オプション）
SERPAPI_KEY=
"@

    Set-Content -Path $envPath -Value $content -Encoding UTF8
    Write-OK ".env ファイルを作成しました"
}

# ===================================
# データベース初期化
# ===================================
function Initialize-Database {
    param([string]$InstallDir, [string]$Python)

    Write-Header "データベース初期化"

    $dbDir = Join-Path $InstallDir 'db'
    $dbFile = Join-Path $dbDir 'digilab_beauty.db'
    $initScript = Join-Path $InstallDir 'scripts\init_database.py'

    if (-not (Test-Path $dbDir)) {
        New-Item -ItemType Directory -Path $dbDir | Out-Null
    }

    if (Test-Path $dbFile) {
        Write-OK "データベースが既に存在します — スキップ ($dbFile)"
        return
    }

    if (-not (Test-Path $initScript)) {
        Write-Warn "init_database.py が見つかりません — データベース初期化をスキップ"
        return
    }

    Write-Step "データベースを初期化中..."
    Push-Location $InstallDir
    try {
        & $Python $initScript 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        if ($LASTEXITCODE -ne 0) {
            Write-Warn "データベース初期化中にエラーが発生しました (終了コード: $LASTEXITCODE)"
        } else {
            Write-OK "データベースを初期化しました"
        }
    } finally {
        Pop-Location
    }
}

# ===================================
# ショートカット (オプション)
# ===================================
function Add-StartMenuShortcut {
    param([string]$InstallDir)

    $answer = Read-Host "スタートメニューにショートカットを作成しますか? [y/N]"
    if ($answer -notmatch '^[Yy]') { return }

    $shortcutPath = Join-Path ([Environment]::GetFolderPath('Programs')) 'DigiLab Beauty.lnk'
    $wsh = New-Object -ComObject WScript.Shell
    $sc  = $wsh.CreateShortcut($shortcutPath)
    $sc.TargetPath       = 'powershell.exe'
    $sc.Arguments        = "-NoExit -Command `"Set-Location '$InstallDir'`""
    $sc.WorkingDirectory = $InstallDir
    $sc.Description      = 'DigiLab Beauty AI組織システム'
    $sc.Save()
    Write-OK "ショートカットを作成しました: $shortcutPath"
}

# ===================================
# メイン
# ===================================
function Main {
    Write-Host ""
    Write-Host "  DigiLab Beauty AI組織システム - インストーラー" -ForegroundColor Cyan
    Write-Host "  ================================================" -ForegroundColor Cyan
    Write-Host ""

    # インストール先の決定
    $defaultDir = Join-Path $env:USERPROFILE 'digilab-beauty'
    Write-Host "インストール先 [$defaultDir]: " -NoNewline
    $installDir = Read-Host
    if (-not $installDir) { $installDir = $defaultDir }
    $installDir = [System.IO.Path]::GetFullPath($installDir)

    $python = Test-Prerequisites
    Install-Repository -InstallDir $installDir
    Install-EnvFile    -InstallDir $installDir
    Initialize-Database -InstallDir $installDir -Python $python
    Add-StartMenuShortcut -InstallDir $installDir

    Write-Header "セットアップ完了"
    Write-Host ""
    Write-Host "  プロジェクトフォルダ : $installDir" -ForegroundColor White
    Write-Host ""
    Write-Host "次のステップ:" -ForegroundColor Cyan
    Write-Host "  cd '$installDir'" -ForegroundColor Gray
    Write-Host "  python scripts\main.py          # 初期セットアップ & レポート表示" -ForegroundColor Gray
    Write-Host "  python scripts\daily_news_collection.py  # ニュース収集" -ForegroundColor Gray
    Write-Host ""
    Write-Host "ドキュメント: docs\guides\ フォルダを参照してください" -ForegroundColor Gray
    Write-Host ""
}

Main
