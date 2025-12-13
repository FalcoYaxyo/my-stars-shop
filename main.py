# main.py
import os
import json
import sqlite3
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# ================== CONFIG ==================
BOT_TOKEN = "8442397420:AAGQeQDRizNQGBxMgAICgPSQ_1Xw3FdsFBw"  # Telegram bot token
WEBAPP_URL = "https://username.github.io/TelegramBot/index.html"  # GitHub Pages URL
ADMIN_ID = 123456789  # Telegram user ID (admin)
HTTP_PORT = 8080  # Web server port
# ============================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
DB = "orders.db"

# SQLite init
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        kind TEXT,
        value TEXT,
        price INTEGER,
        status TEXT,
        payment_provider TEXT,
        payment_link TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def create_order(user_id, username, kind, value, price):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO orders(user_id, username, kind, value, price, status) VALUES(?,?,?,?,?, 'pending')",
                (user_id, username, kind, str(value), price))
    conn.commit()
    oid = cur.lastrowid
    conn.close()
    return oid

def set_order_paid(order_id, provider):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status='paid', payment_provider=? WHERE id=?", (provider, order_id))
    conn.commit()
    conn.close()

def save_payment_link(order_id, provider, link):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE orders SET payment_provider=?, payment_link=? WHERE id=?", (provider, link, order_id))
    conn.commit()
    conn.close()

# Demo payment link generator
async def create_demo_transaction(order_id, amount, provider):
    return f"https://example.com/pay/{provider}?order={order_id}&amount={amount}"

# ---------------- Bot handlers ----------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Stars Shop", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer("Star & Gift do'koniga xush kelibsiz!", reply_markup=kb)

@dp.message()
async def on_message(message: types.Message):
    if message.web_app_data:
        raw = message.web_app_data.data
        try:
            data = json.loads(raw)
        except:
            await message.reply("Noto'g'ri ma'lumot yuborildi.")
            return

        user = message.from_user
        oid = create_order(user.id, getattr(user,"username",""), data.get("type"), data.get("value"), data.get("price"))
        provider = "click"
        amount = int(data.get("price",0))
        pay_link = await create_demo_transaction(oid, amount, provider)
        save_payment_link(oid, provider, pay_link)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="To'lovni boshlash", url=pay_link)],
            [InlineKeyboardButton(text="To'lov qilindimi tekshirish", callback_data=f"check_{oid}")]
        ])
        await message.reply(f"Buyurtma #{oid} yaratildi. To'lov: {amount} so'm. To'lov linki quyida:", reply_markup=kb)
        return

    # admin buyurtmalarni ko'rish
    if message.text and message.text.startswith("/orders"):
        if message.from_user.id != ADMIN_ID:
            await message.reply("Siz admin emassiz.")
            return
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT id, user_id, kind, value, price, status, payment_provider FROM orders ORDER BY id DESC LIMIT 50")
        rows = cur.fetchall()
        conn.close()
        text = "Oxirgi buyurtmalar:\n"
        for r in rows:
            text += f"#{r[0]} uid:{r[1]} {r[2]}:{r[3]} {r[4]} so'm status:{r[5]} prov:{r[6]}\n"
        await message.reply(text)
        return

@dp.callback_query()
async def cb_handler(cb: types.CallbackQuery):
    data = cb.data or ""
    if data.startswith("check_"):
        oid = int(data.split("_",1)[1])
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT status, payment_link FROM orders WHERE id=?", (oid,))
        row = cur.fetchone()
        conn.close()
        if not row:
            await cb.message.answer("Buyurtma topilmadi.")
            return
        status, link = row
        await cb.message.answer(f"Buyurtma #{oid} status: {status}\nLink: {link}")

# Web server (demo callback)
async def handle_callback(request):
    data = await request.json()
    order_id = int(data.get("order_id") or 0)
    status = data.get("status") or ""
    provider = data.get("provider") or "unknown"

    if order_id and status in ("paid","success"):
        set_order_paid(order_id, provider)
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT user_id, kind, value FROM orders WHERE id=?", (order_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            user_id, kind, value = row
            try:
                asyncio.create_task(bot.send_message(user_id, f"To'lov qabul qilindi. Buyurtma #{order_id} — {kind}:{value}."))
            except:
                pass
        return web.json_response({"ok":True})
    return web.json_response({"ok":False, "reason":"invalid"})

async def start_webapp(app):
    print("Web-server started on port", HTTP_PORT)

def create_app():
    app = web.Application()
    app.router.add_post("/payment_callback", handle_callback)
    return app

async def main():
    init_db()
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", HTTP_PORT)
    await site.start()
    print(f"HTTP server running on port {HTTP_PORT}")

    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())