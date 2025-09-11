"""
===============================================================================
 K Stock Quote Web App
 - FastAPI backend serving an HTML form at "/"
 - Enter a ticker -> shows current price
 - Caches quotes in Redis for N seconds
 - Logs every request in SQLite (ticker, price, timestamp, source)
===============================================================================
"""

# ============================== IMPORTS & CONFIG ==============================
import os
import json
import sqlite3
from datetime import datetime, timezone

import requests
import redis
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "")
DB_PATH = os.getenv("DB_PATH", "/data/quotes.db")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "120"))

app = FastAPI(title="Stock Quotes")
templates = Jinja2Templates(directory="templates")

# ================================ REDIS SETUP =================================
# Using the redis-py client (sync). Keys are namespaced "quote:{TICKER}".
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# =============================== SQLITE SETUP =================================
# DB schema: one table `search_history` logging queries/results.
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ticker TEXT NOT NULL,
              price REAL,
              source TEXT NOT NULL,          -- 'cache' or 'api'
              searched_at TEXT NOT NULL      -- ISO timestamp
            );
        """)
        conn.commit()

init_db()

def k_db_insert(ticker: str, price: float | None, source: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO search_history (ticker, price, source, searched_at) VALUES (?, ?, ?, ?)",
            (ticker.upper(), price, source, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()

# =============================== HELPER: QUOTES ===============================
def fetch_quote_from_api(ticker: str) -> tuple[float | None, dict]:
    """Fetch current price via Alpha Vantage GLOBAL_QUOTE and return (price, raw_json)."""
    if not ALPHAVANTAGE_API_KEY:
        # DImaag Kharaab; Return a structured error instead of 500
        return None, {"error": "missing_api_key"}

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker.upper(),
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json() or {}
    except Exception as e:
        # Never throw; return a diagnostic dict
        return None, {"error": "request_failed", "detail": f"{type(e).__name__}: {e}"}

    # Alpha Vantage sometimes returns {"Note": ...} or {"Information": ...} or {"Error Message": ...}
    gq = data.get("Global Quote") or data.get("GlobalQuote")
    if not gq or not isinstance(gq, dict):
        return None, data

    # Try to parse "05. price"
    price_str = gq.get("05. price")
    try:
        price = float(price_str) if price_str not in (None, "") else None
    except (TypeError, ValueError):
        price = None

    return price, data


def get_quote(ticker: str) -> tuple[float | None, str]:
    """
    Return (price, source).
    - Check Redis JSON ({price, cached_at})
    - On miss, call API
    - Cache good results for CACHE_TTL_SECONDS
    - Negative-cache misses for 15s (prevents thrashing) without throwing 500
    """
    key = f"quote:{ticker.upper()}"

    # Cache read
    try:
        cached = r.get(key)
    except Exception as e:
        cached = None
        print(f"[redis-read-error] key={key} err={e}")

    if cached:
        try:
            obj = json.loads(cached)
            return obj.get("price"), "cache"
        except json.JSONDecodeError:
            # corrupted cache; treat as miss
            pass

    # API fetch
    price, raw = fetch_quote_from_api(ticker)

    # Cache write
    try:
        if price is not None:
            r.setex(
                key, CACHE_TTL_SECONDS,
                json.dumps({"price": price, "cached_at": datetime.now(timezone.utc).isoformat()})
            )
        else:
            # Negative cache (safe, serializable reason summary only)
            short_reason = {"reason": raw.get("error") or next(iter(raw.keys()), "unknown")}
            r.setex(
                key, 15,
                json.dumps({"price": None, "cached_at": datetime.now(timezone.utc).isoformat(), **short_reason})
            )
            # Log full raw to stdout for debugging, but don't store large payloads in Redis
            print(f"[quote-null] ticker={ticker} raw={raw}")
    except Exception as e:
        print(f"[redis-write-error] key={key} err={e}")

    return price, "api"

# ================================== ROUTES ====================================
@app.get("/", response_class=HTMLResponse)
def form_page(request: Request, ticker: str | None = None):
    """
    GET / -> HTML form. If `?ticker=TSLA` is provided, we show the result inline.
    """
    price, source = (None, "") if not ticker else get_quote(ticker)
    if ticker:
        k_db_insert(ticker, price, source)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "ticker": ticker, "price": price, "source": source, "ttl": CACHE_TTL_SECONDS}
    )

@app.post("/quote", response_class=HTMLResponse)
def post_quote(request: Request, ticker: str = Form(...)):
    """
    POST /quote -> handles form submission, fetches quote, logs it, renders page.
    """
    price, source = get_quote(ticker)
    k_db_insert(ticker, price, source)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "ticker": ticker, "price": price, "source": source, "ttl": CACHE_TTL_SECONDS}
    )

@app.get("/api/history")
def api_history(limit: int = 50):
    """
    Optional helper: return last 'limit' rows for quick inspection via JSON.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT ticker, price, source, searched_at FROM search_history ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
    return [{"ticker": t, "price": p, "source": s, "searched_at": at} for (t, p, s, at) in rows]

@app.get("/debug/quote")
def debug_quote(ticker: str):
    price, raw = fetch_quote_from_api(ticker)
    return {"ticker": ticker.upper(), "price_parsed": price, "raw_payload": raw}
