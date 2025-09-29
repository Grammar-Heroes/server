from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    grade_level = Column(String, nullable=True)

    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # node_structure_seed will now be moved to the 'adventure' table
    # node_structure_seed = Column(String, nullable=True)