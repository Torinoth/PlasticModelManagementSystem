# Plastic Model Management System
PMMsys

## やりたいこと
1. プラモの在庫管理
    - 製品名
    - メーカー
    - 製品番号
    - 価格
    - 画像
    - 説明文
    - 在庫数
2. 現在作成中のプラモ
3. 料金表

## セットアップ

### 必要なもの
- Python 3.11+
- PostgreSQL 14+

### ローカル開発環境の構築

#### 1. venv の有効化と依存インストール

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して DB 接続情報を入力してください。

#### 3. PostgreSQL のインストールと DB 作成

**macOS (Homebrew)**

```bash
brew install postgresql@16
brew services start postgresql@16
```

**DB とユーザーの作成**

```bash
psql postgres
```

```sql
CREATE DATABASE pmm_db;
CREATE USER pmm_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pmm_db TO pmm_user;
\q
```

`.env` の `DB_USER` / `DB_PASSWORD` を上記に合わせて更新してください。

#### 4. マイグレーション実行

```bash
python manage.py migrate
```

#### 5. 開発サーバー起動

```bash
python manage.py runserver
```

API は `http://127.0.0.1:8000/api/` で利用できます。

### API エンドポイント一覧

| エンドポイント | 説明 |
|---|---|
| `GET /api/kits/` | キット一覧（`?tags=タグ名` でフィルタ可能） |
| `POST /api/kits/` | キット登録 |
| `GET /api/kits/{id}/` | キット詳細 |
| `PUT /api/kits/{id}/` | キット更新 |
| `DELETE /api/kits/{id}/` | キット削除 |
| `GET /api/tags/` | タグ一覧 |
| `POST /api/tags/` | タグ作成 |