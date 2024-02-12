from app.db import db
from sqlalchemy import ForeignKey, Integer, SmallInteger, Time, String, DateTime, UniqueConstraint, Table, Column, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import time, datetime
from typing import List, TYPE_CHECKING, get_args
from schedule import types as schedule_types

if TYPE_CHECKING:
    from users.models import TeacherAccount, StudentAccount

teacher_subject_table = Table(
    "teacher_m2m_subject",
    db.Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("teacher_id", Integer, ForeignKey("teachers_accounts.id", ondelete="CASCADE")),
    Column("subject_id", Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
)

group_subject_table = Table(
    "group_m2m_subject",
    db.Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE")),
    Column("subject_id", Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
)

group_lesson_table = Table(
    "group_m2m_lesson",
    db.Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("part", SQLEnum(*get_args(schedule_types.ScheduleGroupParts), name="lesson_group_parts_enum")),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE")),
    Column("lesson_id", Integer, ForeignKey("lessons.id", ondelete="CASCADE"))
)

class Bell(db.Base):
    __tablename__ = "bells"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[schedule_types.ScheduleBellsNumOptions] = mapped_column(SQLEnum(name="number_of_bell_enum"), unique=True, nullable=False)
    start_at: Mapped[time] = mapped_column(Time, nullable=False)
    end_at: Mapped[time] = mapped_column(Time, nullable=False)
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="bell")

class Classroom(db.Base):
    __tablename__ = "classrooms"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[schedule_types.ScheduleLessonsTypes] = mapped_column(SQLEnum(name="classroom_type_enum"), nullable=False)
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="classroom")
    deleted_at: Mapped[datetime] = mapped_column(String, nullable=False)

class Subject(db.Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    lessons: Mapped[str] = relationship(back_populates="subject")
    teachers: Mapped[List["TeacherAccount"]] = relationship(back_populates="subjects", secondary=teacher_subject_table)
    groups: Mapped[List["Group"]] = relationship(back_populates="groups", secondary=group_subject_table)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class Group(db.Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(10), unique=True)
    year_start: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    year_end: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    subjects: Mapped[List[Subject]] = relationship(back_populates="groups", secondary=group_subject_table)
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="groups", secondary=group_lesson_table)
    students: Mapped[List["StudentAccount"]] = relationship(back_populates="students")
    deleted_at: Mapped[int] = mapped_column(DateTime, nullable=False)

class Lesson(db.Base):
    __tablename__ = "lessons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day: Mapped[schedule_types.ScheduleDaysOptions] = mapped_column(SQLEnum(name="lesson_day_enum"), nullable=False)
    week: Mapped[schedule_types.ScheduleWeeksOptions] = mapped_column(SQLEnum(name="lesson_week_enum"), nullable=False)
    semester: Mapped[schedule_types.ScheduleSemesterOptions] = mapped_column(SQLEnum(name="lesson_semester_enum"), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey("teachers_accounts.id", ondelete="CASCADE"))
    teacher: Mapped["TeacherAccount"] = relationship(back_populates="lessons", foreign_keys=["teacher_id"])
    classroom_id: Mapped[int] = mapped_column(Integer, ForeignKey("classrooms.id", ondelete="CASCADE"))
    classroom: Mapped[Classroom] = relationship(back_populates="lessons", foreign_keys=["classroom_id"])
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id", ondelete="CASCADE"))
    groups: Mapped[List[Group]] = relationship(back_populates="lessons", secondary=group_lesson_table)
    subject_id: Mapped[str] = mapped_column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    subject: Mapped[Subject] = relationship(back_populates="lessons", foreign_keys=["subject_id"])
    bell_id: Mapped[str] = mapped_column(Integer, ForeignKey("bells.id", ondelete="CASCADE"))
    bell: Mapped[Bell] = relationship(back_populates="lessons", foreign_keys=["bell_id"])
    type: Mapped[schedule_types.ScheduleLessonsTypes] = mapped_column(SQLEnum(name="lesson_type_enum"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    __table_args__ = (
        UniqueConstraint("bell_id", "day", "week", "semester", "year", "teacher_id"),
        UniqueConstraint("bell_id", "day", "week", "semester", "year", "classroom_id")
    )