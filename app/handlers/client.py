from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.client_kb import (
    BACK_TO_MENU,
    BACK_TO_PRICE,
    BACK_TO_SERVICES,
    PRICE_DETAILS_PREFIX,
    SERVICE_DETAILS_PREFIX,
    get_client_menu_keyboard,
    get_price_keyboard,
    get_service_actions_keyboard,
    get_services_keyboard,
)
from app.services.reviews_service import format_reviews_message, get_visible_reviews
from app.services.services_service import (
    format_price_overview,
    format_service_card,
    format_services_overview,
    get_active_services,
    get_service_by_id,
)
from app.services.settings_service import get_setting
from config import Settings


client_router = Router()


@client_router.message(CommandStart())
async def cmd_start(message: Message, settings: Settings) -> None:
    await message.answer(get_setting(settings.database_path, 'welcome_text'), reply_markup=get_client_menu_keyboard())


@client_router.message(F.text == '💅 Услуги')
async def show_services(message: Message, settings: Settings) -> None:
    services = get_active_services(settings.database_path)
    await message.answer(format_services_overview(services), reply_markup=get_services_keyboard(services).as_markup())


@client_router.message(F.text == '💰 Прайс')
async def show_price(message: Message, settings: Settings) -> None:
    services = get_active_services(settings.database_path)
    await message.answer(format_price_overview(services), reply_markup=get_price_keyboard(services).as_markup())


@client_router.callback_query(F.data.startswith(SERVICE_DETAILS_PREFIX))
async def show_service_details(callback: CallbackQuery, settings: Settings) -> None:
    service_id = int(callback.data.removeprefix(SERVICE_DETAILS_PREFIX))
    service = get_service_by_id(settings.database_path, service_id)
    if service is None:
        await callback.answer('Услуга не найдена', show_alert=True)
        return
    await callback.message.edit_text(format_service_card(service), reply_markup=get_service_actions_keyboard(service.id, source='services').as_markup())
    await callback.answer()


@client_router.callback_query(F.data.startswith(PRICE_DETAILS_PREFIX))
async def show_price_details(callback: CallbackQuery, settings: Settings) -> None:
    service_id = int(callback.data.removeprefix(PRICE_DETAILS_PREFIX))
    service = get_service_by_id(settings.database_path, service_id)
    if service is None:
        await callback.answer('Услуга не найдена', show_alert=True)
        return
    await callback.message.edit_text(format_service_card(service), reply_markup=get_service_actions_keyboard(service.id, source='price').as_markup())
    await callback.answer()


@client_router.callback_query(F.data == BACK_TO_SERVICES)
async def back_to_services(callback: CallbackQuery, settings: Settings) -> None:
    services = get_active_services(settings.database_path)
    await callback.message.edit_text(format_services_overview(services), reply_markup=get_services_keyboard(services).as_markup())
    await callback.answer()


@client_router.callback_query(F.data == BACK_TO_PRICE)
async def back_to_price(callback: CallbackQuery, settings: Settings) -> None:
    services = get_active_services(settings.database_path)
    await callback.message.edit_text(format_price_overview(services), reply_markup=get_price_keyboard(services).as_markup())
    await callback.answer()


@client_router.callback_query(F.data == BACK_TO_MENU)
async def back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text('Вы вернулись в главное меню. Можно выбрать любой раздел на клавиатуре ниже.')
    await callback.message.answer('Главное меню снова перед вами.', reply_markup=get_client_menu_keyboard())
    await callback.answer()


@client_router.message(F.text == '⭐ Отзывы')
async def show_reviews(message: Message, settings: Settings) -> None:
    await message.answer(format_reviews_message(get_visible_reviews(settings.database_path)))


@client_router.message(F.text == '📸 Портфолио')
async def show_portfolio(message: Message, settings: Settings) -> None:
    await message.answer(get_setting(settings.database_path, 'portfolio_text'))


@client_router.message(F.text == '📍 Адрес')
async def show_address(message: Message, settings: Settings) -> None:
    await message.answer(get_setting(settings.database_path, 'address_text'))


@client_router.message(F.text == '📞 Связаться')
async def show_contacts(message: Message, settings: Settings) -> None:
    await message.answer(get_setting(settings.database_path, 'contacts_text'))
