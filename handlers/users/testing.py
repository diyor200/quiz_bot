import json
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from loader import dp, bot
from states.check_state import AnswerCheck
# from pprint import pprint as p

true_answer = []
response = requests.get("http://127.0.0.1:8000/api/question/random/")
json_data = json.loads(response.text)
count = len(json_data)
for j in range(len(json_data)):
    for i in json_data[j]['answer']:
        if i['is_correct']:
            true_answer.append(i['answer'])
count = len(true_answer)
print(true_answer)


@dp.message_handler(commands=['test'])
async def begin_test(message: types.Message, state: FSMContext):
    start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    start_keyboard.insert(KeyboardButton(text="start"))
    await message.answer("Sizga <code>random</code> tarzda bir qancha testlar yuboriladi.\n"
                         "Boshlash uchun <code>start</code> tugmasini bosing\n"
                         "Ixtiyoriy paytda yakunlash uchun <code>yakunlash</code> tugmasini bosing",
                         reply_markup=start_keyboard)
    # p(json_data)
    await state.set_data(
        {'user_answers': ',',
         'q_id': 0}
    )
    await AnswerCheck.question.set()


@dp.message_handler(state=AnswerCheck.question)
async def send_test(message: types.Message, state: FSMContext):
    data = await state.get_data()
    q_id = int(data.get("q_id"))
    user_answers = data.get("user_answers") + f"{message.text},"
    # print(user_answers)

    if q_id == count:
        await state.finish()
        l = user_answers.split(",")
        l = l[2:-1]
        num = 0
        # for i in true_answer:
        for j in l:
            if j in true_answer:
                num += 1
                # print(num)
        await message.answer(f"Test tugadi!\nSizning natijangiz: {num} ta", reply_markup=ReplyKeyboardRemove())
        await state.reset_data()
    else:
        keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        try:
            for i in json_data[q_id]['answer']:
                keyboard.insert(KeyboardButton(text=f"{i['answer']}"))
            await bot.send_message(chat_id=message.from_user.id, text=f"{json_data[q_id]['title']}",
                                   reply_markup=keyboard)
            await state.update_data(
                {
                    "q_id": q_id + 1,
                    'user_answers': user_answers
                },
            )

            await AnswerCheck.question.set()
        except:
            pass
