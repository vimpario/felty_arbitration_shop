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
            "Карта: 2200 0000 0000 0004\n"
            "Годен до: 12/26\n"
            "CVC-код: 000\n"
        ),
        reply_markup=call.message.reply_markup
    )

@user_router.callback_query(F.data == "my_profile")
async def page_about(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Профиль")

    purchases = await UserDAO.get_purchase_statistics(session=session_without_commit, telegram_id=call.from_user.id)
    total_amount = purchases.get("total_amount", 0)
    total_purchases =purchases.get("total_purchases", 0)

    if total_purchases == 0:
        await call.message.answer(
            text="У вас пока нет покупок",
            reply_markup=main_user_kb(call.from_user.id)
        )
    else:
        text = (
            f"Ваш профиль: \n\n"
            f"Количество покупок: {total_purchases} "
            f"Общая сумма: {total_amount} "
            "Хотите просмотреть детали ваших покупок?"
        )
        await call.message.answer(
            text=text,
            reply_markup=purchases_kb()
        )

@user_router.callback_query(F.data == "purchases")
async def page_user_purchases(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Мои покупки")

    purchases = await UserDAO.get_purchased_products(session=session_without_commit, telegram_id=call.from_user.id)

    if not purchases:
        await call.message.edit_text(
            text=f"У вас пока нет покупок\nОткройте каталог и выберите что-нибудь интересное",
            reply_markup=main_user_kb(call.from_user.id)
        )
        return
    
    for purchase in purchases:
        product = purchase.product
        file_text = "Товар включает файл: " if product.file_id else "Товар не включает файл"

        product_text = (
            f"🛒 <b>Информация о вашем товаре:</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔹 <b>Название:</b> <i>{product.name}</i>\n"
            f"🔹 <b>Описание:</b>\n<i>{product.description}</i>\n"
            f"🔹 <b>Цена:</b> <b>{product.price} ₽</b>\n"
            f"🔹 <b>Закрытое описание:</b>\n<i>{product.hidden_content}</i>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{file_text}\n"
        )

        if product.file_id:
            await call.message.answer_document(
                document=product.file_id,
                caption=product_text,
            )
        else:
            await call.message.answer(
                text=product_text,
            )

    await call.message.answer(
        text="Спасибо за доверие",
        reply_markup=main_user_kb(call.from_user.id)
    )