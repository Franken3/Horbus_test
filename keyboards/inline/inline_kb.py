from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_start_kb(user_id: int) -> InlineKeyboardMarkup:
    start_kb = InlineKeyboardMarkup()
    start_kb.add(InlineKeyboardButton('Выбрать подписки', callback_data=f'get_subs_{user_id}'),
                 InlineKeyboardButton('Сформировать дайджест', callback_data=f'create_digest_{user_id}'))
    return start_kb


def create_subs_kb(user_id: int, subs: List):
    subs_kb = InlineKeyboardMarkup(row_width=2)
    print(subs)
    for sub in subs:
        name, status, sub_id = sub[0], sub[1], sub[2]
        if status:
            call = f'unsub_{sub_id}_{user_id}'
        else:
            call = f'sub_{sub_id}_{user_id}'
        subs_kb.add(InlineKeyboardButton(name, callback_data=call))
    return subs_kb

