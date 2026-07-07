import sqlite3


def get_setting(database_path: str, key: str, default: str = "") -> str:
    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            'SELECT value FROM settings WHERE key = ?',
            (key,),
        ).fetchone()

    if row is None:
        return default

    return str(row[0])


def update_setting(database_path: str, key: str, value: str) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            '''
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            ''',
            (key, value),
        )
        connection.commit()


def get_all_template_settings(database_path: str) -> dict[str, str]:
    keys = [
        'welcome_text',
        'portfolio_text',
        'address_text',
        'faq_text',
        'contacts_text',
    ]
    return {key: get_setting(database_path, key) for key in keys}