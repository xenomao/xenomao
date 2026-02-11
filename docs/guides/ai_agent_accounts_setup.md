# DigiLab Beauty AI組織 - アカウント設定ガイド

## 📋 概要

DigiLab Beauty AI組織システムを運用するための5つのAIエージェントアカウントを設定します。

---

## 🤖 AIエージェントアカウント一覧

### 1. @AI執行役員（Chief AI Officer）

**メールアドレス**: `ai-ceo@digilab-beauty.com`

**役割**:
- 全体統括・戦略立案・意思決定
- 週次・月次レポートの作成と配信
- KPIモニタリングとダッシュボード管理

**必要なアクセス権限**:
- Google Workspace (管理者権限)
- 全データベースへのフルアクセス
- 全AIエージェントの成果物閲覧

**初期設定タスク**:
- [ ] Googleアカウント作成
- [ ] データベース管理者権限付与
- [ ] KPIダッシュボードアクセス設定

---

### 2. @AI営業（Sales AI Agent）

**メールアドレス**: `ai-sales@digilab-beauty.com`

**役割**:
- 営業リスト管理（エステ業界19社など）
- アプローチメール作成・送信
- 商談設定・フォローアップ

**必要なアクセス権限**:
- Gmail API（メール送受信）
- Google Calendar API（商談設定）
- データベース（companies, contacts, contact_history, sales_pipeline）
- CRM（顧客管理）システム

**初期設定タスク**:
- [ ] Googleアカウント作成
- [ ] Gmail API有効化
- [ ] Calendar API連携設定
- [ ] データベースアクセス権限付与
- [ ] メール署名設定

**メール署名テンプレート**:
```
--
DigiLab Beauty AI営業部
Email: ai-sales@digilab-beauty.com
Web: https://digilab-beauty.com/
自動送信メッセージです。ご不明点は上記までお問い合わせください。
```

---

### 3. @AIマーケティング（Marketing AI Agent）

**メールアドレス**: `ai-marketing@digilab-beauty.com`

**役割**:
- PR戦略立案・プレスリリース作成
- SNSコンテンツ自動生成・投稿
- セミナー企画・運営

**必要なアクセス権限**:
- PR TIMES APIアクセス
- SNS APIアクセス（Twitter/X, LinkedIn, Facebook）
- Google Drive（コンテンツ保存）
- データベース（documents, intelligence_log）

**初期設定タスク**:
- [ ] Googleアカウント作成
- [ ] PR TIMES法人アカウント連携
- [ ] SNSアカウント連携
- [ ] コンテンツライブラリ作成

**SNSアカウント**:
- Twitter/X: `@DigiLabBeauty_AI`
- LinkedIn: `DigiLab Beauty`
- Facebook ページ: `DigiLab Beauty Official`

---

### 4. @AI担当（Intelligence AI Agent）

**メールアドレス**: `ai-intelligence@digilab-beauty.com`

**役割**:
- Opal連携・最新情報収集
- 業界ニュース・競合分析
- DD情報の定期更新

**必要なアクセス権限**:
- **Opal API**（最重要）
- Webスクレイピングツール
- データベース（intelligence_log, companies）
- Google Drive（レポート保存）

**初期設定タスク**:
- [ ] Googleアカウント作成
- [ ] Opal APIキー取得・設定
- [ ] 情報収集スクリプト設定
- [ ] 定期実行スケジュール設定

**Opal収集対象**:
- エステ業界ニュース
- 企業倒産・M&A情報
- 新規出店・閉店情報
- 技術トレンド
- 競合企業動向

---

### 5. @AI事務局（Administration AI Agent）

**メールアドレス**: `ai-admin@digilab-beauty.com`

**役割**:
- スケジュール管理・会議設定
- タスク管理・進捗追跡
- ドキュメント整理・アーカイブ

**必要なアクセス権限**:
- Google Calendar API（全AIエージェントのカレンダー）
- Google Drive（ドキュメント管理）
- データベース（tasks, documents）

**初期設定タスク**:
- [ ] Googleアカウント作成
- [ ] Calendar API連携設定
- [ ] Drive フォルダ構造作成
- [ ] タスク管理システム設定

**Driveフォルダ構造**:
```
DigiLab Beauty/
├── 01_戦略・計画/
│   ├── 経営戦略/
│   └── 事業計画/
├── 02_営業/
│   ├── 提案資料/
│   ├── 契約書/
│   └── 商談議事録/
├── 03_マーケティング/
│   ├── プレスリリース/
│   ├── SNSコンテンツ/
│   └── セミナー資料/
├── 04_情報収集/
│   ├── 業界レポート/
│   └── 競合分析/
└── 05_事務局/
    ├── 議事録/
    └── アーカイブ/
```

---

## 🔐 セキュリティ設定

### APIキー管理

すべてのAPIキーは環境変数またはシークレット管理ツールで管理します。

**必要なAPIキー**:
- Google Workspace API キー
- Opal API キー
- PR TIMES API キー
- Twitter/X API キー
- LinkedIn API キー
- Facebook API キー

**環境変数設定例**:
```bash
# .env ファイル
GOOGLE_API_KEY=xxx
OPAL_API_KEY=xxx
PRTIMES_API_KEY=xxx
TWITTER_API_KEY=xxx
LINKEDIN_API_KEY=xxx
FACEBOOK_API_KEY=xxx

# データベース
DB_PATH=C:\Users\pline\.gemini\antigravity\scratch\digilab_beauty.db
```

### 2要素認証

すべてのAIエージェントアカウントで2要素認証を有効にします。

---

## 📅 定期実行スケジュール

### @AI担当（毎日実行）
- **6:00** - 業界ニュース収集（Opal経由）
- **18:00** - DD情報更新チェック

### @AI営業（平日実行）
- **9:00** - 本日の商談確認・リマインダー送信
- **17:00** - 営業アクション実績レポート

### @AIマーケティング（週次実行）
- **月曜 10:00** - 週間コンテンツカレンダー作成
- **金曜 15:00** - SNS投稿予約設定

### @AI事務局（毎日実行）
- **8:00** - 今日のタスクリスト配信
- **19:00** - タスク完了状況レポート

### @AI執行役員（定期レポート）
- **毎週月曜 10:00** - 週次KPIレポート
- **毎月1日 10:00** - 月次経営レポート

---

## 🚀 初回セットアップ手順

### Step 1: Googleアカウント作成
```
1. Google Workspace管理コンソールにアクセス
2. 5つのアカウントを作成
   - ai-ceo@digilab-beauty.com
   - ai-sales@digilab-beauty.com
   - ai-marketing@digilab-beauty.com
   - ai-intelligence@digilab-beauty.com
   - ai-admin@digilab-beauty.com
3. 各アカウントに適切な権限を付与
```

### Step 2: API連携設定
```
1. Google Cloud Consoleでプロジェクト作成
2. 必要なAPI有効化
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Sheets API
3. API認証情報作成
4. 環境変数に設定
```

### Step 3: Opal連携設定
```
1. Opalアカウント作成
2. APIキー取得
3. 収集対象の設定
4. スケジュール実行設定
```

### Step 4: データベース初期化
```
1. SQLiteデータベース作成
2. スキーマ適用
3. エステ業界19社データインポート
4. 初期タスク作成
```

### Step 5: 動作確認
```
1. @AI担当：情報収集テスト
2. @AI営業：テストメール送信
3. @AIマーケティング：SNS投稿テスト
4. @AI事務局：カレンダー同期確認
5. @AI執行役員：ダッシュボード表示確認
```

---

## 📊 アカウント別KPI

### @AI営業
- 月間アプローチ数: 目標 20社
- アポイント獲得率: 目標 15%
- 成約率: 目標 30%

### @AIマーケティング
- リード獲得数: 月間 10件
- SNSエンゲージメント率: 5%以上
- プレスリリース掲載数: 月間 1-2件

### @AI担当
- 情報収集件数: 日次 10件以上
- DD更新精度: 95%以上
- レポート作成: 週次 1件

### @AI事務局
- タスク完了率: 90%以上
- スケジュール遵守率: 95%以上

### @AI執行役員
- 全体KPI達成率: 80%以上
- レポート配信遅延: 0件

---

## ⚠️ 注意事項

1. **個人情報の取り扱い**
   - 顧客データは暗号化して保存
   - アクセスログを記録

2. **メール送信**
   - 特定電子メール法を遵守
   - 配信停止リンクを必ず含める

3. **APIレート制限**
   - Google API: 1日あたりの上限に注意
   - Opal API: プランに応じた制限
   - SNS API: 時間あたりの投稿数制限

4. **バックアップ**
   - データベース: 毎日自動バックアップ
   - ドキュメント: Google Drive自動バックアップ

---

## 🔗 関連ドキュメント

- [実装計画](file:///C:/Users/pline/.gemini/antigravity/brain/2afe8af7-9876-4b0c-bc66-771fe18d81bb/implementation_plan.md)
- [タスク管理](file:///C:/Users/pline/.gemini/antigravity/brain/2afe8af7-9876-4b0c-bc66-771fe18d81bb/task.md)
- [データベース設計](file:///C:/Users/pline/.gemini/antigravity/scratch/digilab_beauty_db_schema.sql)

---

## 📞 サポート

設定に関する質問や問題が発生した場合は、DigiLab Beauty開発チームまでお問い合わせください。
