from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot import database as db
from bot import keyboards as kb
from bot.config import FAQ_TEXTS, PC_BUILD_PRESETS, ADMIN_IDS, ORDER_GROUP_ID
from bot.states import OrderStates, PCBuilderStates
from bot.services.ai_service import ask_ai, reset_history

router = Router()

MENU_BUTTON_TEXTS = {
    "🛒 Katalog",
    "🧺 Savatcha",
    "🖥 Kompyuter yig'ish",
    "❓ Savol-javob (FAQ)",
    "📍 Manzil va aloqa",
    "📦 Buyurtmalarim",
}


# ---------------- /start ----------------

@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\n"
        "Kompyuter va ehtiyot qismlar do'konimiz botiga xush kelibsiz!\n"
        "Bu yerda siz:\n"
        "🛒 Katalogdan mahsulot tanlab buyurtma bera olasiz\n"
        "🖥 O'zingizga mos kompyuter to'plamini tanlab olishingiz mumkin\n"
        "❓ Tez-tez so'raladigan savollarga javob topasiz\n\n"
        "Quyidagi menyudan foydalaning 👇"
    )
    await message.answer(text, reply_markup=kb.main_menu_kb())


# ---------------- Majburiy obuna tekshiruvi ----------------

@router.callback_query(F.data == "check_sub")
async def check_subscription_cb(callback: CallbackQuery):
    channel = await db.get_setting("subscribe_channel")
    if not channel:
        await callback.answer()
        await callback.message.delete()
        await callback.message.answer("✅ Botdan foydalanishingiz mumkin.", reply_markup=kb.main_menu_kb())
        return
    try:
        member = await callback.bot.get_chat_member(chat_id=channel, user_id=callback.from_user.id)
        subscribed = member.status in ("member", "administrator", "creator")
    except Exception:
        subscribed = True
    if subscribed:
        await callback.message.delete()
        await callback.message.answer(
            "✅ Rahmat! Endi botdan bemalol foydalanishingiz mumkin.",
            reply_markup=kb.main_menu_kb(),
        )
    else:
        await callback.answer("❌ Siz hali kanalga obuna bo'lmagansiz.", show_alert=True)


# ---------------- Katalog ----------------

@router.message(F.text == "🛒 Katalog")
async def show_catalog(message: Message):
    categories = await db.get_categories()
    if not categories:
        await message.answer("Hozircha katalogda kategoriyalar mavjud emas. Tez orada to'ldiriladi!")
        return
    await message.answer("Kerakli kategoriyani tanlang 👇", reply_markup=kb.categories_kb(categories))


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    categories = await db.get_categories()
    await callback.message.edit_text("Kerakli kategoriyani tanlang 👇", reply_markup=kb.categories_kb(categories))
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_products(callback: CallbackQuery):
    category_id = int(callback.data.split(":")[1])
    products = await db.get_products_by_category(category_id)
    category = await db.get_category(category_id)
    cat_name = category["name"] if category else ""
    if not products:
        await callback.answer("Bu kategoriyada hozircha mahsulot yo'q.", show_alert=True)
        return
    try:
        await callback.message.edit_text(
            f"<b>{cat_name}</b>\n\nMahsulotni tanlang 👇",
            reply_markup=kb.products_kb(products, category_id),
        )
    except Exception:
        await callback.message.answer(
            f"<b>{cat_name}</b>\n\nMahsulotni tanlang 👇",
            reply_markup=kb.products_kb(products, category_id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("prod:"))
async def show_product_detail(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    product = await db.get_product(product_id)
    if not product:
        await callback.answer("Mahsulot topilmadi.", show_alert=True)
        return
    caption = f"<b>{product['name']}</b>\n\n💰 Narxi: {product['price']}\n\n{product['description'] or ''}"
    markup = kb.product_detail_kb(product_id, product["category_id"])
    if product.get("photo_file_id"):
        await callback.message.answer_photo(product["photo_file_id"], caption=caption, reply_markup=markup)
    else:
        await callback.message.answer(caption, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("addcart:"))
async def add_to_cart_handler(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    await db.add_to_cart(callback.from_user.id, product_id, 1)
    await callback.answer("✅ Savatchaga qo'shildi!", show_alert=True)


# ---------------- Savatcha ----------------

@router.message(F.text == "🧺 Savatcha")
async def show_cart(message: Message):
    items = await db.get_cart(message.from_user.id)
    if not items:
        await message.answer("Savatchangiz bo'sh. Katalogdan mahsulot tanlang 🛒")
        return
    text = "🧺 <b>Sizning savatchangiz:</b>\n\n"
    for item in items:
        text += f"• {item['name']} — {item['price']} x{item['qty']}\n"
    text += "\nMahsulotni o'chirish uchun tugmani bosing, yoki buyurtma bering."
    await message.answer(text, reply_markup=kb.cart_kb(items))


@router.callback_query(F.data.startswith("delcart:"))
async def delete_cart_item(callback: CallbackQuery):
    cart_id = int(callback.data.split(":")[1])
    await db.remove_from_cart(cart_id)
    items = await db.get_cart(callback.from_user.id)
    if not items:
        await callback.message.edit_text("Savatchangiz bo'sh.")
    else:
        text = "🧺 <b>Sizning savatchangiz:</b>\n\n"
        for item in items:
            text += f"• {item['name']} — {item['price']} x{item['qty']}\n"
        await callback.message.edit_text(text, reply_markup=kb.cart_kb(items))
    await callback.answer("O'chirildi")


@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery):
    await db.clear_cart(callback.from_user.id)
    await callback.message.edit_text("Savatchangiz tozalandi.")
    await callback.answer()


# ---------------- Buyurtma berish (checkout) ----------------

@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    items = await db.get_cart(callback.from_user.id)
    if not items:
        await callback.answer("Savatchangiz bo'sh.", show_alert=True)
        return
    await state.set_state(OrderStates.waiting_name)
    await callback.message.answer("Buyurtmani rasmiylashtirish uchun to'liq ismingizni kiriting:")
    await callback.answer()


@router.message(OrderStates.waiting_name)
async def order_get_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(OrderStates.waiting_phone)
    await message.answer("Telefon raqamingizni kiriting (masalan: +998901234567):")


@router.message(OrderStates.waiting_phone)
async def order_get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(OrderStates.waiting_address)
    await message.answer("Yetkazib berish manzilingizni kiriting (shahar, tuman):")


@router.message(OrderStates.waiting_address)
async def order_get_address(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    address = message.text
    items = await db.get_cart(message.from_user.id)
    items_text = "\n".join([f"• {i['name']} — {i['price']} x{i['qty']}" for i in items])

    order_id = await db.create_order(
        user_id=message.from_user.id,
        username=message.from_user.username or "-",
        full_name=data["full_name"],
        phone=data["phone"],
        address=address,
        items_text=items_text,
    )
    await db.clear_cart(message.from_user.id)
    await state.clear()

    await message.answer(
        f"✅ Buyurtmangiz qabul qilindi! Raqami: #{order_id}\n\n"
        "Tez orada operatorimiz siz bilan bog'lanadi. Rahmat! 🙏",
        reply_markup=kb.main_menu_kb(),
    )

    admin_text = (
        f"🆕 <b>Yangi buyurtma #{order_id}</b>\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📞 Tel: {data['phone']}\n"
        f"📍 Manzil: {address}\n"
        f"🔗 Username: @{message.from_user.username or '-'}\n\n"
        f"<b>Mahsulotlar:</b>\n{items_text}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text)
        except Exception:
            pass
    if ORDER_GROUP_ID:
        try:
            await bot.send_message(ORDER_GROUP_ID, admin_text)
        except Exception:
            pass


@router.message(F.text == "📦 Buyurtmalarim")
async def my_orders(message: Message):
    all_orders = await db.get_recent_orders(limit=100)
    my = [o for o in all_orders if o["user_id"] == message.from_user.id][:10]
    if not my:
        await message.answer("Sizda hali buyurtmalar mavjud emas.")
        return
    text = "📦 <b>Oxirgi buyurtmalaringiz:</b>\n\n"
    for o in my:
        text += f"#{o['id']} — {o['status']} — {o['created_at']}\n"
    await message.answer(text)


# ---------------- FAQ ----------------

@router.message(F.text == "❓ Savol-javob (FAQ)")
async def show_faq(message: Message):
    await message.answer("Sizni qaysi savol qiziqtiradi?", reply_markup=kb.faq_kb())


@router.callback_query(F.data.startswith("faq:"))
async def faq_answer(callback: CallbackQuery):
    key = callback.data.split(":")[1]
    text = FAQ_TEXTS.get(key, "Ma'lumot topilmadi.")
    await callback.message.answer(text)
    await callback.answer()


@router.message(F.text == "📍 Manzil va aloqa")
async def show_address(message: Message):
    await message.answer(FAQ_TEXTS["address"], reply_markup=kb.contact_operator_kb())


# ---------------- PC yig'ish yordamchisi ----------------

@router.message(F.text == "🖥 Kompyuter yig'ish")
async def pc_builder_start(message: Message):
    await message.answer(
        "Qanday maqsadda kompyuter yig'moqchisiz? Tanlang 👇",
        reply_markup=kb.pc_purpose_kb(),
    )


@router.callback_query(F.data.startswith("pcbuild:"))
async def pc_builder_result(callback: CallbackQuery):
    key = callback.data.split(":")[1]
    preset = PC_BUILD_PRESETS.get(key)
    if not preset:
        await callback.answer("Topilmadi.", show_alert=True)
        return
    text = f"<b>{preset['label']}</b>\n\nTavsiya etilgan to'plamlar:\n\n"
    for tier_name, spec in preset["tiers"]:
        text += f"🔹 <b>{tier_name}</b>\n{spec}\n\n"
    text += (
        "Bu — taxminiy tavsiyalar. Aniq narx va mavjudlikni bilish uchun "
        "operator bilan bog'laning yoki katalogdan tayyor to'plamlarni ko'ring."
    )
    await callback.message.answer(text, reply_markup=kb.contact_operator_kb())
    await callback.answer()


# ---------------- Fallback ----------------

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Menyudan foydalaning:\n"
        "🛒 Katalog — mahsulotlarni ko'rish\n"
        "🧺 Savatcha — tanlangan mahsulotlar\n"
        "🖥 Kompyuter yig'ish — PC tavsiyasi\n"
        "❓ FAQ — tez-tez so'raladigan savollar\n"
        "📍 Manzil va aloqa\n"
        "📦 Buyurtmalarim",
        reply_markup=kb.main_menu_kb(),
    )


@router.message(Command("reset"))
async def cmd_reset_ai(message: Message):
    reset_history(message.from_user.id)
    await message.answer("🔄 AI suhbat xotirasi tozalandi.")


# ---------------- AI avto-javob (OpenRouter) ----------------
# Bu handler eng oxirida turadi: yuqoridagi barcha aniq tugma/buyruq/holat (FSM)
# handlerlariga to'g'ri kelmagan har qanday oddiy matn shu yerga tushadi va
# OpenRouter AI orqali do'kon kontekstiga mos javob beriladi.

@router.message(StateFilter(None), F.text, ~F.text.in_(MENU_BUTTON_TEXTS))
async def ai_fallback(message: Message, bot: Bot):
    if message.text.startswith("/"):
        return
    try:
        await bot.send_chat_action(message.chat.id, "typing")
    except Exception:
        pass
    answer = await ask_ai(message.from_user.id, message.text)
    await message.answer(answer)
