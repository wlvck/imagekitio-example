# 🚀 FastAPI Media Server

Lightweight FastAPI backend for uploading and serving images via ImageKit.io.

## 📌 Features

- Async FastAPI backend with SQLAlchemy (async)
- JWT authentication (FastAPI Users)
- Image upload + delivery via ImageKit
- SQLite by default (easy to switch to PostgreSQL)
- Dockerfile for containerized deployment
- Clean, modular project layout

---

## 🔧 Requirements

- Python >= 3.11
- pip
- (Optional) Docker for containerized runs

Note: this project expects an async-capable server such as uvicorn to run locally.

---

## 📦 Installation (Local Development)

```bash
git clone <repo-url>
cd fast-api
python -m venv .venv
# Activate the venv:
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (cmd)
.venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

If this repo uses the `uv` CLI (optional), follow its project docs. Otherwise, use uvicorn (installed via requirements) to run the app.

---

## 🔐 Environment variables

Copy the example env and fill values:

```bash
cp .env.example .env
```

Required variables (example):

```env
IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_PUBLIC_KEY=your_public_key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_endpoint
DATABASE_URL=sqlite+aiosqlite:///./db.sqlite3
SECRET_KEY=replace_with_a_random_secret
```

Where to get ImageKit keys:

- Sign in at https://imagekit.io
- Dashboard → Developer → API Keys
- Copy: Private Key, Public Key, and URL Endpoint

Fill these in .env before running.

---

## ▶ Running locally

Use uvicorn to start the app (adjust module path if your app object is not `main:app`):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- http://localhost:8000 - API root
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/redoc - ReDoc (if enabled)

---

## 🐳 Running with Docker

Build:

```bash
docker build -t fast-api-app .
```

Run (use `-d` for detached):

```bash
docker run --rm -p 8000:8000 --env-file .env fast-api-app
```

---
