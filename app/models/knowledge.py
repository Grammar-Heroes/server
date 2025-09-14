from sqlalchemy import Column, Integer, ForeignKey # Float (might call this soon)
from app.core.db import Base

class KnowledgeProgress(Base):
    __tablename__ = "knowledge_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    kc_id = Column(Integer, nullable=False)
    attempts = Column(Integer, default=0) # how many times answered
    correct = Column(Integer, default=0) # how many correct answers