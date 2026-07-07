from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.services.reviews_service import ReviewItem
from app.services.services_service import ServiceItem

ADMIN_SERVICE_PRICE_PREFIX = 'admin:price:'
ADMIN_SERVICE_DELETE_PREFIX = 'admin:delete:'
ADMIN_SERVICE_EDIT_PREFIX = 'admin:edit:'
ADMIN_SERVICE_EDIT_FIELD_PREFIX = 'admin:editfield:'
ADMIN_TEMPLATE_PREFIX = 'admin:setting:'
ADMIN_REVIEW_DELETE_PREFIX = 'admin:review:delete:'
ADMIN_REVIEW_ADD = 'admin:review:add'


def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='📋 Записи'), KeyboardButton(text='➕ Добавить услугу')],
            [KeyboardButton(text='✏️ Изменить услугу'), KeyboardButton(text='❌ Удалить услугу')],
            [KeyboardButton(text='💰 Изменить цену'), KeyboardButton(text='🕒 Свободные окна')],
            [KeyboardButton(text='⭐ Управление отзывами'), KeyboardButton(text='⚙️ Настройки')],
        ],
        resize_keyboard=True,
        input_field_placeholder='Выберите действие',
    )


def get_admin_services_keyboard(services: list[ServiceItem], prefix: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for service in services:
        builder.button(text=f'{service.title} ({service.price} ₽)', callback_data=f'{prefix}{service.id}')
    builder.adjust(1)
    return builder


def get_service_edit_fields_keyboard(service_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text='Название', callback_data=f'{ADMIN_SERVICE_EDIT_FIELD_PREFIX}{service_id}:title')
    builder.button(text='Описание', callback_data=f'{ADMIN_SERVICE_EDIT_FIELD_PREFIX}{service_id}:description')
    builder.button(text='Длительность', callback_data=f'{ADMIN_SERVICE_EDIT_FIELD_PREFIX}{service_id}:duration_minutes')
    builder.adjust(1)
    return builder


def get_template_settings_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text='Приветствие', callback_data=f'{ADMIN_TEMPLATE_PREFIX}welcome_text')
    builder.button(text='Портфолио', callback_data=f'{ADMIN_TEMPLATE_PREFIX}portfolio_text')
    builder.button(text='Адрес', callback_data=f'{ADMIN_TEMPLATE_PREFIX}address_text')
    builder.button(text='Контакты', callback_data=f'{ADMIN_TEMPLATE_PREFIX}contacts_text')
    builder.adjust(1)
    return builder


def get_reviews_management_keyboard(reviews: list[ReviewItem]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text='➕ Добавить отзыв', callback_data=ADMIN_REVIEW_ADD)
    for review in reviews:
        builder.button(text=f'Удалить отзыв #{review.id}', callback_data=f'{ADMIN_REVIEW_DELETE_PREFIX}{review.id}')
    builder.adjust(1)
    return builder
