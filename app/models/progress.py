from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from app.core.db import Base

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    level_id = Column(String, index=True, nullable=False) # e.g. "F1-L2B"
    status = Column(String, default="locked") # locked | unlocked | cleared
    updated_at = Column(DateTime(timezone=True), server_default=func.now())