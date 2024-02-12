from app.db import db
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, TYPE_CHECKING
from users.types import AccountTypes

if TYPE_CHECKING:
    from schedule.models import Group, Subject, Lesson

class User(db.Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    second_name: Mapped[str] = mapped_column(String(20), nullable=True)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    avatart: Mapped[str] = mapped_column(String, nullable=True)
    accounts: Mapped[List["Account"]] = relationship(back_populates="user")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

class Account(db.Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="accounts")
    type: Mapped[AccountTypes] = mapped_column(SQLEnum(name="account_type_enum"))
    __mapper_args__ = {
        "polymorphic_identity": "account",
        "polymorphic_on": "type"
    }

class AdminAccount(Account):
    __tablename__ = "admins_accounts"
    id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True)
    position: Mapped[str] = mapped_column(String(100), nullable=True)
    __mapper_args__ = {
        "polymorphic_identity": AccountTypes.ADMIN
    }

class TeacherAccount(Account):
    __tablename__ = "teachers_accounts"
    id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True)
    subjects: Mapped[List["Subject"]] = relationship(back_populates="teacher")
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="teachers")
    __mapper_args__ = {
        "polymorphic_identity": AccountTypes.TEACHER
    }

class StudentAccount(Account):
    __tablename__ = "students_accounts"
    id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)
    group: Mapped["Group"] = relationship(back_populates="students")
    __mapper_args__ = {
        "polymorphic_identity": AccountTypes.STUDENT
    }

class EmployeeAccount(Account):
    __tablename__ = "employees_accounts"
    id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": AccountTypes.EMPLOYEE
    }

