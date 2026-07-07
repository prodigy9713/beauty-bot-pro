from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.services.booking_service import TimeSlotItem, format_date_display
from app.services.services_service import ServiceItem

BACK_TO_MENU = 'back:menu'
BACK_TO_SERVICES = 'back:services'
BACK_TO_PRICE = 'back:price'
BOOKING_START_PREFIX = 'book:start:'
BOOKING_DATE_PREFIX = 'book:date:'
BOOKING_SLOT_PREFIX = 'book:slot:'
SERVICE_DETAILS_PREFIX = 'service:'
PRICE_DETAILS_PREFIX = 'price:'


def get_client_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='💅 Услуги'), KeyboardButton(text='💰 Прайс')],
            [KeyboardButton(text='📅 Записаться'), KeyboardButton(text='⭐ Отзывы')],
            [KeyboardButton(text='📸 Портфолио'), KeyboardButton(text='📍 Адрес')],
            [KeyboardButton(text='❓ FAQ'), KeyboardButton(text='📞 Связаться')],
        ],
        resize_keyboard=True,
        input_field_placeholder='Выберите раздел',
    )


def get_services_keyboard(services: list[ServiceItem]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for service in services:
        builder.button(text=service.title, callback_data=f'{SERVICE_DETAILS_PREFIX}{service.id}')
    builder.button(text='⬅️ Назад в меню', callback_data=BACK_TO_MENU)
    builder.adjust(1)
    return builder


def get_price_keyboard(services: list[ServiceItem]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for service in services:
        builder.button(text=f'{service.title} • {service.price} ₽', callback_data=f'{PRICE_DETAILS_PREFIX}{service.id}')
    builder.button(text='⬅️ Назад в меню', callback_data=BACK_TO_MENU)
    builder.adjust(1)
    return builder


def get_service_actions_keyboard(service_id: int, source: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text='📅 Записаться', callback_data=f'{BOOKING_START_PREFIX}{source}:{service_id}')

    back_callback = BACK_TO_SERVICES if source == 'services' else BACK_TO_PRICE
    back_text = '⬅️ Назад к услугам' if source == 'services' else '⬅️ Назад к прайсу'
    builder.button(text=back_text, callback_data=back_callback)
    builder.adjust(1)
    return builder


def get_booking_dates_keyboard(service_id: int, source: str, dates: list[str]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for date_iso in dates:
        builder.button(
            text=format_date_display(date_iso),
            callback_data=f'{BOOKING_DATE_PREFIX}{source}:{service_id}:{date_iso}',
        )
    builder.button(text='⬅️ Назад к услуге', callback_data=f'{SERVICE_DETAILS_PREFIX}{service_id}')
    builder.button(text='⬅️ Назад в меню', callback_data=BACK_TO_MENU)
    builder.adjust(1)
    return builder


def get_booking_slots_keyboard(service_id: int, source: str, date_iso: str, slots: list[TimeSlotItem]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for slot in slots:
        builder.button(
            text=slot.time,
            callback_data=f'{BOOKING_SLOT_PREFIX}{source}:{service_id}:{slot.id}',
        )
    builder.button(text='⬅️ Выбрать другую дату', callback_data=f'{BOOKING_START_PREFIX}{source}:{service_id}')
    builder.button(text='⬅️ Назад в меню', callback_data=BACK_TO_MENU)
    builder.adjust(2)
    return builder
