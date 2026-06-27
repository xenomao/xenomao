#!/usr/bin/env python3
"""
@AIマーケティング - LINEステップライン エンジン

LINE公式アカウントの「ステップ配信（ステップライン）」を構築・実行する。
シナリオ（順序＋待機日数つきメッセージ群）に購読者を登録し、
スケジューラが配信予定日になったステップを line_harness 経由で順次送信する。

主な機能:
  init     : ステップライン用テーブルを作成
  seed     : サンプルシナリオ（休眠顧客復活フロー）を投入
  enroll   : 購読者をシナリオに登録
  run      : 配信予定日を迎えたステップを送信（既定はドライラン）
  status   : 進行状況サマリーを表示

必要なパッケージ:
pip install requests python-dotenv

環境変数(.env):
DB_PATH=path/to/digilab_beauty.db
LINE_CHANNEL_ACCESS_TOKEN=...
LINE_DRY_RUN=1
"""

import os
import sys
import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path

from dotenv import load_dotenv

from line_harness import LineHarness, LineHarnessError

load_dotenv()

# DBパス: .env の DB_PATH を優先し、なければリポジトリ内 db/digilab_beauty.db
_DEFAULT_DB = Path(__file__).resolve().parent.parent / "db" / "digilab_beauty.db"
DB_PATH = os.getenv("DB_PATH") or str(_DEFAULT_DB)
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "db" / "line_step_schema.sql"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _today():
    return date.today()


# ======================================================================
# init / seed
# ======================================================================
def init_schema():
    """ステップライン用テーブルを作成"""
    print(f"スキーマ適用中: {SCHEMA_PATH} → {DB_PATH}")
    conn = _connect()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("✓ ステップラインテーブル作成完了")


# 休眠顧客復活フロー（blog/sales/14_line_ai_dormant_revival.md のフローを実装）
DORMANT_REVIVAL = {
    "name": "休眠顧客復活フロー",
    "description": "最終来店からの経過日数に応じて段階的にフォローし、来店を促すステップライン。",
    "trigger_type": "on_dormant",
    "steps": [
        {
            "delay_days": 0,
            "text": "{name}さん、前回の施術から1ヶ月が経ちました。お肌の調子はいかがですか？季節の変わり目はゆらぎやすいので、気になることがあればいつでもご相談くださいね。",
            "note": "休眠30日: 気遣いメッセージのみ（売り込みなし）",
        },
        {
            "delay_days": 30,
            "text": "{name}さんだけの特別ご案内です。今月限定で、次回施術が10%OFFになるクーポンをご用意しました。ぜひこの機会にリフレッシュしにいらしてください。",
            "note": "休眠60日: 軽い特典で来店動機を作る",
        },
        {
            "delay_days": 30,
            "text": "お久しぶりです、{name}さん。新メニューを始めました！初回体験50%OFFでお試しいただけます。気になる肌悩みに合わせてご提案しますので、お気軽にどうぞ。",
            "note": "休眠90日: 新メニュー × 大きな特典で強くアピール",
        },
        {
            "delay_days": 30,
            "text": "{name}さんの肌分析データを改めて確認しました。前回からの変化をぜひお見せしたいので、無料カウンセリングにいらっしゃいませんか？ご予約お待ちしています。",
            "note": "休眠120日以上: データドリブンな理由を提示",
        },
    ],
}


def seed_sample_scenario():
    """サンプルシナリオ（休眠顧客復活フロー）を投入"""
    conn = _connect()
    cur = conn.cursor()

    existing = cur.execute(
        "SELECT scenario_id FROM step_scenarios WHERE name = ?",
        (DORMANT_REVIVAL["name"],),
    ).fetchone()
    if existing:
        print(f"⚠ 既に存在します: {DORMANT_REVIVAL['name']} (scenario_id={existing['scenario_id']})")
        conn.close()
        return existing["scenario_id"]

    cur.execute(
        """INSERT INTO step_scenarios (name, description, trigger_type)
           VALUES (?, ?, ?)""",
        (DORMANT_REVIVAL["name"], DORMANT_REVIVAL["description"], DORMANT_REVIVAL["trigger_type"]),
    )
    scenario_id = cur.lastrowid

    for i, step in enumerate(DORMANT_REVIVAL["steps"], 1):
        cur.execute(
            """INSERT INTO step_messages (scenario_id, step_order, delay_days, message_text, note)
               VALUES (?, ?, ?, ?, ?)""",
            (scenario_id, i, step["delay_days"], step["text"], step["note"]),
        )

    conn.commit()
    conn.close()
    print(f"✓ シナリオ投入完了: {DORMANT_REVIVAL['name']} ({len(DORMANT_REVIVAL['steps'])}ステップ)")
    return scenario_id


# ======================================================================
# 購読者登録 / ステップ登録
# ======================================================================
def upsert_subscriber(line_user_id, display_name=None, segment="新規", company_id=None):
    """LINE友だちを登録 or 更新。subscriber_id を返す。"""
    conn = _connect()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT subscriber_id FROM line_subscribers WHERE line_user_id = ?",
        (line_user_id,),
    ).fetchone()
    if row:
        subscriber_id = row["subscriber_id"]
        cur.execute(
            "UPDATE line_subscribers SET display_name = COALESCE(?, display_name), segment = ? WHERE subscriber_id = ?",
            (display_name, segment, subscriber_id),
        )
    else:
        cur.execute(
            """INSERT INTO line_subscribers (line_user_id, display_name, segment, company_id)
               VALUES (?, ?, ?, ?)""",
            (line_user_id, display_name, segment, company_id),
        )
        subscriber_id = cur.lastrowid
    conn.commit()
    conn.close()
    return subscriber_id


def enroll(subscriber_id, scenario_id, start_date=None):
    """購読者をシナリオに登録。最初のステップの送信予定日を設定する。"""
    conn = _connect()
    cur = conn.cursor()

    first = cur.execute(
        "SELECT delay_days FROM step_messages WHERE scenario_id = ? ORDER BY step_order LIMIT 1",
        (scenario_id,),
    ).fetchone()
    if first is None:
        conn.close()
        raise ValueError(f"シナリオ {scenario_id} にステップがありません。先に seed してください。")

    base = start_date or _today()
    next_send = base + timedelta(days=first["delay_days"])

    try:
        cur.execute(
            """INSERT INTO step_enrollments (subscriber_id, scenario_id, current_step, next_send_date)
               VALUES (?, ?, 0, ?)""",
            (subscriber_id, scenario_id, next_send.isoformat()),
        )
        enrollment_id = cur.lastrowid
        conn.commit()
        print(f"✓ 登録: subscriber={subscriber_id} → scenario={scenario_id} (初回送信予定 {next_send})")
    except sqlite3.IntegrityError:
        existing = cur.execute(
            "SELECT enrollment_id FROM step_enrollments WHERE subscriber_id = ? AND scenario_id = ?",
            (subscriber_id, scenario_id),
        ).fetchone()
        enrollment_id = existing["enrollment_id"]
        print(f"⚠ 既に登録済み: enrollment_id={enrollment_id}")
    conn.close()
    return enrollment_id


# ======================================================================
# スケジューラ本体
# ======================================================================
def _render(text, subscriber):
    """プレースホルダを置換（{name} → 表示名 or 'お客様'）"""
    name = subscriber["display_name"] or "お客様"
    return text.replace("{name}", name)


def run(target_date=None, dry_run=None):
    """配信予定日を迎えた進行中エンロールメントに対し、次ステップを送信する。"""
    run_date = target_date or _today()
    harness = LineHarness(dry_run=dry_run)
    mode = "ドライラン" if harness.dry_run else "本送信"

    print("=" * 60)
    print(f"ステップライン実行 [{mode}] 基準日: {run_date}")
    print("=" * 60)

    conn = _connect()
    cur = conn.cursor()

    due = cur.execute(
        """SELECT e.enrollment_id, e.subscriber_id, e.scenario_id, e.current_step,
                  s.line_user_id, s.display_name, s.status AS sub_status
           FROM step_enrollments e
           JOIN line_subscribers s ON s.subscriber_id = e.subscriber_id
           WHERE e.status = '進行中'
             AND e.next_send_date IS NOT NULL
             AND e.next_send_date <= ?
           ORDER BY e.enrollment_id""",
        (run_date.isoformat(),),
    ).fetchall()

    sent, skipped, completed, failed = 0, 0, 0, 0

    for enr in due:
        # ブロック/退会者はスキップ
        if enr["sub_status"] != "有効":
            skipped += 1
            print(f"  - skip enrollment {enr['enrollment_id']}: 購読者ステータス={enr['sub_status']}")
            continue

        next_step_order = enr["current_step"] + 1
        step = cur.execute(
            "SELECT * FROM step_messages WHERE scenario_id = ? AND step_order = ?",
            (enr["scenario_id"], next_step_order),
        ).fetchone()

        if step is None:
            # ステップ切れ → 完了
            cur.execute(
                "UPDATE step_enrollments SET status='完了', next_send_date=NULL, completed_at=CURRENT_TIMESTAMP WHERE enrollment_id=?",
                (enr["enrollment_id"],),
            )
            completed += 1
            print(f"  ✓ 完了: enrollment {enr['enrollment_id']}")
            continue

        text = _render(step["message_text"], enr)
        try:
            resp = harness.push_text(enr["line_user_id"], text)
            log_status = "ドライラン" if harness.dry_run else "送信完了"
            cur.execute(
                """INSERT INTO step_delivery_log (enrollment_id, message_id, step_order, status, response)
                   VALUES (?, ?, ?, ?, ?)""",
                (enr["enrollment_id"], step["message_id"], next_step_order, log_status, str(resp)[:1000]),
            )

            # 次ステップの予定日を計算
            following = cur.execute(
                "SELECT delay_days FROM step_messages WHERE scenario_id = ? AND step_order = ?",
                (enr["scenario_id"], next_step_order + 1),
            ).fetchone()

            if following is None:
                cur.execute(
                    """UPDATE step_enrollments
                       SET current_step=?, status='完了', next_send_date=NULL, completed_at=CURRENT_TIMESTAMP
                       WHERE enrollment_id=?""",
                    (next_step_order, enr["enrollment_id"]),
                )
                completed += 1
            else:
                next_date = run_date + timedelta(days=following["delay_days"])
                cur.execute(
                    "UPDATE step_enrollments SET current_step=?, next_send_date=? WHERE enrollment_id=?",
                    (next_step_order, next_date.isoformat(), enr["enrollment_id"]),
                )

            sent += 1
            preview = text[:40].replace("\n", " ")
            print(f"  ✓ step{next_step_order} → {enr['display_name'] or enr['line_user_id']}: {preview}…")

        except LineHarnessError as e:
            cur.execute(
                """INSERT INTO step_delivery_log (enrollment_id, message_id, step_order, status, response)
                   VALUES (?, ?, ?, '失敗', ?)""",
                (enr["enrollment_id"], step["message_id"], next_step_order, str(e)[:1000]),
            )
            failed += 1
            print(f"  ✗ 失敗: enrollment {enr['enrollment_id']}: {e}")

    conn.commit()
    conn.close()

    print("-" * 60)
    print(f"送信:{sent}  完了:{completed}  スキップ:{skipped}  失敗:{failed}")
    print("=" * 60)
    return {"sent": sent, "completed": completed, "skipped": skipped, "failed": failed}


# ======================================================================
# status
# ======================================================================
def status():
    """進行状況サマリーを表示"""
    conn = _connect()
    cur = conn.cursor()

    print("=" * 60)
    print("ステップライン 状況サマリー")
    print("=" * 60)

    scenarios = cur.execute(
        "SELECT scenario_id, name, status FROM step_scenarios ORDER BY scenario_id"
    ).fetchall()
    print(f"\nシナリオ: {len(scenarios)}件")
    for s in scenarios:
        steps = cur.execute(
            "SELECT COUNT(*) c FROM step_messages WHERE scenario_id = ?", (s["scenario_id"],)
        ).fetchone()["c"]
        print(f"  [{s['scenario_id']}] {s['name']} ({s['status']}, {steps}ステップ)")

    subs = cur.execute("SELECT COUNT(*) c FROM line_subscribers").fetchone()["c"]
    print(f"\n購読者: {subs}名")

    print("\nエンロールメント状況:")
    rows = cur.execute(
        "SELECT status, COUNT(*) c FROM step_enrollments GROUP BY status"
    ).fetchall()
    for r in rows:
        print(f"  {r['status']}: {r['c']}件")

    print("\n直近の配信ログ（最新5件）:")
    logs = cur.execute(
        """SELECT l.sent_at, l.step_order, l.status, s.display_name
           FROM step_delivery_log l
           JOIN step_enrollments e ON e.enrollment_id = l.enrollment_id
           JOIN line_subscribers s ON s.subscriber_id = e.subscriber_id
           ORDER BY l.log_id DESC LIMIT 5"""
    ).fetchall()
    for lg in logs:
        print(f"  {lg['sent_at']} step{lg['step_order']} [{lg['status']}] {lg['display_name']}")
    if not logs:
        print("  （まだ配信ログはありません）")

    conn.close()
    print("=" * 60)


# ======================================================================
# CLI
# ======================================================================
def _demo():
    """init→seed→ダミー購読者登録→enroll→run を一気に流すデモ（全てドライラン）"""
    init_schema()
    scenario_id = seed_sample_scenario()
    sub_id = upsert_subscriber("Udemo000000000000000000000000demo", "山田 花子", segment="休眠")
    enroll(sub_id, scenario_id)
    print()
    run(dry_run=True)  # 初回ステップ(delay 0)は即日対象
    print()
    status()


def main():
    usage = (
        "使い方: python step_line.py <command>\n"
        "  init    : テーブル作成\n"
        "  seed    : サンプルシナリオ投入\n"
        "  run     : 配信実行（ドライラン。実送信は .env LINE_DRY_RUN=0）\n"
        "  run-live: 配信実行（実送信を強制）\n"
        "  status  : 状況サマリー\n"
        "  demo    : init→seed→登録→run を通しで実行（ドライラン）"
    )
    if len(sys.argv) < 2:
        print(usage)
        return

    cmd = sys.argv[1]
    if cmd == "init":
        init_schema()
    elif cmd == "seed":
        seed_sample_scenario()
    elif cmd == "run":
        run(dry_run=True)
    elif cmd == "run-live":
        run(dry_run=False)
    elif cmd == "status":
        status()
    elif cmd == "demo":
        _demo()
    else:
        print(f"不明なコマンド: {cmd}\n")
        print(usage)


if __name__ == "__main__":
    main()
