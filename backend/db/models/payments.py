import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class Payment(Base):
    __tablename__: "payment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey=("user.id"), nullable=False)
    stripe_checkout_session_id = Column(String, unique=True, nullable=False)
    stripe_payment_intent_id = Column(String, unique=True, nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="eur")
    status = Column(String, nullable=False, default="pending")
    payment_type = Column(String, nullable=False)
    referrence_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # relations
    user = relationship("User", back_populates="payment")
    