from sqlalchemy import Column, Integer, ForeignKey, Float
from app.core.db import Base

class KnowledgeProgress(Base):
    __tablename__ = "knowledge_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    kc_id = Column(Integer, nullable=False)

    attempts = Column(Integer, default=0) # how many times answered
    correct = Column(Integer, default=0) # how many correct answers

    # BKT Parameters

    p_know = Column(Float, default=0.2) # prior knowledge (P(L₀))
    transit = Column(Float, default=0.15) # learning rate (P(T))
    slip = Column(Float, default=0.1) # mistake probability (P(S))
    guess = Column(Float, default=0.2) # lucky guess probability (P(G))