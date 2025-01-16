from typing import List
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from bot.config import settings
from bot.dao.models import Category


def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Мои покупки", callback_data="my_profile")
    kb.button(text="🛍 Каталог", callback_data="catalog")
    kb.button(text="ℹ️ О магазине", callback_data="about")
    if user_id in settings.ADMIN_IDS:
        kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()

def product_navigation_kb(category_id: int, product_index: int, total_products: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    prev_index = (product_index -1) % total_products
    next_index = (product_index + 1) % total_products
    kb.button(text="<-", callback_data=f"prev_{category_id}_{prev_index}")
    kb.button(text=f"{product_index + 1}/{total_products}", callback_data="noop")
    kb.button(text="->", callback_data=f"next_{category_id}_{prev_index}")
    kb.adjust(1)
    return kb.as_markup()

def catalog_kb(catalog_data: List[Category]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in catalog_data:
        kb.button(text=category.category_name, callback_data=f"category_{category.id}")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2)
    return kb.as_markup()

def purchases_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 Смотреть покупки", callback_data="purchases")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()

def purchase_count_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="catalog")
    kb.adjust(1)
    return kb.as_markup()

def product_kb(product_id, price) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💸 Купить", callback_data=f"buy_{product_id}_{price}")
    kb.button(text="🛍 Назад", callback_data="catalog")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2)
    return kb.as_markup()

def get_product_buy_kb(price) -> InlineKeyboardMarkup:
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Оплатить {price}₽', pay=True)],
        [InlineKeyboardButton(text='Отменить', callback_data='home')]
    ])