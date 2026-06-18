import os
import uuid
import requests
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from dotenv import load_dotenv

from db.schemas.pagination import Page
from db.database import get_db
from db.models.movies import Movie
from db.schemas.movie import (
    MovieImport, MovieResponse, MovieResponseFrontPage,
    MovieSearchResult, MoviePosterResponse,
)
from utils.storage import save_image_bytes, create_and_save_thumbnail, delete_object


load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original"

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

router = APIRouter(prefix="/movies", tags=["movies"])


# --- Search στο TMDB (δεν σώζει στη DB) ---
@router.get("/search", response_model=list[MovieSearchResult])
def search_movies(
    q: str = Query(..., description="Τίτλος ταινίας")
    ):
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
def create_movie(
    data: MovieImport, 
    db: Session = Depends(get_db)
    ):
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

    poster_path = tmdb.get("poster_path")
    if poster_path:
        try:
            img_res = requests.get(f"{TMDB_IMAGE_BASE}{poster_path}", timeout=15)
            if img_res.status_code == 200:
                poster = save_image_bytes(
                    content=img_res.content,
                    filename=f"{data.tmdb_id}.jpg",
                    folder="movies/posters",
                )
                thumb = create_and_save_thumbnail(img_res.content)
                movie.poster_url = poster["url"]
                movie.poster_key = poster["key"]
                movie.thumbnail_url = thumb["url"]
                movie.thumbnail_key = thumb["key"]
        except requests.RequestException:
            pass

    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie

@router.get("/", response_model=Page[MovieResponseFrontPage])
def get_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    genre: str | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("title"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    query = db.query(
        Movie.id, Movie.title, Movie.rating, Movie.release_date,
        Movie.genre, Movie.thumbnail_url
    )

    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    if search:
        query = query.filter(Movie.title.ilike(f"%{search}%"))

    sort_columns = {
        "title": Movie.title,
        "rating": Movie.rating,
        "release_date": Movie.release_date
    }

    column = sort_columns.get(sort_by, Movie.title)
    query = query.order_by(column.desc() if order == "desc" else column.asc())

    total = query.count()

    items = query.offset(skip).limit(limit).all()
    
    return Page[MovieResponseFrontPage](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )

@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found.")
    return movie

@router.post("/{movie_id}/poster", response_model=MoviePosterResponse)
def upload_movie_poster(
    movie_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found.")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: jpeg, png, webp.",
        )

    content = file.file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="Image too large (max 5MB).")

    # Πρώτα αποθηκεύονται τα νέα αρχεία, μετά σβήνονται τα παλιά,
    # και τελευταίο γίνεται το commit — μια αποτυχία στη μέση
    # δεν αφήνει ποτέ τη DB να δείχνει σε εικόνα που δεν υπάρχει.
    poster = save_image_bytes(
        content=content,
        filename=file.filename or "poster.jpg",
        folder="movies/posters",
    )
    thumb = create_and_save_thumbnail(content)

    if movie.poster_key:
        delete_object(movie.poster_key)
    if movie.thumbnail_key:
        delete_object(movie.thumbnail_key)

    movie.poster_url = poster["url"]
    movie.poster_key = poster["key"]
    movie.thumbnail_url = thumb["url"]
    movie.thumbnail_key = thumb["key"]
    db.commit()
    db.refresh(movie)

    return MoviePosterResponse(
        movie_id=movie.id,
        poster_url=movie.poster_url,
        thumbnail_url=movie.thumbnail_url,
    )

@router.delete("/{movie_id}/poster", status_code=204)
def delete_movie_poster(
    movie_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found.")
    if not movie.poster_key:
        raise HTTPException(status_code=404, detail="Movie has no poster.")

    delete_object(movie.poster_key)
    if movie.thumbnail_key:
        delete_object(movie.thumbnail_key)

    movie.poster_url = None
    movie.poster_key = None
    movie.thumbnail_url = None
    movie.thumbnail_key = None
    db.commit()
