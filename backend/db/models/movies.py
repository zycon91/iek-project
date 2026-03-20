import uuid
from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base

class Movie(Base):
    __tablename__ = "movie"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    genre = Column(String, nullable=False)
    release_date = Column(Date, nullable=False)
    rating = Column(Integer, nullable=False)
    