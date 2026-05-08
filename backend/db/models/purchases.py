import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from ..database import Base


class Purchase(Base):
    __tablename__ = "purchase"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movie.id"), nullable=False)
    amount_paid = Column(Integer, nullable=False)
    purchased_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # relations
    user = relationship("User", back_populates="purchase")
    movie = relationship("Movie", back_populates="purchase")
