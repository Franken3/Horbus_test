from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.types import Message, CallbackQuery

from keyboards.inline.inline_kb import create_start_kb, create_subs_kb
from loader import dp
from utils.db_api import create_new_or_get_user, get_user_subscriptions, get_user_subscription_status, subscribe_user, \
    create_digest


@dp.message_handler(CommandStart())
async def bot_start_no_state(message: Message):
    user = await create_new_or_get_user(TgId=message.from_user.id,
                                        Name=message.from_user.full_name)
    reply_kb = create_start_kb(user.id)
    await message.answer('Добро пожаловать в меню', reply_markup=reply_kb)


@dp.callback_query_handler(Text(startswith='get_subs_'))
async def show_user_his_subs(call: CallbackQuery):
    user_id = int(call.data.split('_')[-1])
    subs = await get_user_subscription_status(user_id=user_id)
    reply_kb = create_subs_kb(user_id, subs)
    await call.message.edit_text('Доступные подписки:', reply_markup=reply_kb)


@dp.callback_query_handler(Text(startswith=('sub_', 'unsub_')))
async def handle_subscription(call: CallbackQuery):
    user_id = int(call.data.split('_')[-1])
    sub_id = int(call.data.split('_')[-2])
    sub_action = False if 'unsub_' in call.data else True

    await subscribe_user(user_id=user_id,
                         subscription_id=sub_id,
                         sub=sub_action)

    subs = await get_user_subscription_status(user_id=user_id)
    reply_kb = create_subs_kb(user_id, subs)
    await call.message.edit_reply_markup(reply_markup=reply_kb)

@dp.callback_query_handler(Text(startswith='create_digest_'))
async def create_and_send_digest(call: CallbackQuery):
    user_id = int(call.data.split('_')[-1])
    text = '<b>Ваш дайджест постов с популярностью выше 250:</b>\n\n'
    digest_text = await create_digest(user_id)
    if digest_text != '':
        text += digest_text
        await call.message.answer(text)
    else:
        await call.answer(show_alert=True, text='Постов нет, попробуйте выбрать другие подписки')