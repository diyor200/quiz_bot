from aiogram.dispatcher.filters.state import State, StatesGroup


class AnswerCheck(StatesGroup):
    question = State()
    answer = State()
