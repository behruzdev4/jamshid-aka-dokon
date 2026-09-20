from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot import database as db
from bot.config import ADMIN_IDS


class UserTrackingMiddleware(BaseMiddleware):
    """Har bir yangilanishda foydalanuvchini `users` jadvaliga yozib/yangilab boradi.
    Bu statistika (jami/faol foydalanuvchilar) va "hammaga reklama yuborish" uchun ishlatiladi."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is not None and not user.is_bot:
            try:
                await db.upsert_user(user.id, user.username, user.full_name)
            except Exception:
                pass
        return await handler(event, data)


class SubscriptionMiddleware(BaseMiddleware):
    """Agar admin majburiy obuna kanalini o'rnatgan bo'lsa, oddiy foydalanuvchilar
    o'sha kanalga obuna bo'lmaguncha botning asosiy funksiyalaridan foydalana olmaydi.
    Adminlar bu tekshiruvdan ozod qilinadi."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None or user.id in ADMIN_IDS:
            return await handler(event, data)

        channel = await db.get_setting("subscribe_channel")
        if not channel:
            return await handler(event, data)

        bot = data["bot"]
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user.id)
            subscribed = member.status in ("member", "administrator", "creator")
        except Exception:
            # Kanal ID/username noto'g'ri yoki bot kanalda admin emas — foydalanuvchini bloklamaymiz
            subscribed = True

        if subscribed:
            return await handler(event, data)

        from bot import keyboards as kb  # aylanma import'ning oldini olish uchun shu yerda

        await event.answer(
            "📢 Botdan foydalanish uchun avval quyidagi kanalga obuna bo'ling, "
            "so'ng \"✅ Tekshirish\" tugmasini bosing:",
            reply_markup=kb.subscribe_kb(channel),
        )
        return None
