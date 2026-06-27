# LINEステップライン 構築・運用ガイド

LINE公式アカウントの**ステップ配信（ステップライン）**を構築・運用するための手順書です。
`scripts/line_harness.py`（送信ハーネス）と `scripts/step_line.py`（ステップエンジン）で構成されます。

---

## 🧩 アーキテクチャ

```
step_line.py（エンジン）
  ├─ シナリオ定義     : step_scenarios / step_messages
  ├─ 購読者管理       : line_subscribers
  ├─ 進行状況         : step_enrollments
  ├─ 配信ログ         : step_delivery_log
  └─ 送信  ──────────▶ line_harness.py（LINE Messaging API）
                          ├─ push_text       単一ユーザー送信
                          ├─ multicast_text  一斉送信（500件で自動分割）
                          ├─ get_profile     表示名取得
                          └─ quota           無料枠確認
```

「ステップライン」= 経過日数（`delay_days`）に応じて、シナリオ内のメッセージを
**順番に1通ずつ自動配信**する仕組み。スケジューラ（`run`）を毎日1回実行すると、
その日が送信予定日（`next_send_date`）になったエンロールメントだけが次ステップを受信します。

---

## ⚙️ セットアップ

### 1. 依存パッケージ

```bash
pip install requests python-dotenv
```

### 2. 環境変数（`.env`）

```ini
DB_PATH=/path/to/digilab_beauty.db          # 未設定なら repo内 db/digilab_beauty.db
LINE_CHANNEL_ACCESS_TOKEN=（長期チャネルアクセストークン）
LINE_DRY_RUN=1                              # 1=ドライラン（既定/誤送信防止）, 0=本送信
```

トークンは [LINE Developers](https://developers.line.biz/) コンソールの
対象チャネル →「Messaging API設定」→「チャネルアクセストークン（長期）」から取得します。

> ⚠️ 既定は **ドライラン**（`LINE_DRY_RUN=1`）です。実際にLINEへ送るまでは
> APIを叩かず、送信内容のプレビューとログ記録のみ行います。

### 3. テーブル作成 & サンプルシナリオ投入

```bash
cd scripts
python step_line.py init    # 5テーブルを作成（既存DBに追加適用）
python step_line.py seed    # サンプル「休眠顧客復活フロー」を投入
```

---

## 🚀 使い方

### CLIコマンド

| コマンド | 内容 |
|---------|------|
| `python step_line.py init`     | ステップライン用テーブルを作成 |
| `python step_line.py seed`     | サンプルシナリオを投入 |
| `python step_line.py run`      | 配信実行（**ドライラン**） |
| `python step_line.py run-live` | 配信実行（**実送信を強制**） |
| `python step_line.py status`   | 状況サマリーを表示 |
| `python step_line.py demo`     | init→seed→登録→run を通しで実行（ドライラン） |

### 購読者の登録とエンロール（Python）

```python
import step_line

# 1. LINE友だちを登録
sub_id = step_line.upsert_subscriber(
    line_user_id="Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    display_name="山田 花子",
    segment="休眠",
)

# 2. シナリオに登録（scenario_id=1 は休眠顧客復活フロー）
step_line.enroll(sub_id, scenario_id=1)

# 3. 配信実行（その日が送信予定日のステップだけ送信）
step_line.run(dry_run=True)   # 本送信は dry_run=False
```

### 毎日の自動実行（cron例）

```cron
# 毎朝10時にステップ配信を実行
0 10 * * *  cd /path/to/repo/scripts && python step_line.py run-live >> /var/log/step_line.log 2>&1
```

---

## 📨 サンプルシナリオ：休眠顧客復活フロー

`blog/sales/14_line_ai_dormant_revival.md` のフローを実装したものです。

| ステップ | 待機日数 | 配信意図 |
|---------|---------|---------|
| 1 | 0日   | 気遣いメッセージのみ（売り込みなし） |
| 2 | +30日 | 軽い特典（10%OFF）で来店動機を作る |
| 3 | +30日 | 新メニュー × 大きな特典で強くアピール |
| 4 | +30日 | データドリブンな理由で無料カウンセリングへ誘導 |

本文中の `{name}` は購読者の表示名（未設定時は「お客様」）に自動置換されます。

---

## 🛠️ 独自シナリオの作り方

`step_scenarios` に1行、`step_messages` に各ステップを `step_order` 昇順で登録します。

```sql
INSERT INTO step_scenarios (name, description, trigger_type)
VALUES ('新規友だち歓迎フロー', '友だち追加直後のオンボーディング', 'on_friend_add');

INSERT INTO step_messages (scenario_id, step_order, delay_days, message_text, note)
VALUES
  (2, 1, 0,  '{name}さん、友だち追加ありがとうございます！初回クーポンをお送りします。', '即時'),
  (2, 2, 3,  '当サロンのこだわりをご紹介します。', '3日後'),
  (2, 3, 7,  'そろそろご予約はいかがですか？ご希望日をお知らせください。', '7日後');
```

`delay_days` は **前ステップ（ステップ1は登録日）からの待機日数**です。

---

## 📊 運用上の注意

- **配信頻度**: LINEはブロック率が頻度に敏感。過剰配信を避ける（目安: 月2回程度）。
- **ブロック/退会者**: `line_subscribers.status` を `ブロック`/`退会` にすると `run` 時に自動スキップ。
- **無料枠**: `LineHarness().quota()` で当月の送信可能数を確認できる。
- **冪等性**: `run` は送信予定日を過ぎたステップのみ送信し、同日二重送信はしない。
- **multicast**: 一斉配信は500件を超えると自動でバッチ分割される。
