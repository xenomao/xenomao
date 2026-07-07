"""デモ用のサンプルデータを投入するスクリプト。
   実行: python seed.py   （cosmebrain.db を作り直してサンプルを入れます）
"""
import os
import sqlite3
import secrets
from werkzeug.security import generate_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "cosmebrain.db")

PLATFORM_FEE_RATE = 12


def ref():
    return secrets.token_urlsafe(6)


def main():
    if os.path.exists(DB):
        os.remove(DB)
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    with open(os.path.join(BASE, "schema.sql"), encoding="utf-8") as f:
        db.executescript(f.read())

    def add_user(email, name, pw="password", admin=0, bio=""):
        cur = db.execute(
            "INSERT INTO users(email,password_hash,display_name,referral_code,is_admin,bio) VALUES(?,?,?,?,?,?)",
            (email, generate_password_hash(pw), name, ref(), admin, bio),
        )
        return cur.lastrowid

    def add_cert(uid, ctype, verified=1):
        db.execute(
            "INSERT INTO certifications(user_id,cert_type,cert_number,verified,verified_at) VALUES(?,?,?,?,CURRENT_TIMESTAMP)",
            (uid, ctype, f"CC-{secrets.randbelow(9999999):07d}", verified),
        )

    def add_content(seller, title, summary, body, cat, price, rate=30, emoji="📘"):
        cur = db.execute(
            """INSERT INTO contents(seller_id,title,summary,body,cover_emoji,category,price,referral_rate)
               VALUES(?,?,?,?,?,?,?,?)""",
            (seller, title, summary, body, emoji, cat, price, rate),
        )
        return cur.lastrowid

    def buy(cid, buyer, referrer=None):
        c = db.execute("SELECT * FROM contents WHERE id=?", (cid,)).fetchone()
        price = c["price"]
        commission = price * c["referral_rate"] // 100 if referrer else 0
        fee = price * PLATFORM_FEE_RATE // 100
        seller_earn = price - commission - fee
        cur = db.execute(
            """INSERT INTO purchases(content_id,buyer_id,price_paid,referrer_id,referral_commission,seller_earning,platform_fee)
               VALUES(?,?,?,?,?,?,?)""",
            (cid, buyer, price, referrer, commission, seller_earn, fee),
        )
        pid = cur.lastrowid
        db.execute("UPDATE contents SET sales_count=sales_count+1 WHERE id=?", (cid,))
        db.execute("UPDATE users SET balance=balance+? WHERE id=?", (seller_earn, c["seller_id"]))
        db.execute("INSERT INTO earnings(user_id,amount,kind,purchase_id,note) VALUES(?,?,?,?,?)",
                   (c["seller_id"], seller_earn, "sale", pid, f"「{c['title']}」の販売"))
        if referrer and commission:
            db.execute("UPDATE users SET balance=balance+? WHERE id=?", (commission, referrer))
            db.execute("INSERT INTO earnings(user_id,amount,kind,purchase_id,note) VALUES(?,?,?,?,?)",
                       (referrer, commission, "referral", pid, f"「{c['title']}」の紹介報酬"))
        return pid

    def review(cid, uid, rating, comment):
        db.execute("INSERT INTO reviews(content_id,user_id,rating,comment) VALUES(?,?,?,?)",
                   (cid, uid, rating, comment))

    # --- 運営 ---
    add_user("admin@cosmebrain.jp", "運営事務局", "admin", admin=1)

    # --- 販売者（有資格者）---
    mika = add_user("mika@example.com", "美容ライターMIKA", bio="化粧品検定1級。成分オタクです。")
    add_cert(mika, "化粧品検定1級")
    yuki = add_user("yuki@example.com", "エステティシャンYUKI", bio="美肌検定保持。サロン12年。")
    add_cert(yuki, "美肌検定")
    rena = add_user("rena@example.com", "コスメコンシェルRENA", bio="化粧品検定2級／美肌検定。")
    add_cert(rena, "化粧品検定2級")
    add_cert(rena, "美肌検定")

    # --- 一般購入者 ---
    aoi = add_user("aoi@example.com", "あおい")
    sora = add_user("sora@example.com", "そら")

    # 審査待ちの申請（運営画面デモ用）
    pending = add_user("pending@example.com", "申請中ユーザー")
    add_cert(pending, "化粧品検定3級", verified=0)

    # --- コンテンツ ---
    c1 = add_content(mika,
        "化粧品検定1級が教える「成分表示の読み解き方」完全ガイド",
        "全成分表示はルールさえ分かれば怖くない。配合順の意味、避けたい成分、本当に効く成分の見分け方を、現役有資格者が体系的に解説します。",
        "■第1章 全成分表示の基本ルール\n配合量の多い順に記載される——ただし1%以下は順不同。この「1%ライン」を見抜くコツは…\n\n■第2章 注目すべき機能性成分\nナイアシンアミド、トラネキサム酸…\n\n（以下、購入者限定の本文が続きます）",
        "成分・化粧品科学", 1280, 40, "🧪")
    c2 = add_content(yuki,
        "サロン級の毛穴ケア｜自宅でできる正しいクレンジング手順",
        "毛穴の黒ずみ・開きに悩む方へ。エステ歴12年・美肌検定保持者が、毛穴タイプ別の正しいケアと、やってはいけないNGケアを伝授。",
        "■毛穴タイプ診断\nあなたの毛穴は「詰まり毛穴」「開き毛穴」「たるみ毛穴」のどれ？\n\n■タイプ別ケア手順…\n\n（以下、購入者限定）",
        "スキンケア", 980, 30, "🫧")
    c3 = add_content(rena,
        "肌タイプ別スキンケア処方箋｜あなたに本当に合う化粧品の選び方",
        "ダブルライセンス保持者が、肌質診断から化粧品選定までを1冊に。デパコス・プチプラ問わず「自分軸」で選べるようになります。",
        "■肌質を4タイプ＋水分油分バランスで把握する\n\n■予算別おすすめ処方…\n\n（以下、購入者限定）",
        "スキンケア", 1500, 50, "📋")
    c4 = add_content(mika,
        "【無料】はじめての化粧品検定｜独学合格ロードマップ",
        "これから資格を取りたい人向けの入門ガイド。出題範囲、勉強時間の目安、独学スケジュールを無料で公開。",
        "■化粧品検定とは\n3級は無料Web受験、2級・1級は…\n\n■独学3ヶ月スケジュール…",
        "成分・化粧品科学", 0, 0, "🎓")
    c5 = add_content(yuki,
        "崩れないベースメイク｜化粧下地とファンデの黄金比",
        "皮脂・乾燥に負けないベースメイク理論。下地の選び方、塗る量、密着のさせ方をプロが解説。",
        "■崩れる原因は「下地の量」だった\n\n■肌質別・黄金比…\n\n（以下、購入者限定）",
        "メイク", 880, 30, "💄")

    # --- 購入・紹介・レビュー（紹介機能のデモ）---
    # aoi が c1 を購入 → aoi が紹介者になり、sora が aoi の紹介で c1 を購入
    buy(c1, aoi)
    buy(c1, sora, referrer=aoi)          # aoi に紹介報酬
    buy(c2, aoi)
    buy(c2, sora, referrer=rena)         # rena に紹介報酬
    buy(c3, aoi)
    buy(c3, sora)
    buy(c5, aoi, referrer=mika)
    buy(c4, sora)                        # 無料

    review(c1, aoi, 5, "成分表示が読めるようになりました。買い物が変わります！")
    review(c1, sora, 4, "1%ラインの話が目から鱗でした。")
    review(c2, aoi, 5, "毛穴タイプ診断が分かりやすい。")
    review(c3, aoi, 5, "肌質診断から選べるのが良い。")

    db.commit()
    db.close()
    print("✅ seed 完了:", DB)
    print("   運営ログイン : admin@cosmebrain.jp / admin")
    print("   販売者ログイン: mika@example.com / password")
    print("   購入者ログイン: aoi@example.com / password")


if __name__ == "__main__":
    main()
