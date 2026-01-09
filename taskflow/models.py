from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional

from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column # type: ignore[attr-defined]

from taskflow import db
class User(db.Model): # type: ignore
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(60), nullable=False)


    def __repr__(self) -> str:
        return f"User('{self.email}')"