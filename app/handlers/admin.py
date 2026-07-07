from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.admin_kb import (
    ADMIN_REVIEW_ADD,
    ADMIN_REVIEW_DELETE_PREFIX,
    ADMIN_SERVICE_DELETE_PREFIX,
    ADMIN_SERVICE_EDIT_FIELD_PREFIX,
    ADMIN_SERVICE_EDIT_PREFIX,
    ADMIN_SERVICE_PRICE_PREFIX,
    ADMIN_TEMPLATE_PREFIX,
    get_admin_menu_keyboard,
    get_admin_services_keyboard,
    get_reviews_management_keyboard,
    get_service_edit_fields_keyboard,
    get_template_settings_keyboard,
)
from app.services.booking_service import create_time_slots, format_appointments_message, get_upcoming_appointments
from app.services.reviews_service import add_review, format_admin_reviews_message, get_visible_reviews, hide_review
from app.services.services_service import (
    create_service,
    deactivate_service,
    format_admin_services,
    get_active_services,
    get_service_by_id,
    update_service_field,
    update_service_price,
)
from app.services.settings_service import get_all_template_settings, get_setting, update_setting
from app.states.admin_states import (
    AddReviewStates,
    AddServiceStates,
    AddSlotsStates,
    EditServiceStates,
    UpdatePriceStates,
    UpdateTemplateStates,
)
from config import Settings


admin_router = Router()


def _is_admin_user(user_id: int | None, settings: Settings) -> bool:
    return user_id is not None and user_id == settings.admin_id


def _is_admin_message(message: Message, settings: Settings) -> bool:
    return message.from_user is not None and message.from_user.id == settings.admin_id


@admin_router.message(Command('admin'))
async def cmd_admin(message: Message, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        await message.answer('У вас нет доступа к админ-меню.')
        return
    await message.answer(
        'Админ-панель BeautyBot Pro. Выберите нужный раздел.',
        reply_markup=get_admin_menu_keyboard(),
    )


@admin_router.message(F.text == '📋 Записи')
async def show_appointments(message: Message, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    appointments = get_upcoming_appointments(settings.database_path)
    await message.answer(format_appointments_message(appointments))


@admin_router.message(F.text == '🕒 Свободные окна')
async def start_add_slots(message: Message, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_message(message, settings):
        return
    await state.set_state(AddSlotsStates.waiting_date)
    await message.answer('Добавляем свободные окна.\n\nШаг 1 из 4: отправьте дату в формате ДД.ММ.ГГГГ, например 10.07.2026')


@admin_router.message(AddSlotsStates.waiting_date)
async def receive_slot_date(message: Message, state: FSMContext, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    await state.update_data(date_text=(message.text or '').strip())
    await state.set_state(AddSlotsStates.waiting_start_time)
    await message.answer('Шаг 2 из 4: укажите время начала, например 10:00')


@admin_router.message(AddSlotsStates.waiting_start_time)
async def receive_slot_start(message: Message, state: FSMContext, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    await state.update_data(start_time=(message.text or '').strip())
    await state.set_state(AddSlotsStates.waiting_end_time)
    await message.answer('Шаг 3 из 4: укажите время окончания, например 18:00')


@admin_router.message(AddSlotsStates.waiting_end_time)
async def receive_slot_end(message: Message, state: FSMContext, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    await state.update_data(end_time=(message.text or '').strip())
    await state.set_state(AddSlotsStates.waiting_step)
    await message.answer('Шаг 4 из 4: укажите шаг записи в минутах, например 30, 60 или 90')


@admin_router.message(AddSlotsStates.waiting_step)
async def receive_slot_step(message: Message, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_message(message, settings):
        return
    step_text = (message.text or '').strip()
    if not step_text.isdigit():
        await message.answer('Шаг должен быть числом. Например: 30')
        return
    data = await state.get_data()
    try:
        created_count, skipped_count = create_time_slots(
            database_path=settings.database_path,
            date_text=str(data["date_text"]),
            start_time_text=str(data["start_time"]),
            end_time_text=str(data["end_time"]),
            step_minutes=int(step_text),
        )
    except ValueError as exc:
        await message.answer(f'Не получилось создать окна: {exc}')
        return
    await state.clear()
    await message.answer('Готово. Свободные окна обновлены.\n\n' f'Создано слотов: {created_count}\n' f'Пропущено дублей: {skipped_count}')


@admin_router.message(F.text == '➕ Добавить услугу')
async def start_add_service(message: Message, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_message(message, settings):
        return
    await state.set_state(AddServiceStates.waiting_title)
    await message.answer('Добавляем новую услугу. Шаг 1 из 4: отправьте название услуги.')


@admin_router.message(AddServiceStates.waiting_title)
async def receive_service_title(message: Message, state: FSMContext, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    await state.update_data(title=(message.text or '').strip())
    await state.set_state(AddServiceStates.waiting_description)
    await message.answer('Шаг 2 из 4: отправьте описание услуги.')


@admin_router.message(AddServiceStates.waiting_description)
async def receive_service_description(message: Message, state: FSMContext, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    await state.update_data(description=(message.text or '').strip())
    await state.set_state(AddServiceStates.waiting_price)
    await message.answer('Шаг 3 из 4: отправьте цену числом, например 2500')


@admin_router.message(AddServiceStates.waiting_price)
async def receive_service_price(message: Message, state: FSMContext, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    price_text = (message.text or '').strip()
    if not price_text.isdigit():
        await message.answer('Цена должна быть числом. Например: 2500')
        return
    await state.update_data(price=int(price_text))
    await state.set_state(AddServiceStates.waiting_duration)
    await message.answer('Шаг 4 из 4: отправьте длительность в минутах, например 90')


@admin_router.message(AddServiceStates.waiting_duration)
async def receive_service_duration(message: Message, state: FSMContext, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    duration_text = (message.text or '').strip()
    if not duration_text.isdigit():
        await message.answer('Длительность должна быть числом минут. Например: 90')
        return
    data = await state.get_data()
    create_service(settings.database_path, str(data["title"]), str(data["description"]), int(data["price"]), int(duration_text))
    await state.clear()
    await message.answer('Услуга добавлена.')


@admin_router.message(F.text == '💰 Изменить цену')
async def start_change_price(message: Message, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_message(message, settings):
        return
    services = get_active_services(settings.database_path)
    await state.clear()
    await message.answer(format_admin_services(services), reply_markup=get_admin_services_keyboard(services, ADMIN_SERVICE_PRICE_PREFIX).as_markup())


@admin_router.callback_query(F.data.startswith(ADMIN_SERVICE_PRICE_PREFIX))
async def choose_service_for_price(callback: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_user(callback.from_user.id if callback.from_user else None, settings):
        return
    service_id = int(callback.data.removeprefix(ADMIN_SERVICE_PRICE_PREFIX))
    service = get_service_by_id(settings.database_path, service_id)
    if service is None:
        await callback.answer('Услуга не найдена', show_alert=True)
        return
    await state.update_data(service_id=service_id)
    await state.set_state(UpdatePriceStates.waiting_price)
    await callback.message.answer(f'Текущая цена услуги «{service.title}» - {service.price} ₽. Отправьте новую цену числом.')
    await callback.answer()


@admin_router.message(UpdatePriceStates.waiting_price)
async def receive_new_price(message: Message, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_message(message, settings):
        return
    price_text = (message.text or '').strip()
    if not price_text.isdigit():
        await message.answer('Цена должна быть числом. Например: 3000')
        return
    data = await state.get_data()
    update_service_price(settings.database_path, int(data["service_id"]), int(price_text))
    await state.clear()
    await message.answer('Цена обновлена.')


@admin_router.message(F.text == '❌ Удалить услугу')
async def start_delete_service(message: Message, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    services = get_active_services(settings.database_path)
    await message.answer('Выберите услугу, которую нужно скрыть из каталога.', reply_markup=get_admin_services_keyboard(services, ADMIN_SERVICE_DELETE_PREFIX).as_markup())


@admin_router.callback_query(F.data.startswith(ADMIN_SERVICE_DELETE_PREFIX))
async def delete_service_callback(callback: CallbackQuery, settings: Settings) -> None:
    if not _is_admin_user(callback.from_user.id if callback.from_user else None, settings):
        return
    service_id = int(callback.data.removeprefix(ADMIN_SERVICE_DELETE_PREFIX))
    service = get_service_by_id(settings.database_path, service_id)
    if service is None:
        await callback.answer('Услуга не найдена', show_alert=True)
        return
    deactivate_service(settings.database_path, service_id)
    await callback.message.answer(f'Услуга «{service.title}» скрыта из каталога.')
    await callback.answer()


@admin_router.message(F.text == '✏️ Изменить услугу')
async def start_edit_service(message: Message, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    services = get_active_services(settings.database_path)
    await message.answer('Выберите услугу для редактирования.', reply_markup=get_admin_services_keyboard(services, ADMIN_SERVICE_EDIT_PREFIX).as_markup())


@admin_router.callback_query(F.data.startswith(ADMIN_SERVICE_EDIT_PREFIX))
async def choose_service_for_edit(callback: CallbackQuery, settings: Settings) -> None:
    if not _is_admin_user(callback.from_user.id if callback.from_user else None, settings):
        return
    service_id = int(callback.data.removeprefix(ADMIN_SERVICE_EDIT_PREFIX))
    service = get_service_by_id(settings.database_path, service_id)
    if service is None:
        await callback.answer('Услуга не найдена', show_alert=True)
        return
    await callback.message.answer(f'Что изменить в услуге «{service.title}»?', reply_markup=get_service_edit_fields_keyboard(service_id).as_markup())
    await callback.answer()


@admin_router.callback_query(F.data.startswith(ADMIN_SERVICE_EDIT_FIELD_PREFIX))
async def choose_edit_field(callback: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_user(callback.from_user.id if callback.from_user else None, settings):
        return
    payload = callback.data.removeprefix(ADMIN_SERVICE_EDIT_FIELD_PREFIX)
    service_id_text, field_name = payload.split(':', maxsplit=1)
    service_id = int(service_id_text)
    service = get_service_by_id(settings.database_path, service_id)
    if service is None:
        await callback.answer('Услуга не найдена', show_alert=True)
        return
    await state.update_data(service_id=service_id, field_name=field_name)
    await state.set_state(EditServiceStates.waiting_value)
    prompts = {
        'title': 'Отправьте новое название услуги.',
        'description': 'Отправьте новое описание услуги.',
        'duration_minutes': 'Отправьте новую длительность в минутах, например 120.',
    }
    await callback.message.answer(prompts[field_name])
    await callback.answer()


@admin_router.message(EditServiceStates.waiting_value)
async def receive_edited_service_value(message: Message, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_message(message, settings):
        return
    data = await state.get_data()
    field_name = str(data["field_name"])
    raw_value = (message.text or '').strip()
    if field_name == "duration_minutes":
        if not raw_value.isdigit():
            await message.answer('Длительность должна быть числом минут.')
            return
        value: str | int = int(raw_value)
    else:
        value = raw_value
    update_service_field(settings.database_path, int(data["service_id"]), field_name, value)
    await state.clear()
    await message.answer('Услуга обновлена.')


@admin_router.message(F.text == '⚙️ Настройки')
async def show_template_settings(message: Message, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    current = get_all_template_settings(settings.database_path)
    preview = [
        'Что хотите изменить в шаблоне?',
        '',
        f'Приветствие: {current["welcome_text"][:40]}...',
        f'Портфолио: {current["portfolio_text"][:40]}...',
        f'Адрес: {current["address_text"][:40]}...',
        f'FAQ: {current["faq_text"][:40]}...',
        f'Контакты: {current["contacts_text"][:40]}...',
    ]
    await message.answer('\n'.join(preview), reply_markup=get_template_settings_keyboard().as_markup())


@admin_router.callback_query(F.data.startswith(ADMIN_TEMPLATE_PREFIX))
async def choose_template_setting(callback: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_user(callback.from_user.id if callback.from_user else None, settings):
        return
    setting_key = callback.data.removeprefix(ADMIN_TEMPLATE_PREFIX)
    current_value = get_setting(settings.database_path, setting_key)
    labels = {
        'welcome_text': 'приветствие',
        'portfolio_text': 'портфолио',
        'address_text': 'адрес',
        'faq_text': 'FAQ',
        'contacts_text': 'контакты',
    }
    await state.update_data(setting_key=setting_key)
    await state.set_state(UpdateTemplateStates.waiting_value)
    await callback.message.answer(f'Текущее значение для «{labels[setting_key]}»:\n\n{current_value}\n\nОтправьте новый текст целиком.')
    await callback.answer()


@admin_router.message(UpdateTemplateStates.waiting_value)
async def receive_template_value(message: Message, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_message(message, settings):
        return
    data = await state.get_data()
    new_value = (message.text or '').strip()
    update_setting(settings.database_path, str(data["setting_key"]), new_value)
    await state.clear()
    await message.answer('Настройка обновлена.')


@admin_router.message(F.text == '⭐ Управление отзывами')
async def reviews_management(message: Message, settings: Settings) -> None:
    if not _is_admin_message(message, settings):
        return
    reviews = get_visible_reviews(settings.database_path)
    await message.answer(format_admin_reviews_message(reviews), reply_markup=get_reviews_management_keyboard(reviews).as_markup())


@admin_router.callback_query(F.data == ADMIN_REVIEW_ADD)
async def start_add_review(callback: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_user(callback.from_user.id if callback.from_user else None, settings):
        return
    await state.set_state(AddReviewStates.waiting_name)
    await callback.message.answer('Отправьте имя клиента для нового отзыва.')
    await callback.answer()


@admin_router.message(AddReviewStates.waiting_name)
async def receive_review_name(message: Message, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_message(message, settings):
        return
    await state.update_data(client_name=(message.text or '').strip())
    await state.set_state(AddReviewStates.waiting_text)
    await message.answer('Теперь отправьте текст отзыва.')


@admin_router.message(AddReviewStates.waiting_text)
async def receive_review_text(message: Message, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_message(message, settings):
        return
    await state.update_data(review_text=(message.text or '').strip())
    await state.set_state(AddReviewStates.waiting_rating)
    await message.answer('Осталось отправить рейтинг числом от 1 до 5.')


@admin_router.message(AddReviewStates.waiting_rating)
async def receive_review_rating(message: Message, settings: Settings, state: FSMContext) -> None:
    if not _is_admin_message(message, settings):
        return
    rating_text = (message.text or '').strip()
    if rating_text not in {'1', '2', '3', '4', '5'}:
        await message.answer('Рейтинг должен быть числом от 1 до 5.')
        return
    data = await state.get_data()
    add_review(settings.database_path, str(data["client_name"]), str(data["review_text"]), int(rating_text))
    await state.clear()
    await message.answer('Отзыв добавлен и уже виден клиентам.')


@admin_router.callback_query(F.data.startswith(ADMIN_REVIEW_DELETE_PREFIX))
async def delete_review_callback(callback: CallbackQuery, settings: Settings) -> None:
    if not _is_admin_user(callback.from_user.id if callback.from_user else None, settings):
        return
    review_id = int(callback.data.removeprefix(ADMIN_REVIEW_DELETE_PREFIX))
    hide_review(settings.database_path, review_id)
    await callback.message.answer(f'Отзыв #{review_id} скрыт.')
    await callback.answer()