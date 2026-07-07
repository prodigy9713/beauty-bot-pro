from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.client_kb import (
    BOOKING_DATE_PREFIX,
    BOOKING_SLOT_PREFIX,
    BOOKING_START_PREFIX,
    get_booking_dates_keyboard,
    get_booking_slots_keyboard,
    get_services_keyboard,
)
from app.services.booking_service import (
    create_appointment,
    format_date_display,
    get_available_dates,
    get_available_slots_by_date,
)
from app.services.services_service import get_active_services, get_service_by_id
from app.states.booking_states import BookingStates
from config import Settings


booking_router = Router()


@booking_router.message(F.text == '📅 Записаться')
async def start_booking(message: Message, settings: Settings) -> None:
    services = get_active_services(settings.database_path)
    await message.answer(
        'С какого направления начнем запись? Выберите услугу кнопкой ниже.',
        reply_markup=get_services_keyboard(services).as_markup(),
    )


@booking_router.callback_query(F.data.startswith(BOOKING_START_PREFIX))
async def choose_booking_date(callback: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    payload = callback.data.removeprefix(BOOKING_START_PREFIX)
    source, service_id_text = payload.split(':', maxsplit=1)
    service_id = int(service_id_text)
    service = get_service_by_id(settings.database_path, service_id)

    if service is None:
        await callback.answer('Услуга не найдена', show_alert=True)
        return

    await state.clear()
    dates = get_available_dates(settings.database_path)
    if not dates:
        await callback.message.edit_text(
            'Свободных дат пока нет. Администратор еще не добавил рабочие окна.',
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        '\n'.join(
            [
                f'📅 Запись на услугу «{service.title}».',
                '',
                'Выберите удобную дату:',
            ]
        ),
        reply_markup=get_booking_dates_keyboard(service_id, source, dates).as_markup(),
    )
    await callback.answer()


@booking_router.callback_query(F.data.startswith(BOOKING_DATE_PREFIX))
async def choose_booking_slot(callback: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    payload = callback.data.removeprefix(BOOKING_DATE_PREFIX)
    source, service_id_text, date_iso = payload.split(':', maxsplit=2)
    service_id = int(service_id_text)
    service = get_service_by_id(settings.database_path, service_id)

    if service is None:
        await callback.answer('Услуга не найдена', show_alert=True)
        return

    slots = get_available_slots_by_date(settings.database_path, date_iso)
    if not slots:
        await callback.answer('На эту дату свободных окон уже нет', show_alert=True)
        return

    await state.update_data(service_id=service_id, source=source, date_iso=date_iso)
    await callback.message.edit_text(
        '\n'.join(
            [
                f'📅 {service.title}',
                f'Дата: {format_date_display(date_iso)}',
                '',
                'Выберите удобное время:',
            ]
        ),
        reply_markup=get_booking_slots_keyboard(service_id, source, date_iso, slots).as_markup(),
    )
    await callback.answer()


@booking_router.callback_query(F.data.startswith(BOOKING_SLOT_PREFIX))
async def ask_client_name(callback: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    payload = callback.data.removeprefix(BOOKING_SLOT_PREFIX)
    source, service_id_text, slot_id_text = payload.split(':', maxsplit=2)
    service_id = int(service_id_text)
    slot_id = int(slot_id_text)

    service = get_service_by_id(settings.database_path, service_id)
    if service is None:
        await callback.answer('Услуга не найдена', show_alert=True)
        return

    await state.update_data(service_id=service_id, slot_id=slot_id, source=source)
    await state.set_state(BookingStates.waiting_name)
    await callback.message.answer(
        f'Отлично, выбрали «{service.title}». Теперь отправьте ваше имя.'
    )
    await callback.answer()


@booking_router.message(BookingStates.waiting_name)
async def receive_client_name(message: Message, state: FSMContext) -> None:
    client_name = (message.text or '').strip()
    if len(client_name) < 2:
        await message.answer('Пожалуйста, введите имя чуть подробнее, минимум 2 символа.')
        return

    await state.update_data(client_name=client_name)
    await state.set_state(BookingStates.waiting_contact)
    await message.answer('Теперь отправьте телефон, username или удобный контакт для связи.')


@booking_router.message(BookingStates.waiting_contact)
async def receive_client_contact(message: Message, state: FSMContext, settings: Settings, bot: Bot) -> None:
    client_contact = (message.text or '').strip()
    if len(client_contact) < 3:
        await message.answer('Контакт выглядит слишком коротким. Отправьте телефон или username еще раз.')
        return

    data = await state.get_data()

    try:
        appointment = create_appointment(
            database_path=settings.database_path,
            service_id=int(data['service_id']),
            slot_id=int(data['slot_id']),
            client_name=str(data['client_name']),
            client_contact=client_contact,
        )
    except ValueError as exc:
        await state.clear()
        await message.answer(str(exc))
        return

    await state.clear()

    await message.answer(
        '✅ Вы записаны:\n'
        f'Услуга: {appointment.service_title}\n'
        f'Дата: {format_date_display(appointment.slot_date)}\n'
        f'Время: {appointment.slot_time}\n\n'
        'Если планы изменятся — напишите мастеру.'
    )

    await bot.send_message(
        chat_id=settings.admin_id,
        text=(
            '🔔 Новая запись:\n'
            f'Клиент: {appointment.client_name}\n'
            f'Услуга: {appointment.service_title}\n'
            f'Дата: {format_date_display(appointment.slot_date)}\n'
            f'Время: {appointment.slot_time}\n'
            f'Контакт: {appointment.client_contact}'
        ),
    )
