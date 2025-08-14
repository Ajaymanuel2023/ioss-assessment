# backend/main.py
import os
import string
import random
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, HttpUrl

from database import init_db, get_conn

# ---------- App & CORS ----------
app = FastAPI(title="URL Shortener")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod if you know your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DB ----------
init_db()

# ---------- Models ----------
class ShortenIn(BaseModel):
    url: HttpUrl  # built-in validation

class ShortenOut(BaseModel):
    short_url: str
    short_code: str
    long_url: str

class StatsOut(BaseModel):
    short_code: str
    long_url: str
    clicks: int
    created_at: str

# ---------- Helpers ----------
ALPHABET = string.ascii_letters + string.digits

def make_code(n: int = 6) -> str:
    return "".join(random.choices(ALPHABET, k=n))

def base_url(request: Request) -> str:
    # Useful locally and on Render
    # If you deploy, set FRONTEND_URL or leave as request.base_url
    return str(request.base_url).rstrip("/")

def get_by_long_url(long_url: str) -> Optional[dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM urls WHERE long_url = ? LIMIT 1;", (long_url,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def insert_mapping(short_code: str, long_url: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO urls (short_code, long_url) VALUES (?, ?);",
        (short_code, long_url),
    )
    conn.commit()
    conn.close()

def get_by_code(code: str) -> Optional[dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM urls WHERE short_code = ? LIMIT 1;", (code,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def increment_clicks(code: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?;", (code,))
    conn.commit()
    conn.close()

# ---------- Routes ----------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/shorten", response_model=ShortenOut)
def shorten(payload: ShortenIn, request: Request):
    long_url = str(payload.url).strip()

    # If URL already exists, reuse the same short code (nice UX)
    existing = get_by_long_url(long_url)
    if existing:
        short = f"{base_url(request)}/{existing['short_code']}"
        return ShortenOut(short_url=short, short_code=existing["short_code"], long_url=long_url)

    # Generate a unique short code
    for _ in range(10):  # try up to 10 times for uniqueness
        code = make_code(6)
        if not get_by_code(code):
            insert_mapping(code, long_url)
            short = f"{base_url(request)}/{code}"
            return ShortenOut(short_url=short, short_code=code, long_url=long_url)

    raise HTTPException(status_code=500, detail="Could not generate a unique short code. Try again.")

@app.get("/{code}")
def go(code: str):
    row = get_by_code(code)
    if not row:
        raise HTTPException(status_code=404, detail="Short code not found")
    increment_clicks(code)
    return RedirectResponse(url=row["long_url"], status_code=307)

@app.get("/stats/{code}", response_model=StatsOut)
def stats(code: str):
    row = get_by_code(code)
    if not row:
        raise HTTPException(status_code=404, detail="Short code not found")
    return StatsOut(
        short_code=row["short_code"],
        long_url=row["long_url"],
        clicks=row["clicks"],
        created_at=row["created_at"],
    )

# ---------- Uvicorn entry (local dev only) ----------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))  # Render will set PORT=10000
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
