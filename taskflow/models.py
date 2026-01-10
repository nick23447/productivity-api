from __future__ import annotations
from datetime import date, datetime, timezone
from typing import List, Optional

from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship # type: ignore[attr-defined]

from taskflow import db
class User(db.Model): # type: ignore
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(60), nullable=False)

    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="user",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"User('{self.email}')"

class Task(db.Model):  # type: ignore
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="tasks")

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)

    reminder_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    tags: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)