from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from bot.dao.dao import UserDAO
from bot.user.kbs import main_user_kb, purchases_kb
from bot.user.schemas import TelegramIDModel, UserModel

user_router = Router()

@user_router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession):
    user_id = message.from_user.id
    user_info = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDModel(telegram_id=user_id)
    )

    if user_info:
        return await message.answer(
            f"👋 Привет, {message.from_user.full_name}! Выберите необходимое действие",
            reply_markup=main_user_kb(user_id)
        )

    values = UserModel(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await UserDAO.add(session=session_with_commit, values=values)
    await message.answer(f"🎉 <b>Благодарим за регистрацию!</b>. Теперь выберите необходимое действие.",
                         reply_markup=main_user_kb(user_id))
    
@user_router.callback_query(F.data == "home")
async def page_home(call: CallbackQuery):
    await call.answer("Главная страница")
    return await call.message.answer(
        f"👋 Привет, {call.from_user.full_name}! Выберите необходимое действие",
        reply_markup=main_user_kb(call.from_user.id)
    )

@user_router.callback_query(F.data == "about")
async def page_about(call: CallbackQuery):
    await call.answer("О магазине")
    await call.message.answer(
        text=(
            "Данные для тестовой оплаты:\n\n"
            "Карта: 1111 1111 1111 1026\n"
            "Годен до: 12/26\n"
            "CVC-код: 000\n"
        ),
        reply_markup=call.message.reply_markup
    )

