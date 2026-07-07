import sqlite3
from pathlib import Path

DEFAULT_SERVICES = [
    {
        "title": "Маникюр с покрытием",
        "description": "Классический маникюр с аккуратным покрытием и базовым дизайном.",
        "price": 2200,
        "duration_minutes": 120,
    },
    {
        "title": "Коррекция бровей",
        "description": "Форма, коррекция и легкое окрашивание для аккуратного результата.",
        "price": 1500,
        "duration_minutes": 60,
    },
    {
        "title": "Ламинирование ресниц",
        "description": "Подкручивание, питание и выразительный натуральный эффект.",
        "price": 2800,
        "duration_minutes": 90,
    },
]

DEFAULT_SETTINGS = {
    "welcome_text": "Добро пожаловать в BeautyBot Pro.\n\nЭтот бот поможет клиентам посмотреть услуги, цены, отзывы и записаться к мастеру.",
    "portfolio_text": "Портфолио мастера:\n\nInstagram: https://instagram.com/your_profile\nVK: https://vk.com/your_profile\nTelegram: https://t.me/your_profile\n\nПозже сюда можно добавить фото работ.",
    "address_text": "Мы находимся по адресу:\nг. Ваш город, ул. Примерная, д. 10\n\nОриентир: рядом с метро или торговым центром.\nГрафик работы: ежедневно с 10:00 до 20:00\nКарта: https://yandex.ru/maps",
    "faq_text": "Частые вопросы:\n\n1. Как подготовиться к процедуре?\nЛучше прийти без косметики или старого покрытия, если это возможно.\n\n2. Сколько длится услуга?\nСредняя длительность указана в разделе «💰 Прайс».\n\n3. Можно ли отменить запись?\nДа, но лучше предупредить мастера заранее.\n\n4. Какие способы оплаты?\nНаличные и перевод.\n\n5. Где вы находитесь?\nАдрес есть в разделе «📍 Адрес».",
    "contacts_text": "Связаться с мастером:\nТелефон: +7 (900) 000-00-00\nTelegram: @your_username\n\nЗдесь позже можно подставлять контакты из настроек.",
}

DEFAULT_REVIEWS = [
    {
        "client_name": "Анна",
        "text": "Очень аккуратная работа и приятная атмосфера. Обязательно приду еще раз.",
        "rating": 5,
    },
    {
        "client_name": "Мария",
        "text": "Все понравилось: быстро, красиво и без лишней суеты. Спасибо за заботу.",
        "rating": 5,
    },
    {
        "client_name": "Екатерина",
        "text": "Удобная запись, понятный прайс и отличный результат после процедуры.",
        "rating": 5,
    },
]


def init_db(database_path: str) -> None:
    db_file = Path(database_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_file) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                price INTEGER NOT NULL,
                duration_minutes INTEGER NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS time_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                is_booked INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_time_slots_date_time ON time_slots(date, time)"
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL,
                slot_id INTEGER NOT NULL,
                client_name TEXT NOT NULL,
                client_contact TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (service_id) REFERENCES services (id),
                FOREIGN KEY (slot_id) REFERENCES time_slots (id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                text TEXT NOT NULL,
                rating INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                is_visible INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        _seed_default_services(cursor)
        _seed_default_settings(cursor)
        _seed_default_reviews(cursor)
        connection.commit()


def _seed_default_services(cursor: sqlite3.Cursor) -> None:
    cursor.execute("SELECT COUNT(*) FROM services")
    services_count = cursor.fetchone()[0]

    if services_count > 0:
        return

    cursor.executemany(
        """
        INSERT INTO services (title, description, price, duration_minutes, is_active)
        VALUES (:title, :description, :price, :duration_minutes, 1)
        """,
        DEFAULT_SERVICES,
    )


def _seed_default_settings(cursor: sqlite3.Cursor) -> None:
    cursor.executemany(
        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
        list(DEFAULT_SETTINGS.items()),
    )


def _seed_default_reviews(cursor: sqlite3.Cursor) -> None:
    cursor.execute("SELECT COUNT(*) FROM reviews")
    reviews_count = cursor.fetchone()[0]

    if reviews_count > 0:
        return

    cursor.executemany(
        """
        INSERT INTO reviews (client_name, text, rating, created_at, is_visible)
        VALUES (:client_name, :text, :rating, CURRENT_TIMESTAMP, 1)
        """,
        DEFAULT_REVIEWS,
    )
