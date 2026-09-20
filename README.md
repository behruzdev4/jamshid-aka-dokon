# Kompyuter Do'koni Telegram Bot (aiogram 3)

Kompyuter, ehtiyot qismlar, noutbuklar va h.k. sotuvchi do'kon uchun to'liq
Telegram bot: katalog, savatcha, buyurtma, PC yig'ish yordamchisi, FAQ va
admin panel.

## Imkoniyatlar

- 🛒 **Katalog** — kategoriyalar va mahsulotlar (nom, narx, rasm, tavsif)
- 🧺 **Savatcha** — mahsulot qo'shish/o'chirish
- ✅ **Buyurtma** — ism, telefon, manzil so'rab, admin(lar)ga va/yoki guruhga yuboradi
- 🖥 **PC yig'ish yordamchisi** — maqsad bo'yicha (gaming/ish/dizayn) tavsiya
- ❓ **Avto-FAQ** — yetkazib berish, to'lov, kafolat, ish vaqti, manzil
- 🛠 **Admin panel** (`/admin`) — reply-klaviatura orqali: katalog/mahsulot
  qo'shish va o'chirish, buyurtmalar, statistika, majburiy obuna kanali va
  reklama yuborish (faqat `ADMIN_IDS` ro'yxatidagilarga ko'rinadi)
- 📊 **Statistika** — oxirgi 30 kundagi buyurtmalar soni, jami va faol
  foydalanuvchilar soni
- 📢 **Majburiy obuna** — admin bitta kanal belgilaydi, foydalanuvchi o'sha
  kanalga obuna bo'lmaguncha botdan foydalana olmaydi
- 📣 **Reklama yuborish** — admin yuborgan har qanday xabar (matn/rasm/video)
  botga kirgan BARCHA foydalanuvchiga yuboriladi
- 🤖 **AI avto-javob** — OpenRouter orqali, do'kon katalogiga asoslangan javoblar

## 1. O'rnatish (lokal yoki serverda)

```bash
# Python 3.10+ talab qilinadi
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Sozlash

`.env.example` faylini nusxalab `.env` nomida saqlang:

```bash
cp .env.example .env
```

`.env` faylini oching va to'ldiring:

- `BOT_TOKEN` — @BotFather orqali yaratilgan bot tokeni
- `ADMIN_IDS` — sizning (va boshqa adminlarning) Telegram ID raqami.
  ID ni bilish uchun Telegram'da `@userinfobot` ga `/start` bosing.
- `ORDER_GROUP_ID` — (ixtiyoriy) buyurtmalar tushadigan guruh ID raqami
- `AI_API_KEY` — https://openrouter.ai saytidan olingan API kalit (AI avto-javob uchun)
- `AI_MODEL` — ishlatiladigan model nomi (standart: `openai/gpt-4o-mini`)

Barcha sozlama shu bitta `.env` faylida — token, admin ID va AI kaliti
boshqa hech qayerga qo'lda yozilmaydi, kod ularni shu yerdan o'qiydi.

## 3. Ishga tushirish (test uchun)

```bash
python3 main.py
```

Botga `/start` yozib tekshiring. Keyin `/admin` orqali (faqat ADMIN_IDS
ro'yxatidagilar uchun ishlaydi) kategoriya va mahsulotlar qo'shing.

## 4. Oracle serverda 24/7 ishlatish (systemd bilan)

1. Loyihani serverga yuklang (masalan `/home/ubuntu/telegram_bot` ga):

```bash
scp -r telegram_bot ubuntu@SERVER_IP:/home/ubuntu/
```

2. Serverga ulaning va sozlang:

```bash
ssh ubuntu@SERVER_IP
cd /home/ubuntu/telegram_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env   # BOT_TOKEN va ADMIN_IDS ni kiriting
```

3. `kompyuter_bot.service` faylini tekshiring — `WorkingDirectory`,
   `ExecStart` va `User` qatorlaridagi yo'l/foydalanuvchi nomini o'z
   serveringizga moslang, so'ng uni joylashtiring:

```bash
sudo cp kompyuter_bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kompyuter_bot
sudo systemctl start kompyuter_bot
```

4. Holatini va loglarini tekshirish:

```bash
sudo systemctl status kompyuter_bot
sudo journalctl -u kompyuter_bot -f
```

Endi bot server qayta yuklansa ham avtomatik ishga tushadi va yiqilib
qolsa avtomatik qayta ishga tushadi (`Restart=always`).

## 5. Ma'lumotlar bazasi

Bot SQLite (`bot_database.db`) fayli orqali ishlaydi — alohida server
kerak emas. Fayl birinchi ishga tushganda avtomatik yaratiladi.
Zaxira nusxa olish uchun shunchaki ushbu faylni nusxalab qo'ying.

## 6. Papka tuzilishi

```
telegram_bot/
├── main.py                  # Botni ishga tushiruvchi asosiy fayl
├── requirements.txt
├── .env.example
├── kompyuter_bot.service     # systemd uchun namuna
└── bot/
    ├── config.py             # Sozlamalar, FAQ matnlari, PC preset'lar
    ├── database.py           # SQLite bilan ishlash (aiosqlite)
    ├── keyboards.py          # Barcha tugmalar (inline/reply)
    ├── states.py             # FSM holatlari
    ├── middlewares.py        # Foydalanuvchi tracking + majburiy obuna tekshiruvi
    └── handlers/
        ├── user.py           # Mijozlar uchun funksiyalar
        └── admin.py          # Admin panel funksiyalari
```

## 7. AI avto-javob (OpenRouter)

Bot mijozning **istalgan oddiy savoliga** (menyu tugmalariga to'g'ri kelmagan
har qanday matnga) OpenRouter orqali, do'kon katalogi va aloqa
ma'lumotlariga moslashib javob beradi.

1. https://openrouter.ai saytida ro'yxatdan o'ting va API kalit oling.
2. `.env` fayliga qo'shing:
   ```
   AI_API_KEY=sizning_kalitingiz
   AI_MODEL=openai/gpt-4o-mini
   ```
   (Boshqa modellarni https://openrouter.ai/models sahifasidan tanlashingiz mumkin.)
3. Botni qayta ishga tushiring (`sudo systemctl restart kompyuter_bot`).

AI javoblari faqat **admin panel orqali qo'shilgan kategoriya/mahsulotlarga**
asoslanadi — o'zidan narx yoki mahsulot o'ylab topmaydi. Agar biror savolga
javob bera olmasa yoki xatolik chiqsa, mijozga operator bilan bog'lanish
tavsiya etiladi (bot hech qachon "xato" bilan to'xtab qolmaydi).

- `/reset` — foydalanuvchi AI bilan suhbat xotirasini tozalash uchun yozishi mumkin.
- `AI_API_KEY` bo'sh qoldirilsa, AI o'chiq holatda ishlaydi va shunchaki
  operatorga murojaat qilishni tavsiya qiluvchi xabar chiqadi — bot xato bermaydi.

## 8. Admin panel (`/admin`)

`/admin` yozganda (faqat `ADMIN_IDS` dagilarga) pastki menyuda quyidagi
tugmalar chiqadi:

- **📁 Katalog qo'shish / 🗑 Katalogni o'chirish** — kategoriya boshqarish
- **➕ Mahsulot qo'shish / 🗑 Mahsulotni o'chirish** — mahsulot boshqarish
- **📋 Barcha mahsulotlar** — to'liq ro'yxat
- **📦 Buyurtmalar** — so'nggi 15 ta buyurtma
- **📊 Statistika** — so'nggi 30 kundagi buyurtmalar, jami va faol foydalanuvchilar soni
- **📢 Obuna kanal qo'shish** — majburiy obuna kanalini o'rnatish (link yuboriladi,
  so'ng tasdiqlash/bekor qilish so'raladi). ⚠️ Bot o'sha kanalda **admin** bo'lishi
  shart, aks holda obunani tekshira olmaydi va hamma foydalanuvchiga ruxsat beradi.
- **📣 Reklama yuborish** — yuborgan xabaringiz (matn, rasm, video, hujjat va h.k.)
  botga hech bo'lmasa bir marta `/start` bosgan **barcha** foydalanuvchilarga yuboriladi
- **⬅️ Admin paneldan chiqish** — oddiy mijoz menyusiga qaytish

## Eslatma

Kanaldagi (`@optomkompyutersavdosi`) postlar formati turlicha bo'lgani
uchun, mahsulotlarni avtomatik "o'qib olish" ishonchsiz. Shu sabab admin
panel orqali qo'lda kiritish yechimi tanlandi — bu tezroq va xatosiz
ishlaydi. Mahsulotlarni `/admin` → "➕ Mahsulot qo'shish" orqali kiriting.
