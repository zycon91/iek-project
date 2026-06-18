import uuid
from pydantic import BaseModel
from datetime import date


class MovieImport(BaseModel):
    tmdb_id: int


class MovieSearchResult(BaseModel):
    tmdb_id: int
    title: str
    release_date: str
    description: str
    rating: float


class MovieBase(BaseModel):
    title: str
    duration: int
    description: str
    genre: str
    release_date: date
    rating: float
    rental_price: int = 399
    purchase_price: int = 1499


class MovieCreate(MovieBase):
    pass


class MovieResponseFrontPage(BaseModel):
    id: uuid.UUID
    title: str
    release_date: date
    rating: float
    thumbnail_url: str | None = None   # στη λίστα δείχνουμε το ελαφρύ thumbnail

    class Config:
        from_attributes = True


class MovieUpdate(BaseModel):
    title: str | None = None
    duration: int | None = None
    description: str | None = None
    genre: str | None = None
    release_date: date | None = None
    rating: float | None = None
    rental_price: int | None = None
    purchase_price: int | None = None


class MovieResponse(MovieBase):
    id: uuid.UUID
    poster_url: str | None = None
    thumbnail_url: str | None = None

    class Config:
        from_attributes = True


class MoviePosterResponse(BaseModel):
    movie_id: uuid.UUID
    poster_url: str
    thumbnail_url: str

    class Config:
        from_attributes = True
