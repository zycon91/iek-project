import os
import uuid
import requests
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query
from dotenv import load_dotenv

from db.database import get_db
from db.models.movies import Movie
from db.schemas.movie import MovieImport, MovieResponse, MovieSearchResult


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
        release_date=tmdb.get("release_date"),
        rating=round(tmdb.get("vote_average", 0)),
    )

    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie

@router.get("/", response_model=list[MovieResponse])
def get_movies(
    db: Session = Depends(get_db)
):
    return db.query(Movie).all()

@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found.")
    return movie
