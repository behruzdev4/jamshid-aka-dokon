import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin Telegram ID'lari (vergul bilan ajratilgan): 123456789,987654321
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

# Buyurtmalar tushadigan guruh ID (ixtiyoriy). Bo'sh qoldirsangiz faqat adminlarga shaxsiy yuboriladi.
_group_id = os.getenv("ORDER_GROUP_ID", "").strip()
ORDER_GROUP_ID = int(_group_id) if _group_id.lstrip("-").isdigit() else None

DB_PATH = os.getenv("DB_PATH", "bot_database.db")

SHOP_NAME = os.getenv("SHOP_NAME", "iTech Kompyuter Savdo Markazi")
CONTACT_PHONES = ["+998(95)727-44-00", "+998(99)342-97-00"]
CONTACT_TELEGRAM = ["@Itech_operator", "@Itech_adm"]
CHANNEL_LINK = "https://t.me/optomkompyutersavdosi"

# ---------------- AI (OpenRouter orqali avto-javob yordamchisi) ----------------
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-4o-mini")
# AI javob berish so'nggi N ta xabarni "xotira" sifatida eslab qoladi (foydalanuvchi bo'yicha)
AI_HISTORY_LIMIT = 6

FAQ_TEXTS = {
    "delivery": (
        "🚚 <b>Yetkazib berish</b>\n\n"
        "O'zbekiston bo'ylab yetkazib beramiz!\n"
        "Buyurtma bergandan so'ng operatorimiz siz bilan bog'lanib, "
        "aniq narx va yetkazib berish muddatini aytadi."
    ),
    "address": (
        "📍 <b>Manzil va aloqa</b>\n\n"
        f"☎️ Tel: {', '.join(CONTACT_PHONES)}\n"
        f"✈️ Telegram: {', '.join(CONTACT_TELEGRAM)}\n\n"
        f"📢 Kanalimiz: {CHANNEL_LINK}"
    ),
    "payment": (
        "💳 <b>To'lov turlari</b>\n\n"
        "Naqd, plastik karta va bo'lib to'lash imkoniyatlari mavjud. "
        "Batafsil ma'lumot uchun operator bilan bog'laning."
    ),
    "warranty": (
        "🛡 <b>Kafolat</b>\n\n"
        "Barcha mahsulotlarga kafolat beriladi. Kafolat muddati mahsulot "
        "turiga qarab farqlanadi — sotib olishdan oldin operatordan so'rang."
    ),
    "hours": (
        "🕒 <b>Ish vaqti</b>\n\n"
        "Har kuni 9:00 — 19:00 (dam olish kunlarisiz yoki jadval bo'yicha, "
        "aniqlashtirish uchun operatorga yozing)."
    ),
}

# Kompyuter yig'ish yordamchisi uchun namunaviy to'plamlar (admin keyinchalik yangilashi mumkin)
PC_BUILD_PRESETS = {
    "gaming": {
        "label": "🎮 O'yin uchun (Gaming)",
        "tiers": [
            ("Kirish darajasi (~5-8 mln so'm)", "Ryzen 5 5500 / GTX 1650 / 16GB RAM / 512GB SSD"),
            ("O'rta daraja (~10-15 mln so'm)", "Ryzen 5 7500F / RTX 4060 / 16GB RAM / 1TB SSD"),
            ("Yuqori daraja (~20+ mln so'm)", "Ryzen 7 7700 / RTX 4070 Super / 32GB RAM / 1TB NVMe"),
        ],
    },
    "work": {
        "label": "💼 Ish/Ofis uchun",
        "tiers": [
            ("Boshlang'ich (~3-5 mln so'm)", "Intel i3 / integrated GPU / 8GB RAM / 256GB SSD"),
            ("O'rta (~6-9 mln so'm)", "Intel i5 / integrated GPU / 16GB RAM / 512GB SSD"),
        ],
    },
    "design": {
        "label": "🎨 Dizayn/Montaj uchun",
        "tiers": [
            ("O'rta (~15-20 mln so'm)", "Ryzen 7 / RTX 4060 Ti / 32GB RAM / 1TB NVMe"),
            ("Yuqori (~25+ mln so'm)", "Ryzen 9 / RTX 4070 Ti Super / 64GB RAM / 2TB NVMe"),
        ],
    },
}
