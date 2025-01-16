from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, SuccessfulPayment
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from bot.config import bot, settings
from bot.dao.dao import UserDAO, CategoryDao, ProductDao, PurchaseDao
from bot.user.kbs import main_user_kb, catalog_kb, product_kb, get_product_buy_kb, product_navigation_kb, purchase_count_kb
from bot.user.schemas import TelegramIDModel, ProductCategoryIDModel, PaymentData
from unittest.mock import AsyncMock

catalog_router = Router()

from aiogram import Router, F
from aiogram.types import Message, SuccessfulPayment
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
catalog_router = Router()

@catalog_router.callback_query(F.data == "catalog")
async def page_catalog(call: CallbackQuery, session_without_commit: AsyncSession):
    catalog_data = await CategoryDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text="Выберите категорию товаров:",
        reply_markup=catalog_kb(catalog_data)
    )

@catalog_router.callback_query(F.data.startswith("category_"))
async def page_catalog_products(call: CallbackQuery, session_without_commit: AsyncSession):
    category_id = int(call.data.split("_")[-1])
    products_category = await ProductDao.find_all(session=session_without_commit,
                                                  filters=ProductCategoryIDModel(category_id=category_id, is_buyed=False))
    count_products = len(products_category)
    if count_products:
        await call.answer(f"В данной категории {count_products} товаров.")
        # for product in products_category:
        product_text = (
            f"📦 <b>Название товара:</b> {products_category[0].name}\n\n"
            f"💰 <b>Цена:</b> {products_category[0].price} руб.\n\n"
            f"📝 <b>Описание:</b>\n<i>{products_category[0].description}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        await call.message.answer(
            product_text,
            reply_markup=product_kb(products_category[0].id, products_category[0].price)
        )
        
    else:
        await call.answer("В данной категории нет товаров.")

@catalog_router.callback_query(F.data.startswith('buy_'))
async def initiate_purchase(call: CallbackQuery, state: FSMContext):
    logger.info(f"initiate_purchase call.data: {call.data}")
    _, product_id, price = call.data.split("_")
    msg = await call.message.answer(
        "Введите количество файлов, которые желаете купить:",
        reply_markup=purchase_count_kb()
    )
    
    await state.update_data(product_id=product_id, price=price, last_msg_id = msg.message_id)
    await state.set_state("waiting_quantity")
    logger.info(f"Received message: {msg.text}")
    logger.info(f"State: {await state.get_state()}")
    
@catalog_router.message(StateFilter("waiting_quantity"))
async def set_quantity(message: Message, state: FSMContext, session_with_commit: AsyncSession):
    state_data = await state.get_data()
    product_id = state_data.get("product_id")
    price = float(state_data.get("price"))
        
    try:
        logger.info(f"Message.text: {message.text}")
        quantity = int(message.text)
        if quantity <= 0:
            await message.answer("Количество должно быть больше нуля. Попробуйте снова.")
            return
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
        return

    total_price = price * quantity
    user_info = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDModel(telegram_id=message.from_user.id)
    )

    logger.info(f"Отправка счета с payload: {user_info.id}_{product_id}_{quantity}")
    await bot.send_invoice(
        chat_id=message.from_user.id,
        title="Оплата",
        description=f"Пожалуйста, завершите оплату на сумму {total_price} рублей, чтобы открыть доступ к выбранным товарам",
        payload=f"{user_info.id}_{product_id}_{quantity}",
        provider_token=settings.PROVIDER_TOKEN,
        currency="rub",
        prices=[LabeledPrice(label=f"Оплата {total_price}", amount=int(total_price * 100))],
        reply_markup=get_product_buy_kb(total_price)
    )

    await message.delete()
    await state.set_state("waiting_payment")
    logger.info(f"Состояние обновлено: {await state.get_state()}")


@catalog_router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@catalog_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT )
async def successful_payment(message: Message, state: FSMContext, session_with_commit: AsyncSession):
    payment_info = message.successful_payment
    logger.info(f"Payment_info {payment_info}")
    logger.info(f"payment_info.invoice_payload: {payment_info.invoice_payload}")
    user_id, product_id, quantity = payment_info.invoice_payload.split("_")
    logger.info(f"payment_info.invoice_payload: {payment_info.invoice_payload}")
    state_data = await state.get_data()
    quantity = int(quantity)
    logger.info(f"successful_payment quantity: {quantity}")
    product_data = await ProductDao.find_unpurchased_items(session=session_with_commit, limit=quantity)
    logger.info(f"Quantity after succ purchase: {quantity}")
    logger.info(f"Product data after succ purchase: {product_data}")

    for product in product_data[:quantity]:
        payment = PaymentData(
            user_id=int(user_id),
            payment_id=payment_info.telegram_payment_charge_id,
            price=payment_info.total_amount / 100,
            product_id=int(product.id)
        )
        await PurchaseDao.add(session=session_with_commit, values=payment)
        logger.info(f"Product name: {product.name}, Product ID: {product.id}")
        product.is_buyed = True
        session_with_commit.add(product) 
        for admin_id in settings.ADMIN_IDS:
            try:
                username = message.from_user.username
                user_info = f"@{username} ({message.from_user.id})" if username else f"с ID {message.from_user.id}"

                await bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f"Пользователь {user_info} купил {quantity} шт. товара <b>{product.name}</b> (ID: {product.id})"
                        f"на сумму <b>{payment_info.total_amount / 100} ₽</b>"
                    )
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления администраторам: {e}")

    

        file_text = "<b>Товар включает файлы:</b>" if product.file_id else "<b>Товар не включает файлы:</b>"
        product_text = (
            f"🎉 <b>Спасибо за покупку!</b>\n\n"
            f"🛒 <b>Информация о вашем товаре:</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔹 <b>Название:</b> <b>{product.name}</b>\n"
            f"🔹 <b>Описание:</b>\n<i>{product.description}</i>\n"
            f"🔹 <b>Цена:</b> <b>{product.price} ₽</b>\n"
            f"🔹 <b>Количество:</b> <b>{quantity} шт.</b>\n"
            f"🔹 <b>Общая стоимость:</b> <b>{payment_info.total_amount / 100} ₽</b>\n"
            f"{file_text}\n\n"
            f"ℹ️ <b>Информацию о всех ваших покупках вы можете найти в личном профиле.</b>"
        )

        if product.file_id:
            await message.answer_document(
                document=product.file_id,
                caption=product_text,
                reply_markup=main_user_kb(message.from_user.id)
            )
        else:
            await message.answer(
                text=product_text,
                reply_markup=main_user_kb(message.from_user.id)
            )
    
    await session_with_commit.commit() 
    await state.clear()
    logger.info(f"Состояние очищено для пользователя {message.from_user.id}")



