"""Γέφυρα Clerk -> DB χρήστη.

Το frontend στέλνει το Clerk session token (JWT) στο header
`Authorization: Bearer <token>`. Εδώ επαληθεύουμε την υπογραφή του μέσω
του JWKS του Clerk (offline, με το public key), βγάζουμε το `sub`
(= clerk_user_id) και κάνουμε get-or-create την αντίστοιχη εγγραφή `User`.
"""

import os

import httpx
from jose import jwt
from jose.exceptions import JWTError
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from db.database import get_db
from db.models.users import User

load_dotenv()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

# Cache του JWKS ανά issuer — δεν αλλάζει συχνά, το κρατάμε in-memory.
_jwks_cache: dict[str, dict] = {}


async def _get_jwks(issuer: str) -> dict:
    if issuer not in _jwks_cache:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(f"{issuer}/.well-known/jwks.json")
            res.raise_for_status()
            _jwks_cache[issuer] = res.json()
    return _jwks_cache[issuer]


async def _fetch_clerk_profile(clerk_id: str) -> dict:
    """Φέρνει το πλήρες προφίλ από το Clerk Backend API (μόνο όταν φτιάχνουμε νέο χρήστη)."""
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(
            f"https://api.clerk.com/v1/users/{clerk_id}",
            headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"},
        )
        res.raise_for_status()
        return res.json()


def _primary_email(profile: dict, clerk_id: str) -> str:
    emails = profile.get("email_addresses") or []
    primary_id = profile.get("primary_email_address_id")
    for entry in emails:
        if entry.get("id") == primary_id:
            return entry["email_address"]
    if emails:
        return emails[0]["email_address"]
    # Fallback όταν ο χρήστης δεν έχει email (π.χ. εγγραφή με τηλέφωνο)
    return f"{clerk_id}@clerk.local"


def _unique_username(db: Session, base: str, clerk_id: str) -> str:
    base = (base or "user").strip().replace(" ", "_")
    candidate = base
    if not db.query(User).filter(User.username == candidate).first():
        return candidate
    # Σε σύγκρουση, προσθέτουμε ένα σταθερό suffix από το clerk_id
    return f"{base}_{clerk_id[-6:]}"


async def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.removeprefix("Bearer ")

    try:
        issuer = jwt.get_unverified_claims(token)["iss"]
        jwks = await _get_jwks(issuer)
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=issuer,
            options={"verify_aud": False},
        )
    except (JWTError, KeyError, httpx.HTTPError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    clerk_id = claims.get("sub")
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Token missing subject")

    user = db.query(User).filter(User.clerk_user_id == clerk_id).first()
    if user:
        return user

    # get-or-create: ο χρήστης υπάρχει στο Clerk αλλά όχι ακόμη στη DB μας
    try:
        profile = await _fetch_clerk_profile(clerk_id)
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Could not fetch user profile from Clerk")

    email = _primary_email(profile, clerk_id)
    full = " ".join(
        p for p in [profile.get("first_name"), profile.get("last_name")] if p
    ).strip()
    fullname = full or profile.get("username") or email
    username = _unique_username(
        db, profile.get("username") or email.split("@")[0], clerk_id
    )

    user = User(
        clerk_user_id=clerk_id,
        email=email,
        username=username,
        fullname=fullname,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def require_admin(
        user: User = Depends(get_current_user)
) -> User:
    """Authorization guard: επιτρέπει μόνο admins. Πρώτα τρέχει το
    get_current_user (authentication) και μετά ελέγχουμε τον ρόλο."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
