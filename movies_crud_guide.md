# Movies CRUD με TMDB API

Ο χρήστης ψάχνει ταινία με τίτλο → βλέπει αποτελέσματα με `tmdb_id` → κάνει POST με το id → σώζεται στη DB.

---

## 1. `.env` — Προσθήκη TMDB API Key

Πήγαινε στο [themoviedb.org](https://www.themoviedb.org/), κάνε εγγραφή και πάρε δωρεάν API key.

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/project
TMDB_API_KEY=your_tmdb_api_key_here
```

---

## 2. `db/schemas/movie.py` — Νέα schemas

Πρόσθεσε στο τέλος του αρχείου:

```python
class MovieImport(BaseModel):
    tmdb_id: int

class MovieSearchResult(BaseModel):
    tmdb_id: int
    title: str
    release_date: str
    description: str
    rating: float
```

---

## 3. `routers/movies.py` — Νέο αρχείο

Δημιούργησε το αρχείο `backend/routers/movies.py`:

```python
import uuid
import os
import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from db.database import get_db
from db.models.movies import Movie
from db.schemas.movie import MovieUpdate, MovieResponse, MovieImport, MovieSearchResult

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

router = APIRouter(prefix="/movies", tags=["movies"])


# --- Search στο TMDB (δεν σώζει στη DB) ---
@router.get("/search", response_model=list[MovieSearchResult])
def search_movies(q: str = Query(..., description="Τίτλος ταινίας")):
    res = requests.get(
        f"{TMDB_BASE_URL}/search/movie",
        params={"api_key": TMDB_API_KEY, "query": q}
    )
    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="TMDB API error.")

    results = res.json().get("results", [])
    return [
        MovieSearchResult(
            tmdb_id=m["id"],
            title=m["title"],
            release_date=m.get("release_date") or "N/A",
            description=m.get("overview") or "",
            rating=round(m.get("vote_average", 0), 1),
        )
        for m in results
    ]


# --- CRUD ---

@router.get("/", response_model=list[MovieResponse])
def get_movies(db: Session = Depends(get_db)):
    return db.query(Movie).all()


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: uuid.UUID, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found.")
    return movie


@router.post("/", response_model=MovieResponse, status_code=201)
def create_movie(data: MovieImport, db: Session = Depends(get_db)):
    # Fetch λεπτομερειών από TMDB με το tmdb_id
    res = requests.get(
        f"{TMDB_BASE_URL}/movie/{data.tmdb_id}",
        params={"api_key": TMDB_API_KEY}
    )
    if res.status_code != 200:
        raise HTTPException(status_code=404, detail="Movie not found on TMDB.")

    tmdb = res.json()

    movie = Movie(
        id=uuid.uuid4(),
        title=tmdb["title"],
        description=tmdb.get("overview", ""),
        duration=tmdb.get("runtime", 0),
        genre=", ".join(g["name"] for g in tmdb.get("genres", [])),
        release_date=tmdb.get("release_date") or "1900-01-01",
        rating=round(tmdb.get("vote_average", 0)),
    )

    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


@router.patch("/{movie_id}", response_model=MovieResponse)
def update_movie(movie_id: uuid.UUID, movie_data: MovieUpdate, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")

    for field, value in movie_data.model_dump(exclude_unset=True).items():
        setattr(movie, field, value)

    db.commit()
    db.refresh(movie)
    return movie


@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: uuid.UUID, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")

    db.delete(movie)
    db.commit()
```

---

## 4. `routers/__init__.py` — Καταχώριση router

```python
from .users import router as users_router
from .movies import router as movies_router
```

---

## 5. `main.py` — Προσθήκη movies router

```python
from routers import users_router, movies_router

app.include_router(users_router)
app.include_router(movies_router)
```

---

## Εγκατάσταση dependency

```bash
pip install requests
```

---

## Τυπική ροή χρήσης

### Βήμα 1 — Ψάξε ταινία
```
GET /movies/search?q=Inception
```
Απάντηση:
```json
[
  { "tmdb_id": 27205, "title": "Inception", "release_date": "2010-07-16", "rating": 8.4, "description": "..." },
  { "tmdb_id": 843906, "title": "Inception (Short)", ... }
]
```

### Βήμα 2 — Αποθήκευσε στη DB
```
POST /movies
{ "tmdb_id": 27205 }
```
Το backend κάνει fetch τα πλήρη στοιχεία από TMDB και τα σώζει στη δική μας PostgreSQL.

### Βήμα 3 — Δες/Επεξεργάσου/Διέγραψε
```
GET    /movies
GET    /movies/{id}
PATCH  /movies/{id}   ← για manual διόρθωση πεδίων
DELETE /movies/{id}
```

> **Σημείωση:** Στο επόμενο στάδιο θα προστεθεί authentication (JWT) και διαχωρισμός ρόλων,
> όπου `search`, `POST` και `DELETE` θα είναι admin-only endpoints.
