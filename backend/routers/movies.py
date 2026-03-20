import os
import requests
from fastapi import APIRouter, HTTPException, Query
from dotenv import load_dotenv

from db.schemas.movie import MovieSearchResult


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