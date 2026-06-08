import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = "8050290456:AAEtLMEGkR9YnPeP_LeyQEBjkC0Gm4p2q8g"
ADMIN_ID = 7474852341
import os

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CARD_NUMBER = os.getenv("CARD_NUMBER")
CARD_NAME = os.getenv("CARD_NAME")
CARD_NUMBER = "6219-8618-0856-4438"
CARD_NAME = "فرحان نصرتی"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# پلن‌ها
PLANS = {
    "p1": ("20 گیگ 1 ماهه", 350000),
    "p2": ("40 گیگ 1 ماهه", 450000),
    "p3": ("50 گیگ 1 ماهه", 650000),
}

orders = {}

# ---------------- STATES ----------------
class Order(StatesGroup):
    name = State()
    plan = State()
    receipt = State()
    admin_link = State()

# ---------------- START ----------------
@dp.message(F.text == "/start")
async def start(msg: Message):
    await msg.answer_sticker("CAACAgIAAxkBAAEB...")  # استیکر خوش‌آمد

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 شروع خرید VPN", callback_data="buy")]
    ])

    await msg.answer(
        "👋 به فروشگاه VPN خوش آمدی\n\nبرای شروع روی دکمه زیر بزن 👇",
        reply_markup=kb
    )

# ---------------- BUY ----------------
@dp.callback_query(F.data == "buy")
async def buy(call: CallbackQuery, state: FSMContext):
    await call.message.answer_sticker("CAACAgIAAxkBAAEB...")  # shopping

    await state.set_state(Order.name)
    await call.message.answer("✍️ اسم خودتو وارد کن:")

# ---------------- NAME ----------------
@dp.message(Order.name)
async def get_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{PLANS['p1'][0]} - 350K", callback_data="p1")],
        [InlineKeyboardButton(text=f"{PLANS['p2'][0]} - 450K", callback_data="p2")],
        [InlineKeyboardButton(text=f"{PLANS['p3'][0]} - 650K", callback_data="p3")]
    ])

    await msg.answer("📦 پلن مورد نظر رو انتخاب کن 👇", reply_markup=kb)
    await state.set_state(Order.plan)

# ---------------- PLAN ----------------
@dp.callback_query(Order.plan)
async def choose_plan(call: CallbackQuery, state: FSMContext):
    await call.message.answer_sticker("CAACAgIAAxkBAAEB...")  # payment

    plan = call.data
    data = await state.get_data()

    orders[call.from_user.id] = {
        "name": data["name"],
        "plan": plan
    }

    price = PLANS[plan][1]

    await call.message.answer(
f"""
🏦 پرداخت کارت به کارت

💰 مبلغ: {price} تومان

💳 کارت: {CARD_NUMBER}
👤 نام: {CARD_NAME}

📌 بعد از پرداخت رسید ارسال کن
"""
    )

    await state.set_state(Order.receipt)

# ---------------- RECEIPT ----------------
@dp.message(Order.receipt)
async def receipt(msg: Message, state: FSMContext):
    user_id = msg.from_user.id

    await msg.answer_sticker("CAACAgIAAxkBAAEB...")  # waiting

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏳ در حال بررسی پرداخت...", callback_data="wait")]
    ])

    await msg.answer("⏳ رسید دریافت شد و در حال بررسی است...", reply_markup=kb)

    # ارسال به ادمین
    order = orders.get(user_id)

    kb_admin = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تایید", callback_data=f"ok_{user_id}"),
            InlineKeyboardButton(text="❌ رد", callback_data=f"no_{user_id}")
        ]
    ])

    await bot.send_message(
        ADMIN_ID,
        f"""
🧾 سفارش جدید

👤 اسم: {order['name']}
📦 پلن: {order['plan']}
🆔 کاربر: @{msg.from_user.username}
""",
        reply_markup=kb_admin
    )

    if msg.photo:
        await bot.send_photo(ADMIN_ID, msg.photo[-1].file_id)

# ---------------- ADMIN APPROVE ----------------
@dp.callback_query(F.data.startswith("ok_"))
async def approve(call: CallbackQuery, state: FSMContext):
    user_id = int(call.data.split("_")[1])

    await state.update_data(target=user_id)

    await call.message.answer("🔗 لینک اشتراک رو بفرست:")
    await state.set_state(Order.admin_link)

# ---------------- ADMIN REJECT ----------------
@dp.callback_query(F.data.startswith("no_"))
async def reject(call: CallbackQuery):
    user_id = int(call.data.split("_")[1])

    await bot.send_sticker(user_id, "CAACAgIAAxkBAAEB...")  # fail
    await bot.send_message(user_id, "❌ پرداخت شما تایید نشد")

    await call.message.answer("رد شد ❌")

# ---------------- SEND LINK ----------------
@dp.message(Order.admin_link)
async def send_link(msg: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["target"]

    link = msg.text

    await bot.send_message(
        user_id,
f"""
🎉 پرداخت تایید شد!

🚀 اشتراک VPN شما آماده است

🔗 لینک:
{link}

😎 از اینترنت آزاد لذت ببر
"""
    )

    await msg.answer("✅ ارسال شد")
    await state.clear()

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())