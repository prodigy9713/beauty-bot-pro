import sqlite3
from dataclasses import dataclass


@dataclass(slots=True)
class ReviewItem:
    id: int
    client_name: str
    text: str
    rating: int
    created_at: str


def get_visible_reviews(database_path: str) -> list[ReviewItem]:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            '''
            SELECT id, client_name, text, rating, created_at
            FROM reviews
            WHERE is_visible = 1
            ORDER BY created_at DESC, id DESC
            '''
        ).fetchall()

    return [_row_to_review(row) for row in rows]


def add_review(database_path: str, client_name: str, text: str, rating: int) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            '''
            INSERT INTO reviews (client_name, text, rating, created_at, is_visible)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
            ''',
            (client_name.strip(), text.strip(), rating),
        )
        connection.commit()


def hide_review(database_path: str, review_id: int) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute('UPDATE reviews SET is_visible = 0 WHERE id = ?', (review_id,))
        connection.commit()


def format_reviews_message(reviews: list[ReviewItem]) -> str:
    if not reviews:
        return 'Пока отзывов нет. Совсем скоро здесь появятся впечатления клиентов.'

    parts = ['⭐ Отзывы клиентов:', '']
    for review in reviews:
        stars = '★' * max(1, min(review.rating, 5))
        parts.append('\n'.join([f'{stars} {review.client_name}', review.text]))
        parts.append('')
    return '\n'.join(parts).strip()


def format_admin_reviews_message(reviews: list[ReviewItem]) -> str:
    if not reviews:
        return 'Видимых отзывов пока нет.'

    parts = ['⭐ Видимые отзывы:', '']
    for review in reviews:
        parts.append(f'{review.id}. {review.client_name} - {review.rating}/5')
        parts.append(review.text)
        parts.append('')
    return '\n'.join(parts).strip()


def _row_to_review(row: sqlite3.Row) -> ReviewItem:
    return ReviewItem(
        id=row['id'],
        client_name=row['client_name'],
        text=row['text'],
        rating=row['rating'],
        created_at=row['created_at'],
    )