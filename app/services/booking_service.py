import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(slots=True)
class TimeSlotItem:
    id: int
    date: str
    time: str


@dataclass(slots=True)
class AppointmentItem:
    id: int
    service_title: str
    slot_date: str
    slot_time: str
    client_name: str
    client_contact: str
    created_at: str


def normalize_date(date_text: str) -> str:
    cleaned = date_text.strip()
    for pattern in ('%d.%m.%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(cleaned, pattern).strftime('%Y-%m-%d')
        except ValueError:
            continue
    raise ValueError('Введите дату в формате ДД.ММ.ГГГГ, например 10.07.2026.')


def normalize_time(time_text: str) -> str:
    cleaned = time_text.strip()
    try:
        return datetime.strptime(cleaned, '%H:%M').strftime('%H:%M')
    except ValueError as exc:
        raise ValueError('Введите время в формате ЧЧ:ММ, например 10:00.') from exc


def format_date_display(date_iso: str) -> str:
    return datetime.strptime(date_iso, '%Y-%m-%d').strftime('%d.%m.%Y')


def create_time_slots(
    database_path: str,
    date_text: str,
    start_time_text: str,
    end_time_text: str,
    step_minutes: int,
) -> tuple[int, int]:
    if step_minutes <= 0:
        raise ValueError('Шаг должен быть положительным числом минут.')

    date_iso = normalize_date(date_text)
    start_time = normalize_time(start_time_text)
    end_time = normalize_time(end_time_text)

    start_dt = datetime.strptime(f'{date_iso} {start_time}', '%Y-%m-%d %H:%M')
    end_dt = datetime.strptime(f'{date_iso} {end_time}', '%Y-%m-%d %H:%M')

    if start_dt >= end_dt:
        raise ValueError('Время начала должно быть раньше времени окончания.')

    created_count = 0
    skipped_count = 0

    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()
        current_dt = start_dt

        while current_dt < end_dt:
            slot_time = current_dt.strftime('%H:%M')
            cursor.execute(
                '''
                INSERT OR IGNORE INTO time_slots (date, time, is_booked)
                VALUES (?, ?, 0)
                ''',
                (date_iso, slot_time),
            )
            if cursor.rowcount == 1:
                created_count += 1
            else:
                skipped_count += 1
            current_dt += timedelta(minutes=step_minutes)

        connection.commit()

    return created_count, skipped_count


def get_available_dates(database_path: str) -> list[str]:
    today_iso = datetime.now().strftime('%Y-%m-%d')
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            '''
            SELECT DISTINCT date
            FROM time_slots
            WHERE is_booked = 0 AND date >= ?
            ORDER BY date, time
            ''',
            (today_iso,),
        ).fetchall()

    return [row[0] for row in rows]


def get_available_slots_by_date(database_path: str, date_iso: str) -> list[TimeSlotItem]:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            '''
            SELECT id, date, time
            FROM time_slots
            WHERE date = ? AND is_booked = 0
            ORDER BY time
            ''',
            (date_iso,),
        ).fetchall()

    return [TimeSlotItem(id=row['id'], date=row['date'], time=row['time']) for row in rows]


def create_appointment(
    database_path: str,
    service_id: int,
    slot_id: int,
    client_name: str,
    client_contact: str,
) -> AppointmentItem:
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        slot_row = connection.execute(
            '''
            SELECT id, date, time, is_booked
            FROM time_slots
            WHERE id = ?
            ''',
            (slot_id,),
        ).fetchone()

        if slot_row is None:
            raise ValueError('Выбранный слот не найден.')
        if slot_row['is_booked']:
            raise ValueError('Этот слот уже занят. Выберите другое время.')

        service_row = connection.execute(
            '''
            SELECT id, title
            FROM services
            WHERE id = ? AND is_active = 1
            ''',
            (service_id,),
        ).fetchone()

        if service_row is None:
            raise ValueError('Услуга больше недоступна.')

        cursor = connection.cursor()
        cursor.execute(
            '''
            INSERT INTO appointments (service_id, slot_id, client_name, client_contact, created_at)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (service_id, slot_id, client_name.strip(), client_contact.strip(), created_at),
        )
        appointment_id = cursor.lastrowid

        cursor.execute(
            '''
            UPDATE time_slots
            SET is_booked = 1
            WHERE id = ?
            ''',
            (slot_id,),
        )
        connection.commit()

    return AppointmentItem(
        id=appointment_id,
        service_title=service_row['title'],
        slot_date=slot_row['date'],
        slot_time=slot_row['time'],
        client_name=client_name.strip(),
        client_contact=client_contact.strip(),
        created_at=created_at,
    )


def get_upcoming_appointments(database_path: str, limit: int = 10) -> list[AppointmentItem]:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            '''
            SELECT
                appointments.id,
                services.title AS service_title,
                time_slots.date AS slot_date,
                time_slots.time AS slot_time,
                appointments.client_name,
                appointments.client_contact,
                appointments.created_at
            FROM appointments
            JOIN services ON services.id = appointments.service_id
            JOIN time_slots ON time_slots.id = appointments.slot_id
            ORDER BY time_slots.date, time_slots.time
            LIMIT ?
            ''',
            (limit,),
        ).fetchall()

    return [
        AppointmentItem(
            id=row['id'],
            service_title=row['service_title'],
            slot_date=row['slot_date'],
            slot_time=row['slot_time'],
            client_name=row['client_name'],
            client_contact=row['client_contact'],
            created_at=row['created_at'],
        )
        for row in rows
    ]


def format_appointments_message(appointments: list[AppointmentItem]) -> str:
    if not appointments:
        return 'Ближайших записей пока нет.'

    parts = ['📋 Ближайшие записи:', '']
    for item in appointments:
        parts.append(
            '\n'.join(
                [
                    f'• {format_date_display(item.slot_date)} в {item.slot_time}',
                    f'Услуга: {item.service_title}',
                    f'Клиент: {item.client_name}',
                    f'Контакт: {item.client_contact}',
                ]
            )
        )
        parts.append('')

    return '\n'.join(parts).strip()
