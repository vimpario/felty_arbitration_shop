from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from bot.config import bot, settings
from bot.dao.dao import UserDAO, CategoryDao, ProductDao, PurchaseDao
from bot.user.kbs import main_user_kb, catalog_kb, product_kb, get_product_buy_kb
from bot.user.schemas import TelegramIDModel, ProductCategoryIDModel, PaymentData

catalog_router = Router()

@catalog_router.callback_query(F.data == "catalog")
async def page_catalog(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Загрузка каталога...")
    catalog_data = await CategoryDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text="Выберите категорию товаров:",
        reply_markup=catalog_kb(catalog_data)
    )

@catalog_router.callback_query(F.data.startswith("category_"))
async def page_catalog_products(call: CallbackQuery, session_without_commit: AsyncSession):
    category_id = int(call.data.split("_")[-1])
    products_category = await ProductDao.find_all(session=session_without_commit,
                                                  filters=ProductCategoryIDModel(category_id=category_id))
    count_products = len(products_category)
    if count_products:
        await call.answer(f"В данной категории {count_products} товаров.")
        for product in products_category:
            product_text = (
                f"📦 <b>Название товара:</b> {product.name}\n\n"
                f"💰 <b>Цена:</b> {product.price} руб.\n\n"
                f"📝 <b>Описание:</b>\n<i>{product.description}</i>\n\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            await call.message.answer(
                product_text,
                reply_markup=product_kb(product.id, product.price)
            )
    else:
        await call.answer("В данной категории нет товаров.")

