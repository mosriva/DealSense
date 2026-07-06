import os
import sqlite3

DB = "data/dealsense.db"

def init_db() -> None:
    """Init DB tables."""
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT UNIQUE, price TEXT, source TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        c.execute("CREATE TABLE IF NOT EXISTS price_history (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, price TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(product_id) REFERENCES products(id))")
        c.execute("CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT UNIQUE, threshold_price REAL, active INTEGER DEFAULT 1, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        try:
            c.execute("DELETE FROM alerts WHERE id NOT IN (SELECT MIN(id) FROM alerts GROUP BY product_name)")
            c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_alerts_product_name ON alerts (product_name)")
        except Exception: pass

def save_product(name: str, url: str, price: str, source: str) -> int:
    """Save product and return id."""
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO products (name, url, price, source, timestamp) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP) ON CONFLICT(url) DO UPDATE SET price=excluded.price, timestamp=CURRENT_TIMESTAMP", (name, url, str(price), source))
        c.execute("SELECT id FROM products WHERE url = ?", (url,))
        return c.fetchone()[0]

def save_price_history(product_id: int, price: str) -> None:
    """Log price point."""
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT INTO price_history (product_id, price) VALUES (?, ?)", (product_id, str(price)))

def get_price_history(product_name: str) -> list:
    """Return price history."""
    with sqlite3.connect(DB) as conn:
        return conn.execute("SELECT ph.price, ph.timestamp FROM price_history ph JOIN products p ON ph.product_id = p.id WHERE p.name LIKE ?", (f"%{product_name}%",)).fetchall()

def set_alert(product_name: str, threshold_price: float) -> None:
    """Create alert."""
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT OR IGNORE INTO alerts (product_name, threshold_price) VALUES (?, ?)", (product_name, threshold_price))

def check_alerts(products: list[dict]) -> list[dict]:
    """Return triggered alerts."""
    with sqlite3.connect(DB) as conn:
        alerts = conn.execute("SELECT id, product_name, threshold_price FROM alerts WHERE active = 1").fetchall()
    triggered = []
    for aid, name, threshold in alerts:
        for p in products:
            if name.lower() in p["name"].lower():
                cleaned = "".join(c for c in str(p["price"]) if c.isdigit() or c == ".")
                val = float(cleaned) if cleaned else None
                if val is not None and val <= threshold:
                    triggered.append({"alert_id": aid, "product_name": p["name"], "threshold_price": threshold, "current_price": val, "url": p["url"]})
    return triggered
