from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from app.core.db import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    kc_id = Column(Integer, nullable=False)

    sentence = Column(String, nullable=False)
    is_correct = Column(Integer, nullable=False, default=0) # store as 0/1
    feedback = Column(JSON, nullable=True) # { "error_indices": [...] }

    created_at = Column(DateTime(timezone=True), server_default=func.now())