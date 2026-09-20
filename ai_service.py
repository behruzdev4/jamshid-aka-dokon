import asyncio
import logging

import aiohttp

from bot import database as db
from bot.config import (
    AI_API_KEY,
    AI_MODEL,
    SHOP_NAME,
    CONTACT_PHONES,
    CONTACT_TELEGRAM,
    CHANNEL_LINK,
    AI_HISTORY_LIMIT,
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Foydalanuvchi bo'yicha oxirgi xabarlar (oddiy operativ xotira, RAM'da saqlanadi)
_user_history: dict[int, list[dict]] = {}

FALLBACK_ANSWER = (
    "🤖 Kechirasiz, hozir AI yordamchi javob bera olmadi.\n"
    f"Operator bilan bog'laning: {', '.join(CONTACT_TELEGRAM)} yoki {', '.join(CONTACT_PHONES)}"
)


async def build_system_prompt() -> str:
    """Do'kon katalogi va aloqa ma'lumotlariga asoslangan tizim ko'rsatmasini yasaydi."""
    categories = await db.get_categories()
    lines = []
    for cat in categories:
        products = await db.get_products_by_category(cat["id"])
        if products:
            prod_list = ", ".join(f"{p['name']} — {p['price']}" for p in products[:20])
        else:
            prod_list = "hozircha mahsulot qo'shilmagan"
        lines.append(f"• {cat['name']}: {prod_list}")
    catalog_text = "\n".join(lines) if lines else "Hozircha katalogda kategoriyalar yo'q."

    prompt = f"""Sen "{SHOP_NAME}" nomli kompyuter, noutbuk, ehtiyot qismlar va gaming\
 aksessuarlar sotuvchi do'konning Telegram botidagi AI yordamchisisan.

DO'KON HAQIDA:
- Kanal: {CHANNEL_LINK}
- Telefon: {', '.join(CONTACT_PHONES)}
- Telegram operatorlar: {', '.join(CONTACT_TELEGRAM)}
- Yetkazib berish: O'zbekiston bo'ylab
- Kafolat: mahsulot turiga qarab beriladi

HOZIRGI KATALOG (kategoriya: mahsulotlar va narxlari):
{catalog_text}

QOIDALAR:
1. Faqat o'zbek tilida, qisqa, do'stona va aniq javob ber.
2. Faqat kompyuter texnikasi, ehtiyot qismlar va shu do'kon xizmatlariga oid savollarga javob ber.
3. Narx va mavjudlik haqida FAQAT yuqoridagi katalogdagi ma'lumotdan foydalan. Agar mahsulot\
 katalogda yo'q bo'lsa, "hozircha katalogda yo'q, operator bilan tekshiring" deb javob ber — hech\
 qachon narxni o'zingdan o'ylab topma.
4. Aniq buyurtma berish uchun foydalanuvchini botdagi "🛒 Katalog" tugmasidan foydalanishga yoki\
 operator bilan bog'lanishga yo'llang.
5. Agar savol do'konga aloqador bo'lmasa, muloyimlik bilan mavzuni do'kon xizmatlariga qaytar.
6. Javoblaring qisqa bo'lsin (odatda 2-5 gap), ortiqcha cho'zma."""
    return prompt


def _get_history(user_id: int) -> list[dict]:
    return _user_history.setdefault(user_id, [])


def _append_history(user_id: int, role: str, text: str):
    history = _get_history(user_id)
    history.append({"role": role, "content": text})
    if len(history) > AI_HISTORY_LIMIT:
        del history[: len(history) - AI_HISTORY_LIMIT]


def reset_history(user_id: int):
    _user_history.pop(user_id, None)


async def ask_ai(user_id: int, user_message: str) -> str:
    if not AI_API_KEY:
        return (
            "🤖 AI yordamchi hali sozlanmagan. Admin AI_API_KEY ni `.env` fayliga "
            "qo'shishi kerak. Hozircha savolingiz uchun operatorga yozing: "
            f"{', '.join(CONTACT_TELEGRAM)}"
        )

    system_prompt = await build_system_prompt()
    history = _get_history(user_id)

    messages = (
        [{"role": "system", "content": system_prompt}]
        + history
        + [{"role": "user", "content": user_message}]
    )

    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 500,
    }
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
        # OpenRouter tavsiya qiladigan ixtiyoriy sarlavhalar (statistika/reyting uchun)
        "HTTP-Referer": CHANNEL_LINK,
        "X-Title": SHOP_NAME,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                OPENROUTER_URL, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=25)
            ) as resp:
                data = await resp.json()
                if resp.status != 200:
                    err = data.get("error", {}).get("message", "Noma'lum xatolik")
                    logging.error("OpenRouter API xatosi: %s", err)
                    return FALLBACK_ANSWER

                choices = data.get("choices", [])
                if not choices:
                    return FALLBACK_ANSWER

                answer = (choices[0].get("message", {}).get("content") or "").strip()
                if not answer:
                    return FALLBACK_ANSWER

                _append_history(user_id, "user", user_message)
                _append_history(user_id, "assistant", answer)
                return answer

    except asyncio.TimeoutError:
        logging.error("OpenRouter API vaqt tugadi (timeout)")
        return "⌛️ AI javob berish vaqti tugadi. Birozdan so'ng qayta urinib ko'ring."
    except aiohttp.ClientError as e:
        logging.error("OpenRouter API tarmoq xatosi: %s", e)
        return FALLBACK_ANSWER
    except Exception as e:
        logging.exception("OpenRouter API kutilmagan xatolik: %s", e)
        return FALLBACK_ANSWER
