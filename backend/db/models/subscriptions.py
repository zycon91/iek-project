from datetime import datetime, timezone
import enum
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.database import Base


class PlanType(str, enum.Enum):
    monthly = "μηνιαία συνδρομή"
    three_months = "τρίμηνη συνδρομή"
    yearly = "ετήσια συνδρομή"


class Subscription(Base):
    __tablename__ = "subscription"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    plan = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relations
    user = relationship("User", back_populates="subscription")
