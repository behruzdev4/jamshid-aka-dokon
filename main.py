import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from bot.config import BOT_TOKEN, ADMIN_IDS
from bot.database import init_db
from bot.handlers import user, admin
from bot.middlewares import UserTrackingMiddleware, SubscriptionMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def setup_commands(bot: Bot):
    default_commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam"),
    ]
    await bot.set_my_commands(default_commands, scope=BotCommandScopeDefault())

    admin_commands = default_commands + [
        BotCommand(command="admin", description="Admin panel"),
        BotCommand(command="reset", description="AI suhbat xotirasini tozalash"),
    ]
    for admin_id in ADMIN_IDS:
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
        except Exception:
            pass


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi! .env faylida BOT_TOKEN ni kiriting.")

    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Har bir yangilanishda foydalanuvchini bazaga yozib boradi (statistika/reklama uchun)
    dp.update.outer_middleware(UserTrackingMiddleware())
    # Majburiy obuna tekshiruvi faqat oddiy xabarlarga (adminlar bundan ozod)
    dp.message.outer_middleware(SubscriptionMiddleware())

    # admin router birinchi bo'lishi kerak, chunki /admin va boshqa admin tugmalari ustuvor
    dp.include_router(admin.router)
    dp.include_router(user.router)

    await setup_commands(bot)

    logging.info("Bot ishga tushmoqda...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi.")
