# OpenAI Codex CLI 導入ガイド

## ✅ インストール完了

| 項目 | 内容 |
|------|------|
| **バージョン** | codex-cli 0.98.0 |
| **インストール先** | C:\Users\pline\AppData\Roaming\npm |
| **前提条件** | Node.js v25.6.0 ✅ |

---

## 🔑 APIキーの設定（必須）

Codex CLIを使うにはOpenAI APIキーが必要です。

### Step 1: OpenAI APIキーを取得
```
1. https://platform.openai.com/api-keys にアクセス
2. OpenAIアカウントでログイン（なければ作成）
3. 「Create new secret key」をクリック
4. キー名: 「DigiLab Beauty Codex」
5. 生成されたキー（sk-で始まる文字列）をコピー
```

### Step 2: 環境変数を設定
PowerShellで以下を実行：
```powershell
# 一時的に設定（現在のセッションのみ）
$env:OPENAI_API_KEY = "sk-ここにAPIキーを貼り付け"

# 永続的に設定（推奨）
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-ここにAPIキーを貼り付け", "User")
```

### Step 3: 動作確認
```powershell
codex "Hello, what can you do?"
```

---

## 🚀 DigiLab Beautyでの活用方法

### 使い方の基本
```powershell
# プロジェクトフォルダに移動
cd C:\Users\pline\.gemini\antigravity\scratch\digilab-beauty

# Codexに指示を出す
codex "このプロジェクトの構成を説明して"
codex "daily_news_collection.pyにエラーハンドリングを追加して"
codex "営業メールのテンプレートを作成して"
```

### 具体的な活用シーン

#### @AI担当として
```powershell
codex "scripts/daily_news_collection.pyを改善して、
       収集したニュースの重要度を自動判定する機能を追加して"
```

#### @AI営業として
```powershell
codex "Tier A企業5社向けの個別カスタマイズされた
       アプローチメールを作成して"
```

#### @AIマーケティングとして
```powershell
codex "DigiLab Beautyのプレスリリースを
       PR TIMES形式で作成して"
```

#### @AI事務局として
```powershell
codex "bulk_email_procedure.mdの手順に基づいて、
       メール送信の自動化スクリプトを作成して"
```

---

## ⚙️ 設定オプション

### 安全モード（推奨）
```powershell
# ファイル変更前に確認を求めるモード（デフォルト）
codex --approval-mode suggest "タスク内容"

# 自動実行モード（上級者向け）
codex --approval-mode auto-edit "タスク内容"

# 完全自動モード（注意して使用）
codex --approval-mode full-auto "タスク内容"
```

### モデル指定
```powershell
# デフォルトモデル
codex "タスク内容"

# 特定モデルを指定
codex --model gpt-4o "タスク内容"
```

---

## 📁 プロジェクト設定ファイル

Codexがプロジェクトの文脈を理解できるよう、
以下のファイルをプロジェクトルートに配置済みです。

### codex.md（プロジェクト説明）
Codexに渡すプロジェクト概要を記載します。

---

## 💰 料金について

OpenAI APIは従量課金制です：
- **GPT-4o**: $2.50 / 100万入力トークン
- **GPT-4o mini**: $0.15 / 100万入力トークン
- 初回$5の無料クレジットあり（新規アカウント）

---

## ✅ セットアップ完了チェックリスト

- [x] Node.js v25.6.0 インストール済み
- [x] Codex CLI v0.98.0 インストール済み
- [x] PATH設定済み
- [ ] OpenAI APIキー取得（ユーザー操作必要）
- [ ] 環境変数 OPENAI_API_KEY 設定（ユーザー操作必要）
- [ ] 動作確認テスト

**作成日**: 2026-02-11  
**担当**: @AI担当
