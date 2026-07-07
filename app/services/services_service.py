import sqlite3
from dataclasses import dataclass


@dataclass(slots=True)
class ServiceItem:
    id: int
    title: str
    description: str
    price: int
    duration_minutes: int


def get_active_services(database_path: str) -> list[ServiceItem]:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            '''
            SELECT id, title, description, price, duration_minutes
            FROM services
            WHERE is_active = 1
            ORDER BY id
            '''
        ).fetchall()

    return [_row_to_service(row) for row in rows]


def get_service_by_id(database_path: str, service_id: int) -> ServiceItem | None:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            '''
            SELECT id, title, description, price, duration_minutes
            FROM services
            WHERE id = ? AND is_active = 1
            ''',
            (service_id,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_service(row)


def create_service(database_path: str, title: str, description: str, price: int, duration_minutes: int) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            '''
            INSERT INTO services (title, description, price, duration_minutes, is_active)
            VALUES (?, ?, ?, ?, 1)
            ''',
            (title.strip(), description.strip(), price, duration_minutes),
        )
        connection.commit()


def update_service_price(database_path: str, service_id: int, new_price: int) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            'UPDATE services SET price = ? WHERE id = ? AND is_active = 1',
            (new_price, service_id),
        )
        connection.commit()


def update_service_field(database_path: str, service_id: int, field_name: str, value: str | int) -> None:
    allowed_fields = {'title', 'description', 'duration_minutes'}
    if field_name not in allowed_fields:
        raise ValueError('Недопустимое поле для обновления услуги.')

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            f'UPDATE services SET {field_name} = ? WHERE id = ? AND is_active = 1',
            (value, service_id),
        )
        connection.commit()


def deactivate_service(database_path: str, service_id: int) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            'UPDATE services SET is_active = 0 WHERE id = ? AND is_active = 1',
            (service_id,),
        )
        connection.commit()


def format_services_overview(services: list[ServiceItem]) -> str:
    if not services:
        return 'Сейчас услуги еще не добавлены.'

    parts = [
        '💅 Выберите интересующую услугу.',
        '',
        'Нажмите на кнопку ниже, и я покажу подробное описание, цену и длительность.',
    ]
    return '\n'.join(parts)


def format_price_overview(services: list[ServiceItem]) -> str:
    if not services:
        return 'Прайс пока пуст.'

    parts = [
        '💰 Актуальный прайс:',
        '',
    ]
    for service in services:
        parts.append(f'• {service.title} - {service.price} ₽ ({service.duration_minutes} мин.)')

    parts.extend([
        '',
        'Ниже можно выбрать услугу, чтобы посмотреть подробности и перейти к записи.',
    ])
    return '\n'.join(parts)


def format_service_card(service: ServiceItem) -> str:
    return '\n'.join(
        [
            f'✨ {service.title}',
            '',
            service.description,
            '',
            f'💰 Цена: {service.price} ₽',
            f'🕒 Длительность: {service.duration_minutes} мин.',
            '',
            'Если услуга подходит, можно перейти к записи.',
        ]
    )


def format_admin_services(services: list[ServiceItem]) -> str:
    if not services:
        return 'Активных услуг пока нет.'

    parts = ['💅 Активные услуги:', '']
    for service in services:
        parts.append(f'{service.id}. {service.title} - {service.price} ₽ - {service.duration_minutes} мин.')
    return '\n'.join(parts)


def _row_to_service(row: sqlite3.Row) -> ServiceItem:
    return ServiceItem(
        id=row['id'],
        title=row['title'],
        description=row['description'],
        price=row['price'],
        duration_minutes=row['duration_minutes'],
    )