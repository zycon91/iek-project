import datetime
import enum
import uuid
from sqlalchemy import UUID, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


class RentType(str, enum.Enum):
    daily = "1 ημέρα"
    weekly = "1 εβδομάδα"
    other = "Άλλο..."
    

class Rental(Base):
    __tablename__ = "rental"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movie.id"), nullable=False)
    start_date = Column(DateTime, nullable=False, default=lambda: datetime.now(datetime.timezone.utc))
    end_date = Column(DateTime, nullable=False)

    # Relations
    user = relationship("User", back_populates="rentals")
    movie = relationship("Movie", back_populates="rentals")