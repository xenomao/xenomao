"""
コスメブレイン (CosmeBrain)
================================================================
化粧品検定・美肌検定の有資格者（約180万人）が、自分の美容知識を
ファイル/記事にしてアップロード・販売できるマーケットプレイス。

ビジネスモデルのベンチマーク = Brain
  - 有資格者だけが販売者になれる（資格審査 → 安心して学べる）
  - コンテンツ（知識ファイル/記事）を価格を付けて販売
  - 紹介機能：購入者は誰でも紹介者になれ、自分の紹介リンク経由の
    購入に対して「紹介報酬率(%)」分の報酬を受け取れる
  - レビュー・ランキング・収益ダッシュボード

技術: Flask + SQLite（既存 DigiLab Beauty プロジェクトの Python/SQLite 構成に準拠）
================================================================
"""
import os
import sqlite3
import secrets
from functools import wraps
from datetime import datetime

from flask import (
    Flask, g, render_template, request, redirect, url_for,
    session, flash, abort, send_from_directory,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cosmebrain.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# プラットフォーム手数料率（販売額に対して運営が取る割合）
PLATFORM_FEE_RATE = 12  # %

# 販売可能な資格（この資格を承認された人だけがコンテンツを出せる）
ALLOWED_CERTS = [
    "化粧品検定1級",
    "化粧品検定2級",
    "化粧品検定3級",
    "美肌検定",
]

CATEGORIES = [
    "スキンケア", "メイク", "成分・化粧品科学", "エイジングケア",
    "ヘアケア", "ネイル", "サロン経営", "その他",
]

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("COSMEBRAIN_SECRET", "dev-secret-change-me")
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)


# --------------------------------------------------------------------- #
# DB ヘルパ
# --------------------------------------------------------------------- #
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    with open(os.path.join(BASE_DIR, "schema.sql"), encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()
    db.close()


# --------------------------------------------------------------------- #
# 認証ヘルパ
# --------------------------------------------------------------------- #
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return get_db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()


@app.context_processor
def inject_globals():
    return {
        "current_user": current_user(),
        "CATEGORIES": CATEGORIES,
        "now_year": datetime.now().year,
    }


def login_required(f):
    @wraps(f)
    def wrap(*a, **kw):
        if not session.get("user_id"):
            flash("ログインが必要です。", "warn")
            return redirect(url_for("login", next=request.path))
        return f(*a, **kw)
    return wrap


def admin_required(f):
    @wraps(f)
    def wrap(*a, **kw):
        u = current_user()
        if not u or not u["is_admin"]:
            abort(403)
        return f(*a, **kw)
    return wrap


def is_verified_seller(user_id):
    """承認済み資格を1つ以上持つ＝販売可能。"""
    row = get_db().execute(
        "SELECT COUNT(*) c FROM certifications WHERE user_id=? AND verified=1",
        (user_id,),
    ).fetchone()
    return row["c"] > 0


def has_purchased(user_id, content_id):
    if not user_id:
        return False
    row = get_db().execute(
        "SELECT 1 FROM purchases WHERE buyer_id=? AND content_id=?",
        (user_id, content_id),
    ).fetchone()
    return row is not None


app.jinja_env.globals.update(
    is_verified_seller=is_verified_seller,
    has_purchased=has_purchased,
)


def content_stats(content_id):
    db = get_db()
    r = db.execute(
        "SELECT COUNT(*) n, COALESCE(AVG(rating),0) avg FROM reviews WHERE content_id=?",
        (content_id,),
    ).fetchone()
    return {"review_count": r["n"], "avg_rating": round(r["avg"], 1)}


app.jinja_env.globals.update(content_stats=content_stats)


def gen_referral_code():
    db = get_db()
    while True:
        code = secrets.token_urlsafe(6)
        if not db.execute("SELECT 1 FROM users WHERE referral_code=?", (code,)).fetchone():
            return code


# --------------------------------------------------------------------- #
# トップ / 検索
# --------------------------------------------------------------------- #
@app.route("/")
def index():
    db = get_db()
    # 売れ筋ランキング
    ranking = db.execute(
        """SELECT c.*, u.display_name FROM contents c
           JOIN users u ON u.id=c.seller_id
           WHERE c.status='published'
           ORDER BY c.sales_count DESC, c.created_at DESC LIMIT 6"""
    ).fetchall()
    newest = db.execute(
        """SELECT c.*, u.display_name FROM contents c
           JOIN users u ON u.id=c.seller_id
           WHERE c.status='published'
           ORDER BY c.created_at DESC LIMIT 6"""
    ).fetchall()
    stats = {
        "users": db.execute("SELECT COUNT(*) c FROM users").fetchone()["c"],
        "contents": db.execute("SELECT COUNT(*) c FROM contents WHERE status='published'").fetchone()["c"],
        "verified": db.execute("SELECT COUNT(DISTINCT user_id) c FROM certifications WHERE verified=1").fetchone()["c"],
    }
    return render_template("index.html", ranking=ranking, newest=newest, stats=stats)


@app.route("/search")
def search():
    db = get_db()
    q = request.args.get("q", "").strip()
    cat = request.args.get("cat", "").strip()
    sql = ("""SELECT c.*, u.display_name FROM contents c
              JOIN users u ON u.id=c.seller_id
              WHERE c.status='published'""")
    params = []
    if q:
        sql += " AND (c.title LIKE ? OR c.summary LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    if cat:
        sql += " AND c.category=?"
        params.append(cat)
    sql += " ORDER BY c.sales_count DESC, c.created_at DESC"
    items = db.execute(sql, params).fetchall()
    return render_template("search.html", items=items, q=q, cat=cat)


# --------------------------------------------------------------------- #
# 認証
# --------------------------------------------------------------------- #
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        name = request.form["display_name"].strip()
        pw = request.form["password"]
        db = get_db()
        if not (email and name and pw):
            flash("すべての項目を入力してください。", "error")
        elif db.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            flash("このメールアドレスは登録済みです。", "error")
        else:
            db.execute(
                "INSERT INTO users(email,password_hash,display_name,referral_code) VALUES(?,?,?,?)",
                (email, generate_password_hash(pw), name, gen_referral_code()),
            )
            db.commit()
            user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            session["user_id"] = user["id"]
            flash("ようこそ！まずは資格を登録して販売者になりましょう。", "ok")
            return redirect(url_for("cert_submit"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        pw = request.form["password"]
        user = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], pw):
            session["user_id"] = user["id"]
            flash("ログインしました。", "ok")
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("メールアドレスまたはパスワードが違います。", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました。", "ok")
    return redirect(url_for("index"))


# --------------------------------------------------------------------- #
# 資格登録・審査
# --------------------------------------------------------------------- #
@app.route("/certifications", methods=["GET", "POST"])
@login_required
def cert_submit():
    db = get_db()
    user = current_user()
    if request.method == "POST":
        cert_type = request.form["cert_type"]
        cert_number = request.form.get("cert_number", "").strip()
        evidence = ""
        f = request.files.get("evidence")
        if f and f.filename:
            fn = f"cert_{user['id']}_{secure_filename(f.filename)}"
            f.save(os.path.join(UPLOAD_DIR, fn))
            evidence = fn
        if cert_type not in ALLOWED_CERTS:
            flash("対象資格を選択してください。", "error")
        else:
            db.execute(
                "INSERT INTO certifications(user_id,cert_type,cert_number,evidence) VALUES(?,?,?,?)",
                (user["id"], cert_type, cert_number, evidence),
            )
            db.commit()
            flash("資格を申請しました。運営の審査後に販売できるようになります。", "ok")
            return redirect(url_for("dashboard"))
    certs = db.execute(
        "SELECT * FROM certifications WHERE user_id=? ORDER BY created_at DESC",
        (user["id"],),
    ).fetchall()
    return render_template("cert_submit.html", certs=certs, allowed=ALLOWED_CERTS)


# --------------------------------------------------------------------- #
# コンテンツ：作成・閲覧・購入
# --------------------------------------------------------------------- #
@app.route("/contents/new", methods=["GET", "POST"])
@login_required
def content_new():
    user = current_user()
    if not is_verified_seller(user["id"]):
        flash("コンテンツの販売には承認済みの資格が必要です。", "warn")
        return redirect(url_for("cert_submit"))
    db = get_db()
    if request.method == "POST":
        title = request.form["title"].strip()
        summary = request.form.get("summary", "").strip()
        body = request.form.get("body", "").strip()
        category = request.form.get("category", CATEGORIES[0])
        emoji = request.form.get("cover_emoji", "📘").strip() or "📘"
        try:
            price = max(0, int(request.form.get("price", 0)))
            rate = min(80, max(0, int(request.form.get("referral_rate", 30))))
        except ValueError:
            flash("価格・紹介報酬率は数値で入力してください。", "error")
            return render_template("content_new.html")
        file_name = ""
        f = request.files.get("file")
        if f and f.filename:
            fn = f"content_{user['id']}_{secrets.token_hex(4)}_{secure_filename(f.filename)}"
            f.save(os.path.join(UPLOAD_DIR, fn))
            file_name = fn
        if not title:
            flash("タイトルを入力してください。", "error")
        else:
            db.execute(
                """INSERT INTO contents
                   (seller_id,title,summary,body,file_name,cover_emoji,category,price,referral_rate)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (user["id"], title, summary, body, file_name, emoji, category, price, rate),
            )
            db.commit()
            flash("コンテンツを公開しました！", "ok")
            return redirect(url_for("dashboard"))
    return render_template("content_new.html")


@app.route("/c/<int:cid>")
def content_detail(cid):
    db = get_db()
    c = db.execute(
        """SELECT c.*, u.display_name, u.bio, u.referral_code AS seller_ref
           FROM contents c JOIN users u ON u.id=c.seller_id WHERE c.id=?""",
        (cid,),
    ).fetchone()
    if not c:
        abort(404)
    # 販売者の保有資格（安心材料として表示）
    seller_certs = db.execute(
        "SELECT cert_type FROM certifications WHERE user_id=? AND verified=1",
        (c["seller_id"],),
    ).fetchall()
    reviews = db.execute(
        """SELECT r.*, u.display_name FROM reviews r
           JOIN users u ON u.id=r.user_id WHERE r.content_id=?
           ORDER BY r.created_at DESC""",
        (cid,),
    ).fetchall()
    # 紹介リンク経由のアクセスを記録
    ref = request.args.get("ref")
    if ref:
        session[f"ref_{cid}"] = ref
    purchased = has_purchased(session.get("user_id"), cid)
    return render_template(
        "content_detail.html",
        c=c, seller_certs=seller_certs, reviews=reviews,
        purchased=purchased, stats=content_stats(cid),
    )


@app.route("/c/<int:cid>/buy", methods=["POST"])
@login_required
def content_buy(cid):
    db = get_db()
    user = current_user()
    c = db.execute("SELECT * FROM contents WHERE id=? AND status='published'", (cid,)).fetchone()
    if not c:
        abort(404)
    if c["seller_id"] == user["id"]:
        flash("自分のコンテンツは購入できません。", "warn")
        return redirect(url_for("content_detail", cid=cid))
    if has_purchased(user["id"], cid):
        flash("すでに購入済みです。", "warn")
        return redirect(url_for("content_view", cid=cid))

    price = c["price"]
    # 紹介者の特定（紹介リンクの ref コード）。自己紹介・販売者本人は無効。
    referrer = None
    ref_code = session.pop(f"ref_{cid}", None) or request.form.get("ref")
    if ref_code:
        r = db.execute("SELECT * FROM users WHERE referral_code=?", (ref_code,)).fetchone()
        if r and r["id"] not in (user["id"], c["seller_id"]):
            referrer = r

    referral_commission = 0
    if referrer:
        referral_commission = price * c["referral_rate"] // 100
    platform_fee = price * PLATFORM_FEE_RATE // 100
    seller_earning = price - referral_commission - platform_fee

    # 決済（デモ：実決済の代わりに記録のみ。実運用では Stripe 等を接続）
    cur = db.execute(
        """INSERT INTO purchases
           (content_id,buyer_id,price_paid,referrer_id,referral_commission,seller_earning,platform_fee)
           VALUES(?,?,?,?,?,?,?)""",
        (cid, user["id"], price,
         referrer["id"] if referrer else None,
         referral_commission, seller_earning, platform_fee),
    )
    pid = cur.lastrowid
    db.execute("UPDATE contents SET sales_count=sales_count+1 WHERE id=?", (cid,))
    # 販売者へ入金
    db.execute("UPDATE users SET balance=balance+? WHERE id=?", (seller_earning, c["seller_id"]))
    db.execute(
        "INSERT INTO earnings(user_id,amount,kind,purchase_id,note) VALUES(?,?,?,?,?)",
        (c["seller_id"], seller_earning, "sale", pid, f"「{c['title']}」の販売"),
    )
    # 紹介者へ報酬
    if referrer and referral_commission > 0:
        db.execute("UPDATE users SET balance=balance+? WHERE id=?", (referral_commission, referrer["id"]))
        db.execute(
            "INSERT INTO earnings(user_id,amount,kind,purchase_id,note) VALUES(?,?,?,?,?)",
            (referrer["id"], referral_commission, "referral", pid, f"「{c['title']}」の紹介報酬"),
        )
    db.commit()
    flash("購入が完了しました！本文とダウンロードが閲覧できます。", "ok")
    return redirect(url_for("content_view", cid=cid))


@app.route("/c/<int:cid>/read")
@login_required
def content_view(cid):
    db = get_db()
    user = current_user()
    c = db.execute(
        """SELECT c.*, u.display_name FROM contents c
           JOIN users u ON u.id=c.seller_id WHERE c.id=?""",
        (cid,),
    ).fetchone()
    if not c:
        abort(404)
    if not has_purchased(user["id"], cid) and c["seller_id"] != user["id"]:
        flash("このコンテンツは未購入です。", "warn")
        return redirect(url_for("content_detail", cid=cid))
    my_review = db.execute(
        "SELECT * FROM reviews WHERE content_id=? AND user_id=?", (cid, user["id"])
    ).fetchone()
    # 購入者が手に入れる「自分の紹介リンク」（Brain の肝）
    ref_url = url_for("content_detail", cid=cid, ref=user["referral_code"], _external=True)
    return render_template("content_view.html", c=c, my_review=my_review, ref_url=ref_url)


@app.route("/c/<int:cid>/review", methods=["POST"])
@login_required
def content_review(cid):
    db = get_db()
    user = current_user()
    if not has_purchased(user["id"], cid):
        flash("購入者のみレビューできます。", "warn")
        return redirect(url_for("content_detail", cid=cid))
    try:
        rating = min(5, max(1, int(request.form["rating"])))
    except (ValueError, KeyError):
        rating = 5
    comment = request.form.get("comment", "").strip()
    existing = db.execute(
        "SELECT id FROM reviews WHERE content_id=? AND user_id=?", (cid, user["id"])
    ).fetchone()
    if existing:
        db.execute("UPDATE reviews SET rating=?, comment=? WHERE id=?", (rating, comment, existing["id"]))
    else:
        db.execute(
            "INSERT INTO reviews(content_id,user_id,rating,comment) VALUES(?,?,?,?)",
            (cid, user["id"], rating, comment),
        )
    db.commit()
    flash("レビューを投稿しました。ありがとうございます！", "ok")
    return redirect(url_for("content_detail", cid=cid))


@app.route("/download/<path:fn>")
@login_required
def download(fn):
    """添付ファイルは購入者・販売者・運営のみダウンロード可。"""
    db = get_db()
    user = current_user()
    c = db.execute("SELECT * FROM contents WHERE file_name=?", (fn,)).fetchone()
    if c:
        if not (user["is_admin"] or c["seller_id"] == user["id"] or has_purchased(user["id"], c["id"])):
            abort(403)
    elif not user["is_admin"]:
        abort(403)  # 資格証明など、その他のファイルは運営のみ
    return send_from_directory(UPLOAD_DIR, fn, as_attachment=True)


# --------------------------------------------------------------------- #
# ダッシュボード / 収益
# --------------------------------------------------------------------- #
@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user = current_user()
    my_contents = db.execute(
        "SELECT * FROM contents WHERE seller_id=? ORDER BY created_at DESC", (user["id"],)
    ).fetchall()
    purchases = db.execute(
        """SELECT p.*, c.title, c.cover_emoji, c.id AS cid FROM purchases p
           JOIN contents c ON c.id=p.content_id
           WHERE p.buyer_id=? ORDER BY p.created_at DESC""",
        (user["id"],),
    ).fetchall()
    certs = db.execute(
        "SELECT * FROM certifications WHERE user_id=? ORDER BY created_at DESC", (user["id"],)
    ).fetchall()
    earn = db.execute(
        """SELECT COALESCE(SUM(CASE WHEN kind='sale' THEN amount END),0) sale,
                  COALESCE(SUM(CASE WHEN kind='referral' THEN amount END),0) ref
           FROM earnings WHERE user_id=?""",
        (user["id"],),
    ).fetchone()
    return render_template(
        "dashboard.html",
        my_contents=my_contents, purchases=purchases, certs=certs, earn=earn,
        verified=is_verified_seller(user["id"]),
    )


@app.route("/earnings")
@login_required
def earnings():
    db = get_db()
    user = current_user()
    rows = db.execute(
        "SELECT * FROM earnings WHERE user_id=? ORDER BY created_at DESC", (user["id"],)
    ).fetchall()
    return render_template("earnings.html", rows=rows)


@app.route("/u/<int:uid>")
def profile(uid):
    db = get_db()
    u = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not u:
        abort(404)
    certs = db.execute(
        "SELECT cert_type FROM certifications WHERE user_id=? AND verified=1", (uid,)
    ).fetchall()
    contents = db.execute(
        "SELECT * FROM contents WHERE seller_id=? AND status='published' ORDER BY created_at DESC",
        (uid,),
    ).fetchall()
    return render_template("profile.html", u=u, certs=certs, contents=contents)


# --------------------------------------------------------------------- #
# 運営（資格審査）
# --------------------------------------------------------------------- #
@app.route("/admin")
@admin_required
def admin():
    db = get_db()
    pending = db.execute(
        """SELECT ce.*, u.display_name, u.email FROM certifications ce
           JOIN users u ON u.id=ce.user_id
           WHERE ce.verified=0 ORDER BY ce.created_at""",
    ).fetchall()
    return render_template("admin.html", pending=pending)


@app.route("/admin/cert/<int:cert_id>/<action>", methods=["POST"])
@admin_required
def admin_cert(cert_id, action):
    db = get_db()
    status = 1 if action == "approve" else 2
    db.execute(
        "UPDATE certifications SET verified=?, verified_at=CURRENT_TIMESTAMP WHERE id=?",
        (status, cert_id),
    )
    db.commit()
    flash("審査結果を反映しました。", "ok")
    return redirect(url_for("admin"))


# --------------------------------------------------------------------- #
if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
