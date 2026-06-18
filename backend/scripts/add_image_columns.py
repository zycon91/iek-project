"""
Μini migration: προσθέτει τις στήλες εικόνων στον πίνακα movie.
(Το create_tables.py δεν αλλάζει υπάρχοντες πίνακες — μόνο δημιουργεί νέους.)

Χρήση (από τον φάκελο backend/):
    python scripts/add_image_columns.py
"""

import sys
from pathlib import Path

# Επιτρέπει "python scripts/add_image_columns.py" από τον φάκελο backend/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from db.database import engine

COLUMNS = ["poster_url", "poster_key", "thumbnail_url", "thumbnail_key"]


def main() -> None:
    with engine.begin() as conn:
        for col in COLUMNS:
            conn.execute(text(f"ALTER TABLE movie ADD COLUMN IF NOT EXISTS {col} VARCHAR"))
            print(f"OK: {col}")

        cols = conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'movie'")
        ).fetchall()
        print("\nΣτήλες του πίνακα movie:", ", ".join(c[0] for c in cols))


if __name__ == "__main__":
    main()
