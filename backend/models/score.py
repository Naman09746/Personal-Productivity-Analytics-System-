"""
Score models - Weekly and Monthly aggregations
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Integer, Float, String, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class WeeklyScore(Base):
    __tablename__ = "weekly_scores"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    weighted_score: Mapped[float] = mapped_column(Float, default=0.0)
    consistency_score: Mapped[float] = mapped_column(Float, default=0.0)
    total_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_possible: Mapped[int] = mapped_column(Integer, default=0)
    
    # Detailed breakdown per habit
    habit_breakdown: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Why score changed
    insights: Mapped[list] = mapped_column(JSONB, default=list)
    
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    user = relationship("User", back_populates="weekly_scores")


class MonthlyScore(Base):
    __tablename__ = "monthly_scores"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_completion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    avg_weighted_score: Mapped[float] = mapped_column(Float, default=0.0)
    consistency_trend: Mapped[float] = mapped_column(Float, default=0.0)
    performance_grade: Mapped[str] = mapped_column(String(2), default="C")
    
    # Best and worst performing habits
    top_habits: Mapped[list] = mapped_column(JSONB, default=list)
    struggling_habits: Mapped[list] = mapped_column(JSONB, default=list)
    
    # Detailed explanation of performance
    score_explanation: Mapped[list] = mapped_column(JSONB, default=list)
    
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    user = relationship("User", back_populates="monthly_scores")
