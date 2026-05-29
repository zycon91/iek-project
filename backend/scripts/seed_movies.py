"""
Seed script: διαβάζει ένα αρχείο με ονόματα ταινιών (ένα ανά γραμμή),
ψάχνει κάθε τίτλο στο TMDB μέσω του /movies/search και προσθέτει
την πρώτη αντιστοίχιση στη βάση μέσω του /movies/.

Χρήση:
    python scripts/seed_movies.py movies.txt
    python scripts/seed_movies.py movies.txt --base-url http://localhost:8000

Μορφή αρχείου (movies.txt):
    The Matrix
    Inception
    # γραμμές που ξεκινούν με # αγνοούνται
"""

import argparse
import sys
import time

import requests

# Σιγουρεύουμε UTF-8 output (π.χ. ελληνικά) στο Windows console.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def read_titles(path: str) -> list[str]:
    """Διαβάζει τους τίτλους, αγνοώντας κενές γραμμές και σχόλια (#)."""
    with open(path, encoding="utf-8") as f:
        titles = []
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                titles.append(line)
    return titles


def seed(path: str, base_url: str, delay: float) -> None:
    base_url = base_url.rstrip("/")
    titles = read_titles(path)

    if not titles:
        print("Δεν βρέθηκαν τίτλοι στο αρχείο.")
        return

    print(f"Βρέθηκαν {len(titles)} τίτλοι. Ξεκινάμε...\n")

    added = 0
    skipped = 0
    failed = 0

    for i, title in enumerate(titles, start=1):
        prefix = f"[{i}/{len(titles)}] {title}"

        # 1) Αναζήτηση στο TMDB
        try:
            res = requests.get(
                f"{base_url}/movies/search",
                params={"q": title},
                timeout=15,
            )
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"{prefix} -> ΣΦΑΛΜΑ αναζήτησης: {e}")
            failed += 1
            continue

        results = res.json()
        if not results:
            print(f"{prefix} -> δεν βρέθηκε αποτέλεσμα, παράλειψη.")
            skipped += 1
            continue

        match = results[0]
        tmdb_id = match["tmdb_id"]

        # 2) Δημιουργία στη βάση
        try:
            create = requests.post(
                f"{base_url}/movies/",
                json={"tmdb_id": tmdb_id},
                timeout=15,
            )
            create.raise_for_status()
        except requests.RequestException as e:
            detail = ""
            if e.response is not None:
                try:
                    detail = f" ({e.response.json().get('detail', '')})"
                except ValueError:
                    detail = f" ({e.response.text[:100]})"
            print(f"{prefix} -> ΣΦΑΛΜΑ δημιουργίας{detail}")
            failed += 1
            continue

        movie = create.json()
        print(
            f"{prefix} -> προστέθηκε: "
            f"{movie['title']} ({match.get('release_date', 'N/A')}) "
            f"[tmdb:{tmdb_id}]"
        )
        added += 1

        if delay:
            time.sleep(delay)

    print(
        f"\nΟλοκληρώθηκε. Προστέθηκαν: {added}, "
        f"χωρίς αποτέλεσμα: {skipped}, σφάλματα: {failed}."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed ταινιών από αρχείο με τίτλους.")
    parser.add_argument("file", help="Αρχείο με ονόματα ταινιών (ένα ανά γραμμή).")
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

    try:
        seed(args.file, args.base_url, args.delay)
    except FileNotFoundError:
        print(f"Το αρχείο δεν βρέθηκε: {args.file}")
        sys.exit(1)


if __name__ == "__main__":
    main()
