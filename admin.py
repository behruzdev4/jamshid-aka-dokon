import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot import database as db
from bot import keyboards as kb
from bot.config import ADMIN_IDS
from bot.states import (
    AdminCategoryStates,
    AdminProductStates,
    AdminBroadcastStates,
    AdminChannelStates,
)

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🛠 <b>Admin panel</b>", reply_markup=kb.admin_menu_kb())


@router.message(F.text == "⬅️ Admin paneldan chiqish")
async def admin_exit(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Admin paneldan chiqdingiz.", reply_markup=kb.main_menu_kb())


# ---------------- Katalog (kategoriya) qo'shish ----------------

@router.message(F.text == "📁 Katalog qo'shish")
async def admin_add_category_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminCategoryStates.waiting_name)
    await message.answer("Yangi katalog (kategoriya) nomini kiriting:")


@router.message(AdminCategoryStates.waiting_name)
async def admin_add_category_save(message: Message, state: FSMContext):
    ok = await db.add_category(message.text.strip())
    if ok:
        await message.answer(f"✅ Katalog qo'shildi: {message.text.strip()}", reply_markup=kb.admin_menu_kb())
    else:
        await message.answer("⚠️ Bu nomdagi katalog allaqachon mavjud.", reply_markup=kb.admin_menu_kb())
    await state.clear()


# ---------------- Katalogni o'chirish ----------------

@router.message(F.text == "🗑 Katalogni o'chirish")
async def admin_del_category_list(message: Message):
    if not is_admin(message.from_user.id):
        return
    categories = await db.get_categories()
    if not categories:
        await message.answer("Kataloglar mavjud emas.")
        return
    await message.answer(
        "O'chirmoqchi bo'lgan katalogni tanlang (undagi mahsulotlar bilan birga o'chiriladi):",
        reply_markup=kb.admin_categories_kb(categories, "admin_delcat"),
    )


@router.callback_query(F.data.startswith("admin_delcat:"))
async def admin_del_category_confirm(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    category_id = int(callback.data.split(":")[1])
    await db.delete_category(category_id)
    await callback.message.answer("🗑 Katalog va uning mahsulotlari o'chirildi.")
    await callback.answer()


# ---------------- Mahsulot qo'shish ----------------

@router.message(F.text == "➕ Mahsulot qo'shish")
async def admin_add_product_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    categories = await db.get_categories()
    if not categories:
        await message.answer("Avval katalog (kategoriya) qo'shing.")
        return
    await state.set_state(AdminProductStates.choosing_category)
    await message.answer(
        "Mahsulot qaysi katalogga tegishli?",
        reply_markup=kb.admin_categories_kb(categories, "admin_prodcat"),
    )


@router.callback_query(AdminProductStates.choosing_category, F.data.startswith("admin_prodcat:"))
async def admin_add_product_category_chosen(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split(":")[1])
    await state.update_data(category_id=category_id)
    await state.set_state(AdminProductStates.waiting_name)
    await callback.message.answer("Mahsulot nomini kiriting:")
    await callback.answer()


@router.message(AdminProductStates.waiting_name)
async def admin_add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminProductStates.waiting_price)
    await message.answer("Narxini kiriting (masalan: 4 500 000 so'm yoki $350):")


@router.message(AdminProductStates.waiting_price)
async def admin_add_product_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text.strip())
    await state.set_state(AdminProductStates.waiting_description)
    await message.answer("Mahsulot tavsifini kiriting (texnik xususiyatlari va h.k.):")


@router.message(AdminProductStates.waiting_description)
async def admin_add_product_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AdminProductStates.waiting_photo)
    await message.answer(
        "Mahsulot rasmini yuboring (yoki rasmsiz davom eting):",
        reply_markup=kb.skip_photo_kb(),
    )


@router.message(AdminProductStates.waiting_photo, F.photo)
async def admin_add_product_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()
    product_id = await db.add_product(
        category_id=data["category_id"],
        name=data["name"],
        price=data["price"],
        description=data["description"],
        photo_file_id=photo_file_id,
    )
    await state.clear()
    await message.answer(f"✅ Mahsulot qo'shildi! ID: {product_id}", reply_markup=kb.admin_menu_kb())


@router.callback_query(AdminProductStates.waiting_photo, F.data == "skip_photo")
async def admin_add_product_skip_photo(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = await db.add_product(
        category_id=data["category_id"],
        name=data["name"],
        price=data["price"],
        description=data["description"],
        photo_file_id=None,
    )
    await state.clear()
    await callback.message.answer(f"✅ Mahsulot qo'shildi! ID: {product_id}", reply_markup=kb.admin_menu_kb())
    await callback.answer()


# ---------------- Mahsulotni o'chirish ----------------

@router.message(F.text == "🗑 Mahsulotni o'chirish")
async def admin_del_product_list(message: Message):
    if not is_admin(message.from_user.id):
        return
    products = await db.get_all_products()
    if not products:
        await message.answer("Mahsulotlar mavjud emas.")
        return
    await message.answer(
        "O'chirmoqchi bo'lgan mahsulotni tanlang:",
        reply_markup=kb.admin_products_delete_kb(products),
    )


@router.callback_query(F.data.startswith("admin_delprod:"))
async def admin_del_product_confirm(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    product_id = int(callback.data.split(":")[1])
    await db.delete_product(product_id)
    await callback.message.answer("🗑 Mahsulot o'chirildi.")
    await callback.answer()


# ---------------- Barcha mahsulotlar / buyurtmalar ----------------

@router.message(F.text == "📋 Barcha mahsulotlar")
async def admin_list_products(message: Message):
    if not is_admin(message.from_user.id):
        return
    products = await db.get_all_products()
    if not products:
        await message.answer("Mahsulotlar mavjud emas.")
        return
    text = "📋 <b>Barcha mahsulotlar:</b>\n\n"
    for p in products:
        text += f"#{p['id']} [{p['category_name']}] {p['name']} — {p['price']}\n"
    for chunk_start in range(0, len(text), 4000):
        await message.answer(text[chunk_start:chunk_start + 4000])


@router.message(F.text == "📦 Buyurtmalar")
async def admin_orders(message: Message):
    if not is_admin(message.from_user.id):
        return
    orders = await db.get_recent_orders(limit=15)
    if not orders:
        await message.answer("Buyurtmalar mavjud emas.")
        return
    for o in orders:
        text = (
            f"🧾 <b>Buyurtma #{o['id']}</b> ({o['status']})\n"
            f"👤 {o['full_name']} | 📞 {o['phone']}\n"
            f"📍 {o['address']}\n"
            f"🔗 @{o['username']}\n"
            f"🕒 {o['created_at']}\n\n"
            f"{o['items_text']}"
        )
        await message.answer(text)


# ---------------- Statistika ----------------

@router.message(F.text == "📊 Statistika")
async def admin_statistics(message: Message):
    if not is_admin(message.from_user.id):
        return
    total_users = await db.get_users_count()
    active_users = await db.get_active_users_count(30)
    orders_30 = await db.get_orders_count(30)
    text = (
        "📊 <b>Statistika (oxirgi 30 kun)</b>\n\n"
        f"🛒 Buyurtmalar soni: {orders_30}\n"
        f"👤 Jami botga kirgan foydalanuvchilar: {total_users}\n"
        f"🟢 Faol foydalanuvchilar (oxirgi 30 kun): {active_users}"
    )
    await message.answer(text)


# ---------------- Obuna kanal qo'shish (majburiy obuna) ----------------

@router.message(F.text == "📢 Obuna kanal qo'shish")
async def admin_add_channel_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminChannelStates.waiting_link)
    await message.answer(
        "Kanal username yoki linkini yuboring (masalan: @mychannel yoki https://t.me/mychannel).\n\n"
        "⚠️ Bot o'sha kanalda ADMIN bo'lishi shart, aks holda obunani tekshira olmaydi."
    )


@router.message(AdminChannelStates.waiting_link)
async def admin_add_channel_input(message: Message, state: FSMContext):
    channel = message.text.strip()
    await state.update_data(channel=channel)
    await message.answer(
        f"Quyidagi kanalni majburiy obuna sifatida o'rnatishni tasdiqlaysizmi?\n\n<b>{channel}</b>",
        reply_markup=kb.confirm_channel_kb(),
    )


@router.callback_query(F.data == "channel_confirm")
async def admin_add_channel_confirm(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    data = await state.get_data()
    channel = data.get("channel")
    await state.clear()
    if not channel:
        await callback.answer("Xatolik: kanal topilmadi, qaytadan urinib ko'ring.", show_alert=True)
        return
    await db.set_setting("subscribe_channel", channel)
    await callback.message.edit_text(f"✅ Majburiy obuna kanali o'rnatildi: {channel}")
    await callback.answer()


@router.callback_query(F.data == "channel_cancel")
async def admin_add_channel_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()


# ---------------- Reklama yuborish (hammaga) ----------------

@router.message(F.text == "📣 Reklama yuborish")
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminBroadcastStates.waiting_message)
    await message.answer(
        "Yubormoqchi bo'lgan reklama xabarini yuboring — matn, rasm, video yoki boshqa "
        "istalgan turdagi xabar bo'lishi mumkin. U botga kirgan HAMMA foydalanuvchiga yuboriladi."
    )


@router.message(AdminBroadcastStates.waiting_message)
async def broadcast_send(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user_ids = await db.get_all_user_ids()
    sent = 0
    failed = 0
    await message.answer(f"⏳ Yuborilmoqda... ({len(user_ids)} ta foydalanuvchi)")
    for uid in user_ids:
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # Telegram flood-limitidan saqlanish uchun
    await message.answer(
        f"✅ Reklama {sent} ta foydalanuvchiga yuborildi.\n❌ {failed} ta foydalanuvchiga yetib bormadi.",
        reply_markup=kb.admin_menu_kb(),
    )
