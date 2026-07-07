-- =====================================================================
-- コスメブレイン (CosmeBrain) データベーススキーマ
-- 有資格者（化粧品検定・美肌検定 約180万人）向け
-- コンテンツ販売 ＋ 紹介機能付きマーケットプレイス
-- ベンチマーク: Brain（コンテンツ販売プラットフォーム）
-- =====================================================================

-- 1. ユーザー（資格保持者＝販売者 兼 購入者 兼 紹介者）
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name  TEXT NOT NULL,
    bio           TEXT DEFAULT '',
    avatar_url    TEXT DEFAULT '',
    referral_code TEXT UNIQUE NOT NULL,          -- 紹介用コード
    is_admin      INTEGER DEFAULT 0,             -- 運営（資格審査担当）
    balance       INTEGER DEFAULT 0,             -- 受取可能残高（円）
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 資格情報（販売の前提となる本人の保有資格）
--    verified=1 になって初めてコンテンツを販売できる（安心して学べる根拠）
CREATE TABLE IF NOT EXISTS certifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    cert_type   TEXT NOT NULL,                   -- 化粧品検定1級/2級/3級, 美肌検定 など
    cert_number TEXT DEFAULT '',                 -- 認定番号
    evidence    TEXT DEFAULT '',                 -- 証明書ファイル名/URL
    verified    INTEGER DEFAULT 0,               -- 0:審査中 1:承認 2:却下
    verified_at TIMESTAMP,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 3. コンテンツ（販売される知識ファイル/記事）
CREATE TABLE IF NOT EXISTS contents (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id     INTEGER NOT NULL,
    title         TEXT NOT NULL,
    summary       TEXT DEFAULT '',               -- 無料で見える紹介文
    body          TEXT DEFAULT '',               -- 購入者のみ閲覧できる本文
    file_name     TEXT DEFAULT '',               -- 添付ダウンロードファイル
    cover_emoji   TEXT DEFAULT '📘',
    category      TEXT DEFAULT 'スキンケア',
    price         INTEGER NOT NULL DEFAULT 0,    -- 価格（円）
    referral_rate INTEGER NOT NULL DEFAULT 30,   -- 紹介報酬率(%) Brain型の肝
    status        TEXT DEFAULT 'published',      -- draft / published
    sales_count   INTEGER DEFAULT 0,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(id)
);

-- 4. 購入（決済記録）。紹介者がいれば referrer_id に記録し報酬を配分
CREATE TABLE IF NOT EXISTS purchases (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id          INTEGER NOT NULL,
    buyer_id            INTEGER NOT NULL,
    price_paid          INTEGER NOT NULL,
    referrer_id         INTEGER,                 -- 紹介者（購入者は誰でも紹介者になれる）
    referral_commission INTEGER DEFAULT 0,       -- 紹介者へ配分された額
    seller_earning      INTEGER DEFAULT 0,       -- 販売者の取り分
    platform_fee        INTEGER DEFAULT 0,       -- プラットフォーム手数料
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES contents(id),
    FOREIGN KEY (buyer_id)   REFERENCES users(id),
    FOREIGN KEY (referrer_id) REFERENCES users(id)
);

-- 5. レビュー（購入者のみ投稿可）
CREATE TABLE IF NOT EXISTS reviews (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    rating     INTEGER NOT NULL,                 -- 1〜5
    comment    TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES contents(id),
    FOREIGN KEY (user_id)    REFERENCES users(id)
);

-- 6. 収益台帳（販売・紹介の入金履歴）
CREATE TABLE IF NOT EXISTS earnings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    amount      INTEGER NOT NULL,
    kind        TEXT NOT NULL,                   -- 'sale' / 'referral'
    purchase_id INTEGER,
    note        TEXT DEFAULT '',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
