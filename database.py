import aiosqlite
from datetime import datetime, timedelta
from bot.config import DB_PATH

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    joined_at TEXT,
    last_seen TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    price TEXT NOT NULL,
    description TEXT,
    photo_file_id TEXT,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    qty INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT,
    full_name TEXT,
    phone TEXT,
    address TEXT,
    items_text TEXT,
    status TEXT DEFAULT 'yangi',
    created_at TEXT
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES_SQL)
        await db.commit()


# ---------------- Categories ----------------

async def add_category(name: str) -> bool:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            await db.commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def get_categories():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM categories ORDER BY name")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_category(category_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def delete_category(category_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products WHERE category_id = ?", (category_id,))
        await db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        await db.commit()


# ---------------- Products ----------------

async def add_product(category_id: int, name: str, price: str, description: str, photo_file_id: str = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO products (category_id, name, price, description, photo_file_id) VALUES (?, ?, ?, ?, ?)",
            (category_id, name, price, description, photo_file_id),
        )
        await db.commit()
        return cursor.lastrowid


async def get_products_by_category(category_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM products WHERE category_id = ? AND is_active = 1 ORDER BY id DESC", (category_id,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def delete_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        await db.commit()


async def get_all_products():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT products.*, categories.name AS category_name FROM products "
            "JOIN categories ON products.category_id = categories.id ORDER BY products.id DESC"
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


# ---------------- Cart ----------------

async def add_to_cart(user_id: int, product_id: int, qty: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM cart_items WHERE user_id = ? AND product_id = ?", (user_id, product_id)
        )
        row = await cursor.fetchone()
        if row:
            await db.execute(
                "UPDATE cart_items SET qty = qty + ? WHERE id = ?", (qty, row["id"])
            )
        else:
            await db.execute(
                "INSERT INTO cart_items (user_id, product_id, qty) VALUES (?, ?, ?)", (user_id, product_id, qty)
            )
        await db.commit()


async def get_cart(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT cart_items.id AS cart_id, cart_items.qty, products.* FROM cart_items "
            "JOIN products ON cart_items.product_id = products.id WHERE cart_items.user_id = ?",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def remove_from_cart(cart_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cart_items WHERE id = ?", (cart_id,))
        await db.commit()


async def clear_cart(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
        await db.commit()


# ---------------- Orders ----------------

async def create_order(user_id: int, username: str, full_name: str, phone: str, address: str, items_text: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO orders (user_id, username, full_name, phone, address, items_text, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, username, full_name, phone, address, items_text, datetime.now().isoformat(timespec="seconds")),
        )
        await db.commit()
        return cursor.lastrowid


async def get_recent_orders(limit: int = 20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_orders_count(days: int = 30) -> int:
    cutoff = (datetime.now() - timedelta(days=days)).isoformat(timespec="seconds")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM orders WHERE created_at >= ?", (cutoff,))
        row = await cursor.fetchone()
        return row[0] if row else 0


# ---------------- Users (statistika va reklama uchun) ----------------

async def upsert_user(user_id: int, username: str | None, full_name: str | None):
    now = datetime.now().isoformat(timespec="seconds")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            await db.execute(
                "UPDATE users SET username = ?, full_name = ?, last_seen = ? WHERE user_id = ?",
                (username, full_name, now, user_id),
            )
        else:
            await db.execute(
                "INSERT INTO users (user_id, username, full_name, joined_at, last_seen) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, full_name, now, now),
            )
        await db.commit()


async def get_users_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0] if row else 0


async def get_active_users_count(days: int = 30) -> int:
    cutoff = (datetime.now() - timedelta(days=days)).isoformat(timespec="seconds")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (cutoff,))
        row = await cursor.fetchone()
        return row[0] if row else 0


async def get_all_user_ids() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [r[0] for r in rows]


# ---------------- Settings (masalan: majburiy obuna kanali) ----------------

async def get_setting(key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else None


async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        await db.commit()
