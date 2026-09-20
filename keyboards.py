from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import PC_BUILD_PRESETS


def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🛒 Katalog"), KeyboardButton(text="🧺 Savatcha")],
        [KeyboardButton(text="🖥 Kompyuter yig'ish"), KeyboardButton(text="❓ Savol-javob (FAQ)")],
        [KeyboardButton(text="📍 Manzil va aloqa"), KeyboardButton(text="📦 Buyurtmalarim")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def categories_kb(categories) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat["name"], callback_data=f"cat:{cat['id']}")
    builder.adjust(2)
    return builder.as_markup()


def products_kb(products, category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in products:
        builder.button(text=f"{p['name']} — {p['price']}", callback_data=f"prod:{p['id']}")
    builder.button(text="⬅️ Kategoriyalarga qaytish", callback_data="back_to_categories")
    builder.adjust(1)
    return builder.as_markup()


def product_detail_kb(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Savatchaga qo'shish", callback_data=f"addcart:{product_id}")
    builder.button(text="⬅️ Orqaga", callback_data=f"cat:{category_id}")
    builder.adjust(1)
    return builder.as_markup()


def cart_kb(cart_items) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in cart_items:
        builder.button(
            text=f"❌ {item['name']} ({item['qty']} dona)",
            callback_data=f"delcart:{item['cart_id']}",
        )
    if cart_items:
        builder.button(text="✅ Buyurtma berish", callback_data="checkout")
        builder.button(text="🗑 Savatchani tozalash", callback_data="clear_cart")
    builder.adjust(1)
    return builder.as_markup()


def faq_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚚 Yetkazib berish", callback_data="faq:delivery")
    builder.button(text="💳 To'lov turlari", callback_data="faq:payment")
    builder.button(text="🛡 Kafolat", callback_data="faq:warranty")
    builder.button(text="🕒 Ish vaqti", callback_data="faq:hours")
    builder.button(text="📍 Manzil va aloqa", callback_data="faq:address")
    builder.adjust(1)
    return builder.as_markup()


def pc_purpose_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, preset in PC_BUILD_PRESETS.items():
        builder.button(text=preset["label"], callback_data=f"pcbuild:{key}")
    builder.adjust(1)
    return builder.as_markup()


def contact_operator_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✈️ Operator bilan bog'lanish", url="https://t.me/Itech_operator")
    return builder.as_markup()


# ---------------- Admin keyboards ----------------

def admin_menu_kb() -> ReplyKeyboardMarkup:
    kb_layout = [
        [KeyboardButton(text="📁 Katalog qo'shish"), KeyboardButton(text="🗑 Katalogni o'chirish")],
        [KeyboardButton(text="➕ Mahsulot qo'shish"), KeyboardButton(text="🗑 Mahsulotni o'chirish")],
        [KeyboardButton(text="📋 Barcha mahsulotlar"), KeyboardButton(text="📦 Buyurtmalar")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📢 Obuna kanal qo'shish")],
        [KeyboardButton(text="📣 Reklama yuborish")],
        [KeyboardButton(text="⬅️ Admin paneldan chiqish")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb_layout, resize_keyboard=True)


def confirm_channel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data="channel_confirm")
    builder.button(text="❌ Bekor qilish", callback_data="channel_cancel")
    builder.adjust(2)
    return builder.as_markup()


def subscribe_kb(channel: str) -> InlineKeyboardMarkup:
    url = channel if channel.startswith("http") else f"https://t.me/{channel.lstrip('@')}"
    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 Kanalga o'tish", url=url)
    builder.button(text="✅ Tekshirish", callback_data="check_sub")
    builder.adjust(1)
    return builder.as_markup()


def admin_categories_kb(categories, prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat["name"], callback_data=f"{prefix}:{cat['id']}")
    builder.adjust(1)
    return builder.as_markup()


def admin_products_delete_kb(products) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in products:
        builder.button(text=f"❌ {p['name']}", callback_data=f"admin_delprod:{p['id']}")
    builder.adjust(1)
    return builder.as_markup()


def skip_photo_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ Rasmsiz davom etish", callback_data="skip_photo")
    return builder.as_markup()
