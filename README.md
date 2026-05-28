# Plastic Model Management System (PMMsys)

プラモデルの積みリスト管理システム。

## 構成

| コンポーネント | 役割 |
|---|---|
| Django 5.0 + Gunicorn | バックエンド API |
| Vue 3 + Vite | フロントエンド SPA |
| PostgreSQL 16 | データベース |
| Nginx | 静的ファイル配信・リバースプロキシ |
| Cloudflare Tunnel | 外部公開（HTTPS） |

---

## ローカル開発環境（Mac / venv）

### 1. venv の有効化と依存インストール

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
cp .env.example .env
# DB_HOST=localhost, DEBUG=True に書き換え
```

### 3. PostgreSQL の準備（Homebrew）

```bash
brew install postgresql@16 && brew services start postgresql@16
psql postgres -c "CREATE DATABASE pmm_db;"
psql postgres -c "CREATE USER pmm_user WITH PASSWORD 'your_password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE pmm_db TO pmm_user;"
```

### 4. マイグレーション & 起動

```bash
python manage.py migrate
python manage.py runserver
```

API: `http://127.0.0.1:8000/api/`

---

## Docker 開発環境（Mac）

DB とバックエンドを Docker で、フロントエンドは Vite dev server で動かします。

```bash
# バックエンド + PostgreSQL を起動
docker compose -f docker-compose.dev.yml up -d

# フロントエンド（別ターミナル）
cd ../../vue/pmm_vue && npm run dev
```

Vite dev server (`http://localhost:5173`) が `/api/` `/media/` を  
`http://127.0.0.1:8000` へプロキシします。

```bash
# 停止
docker compose -f docker-compose.dev.yml down
```

---

## 本番デプロイ（Raspberry Pi 4 / arm64）

### ディレクトリ構成（前提）

```
~/projects/
├── Django/PlasticModelManagementSystem/   # 本リポジトリ
└── vue/pmm_vue/                           # フロントエンド
```

`docker-compose.yml` は `../../vue/pmm_vue` を参照するため、  
上記の相対配置でクローンしてください。

### 1. SSD のマウントと永続化ディレクトリの作成

```bash
sudo mkdir -p /mnt/ssd/pmm/{postgres,media}
sudo chown -R $USER:$USER /mnt/ssd/pmm
```

### 2. リポジトリのクローン

```bash
mkdir -p ~/projects/Django ~/projects/vue
git clone <backend-repo-url> ~/projects/Django/PlasticModelManagementSystem
git clone <frontend-repo-url> ~/projects/vue/pmm_vue
```

### 3. 環境変数の設定

```bash
cd ~/projects/Django/PlasticModelManagementSystem
cp .env.example .env
nano .env
```

**必須項目：**

| 変数 | 説明 |
|---|---|
| `SECRET_KEY` | ランダムな長い文字列（下記コマンドで生成） |
| `ALLOWED_HOSTS` | ドメイン名（例: `example.com`） |
| `DB_PASSWORD` | PostgreSQL パスワード |
| `CORS_ORIGIN_WHITELIST` | `https://example.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://example.com` |
| `CLOUDFLARE_TUNNEL_TOKEN` | Cloudflare ダッシュボードで取得 |

```bash
# SECRET_KEY 生成
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 4. Cloudflare Tunnel の設定

1. [Cloudflare Zero Trust](https://one.dash.cloudflare.com/) > Networks > Tunnels
2. 新しいトンネルを作成 → トークンをコピーして `.env` に設定
3. Public Hostname を設定:
   - ドメイン: `example.com`
   - Service Type: `HTTP`、URL: `nginx:80`

### 5. 初回起動

```bash
docker compose up -d --build
```

### 6. 初回セットアップ（起動後に一度だけ）

```bash
# 管理者ユーザーの作成
docker compose exec backend python manage.py createsuperuser

# テストデータの投入（任意）
docker compose exec backend python manage.py loaddata pmm/fixtures/test_data.json
```

### 7. 起動確認

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f nginx
docker compose logs -f cloudflared
```

---

## 更新デプロイ

```bash
git pull
cd ../../vue/pmm_vue && git pull && cd -
docker compose up -d --build
```

---

## バックアップ

```bash
# PostgreSQL ダンプ
docker compose exec db pg_dump -U ${DB_USER} ${DB_NAME} > backup_$(date +%Y%m%d).sql

# メディアファイル
tar czf media_backup_$(date +%Y%m%d).tar.gz /mnt/ssd/pmm/media
```

---

## API エンドポイント一覧

| エンドポイント | 説明 |
|---|---|
| `GET /api/kits/` | キット一覧（`?status=` `?tags=` `?ordering=` でフィルタ・ソート） |
| `POST /api/kits/` | キット登録 |
| `GET /api/kits/{id}/` | キット詳細 |
| `PATCH /api/kits/{id}/` | キット更新 |
| `DELETE /api/kits/{id}/` | キット削除 |
| `GET /api/kits/summary/` | サマリー（件数・金額合計・タグTop5） |
| `GET /api/tags/` | タグ一覧 |
| `GET /api/makers/` | メーカー一覧 |
| `GET /api/brands/` | ブランド一覧 |
| `GET /api/scales/` | スケール一覧 |
| `POST /api/auth/login/` | ログイン |
| `POST /api/auth/logout/` | ログアウト |
| `GET /api/auth/me/` | 現在のユーザー情報 |
| `POST /api/auth/register/` | ユーザー登録申請 |

---

## ポート一覧

| ポート | 用途 |
|---|---|
| 80 | Nginx（本番: Cloudflare Tunnel 経由でのみ公開） |
| 8000 | Gunicorn（内部 Docker ネットワークのみ） |
| 5432 | PostgreSQL（内部 / dev 環境のみ外部公開） |
