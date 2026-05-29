# import από libraries (external)
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# import από δικά μου αρχεία
from ..database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    fullname = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    clerk_user_id = Column(String, unique=True, nullable=True)
    stripe_customer_id = Column(String, unique=True, nullable=True)

    # relations
    subscriptions = relationship("Subscription", back_populates="user")
    rentals = relationship("Rental", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    