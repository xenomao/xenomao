-- DigiLab Beauty AI組織システム - LINEステップライン スキーマ
-- LINE公式アカウントのステップ配信（ステップライン）を管理するテーブル群
-- SQLite版（開発環境用）
-- 既存の digilab_beauty_db_schema.sql に追加適用してください。

-- ===========================================
-- 9. LINE友だち（購読者）マスタ
-- ===========================================
CREATE TABLE IF NOT EXISTS line_subscribers (
    subscriber_id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_user_id VARCHAR(64) NOT NULL UNIQUE, -- LINEのユーザーID（Uから始まる33文字）
    display_name VARCHAR(255),                 -- LINEの表示名
    company_id INTEGER,                        -- 紐づく企業（任意）
    segment VARCHAR(50) DEFAULT '新規',        -- '新規', 'リピーター', 'VIP', '休眠'
    status VARCHAR(50) DEFAULT '有効',         -- '有効', 'ブロック', '退会'
    last_visit_date DATE,                       -- 最終来店日（休眠判定用）
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- 10. ステップシナリオ（ステップラインの定義）
-- ===========================================
CREATE TABLE IF NOT EXISTS step_scenarios (
    scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,                 -- 例: '休眠顧客復活フロー'
    description TEXT,
    trigger_type VARCHAR(50) DEFAULT 'manual',  -- 'manual', 'on_friend_add', 'on_dormant'
    status VARCHAR(50) DEFAULT '有効',          -- '有効', '停止'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) DEFAULT '@AIマーケティング'
);

-- ===========================================
-- 11. ステップメッセージ（シナリオ内の各ステップ）
-- ===========================================
CREATE TABLE IF NOT EXISTS step_messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,                -- 1始まりのステップ順
    delay_days INTEGER NOT NULL DEFAULT 0,      -- 前ステップ（または開始）からの待機日数
    message_type VARCHAR(50) DEFAULT 'text',    -- 'text'（将来: 'flex', 'image'）
    message_text TEXT NOT NULL,                 -- 配信本文。{name} 等のプレースホルダ可
    note TEXT,                                  -- 運用メモ（配信意図など）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES step_scenarios(scenario_id),
    UNIQUE (scenario_id, step_order)
);

-- ===========================================
-- 12. ステップ登録（購読者 × シナリオの進行状況）
-- ===========================================
CREATE TABLE IF NOT EXISTS step_enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscriber_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    current_step INTEGER DEFAULT 0,            -- 直近で送信済みのステップ順（0=未送信）
    status VARCHAR(50) DEFAULT '進行中',       -- '進行中', '完了', '停止'
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_send_date DATE,                        -- 次ステップの送信予定日
    completed_at TIMESTAMP,
    FOREIGN KEY (subscriber_id) REFERENCES line_subscribers(subscriber_id),
    FOREIGN KEY (scenario_id) REFERENCES step_scenarios(scenario_id),
    UNIQUE (subscriber_id, scenario_id)
);

-- ===========================================
-- 13. ステップ配信ログ
-- ===========================================
CREATE TABLE IF NOT EXISTS step_delivery_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT '送信完了',     -- '送信完了', '失敗', 'ドライラン'
    response TEXT,                              -- LINE APIレスポンス / エラー内容
    FOREIGN KEY (enrollment_id) REFERENCES step_enrollments(enrollment_id),
    FOREIGN KEY (message_id) REFERENCES step_messages(message_id)
);

-- ===========================================
-- インデックス
-- ===========================================
CREATE INDEX IF NOT EXISTS idx_line_subscribers_status ON line_subscribers(status);
CREATE INDEX IF NOT EXISTS idx_line_subscribers_segment ON line_subscribers(segment);
CREATE INDEX IF NOT EXISTS idx_step_messages_scenario ON step_messages(scenario_id);
CREATE INDEX IF NOT EXISTS idx_step_enrollments_status ON step_enrollments(status);
CREATE INDEX IF NOT EXISTS idx_step_enrollments_next_send ON step_enrollments(next_send_date);
CREATE INDEX IF NOT EXISTS idx_step_delivery_log_enrollment ON step_delivery_log(enrollment_id);

-- ===========================================
-- トリガー：更新日時の自動更新
-- ===========================================
CREATE TRIGGER IF NOT EXISTS update_line_subscribers_timestamp
AFTER UPDATE ON line_subscribers
BEGIN
    UPDATE line_subscribers SET updated_at = CURRENT_TIMESTAMP WHERE subscriber_id = NEW.subscriber_id;
END;

CREATE TRIGGER IF NOT EXISTS update_step_scenarios_timestamp
AFTER UPDATE ON step_scenarios
BEGIN
    UPDATE step_scenarios SET updated_at = CURRENT_TIMESTAMP WHERE scenario_id = NEW.scenario_id;
END;
