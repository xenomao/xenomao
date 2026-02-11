-- DigiLab Beauty AI組織システム - 中央データベース設計
-- SQLite版（開発環境用）

-- ===========================================
-- 1. 企業マスタテーブル
-- ===========================================
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    operating_company VARCHAR(255),
    established_year VARCHAR(50),
    headquarters TEXT,
    phone VARCHAR(50),
    inquiry_phone VARCHAR(50),
    email VARCHAR(255),
    url VARCHAR(500),
    store_count VARCHAR(50),
    main_services TEXT,
    business_status VARCHAR(50) DEFAULT '営業中',
    priority INTEGER DEFAULT 3, -- 1:最優先 5:低優先
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) DEFAULT '@AI担当',
    updated_by VARCHAR(50)
);

-- ===========================================
-- 2. 担当者マスタテーブル
-- ===========================================
CREATE TABLE IF NOT EXISTS contacts (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    contact_name VARCHAR(100),
    position VARCHAR(100),
    department VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    is_primary BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- 3. コンタクト履歴テーブル
-- ===========================================
CREATE TABLE IF NOT EXISTS contact_history (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    contact_date DATE NOT NULL,
    contact_type VARCHAR(50), -- 'email', 'phone', 'meeting', 'demo'
    contact_person VARCHAR(100),
    subject VARCHAR(255),
    content TEXT,
    result VARCHAR(100), -- '送信完了', 'アポ獲得', '検討中', '不成立'
    next_action TEXT,
    next_action_date DATE,
    ai_agent VARCHAR(50), -- '@AI営業', '@AIマーケティング'等
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- 4. タスク管理テーブル
-- ===========================================
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    assigned_to VARCHAR(50) NOT NULL, -- '@AI営業', '@AI事務局'等
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 3, -- 1:緊急 2:高 3:中 4:低 5:最低
    status VARCHAR(50) DEFAULT '未着手', -- '未着手', '進行中', '完了', '保留'
    due_date DATE,
    completed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- 5. 営業ステージテーブル
-- ===========================================
CREATE TABLE IF NOT EXISTS sales_pipeline (
    pipeline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    stage VARCHAR(50) NOT NULL, -- 'リード', 'アプローチ済', 'アポ獲得', '提案', '商談', '成約', '失注'
    stage_date DATE NOT NULL,
    expected_value DECIMAL(10, 2),
    probability INTEGER, -- 0-100%
    notes TEXT,
    ai_agent VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- 6. ドキュメント管理テーブル
-- ===========================================
CREATE TABLE IF NOT EXISTS documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    document_type VARCHAR(50), -- '提案資料', '契約書', '議事録', 'メール'
    title VARCHAR(255) NOT NULL,
    file_path TEXT,
    description TEXT,
    ai_agent VARCHAR(50), -- 作成したAIエージェント
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- 7. 情報収集ログテーブル（Opal連携用）
-- ===========================================
CREATE TABLE IF NOT EXISTS intelligence_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    source VARCHAR(100), -- 'Opal', 'Web検索', 'ニュース'
    info_type VARCHAR(50), -- '企業ニュース', '財務情報', '人事異動', '倒産情報'
    title VARCHAR(255),
    content TEXT,
    url TEXT,
    collected_date DATE NOT NULL,
    ai_agent VARCHAR(50) DEFAULT '@AI担当',
    is_important BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- 8. KPIトラッキングテーブル
-- ===========================================
CREATE TABLE IF NOT EXISTS kpi_tracking (
    kpi_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    ai_agent VARCHAR(50),
    metric_name VARCHAR(100), -- 'アプローチ数', 'アポ獲得数', '成約数'
    metric_value DECIMAL(10, 2),
    target_value DECIMAL(10, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- インデックス作成
-- ===========================================
CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(business_status);
CREATE INDEX IF NOT EXISTS idx_companies_priority ON companies(priority);
CREATE INDEX IF NOT EXISTS idx_contact_history_date ON contact_history(contact_date);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_sales_pipeline_stage ON sales_pipeline(stage);

-- ===========================================
-- トリガー：更新日時の自動更新
-- ===========================================
CREATE TRIGGER IF NOT EXISTS update_companies_timestamp 
AFTER UPDATE ON companies
BEGIN
    UPDATE companies SET updated_at = CURRENT_TIMESTAMP WHERE company_id = NEW.company_id;
END;

CREATE TRIGGER IF NOT EXISTS update_tasks_timestamp 
AFTER UPDATE ON tasks
BEGIN
    UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE task_id = NEW.task_id;
END;
