"""
Backfill script: για κάθε ταινία της βάσης που δεν έχει εικόνα,
ψάχνει τον τίτλο στο TMDB, κατεβάζει το poster και το ανεβάζει
μέσω του POST /movies/{id}/poster (το API φτιάχνει και το thumbnail).

Χρήση (με τον server να τρέχει):
    python scripts/backfill_posters.py
    python scripts/backfill_posters.py --base-url http://localhost:8000
"""

import argparse
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original"

# Σιγουρεύουμε UTF-8 output (π.χ. ελληνικά) στο Windows console.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def fetch_all_movies(base_url: str) -> list[dict]:
    """Μαζεύει όλες τις ταινίες σελίδα-σελίδα από το GET /movies/."""
    movies = []
    skip, limit = 0, 100
    while True:
        res = requests.get(
            f"{base_url}/movies/",
            params={"skip": skip, "limit": limit},
            timeout=15,
        )
        res.raise_for_status()
        page = res.json()
        movies.extend(page["items"])
        if not page["has_more"]:
            return movies
        skip += limit


def find_poster_bytes(title: str) -> bytes | None:
    """Ψάχνει τον τίτλο στο TMDB και κατεβάζει το poster της πρώτης αντιστοίχισης."""
    res = requests.get(
        f"{TMDB_BASE_URL}/search/movie",
        params={"api_key": TMDB_API_KEY, "query": title},
        timeout=15,
    )
    if res.status_code != 200:
        return None

    results = res.json().get("results", [])
    if not results:
        return None

    poster_path = results[0].get("poster_path")
    if not poster_path:
        return None

    img = requests.get(f"{TMDB_IMAGE_BASE}{poster_path}", timeout=15)
    return img.content if img.status_code == 200 else None


def backfill(base_url: str, delay: float) -> None:
    base_url = base_url.rstrip("/")
    movies = fetch_all_movies(base_url)
    pending = [m for m in movies if not m.get("thumbnail_url")]

    print(f"Σύνολο ταινιών: {len(movies)}, χωρίς εικόνα: {len(pending)}\n")

    done = 0
    failed = 0

    for i, movie in enumerate(pending, start=1):
        prefix = f"[{i}/{len(pending)}] {movie['title']}"

        try:
            poster_bytes = find_poster_bytes(movie["title"])
        except requests.RequestException as e:
            print(f"{prefix} -> ΣΦΑΛΜΑ TMDB: {e}")
            failed += 1
            continue

        if not poster_bytes:
            print(f"{prefix} -> δεν βρέθηκε poster, παράλειψη.")
            failed += 1
            continue

        try:
            res = requests.post(
                f"{base_url}/movies/{movie['id']}/poster",
                files={"file": ("poster.jpg", poster_bytes, "image/jpeg")},
                timeout=30,
            )
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"{prefix} -> ΣΦΑΛΜΑ upload: {e}")
            failed += 1
            continue

        print(f"{prefix} -> OK ({res.json()['thumbnail_url']})")
        done += 1

        if delay:
            time.sleep(delay)

    print(f"\nΟλοκληρώθηκε. Με εικόνα: {done}, αποτυχίες/παραλείψεις: {failed}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill posters από το TMDB.")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL του API (default: http://localhost:8000).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.25,
        help="Καθυστέρηση σε δευτερόλεπτα μεταξύ των ταινιών (default: 0.25).",
    )
    args = parser.parse_args()

    if not TMDB_API_KEY:
        print("Λείπει το TMDB_API_KEY από το .env")
        sys.exit(1)

    backfill(args.base_url, args.delay)


if __name__ == "__main__":
    main()
