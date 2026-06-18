"""
Seed DEMO δεδομένων ΑΠΕΥΘΕΙΑΣ στη βάση (χωρίς TMDB/Stripe) — για να δοκιμάσουμε
γρήγορα το admin panel με πραγματικά δεδομένα.

Χρήση (από τον φάκελο backend/):
    python scripts/seed_demo.py            # προσθέτει demo δεδομένα
    python scripts/seed_demo.py --clean    # διαγράφει ΜΟΝΟ τα demo δεδομένα

Ασφαλές να ξανατρέξει: οι demo users/movies γίνονται get-or-create και τα
rentals/purchases/subscriptions μπαίνουν μόνο αν ο πίνακας είναι άδειος.
Τα demo δεδομένα είναι αναγνωρίσιμα (emails @example.com, σταθερές ταινίες),
ώστε το --clean να μη αγγίζει πραγματικά δεδομένα.
"""

import argparse
import os
import random
import sys
from datetime import date, datetime, time, timedelta

# Ώστε να δουλεύουν τα imports (db.*) ανεξάρτητα από πού τρέχουμε.
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from db.database import Base, engine, SessionLocal  # noqa: E402
import db.models  # noqa: F401,E402  (καταχωρεί όλα τα models)
from db.models.users import User  # noqa: E402
from db.models.movies import Movie  # noqa: E402
from db.models.rentals import Rental  # noqa: E402
from db.models.purchases import Purchase  # noqa: E402
from db.models.subscriptions import Subscription  # noqa: E402

random.seed(42)

# (username, fullname, email)
DEMO_USERS = [
    ("giorgos", "Γιώργος Παπαδόπουλος", "giorgos@example.com"),
    ("maria", "Μαρία Ιωάννου", "maria@example.com"),
    ("nikos", "Νίκος Αντωνίου", "nikos@example.com"),
    ("eleni", "Ελένη Δημητρίου", "eleni@example.com"),
    ("kostas", "Κώστας Γεωργίου", "kostas@example.com"),
    ("sofia", "Σοφία Νικολάου", "sofia@example.com"),
    ("dimitris", "Δημήτρης Παππάς", "dimitris@example.com"),
    ("katerina", "Κατερίνα Βασιλείου", "katerina@example.com"),
]

# (title, genre, duration, rating, release_date, rental_price, purchase_price)
DEMO_MOVIES = [
    ("Inception", "Επιστημονική Φαντασία, Δράση", 148, 8.4, date(2010, 7, 16), 399, 1499),
    ("The Matrix", "Επιστημονική Φαντασία, Δράση", 136, 8.7, date(1999, 3, 31), 399, 1299),
    ("Interstellar", "Επιστημονική Φαντασία, Περιπέτεια", 169, 8.6, date(2014, 11, 7), 449, 1599),
    ("The Godfather", "Δράμα, Έγκλημα", 175, 9.2, date(1972, 3, 24), 399, 1499),
    ("Pulp Fiction", "Έγκλημα, Δράμα", 154, 8.9, date(1994, 10, 14), 349, 1299),
    ("The Dark Knight", "Δράση, Έγκλημα", 152, 9.0, date(2008, 7, 18), 449, 1599),
    ("Forrest Gump", "Δράμα, Ρομαντική", 142, 8.8, date(1994, 7, 6), 349, 1299),
    ("Parasite", "Θρίλερ, Δράμα", 132, 8.5, date(2019, 5, 30), 399, 1499),
    ("Gladiator", "Δράση, Περιπέτεια", 155, 8.5, date(2000, 5, 5), 399, 1399),
    ("Whiplash", "Δράμα, Μουσική", 106, 8.5, date(2014, 10, 10), 349, 1199),
]

DEMO_MOVIE_TITLES = [m[0] for m in DEMO_MOVIES]
PLANS = ["μηνιαία συνδρομή", "τρίμηνη συνδρομή", "ετήσια συνδρομή"]


def at_midnight(d: date) -> datetime:
    # Τα RentalResponse/SubscriptionResponse δηλώνουν τα πεδία ως `date`, ενώ τα
    # models είναι `DateTime`. Με ώρα 00:00 το Pydantic δέχεται τη μετατροπή σε date.
    return datetime.combine(d, time.min)


def seed(db) -> None:
    Base.metadata.create_all(bind=engine)

    # --- Users (get-or-create ανά email) ---
    users = []
    for username, fullname, email in DEMO_USERS:
        u = db.query(User).filter(User.email == email).first()
        if not u:
            u = User(username=username, fullname=fullname, email=email)
            db.add(u)
        users.append(u)

    # --- Movies (get-or-create ανά τίτλο) ---
    for title, genre, duration, rating, rel, rp, pp in DEMO_MOVIES:
        if not db.query(Movie).filter(Movie.title == title).first():
            db.add(Movie(
                title=title,
                description=f"Δοκιμαστική περιγραφή για την ταινία «{title}».",
                duration=duration, genre=genre, release_date=rel,
                rating=rating, rental_price=rp, purchase_price=pp,
            ))
    db.commit()

    # Για το linking χρησιμοποιούμε ΟΛΕΣ τις ταινίες της βάσης (demo + τυχόν υπάρχουσες)
    all_movies = db.query(Movie).all()
    users = db.query(User).filter(User.email.like("%@example.com")).all()
    today = date.today()

    # --- Rentals ---
    if db.query(Rental).count() == 0:
        for _ in range(12):
            u = random.choice(users)
            m = random.choice(all_movies)
            start_d = today - timedelta(days=random.randint(0, 12))
            db.add(Rental(user_id=u.id, movie_id=m.id,
                          start_date=at_midnight(start_d),
                          end_date=at_midnight(start_d + timedelta(days=2))))
        print("  + 12 rentals")
    else:
        print("  · rentals υπάρχουν ήδη — skip")

    # --- Purchases (μοναδικά ζεύγη user+movie) ---
    if db.query(Purchase).count() == 0:
        pairs = set()
        attempts = 0
        while len(pairs) < 10 and attempts < 200:
            attempts += 1
            u = random.choice(users)
            m = random.choice(all_movies)
            if (u.id, m.id) in pairs:
                continue
            pairs.add((u.id, m.id))
            db.add(Purchase(user_id=u.id, movie_id=m.id, amount_paid=m.purchase_price,
                            purchased_at=at_midnight(today - timedelta(days=random.randint(0, 60)))))
        print(f"  + {len(pairs)} purchases")
    else:
        print("  · purchases υπάρχουν ήδη — skip")

    # --- Subscriptions (μία ανά χρήστη, σε 5 χρήστες) ---
    if db.query(Subscription).count() == 0:
        for u in random.sample(users, min(5, len(users))):
            start_d = today - timedelta(days=random.randint(0, 25))
            db.add(Subscription(user_id=u.id, plan=random.choice(PLANS),
                                start_date=at_midnight(start_d),
                                end_date=at_midnight(start_d + timedelta(days=30)),
                                is_active=random.random() > 0.3))
        print("  + 5 subscriptions")
    else:
        print("  · subscriptions υπάρχουν ήδη — skip")

    db.commit()


def clean(db) -> None:
    """Διαγράφει ΜΟΝΟ τα demo δεδομένα (FK-safe σειρά: παιδιά -> γονείς)."""
    demo_user_ids = [r[0] for r in db.query(User.id).filter(User.email.like("%@example.com")).all()]
    demo_movie_ids = [r[0] for r in db.query(Movie.id).filter(Movie.title.in_(DEMO_MOVIE_TITLES)).all()]

    db.query(Rental).filter(
        (Rental.user_id.in_(demo_user_ids)) | (Rental.movie_id.in_(demo_movie_ids))
    ).delete(synchronize_session=False)
    db.query(Purchase).filter(
        (Purchase.user_id.in_(demo_user_ids)) | (Purchase.movie_id.in_(demo_movie_ids))
    ).delete(synchronize_session=False)
    db.query(Subscription).filter(
        Subscription.user_id.in_(demo_user_ids)
    ).delete(synchronize_session=False)
    db.query(User).filter(User.id.in_(demo_user_ids)).delete(synchronize_session=False)
    db.query(Movie).filter(Movie.id.in_(demo_movie_ids)).delete(synchronize_session=False)
    db.commit()
    print(f"Καθαρίστηκαν {len(demo_user_ids)} demo users και {len(demo_movie_ids)} demo movies (+ σχετικά records).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo δεδομένων για το admin panel.")
    parser.add_argument("--clean", action="store_true", help="Διέγραψε τα demo δεδομένα αντί να προσθέσεις.")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.clean:
            clean(db)
        else:
            print("Προσθήκη demo δεδομένων...")
            seed(db)
            print("Σύνολα στη βάση:", {
                "users": db.query(User).count(),
                "movies": db.query(Movie).count(),
                "rentals": db.query(Rental).count(),
                "purchases": db.query(Purchase).count(),
                "subscriptions": db.query(Subscription).count(),
            })
            print("Ολοκληρώθηκε.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
