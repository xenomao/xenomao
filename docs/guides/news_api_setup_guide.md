# 情報収集API設定ガイド - Opal代替ソリューション

## 🔍 調査結果: Opalについて

「Opal」という名前のサービスには複数の種類があり、いずれもAI組織システムでの利用には制限があることが判明しました。

### Google Opal
- **概要**: Googleが2025年10月に提供開始したAIミニアプリ構築ツール
- **機能**: ウェブスクレイピング、ウェブ検索などが可能
- **制限**: **外部APIとして利用不可**（Opal内でのみ利用）
- **用途**: GeminiやGoogle AIツールとの連携に特化

### Opal.so
- **概要**: エンタープライズ向けアクセス管理プラットフォーム
- **制限**: **APIアクセスには特別な承認が必要**（NDA、リーダーシップ承認）
- **用途**: 企業のアクセス権限管理（情報収集ツールではない）

---

## ✅ 推奨ソリューション: 実績のあるニュース収集API

DigiLab Beauty AI組織システムの「@AI担当」による自動情報収集には、以下の実績あるAPIサービスを推奨します。

---

## 🎯 Option 1: NewsAPI.org（最推奨）

### 特徴
- ✅ **15万以上の情報源**から世界中のニュースを収集
- ✅ **日本の主要メディア対応**（日本経済新聞、産経新聞など）
- ✅ **シンプルなREST API**（JSON形式）
- ✅ **無料プラン**あり（開発・テスト用）
- ✅ **リアルタイム**＋過去ニュース検索

### 料金
- **Developer**: $0/月（100リクエスト/日）
- **Business**: $449/月（250,000リクエスト/月）
- **Enterprise**: カスタム

### API取得手順

#### Step 1: アカウント作成
```
1. https://newsapi.org/ にアクセス
2. 「Get API Key」をクリック
3. 必要情報を入力:
   - First Name & Last Name
   - Email
   - Password
   - Country: Japan
   - Organization: DigiLab Beauty
4. 「Submit」をクリック
```

#### Step 2: API キー取得
```
1. 登録メールアドレスに確認メールが届く
2. メール内のリンクをクリックして認証
3. ダッシュボードにログイン
4. API キーをコピー（例: 1234567890abcdef1234567890abcdef）
```

#### Step 3: APIテスト
```python
import requests

api_key = "YOUR_API_KEY_HERE"
url = f"https://newsapi.org/v2/everything?q=エステ&language=ja&apiKey={api_key}"

response = requests.get(url)
data = response.json()

print(f"Total Results: {data['totalResults']}")
for article in data['articles'][:5]:
    print(f"- {article['title']}")
    print(f"  Source: {article['source']['name']}")
    print(f"  URL: {article['url']}")
    print()
```

### 使用例: エステ業界ニュース収集

```python
# エステ業界の最新ニュース
params = {
    'q': 'エステ OR 美容サロン OR 脱毛サロン',
    'language': 'ja',
    'sortBy': 'publishedAt',
    'pageSize': 100,
    'apiKey': api_key
}

# 特定企業のニュース（例: TBC）
params = {
    'q': 'エステティックTBC OR "TBCグループ"',
    'language': 'ja',
    'sortBy': 'publishedAt',
    'apiKey': api_key
}

# 倒産・M&A情報
params = {
    'q': 'エステ AND (倒産 OR 破産 OR M&A OR 買収)',
    'language': 'ja',
    'sortBy': 'publishedAt',
    'apiKey': api_key
}
```

---

## 🎯 Option 2: SerpAPI（Google検索ベース）

### 特徴
- ✅ **Google検索結果をAPI化**
- ✅ **Googleニュース対応**
- ✅ **日本語完全対応**
- ✅ **無料プラン**あり（100検索/月）

### 料金
- **Free**: $0/月（100検索）
- **Standard**: $50/月（5,000検索）
- **Professional**: $250/月（30,000検索）

### API取得手順

#### Step 1: アカウント作成
```
1. https://serpapi.com/ にアクセス
2. 「Sign Up Free」をクリック
3. Googleアカウントまたはメールで登録
```

#### Step 2: API キー取得
```
1. ダッシュボードにログイン
2. 「API Key」セクションからキーをコピー
```

#### Step 3: APIテスト
```python
from serpapi import GoogleSearch

params = {
    "engine": "google_news",
    "q": "エステ業界",
    "gl": "jp",
    "hl": "ja",
    "api_key": "YOUR_API_KEY"
}

search = GoogleSearch(params)
results = search.get_dict()

for article in results.get("news_results", [])[:10]:
    print(f"- {article['title']}")
    print(f"  Source: {article['source']['name']}")
    print(f"  Date: {article['date']}")
    print()
```

---

## 🎯 Option 3: Bright Data（エンタープライズ向け）

### 特徴
- ✅ **最も強力なスクレイピング能力**
- ✅ **CAPTCHA自動回避**
- ✅ **プロキシローテーション**
- ✅ **日本サイト対応強化**

### 料金
- 従量課金制（使った分だけ支払い）
- 月額最低$500〜

### API取得手順
```
1. https://brightdata.jp/ にアクセス
2. フォームから問い合わせ
3. セールス担当と価格・プラン協議
```

---

## 📋 推奨: NewsAPI + SerpAPI の組み合わせ

### 最適な構成

```
@AI担当の情報収集システム:
├── NewsAPI
│   └── エステ業界の一般ニュース
│   └── 企業名での検索
│   └── 倒産・M&A情報
│
└── SerpAPI
    └── Google検索結果
    └── 競合分析
    └── トレンド調査
```

### 月額コスト試算

**小規模運用（無料プラン）**:
- NewsAPI: $0（100リクエスト/日）
- SerpAPI: $0（100検索/月）
- **合計: $0/月**

**通常運用**:
- NewsAPI: $449/月（250,000リクエスト）
- SerpAPI: $50/月（5,000検索）
- **合計: $499/月（約75,000円）**

---

## 🔧 実装例: @AI担当の自動収集スクリプト

### 日次実行スクリプト

```python
#!/usr/bin/env python3
"""
@AI担当 - 日次情報収集スクリプト
エステ業界のニュースを自動収集し、データベースに保存
"""

import requests
import sqlite3
from datetime import datetime, timedelta

# API設定
NEWSAPI_KEY = "YOUR_NEWSAPI_KEY"
SERPAPI_KEY = "YOUR_SERPAPI_KEY"

# データベース接続
db_path = "C:\\Users\\pline\\.gemini\\antigravity\\scratch\\digilab_beauty.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 検索キーワード
keywords = [
    "エステ",
    "美容サロン",
    "脱毛サロン",
    "エステティックTBC",
    "ジェイエステティック",
    "たかの友梨",
    "エステ AND 倒産",
    "エステ AND M&A"
]

def collect_news_from_newsapi(keyword):
    """NewsAPIからニュースを収集"""
    url = "https://newsapi.org/v2/everything"
    
    # 過去3日間のニュース
    from_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    
    params = {
        'q': keyword,
        'language': 'ja',
        'from': from_date,
        'sortBy': 'publishedAt',
        'pageSize': 20,
        'apiKey': NEWSAPI_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    articles = []
    if data['status'] == 'ok':
        for article in data.get('articles', []):
            articles.append({
                'source': 'NewsAPI',
                'title': article['title'],
                'content': article.get('description', ''),
                'url': article['url'],
                'published_at': article['publishedAt']
            })
    
    return articles

def save_to_database(company_id, article, info_type):
    """データベースに保存"""
    cursor.execute("""
        INSERT INTO intelligence_log (
            company_id, source, info_type, title, content, url,
            collected_date, ai_agent, is_important
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company_id,
        article['source'],
        info_type,
        article['title'],
        article['content'],
        article['url'],
        datetime.now().strftime('%Y-%m-%d'),
        '@AI担当',
        1 if '倒産' in article['title'] or 'M&A' in article['title'] else 0
    ))

def main():
    """メイン処理"""
    print("=" * 60)
    print("@AI担当 - 日次情報収集開始")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    total_articles = 0
    
    for keyword in keywords:
        print(f"\nキーワード: {keyword}")
        articles = collect_news_from_newsapi(keyword)
        print(f"  収集件数: {len(articles)}件")
        
        for article in articles:
            # 企業IDの判定（簡易版）
            company_id = None
            if 'TBC' in article['title']:
                company_id = 1  # エステティックTBC
            elif 'ジェイエステ' in article['title']:
                company_id = 2  # ジェイエステティック
            
            # 情報種別の判定
            if '倒産' in article['title'] or '破産' in article['title']:
                info_type = '倒産情報'
            elif 'M&A' in article['title'] or '買収' in article['title']:
                info_type = 'M&A情報'
            elif '出店' in article['title'] or '開店' in article['title']:
                info_type = '出店情報'
            else:
                info_type = '企業ニュース'
            
            save_to_database(company_id, article, info_type)
            total_articles += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n合計収集件数: {total_articles}件")
    print("=" * 60)
    print("@AI担当 - 日次情報収集完了")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

### Windows タスクスケジューラー設定

```powershell
# 毎日6:00に実行
schtasks /create /tn "DigiLabBeauty_DailyNewsCollection" /tr "python C:\Users\pline\.gemini\antigravity\scratch\daily_news_collection.py" /sc daily /st 06:00
```

---

## 📊 収集データの活用

### @AI営業への通知

```python
def notify_ai_sales_team(important_news):
    """重要なニュースを@AI営業に通知"""
    if important_news['is_important']:
        subject = f"【重要】{important_news['title']}"
        body = f"""
@AI営業 様

@AI担当からの重要な情報です。

タイトル: {important_news['title']}
情報種別: {important_news['info_type']}
URL: {important_news['url']}

この情報は営業活動に影響する可能性があります。
該当企業への対応を検討してください。

--
@AI担当（自動送信）
        """
        send_email('ai-sales@digilab-beauty.com', subject, body)
```

---

## ⚙️ 環境変数設定

```.env
# NewsAPI
NEWSAPI_KEY=your_newsapi_key_here

# SerpAPI
SERPAPI_KEY=your_serpapi_key_here

# データベース
DB_PATH=C:\Users\pline\.gemini\antigravity\scratch\digilab_beauty.db

# メール設定
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=ai-intelligence@digilab-beauty.com
EMAIL_PASSWORD=your_app_password_here
```

---

## 🚀 セットアップ手順（まとめ）

### Step 1: NewsAPI アカウント作成
1. https://newsapi.org/ にアクセス
2. 無料アカウント作成
3. APIキー取得

### Step 2: SerpAPI アカウント作成（オプション）
1. https://serpapi.com/ にアクセス
2. 無料アカウント作成
3. APIキー取得

### Step 3: 環境設定
1. `.env`ファイル作成
2. APIキーを設定
3. Pythonパッケージインストール
```bash
pip install requests python-dotenv
```

### Step 4: スクリプト配置
1. `daily_news_collection.py`を保存
2. テスト実行
```bash
python daily_news_collection.py
```

### Step 5: 自動化設定
1. Windowsタスクスケジューラーに登録
2. 毎日6:00に自動実行

---

## 💡 Opalの代わりに推奨する理由

| 項目 | NewsAPI | SerpAPI | Google Opal | Opal.so |
|------|---------|---------|-------------|---------|
| 外部API利用 | ✅ 可能 | ✅ 可能 | ❌ 不可 | ❌ 制限あり |
| 日本語対応 | ✅ 対応 | ✅ 対応 | ✅ 対応 | - |
| 無料プラン | ✅ あり | ✅ あり | - | - |
| エステ業界ニュース | ✅ 取得可能 | ✅ 取得可能 | △ 手動のみ | - |
| 自動化 | ✅ 簡単 | ✅ 簡単 | ❌ 困難 | - |
| 商用利用 | ✅ 可能 | ✅ 可能 | ? 要確認 | - |

---

## 📞 次のステップ

1. **NewsAPIアカウント作成**（5分）
2. **APIテスト**（10分）
3. **データベース連携テスト**（30分）
4. **自動化設定**（20分）

まずはNewsAPIの無料プランで始めることをお勧めします！

---

**作成日**: 2026-02-10  
**作成者**: @AI担当
