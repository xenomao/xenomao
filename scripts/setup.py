#!/usr/bin/env python3
"""
DigiLab Beauty - LINEステップライン 初回セットアップウィザード

このスクリプトを1回実行するだけで全部整います。
途中で止まっても、もう一度実行すれば続きから再開できます。
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
DB_PATH = ROOT / "db" / "digilab_beauty.db"

REQUIRED_PACKAGES = ["flask", "requests", "python-dotenv", "pyngrok"]


# ───────────────────────────────────────────────
def header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def ok(text):
    print(f"  ✓ {text}")


def info(text):
    print(f"  ℹ {text}")


def warn(text):
    print(f"  ⚠ {text}")


def ask(prompt, secret=False):
    import getpass
    try:
        if secret:
            return getpass.getpass(f"  → {prompt}: ").strip()
        else:
            return input(f"  → {prompt}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n中断しました。")
        sys.exit(0)


# ───────────────────────────────────────────────
def load_env():
    """現在の .env を {key: value} で返す（コメント行・空行は除外）"""
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def save_env_key(key, value):
    """既存の .env の指定キーを書き換える（なければ末尾に追記）"""
    text = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.exists() else ""
    lines = text.splitlines()
    replaced = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped == f"{key}=":
            new_lines.append(f"{key}={value}")
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        new_lines.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


# ───────────────────────────────────────────────
def step1_packages():
    header("STEP 1 / 4  必要なパッケージをインストール")
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg.replace("-", "_"))
            ok(f"{pkg} （インストール済み）")
        except ImportError:
            info(f"{pkg} をインストール中...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg, "-q",
                 "--ignore-installed", "blinker"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                ok(f"{pkg} インストール完了")
            else:
                warn(f"{pkg} インストール失敗: {result.stderr[:200]}")


def step2_tokens():
    header("STEP 2 / 4  LINEトークンを設定")

    env = load_env()
    token_ok = bool(env.get("LINE_CHANNEL_ACCESS_TOKEN", "").strip())
    secret_ok = bool(env.get("LINE_CHANNEL_SECRET", "").strip())

    if token_ok and secret_ok:
        ok("トークンは既に設定済みです。（変更する場合は .env を直接編集してください）")
        return

    print("""
  LINE Developersコンソールで2つの値を取得してください。
  ブラウザで以下のURLを開いてください:

  https://developers.line.biz/

  ★ 取得手順（5分でできます）★

  1. 上記URLにLINEアカウントでログイン
  2. 「プロバイダー作成」→ 会社名やサービス名を入力
  3. 「チャネル作成」→「Messaging API」を選択
     - チャネル名: DigiLab Beauty（任意）
     - 業種: 美容/エステ
     - メールアドレスを入力 → 作成
  4. 作成したチャネルを開く

  ── チャネルアクセストークン ──
  「Messaging API設定」タブ → 一番下「チャネルアクセストークン（長期）」
  → 「発行」ボタン → 長い文字列をコピー

  ── チャネルシークレット ──
  「チャネル基本設定」タブ → 「チャネルシークレット」の値をコピー
""")

    if not token_ok:
        token = ask("チャネルアクセストークンを貼り付けてください", secret=True)
        if token:
            save_env_key("LINE_CHANNEL_ACCESS_TOKEN", token)
            save_env_key("LINE_DRY_RUN", "0")
            ok("チャネルアクセストークンを保存しました")
        else:
            warn("スキップしました。後で .env に直接入力してください。")

    if not secret_ok:
        secret = ask("チャネルシークレットを貼り付けてください", secret=True)
        if secret:
            save_env_key("LINE_CHANNEL_SECRET", secret)
            ok("チャネルシークレットを保存しました")
        else:
            warn("スキップしました。後で .env に直接入力してください。")


def step3_database():
    header("STEP 3 / 4  データベースを初期化")

    # DB_PATH を repo 内に向ける
    env = load_env()
    if env.get("DB_PATH", "") != str(DB_PATH):
        save_env_key("DB_PATH", str(DB_PATH))
        ok(f"DB_PATH を設定: {DB_PATH}")

    # 環境変数を反映してからインポート
    os.environ["DB_PATH"] = str(DB_PATH)
    os.environ["LINE_DRY_RUN"] = "0"

    # step_line をインポート（ここで初めて可能）
    sys.path.insert(0, str(ROOT / "scripts"))
    import step_line

    step_line.init_schema()

    # シナリオが未投入なら seed
    conn = sqlite3.connect(str(DB_PATH))
    count = conn.execute("SELECT COUNT(*) FROM step_scenarios").fetchone()[0]
    conn.close()
    if count == 0:
        step_line.seed_sample_scenario()
    else:
        ok(f"シナリオは既に {count} 件登録済みです")


def step4_webhook_url():
    header("STEP 4 / 4  LINE DevelopersにWebhook URLを設定")

    print("""
  Webhook URLの設定が必要です。次のステップで行います:

  1. 「launch.py」を起動すると画面に URL が表示されます
     例: https://xxxx.ngrok-free.app/callback

  2. LINE Developers → チャネル →「Messaging API設定」
     「Webhook URL」にそのURLを貼り付け → 「更新」→「検証」

  3. 「Webhookの利用」を ON にする

  ※ launch.py を起動するたびにURLが変わります（ngrok無料版の制限）。
    毎回設定し直しが面倒な場合は、ngrokの固定ドメイン（無料で1つ取得可）をお使いください。
""")
    ok("確認できたらそのまま続けてください")


# ───────────────────────────────────────────────
def main():
    print()
    print("  DigiLab Beauty - LINEステップライン セットアップウィザード")
    print("  途中で止まっても、もう一度実行すれば続きから再開できます。")

    step1_packages()
    step2_tokens()
    step3_database()
    step4_webhook_url()

    header("セットアップ完了！")
    print("""
  次のコマンドを実行してシステムを起動してください:

      python scripts/launch.py

  表示されたWebhook URLをLINE Developersに貼り付ければ、
  友だち追加した瞬間から自動でステップラインが始まります。
""")


if __name__ == "__main__":
    main()
