import time
import asyncpg
import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import dp, db, bot
from data.config import ADMINS
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import ReplyKeyboardRemove


@dp.message_handler(commands=['poll'])
async def send_poll(message: types.Message):
    await message.reply_poll(
        question="Kim katta men yo sen?",
        is_anonymous=False,
        options=['men', 'sen', 'tori javob yo\'q'],
        correct_option_id=1,
        explanation="To'g'ri javob: men",
        type="quiz",
        close_date=time.time()+10
    )


@dp.poll_answer_handler()
async def get_poll_answer(poll: types.PollAnswer):
    await poll.bot.send_message(chat_id=poll.user.id, text=poll.poll_id)
    test = poll.option_ids
    if test == 1:
        await poll.bot.send_message(chat_id=poll.user.id, text="")
    answer = poll.values
    text = poll.bot
    print(test)
    print(answer)
    print(text)


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    logging.info(message)
    logging.info(f"{message.from_user.id=}")
    logging.info(f"{message.from_user.full_name=}")
    msg = f"Assalomu alaykum!\n" \
              f"Ball yeg'ib bizning konkursimizda g'alaba" \
              f"qozonishni istasangiz, quyidagi linkni bosing:\n" \
              f"https://t.me/ovoztoplavayut_bot?start={message.from_user.id}"
    share_inline = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ulashish", switch_inline_query=msg)]
        ]
    )
    # user ma'lumotlari olinmoqda
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    referral = message.get_args()
    url = message.from_user.get_mention(message.from_user.full_name, as_html=True)
    bot_username = (await bot.get_me()).username
    referral_link = "https://t.me/{bot_username}?start={telegram_id}".format(
        bot_username=bot_username,
        telegram_id=str(telegram_id)
    )

    if referral:
        if int(referral) == message.from_user.id:
            referral = None
    try:
        user = await db.add_user(
            full_name=full_name,
            username=username,
            telegram_id=telegram_id,
            # referral_link=referral_link,
            referral=referral,
        )
        # ADMINGA xabar beramiz
        count = await db.count_users()
        msg = f"{url} bazaga qo'shildi."
        await bot.send_message(chat_id=ADMINS[0], text=msg,)

    except asyncpg.exceptions.UniqueViolationError:
        user = await db.select_user(telegram_id=message.from_user.id)

    await message.answer(
        f"Botimizga xush kelibsiz!\n\n"
        f"Sizning referalingiz: {referral_link}\n"
        f"Balancingiz: {user[4]}",
        reply_markup=share_inline,
    )


@dp.message_handler(commands=['referral'])
async def send_referral(message: types.Message):
    bot_username = (await bot.get_me()).username
    telegram_id = message.from_user.id
    text = f"Sizning referral linkingiz:\n" \
           f"https://t.me/{bot_username}?start={telegram_id}".format(
        bot_username=bot_username,
        telegram_id=str(telegram_id)
    )
    await message.answer(text=text)
