"""
Δημιουργεί όλους τους πίνακες της βάσης (π.χ. στο Supabase) με βάση τα models.

Χρήση (από τον φάκελο backend/):
    python scripts/create_tables.py

Με --drop διαγράφει πρώτα τους υπάρχοντες πίνακες και τους ξαναφτιάχνει:
    python scripts/create_tables.py --drop
"""

import argparse
import os
import sys

# Προσθέτουμε τον φάκελο backend/ στο path ώστε να δουλεύουν τα imports
# (db.*, models.*) ανεξάρτητα από το πού τρέχουμε το script.
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

# Σιγουρεύουμε UTF-8 output (π.χ. ελληνικά) στο Windows console.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from db.database import Base, engine

# Σημαντικό: κάνουμε import όλα τα models ώστε να καταχωρηθούν στο Base.metadata.
import db.models  # noqa: F401


def main() -> None:
    parser = argparse.ArgumentParser(description="Δημιουργία πινάκων στη βάση.")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Διέγραψε πρώτα όλους τους πίνακες πριν τη δημιουργία.",
    )
    args = parser.parse_args()

    tables = ", ".join(Base.metadata.tables.keys()) or "(κανένας)"
    print(f"Πίνακες προς δημιουργία: {tables}\n")

    if args.drop:
        print("Διαγραφή υπαρχόντων πινάκων...")
        Base.metadata.drop_all(bind=engine)

    print("Δημιουργία πινάκων...")
    Base.metadata.create_all(bind=engine)
    print("Ολοκληρώθηκε.")


if __name__ == "__main__":
    main()
