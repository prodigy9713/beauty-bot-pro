import sqlite3
from pathlib import Path

DEFAULT_SERVICES = [
    {
        "title": "Маникюр с покрытием гель-лак",
        "description": "Комбинированный маникюр, выравнивание, однотонное покрытие и аккуратная форма ногтей.",
        "price": 2200,
        "duration_minutes": 120,
    },
    {
        "title": "Укрепление + маникюр",
        "description": "Маникюр с укреплением базы для более стойкого покрытия и аккуратного результата.",
        "price": 2500,
        "duration_minutes": 150,
    },
    {
        "title": "Педикюр с покрытием",
        "description": "Обработка стоп и пальчиков, педикюр и покрытие гель-лаком в один тон.",
        "price": 2900,
        "duration_minutes": 120,
    },
    {
        "title": "Снятие чужого покрытия",
        "description": "Аккуратное снятие старого покрытия перед новой процедурой.",
        "price": 400,
        "duration_minutes": 30,
    },
]

DEFAULT_SETTINGS = {
    "welcome_text": "Добро пожаловать в студию маникюра BeautyBot Pro.\n\nЗдесь можно посмотреть услуги, цены, отзывы и быстро записаться на удобное время.",
    "portfolio_text": "Портфолио мастера:\n\nInstagram: https://instagram.com/nails_demo\nVK: https://vk.com/nails_demo\nTelegram: https://t.me/nails_demo\n\nЗдесь можно показать работы, дизайны, педикюр и актуальные фото клиентов.",
    "address_text": "Мы находимся по адресу:\nг. Ваш город, ул. Примерная, д. 10\n\nОриентир: 5 минут от метро, вход со стороны двора.\nГрафик работы: ежедневно с 10:00 до 20:00\nКарта: https://yandex.ru/maps",
    "faq_text": "Частые вопросы:\n\n1. Сколько держится покрытие?\nВ среднем 2-3 недели, в зависимости от образа жизни и ухода.\n\n2. Можно ли прийти со своим дизайном?\nДа, можно заранее прислать референс в Telegram.\n\n3. Как подготовиться к визиту?\nНичего специального не нужно, достаточно прийти в назначенное время.\n\n4. Можно ли отменить запись?\nДа, но лучше предупредить заранее, если планы изменились.\n\n5. Какие способы оплаты?\nНаличные и перевод.",
    "contacts_text": "Связаться с мастером:\nТелефон: +7 (900) 000-00-00\nTelegram: @nails_demo\n\nЕсли хотите уточнить дизайн, напишите заранее и пришлите пример фото.",
}

DEFAULT_REVIEWS = [
    {
        "client_name": "Анна",
        "text": "Очень аккуратный маникюр, идеальное выравнивание и красивое покрытие. Ношу уже третью неделю.",
        "rating": 5,
    },
    {
        "client_name": "Мария",
        "text": "Записалась через бот за пару минут. Педикюр сделали очень бережно и красиво.",
        "rating": 5,
    },
    {
        "client_name": "Екатерина",
        "text": "Понравилось, что сразу видно прайс, отзывы и свободное время. Очень удобно для клиента.",
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
