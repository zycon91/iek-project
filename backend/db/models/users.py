# import από libraries (external)
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

# import από δικά μου αρχεία
from ..database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    clerk_user_id = Column(String, unique=True, nullable=True)
    stripe_customer_id = Column(String, unique=True, nullable=True)
