import uuid
from sqlalchemy import Column, Float, String, Integer, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Movie(Base):
    __tablename__ = "movie"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    genre = Column(String, nullable=False, index=True)
    release_date = Column(Date, nullable=False, index=True)
    rating = Column(Float, nullable=False, index=True)
    rental_price = Column(Integer, nullable=False, default=399)
    purchase_price = Column(Integer, nullable=False, default=1499)

    poster_url = Column(String, nullable=True)
    poster_key = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    thumbnail_key = Column(String, nullable=True)

    # relations
    rentals = relationship("Rental", back_populates="movie")
    purchases = relationship("Purchase", back_populates="movie")
    