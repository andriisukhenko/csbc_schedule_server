from app.db import db
from sqlalchemy import ForeignKey, Integer, SmallInteger, Time, String, DateTime, UniqueConstraint, Table, Column, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import time, datetime
from enum import Enum
from typing import List, Literal, get_args

WeeksOptions = Literal['upper', 'lower']

SemesterOptions = Literal["1", "2"]

DayOptions = Literal["1", "2", "3", "4", "5", "6"]

BellsNumOptions = Literal["1", "2", "3", "4", "5", "6", "7", "8", "9"]

LessonsTypes = Literal["lecture", "practice"]

teacher_subject_table = Table(
    "teacher_m2m_subject",
    db.Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("teacher_id", Integer, ForeignKey("teachers.id", ondelete="CASCADE")),
    Column("subject_id", Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
)

group_subject_table = Table(
    "group_m2m_subject",
    db.Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE")),
    Column("subject_id", Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
)

class Bell(db.Base):
    __tablename__ = "bells"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[BellsNumOptions] = mapped_column(SQLEnum(*get_args(BellsNumOptions), name="number_of_bell_enum"), unique=True, nullable=False)
    start_at: Mapped[time] = mapped_column(Time, nullable=False)
    end_at: Mapped[time] = mapped_column(Time, nullable=False)
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="bell")

class Teacher(db.Base):
    __tablename__ = "teachers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    second_name: Mapped[str] = mapped_column(String(20), nullable=True)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="teacher")
    subjects: Mapped[List["Subject"]] = relationship(back_populates="teachers", secondary=teacher_subject_table)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class Classroom(db.Base):
    __tablename__ = "classrooms"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[LessonsTypes] = mapped_column(SQLEnum(*get_args(LessonsTypes), name="classroom_type_enum"), nullable=False)
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="classroom")
    deleted_at: Mapped[datetime] = mapped_column(String, nullable=False)

class Subject(db.Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    lessons: Mapped[str] = relationship(back_populates="subject")
    teachers: Mapped[List["Teacher"]] = relationship(back_populates="subjects", secondary=teacher_subject_table)
    groups: Mapped[List["Group"]] = relationship(back_populates="groups", secondary=group_subject_table)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class Group(db.Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(10), unique=True)
    year_start: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    year_end: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="group", secondary=group_subject_table) 
    deleted_at: Mapped[int] = mapped_column(DateTime, nullable=False)

class Lesson(db.Base):
    __tablename__ = "lessons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day: Mapped[DayOptions] = mapped_column(SQLEnum(*get_args(DayOptions), name="lesson_day_enum"), nullable=False)
    week: Mapped[WeeksOptions] = mapped_column(SQLEnum(*get_args(WeeksOptions), name="lesson_week_enum"), nullable=False)
    semester: Mapped[SemesterOptions] = mapped_column(SQLEnum(*get_args(SemesterOptions), name="lesson_semester_enum"), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"))
    teacher: Mapped[Teacher] = relationship(back_populates="lessons", foreign_keys=["teacher_id"])
    classroom_id: Mapped[int] = mapped_column(Integer, ForeignKey("classrooms.id", ondelete="CASCADE"))
    classroom: Mapped[Classroom] = relationship(back_populates="lessons", foreign_keys=["classroom_id"])
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id", ondelete="CASCADE"))
    group: Mapped[Group] = relationship(back_populates="lessons", foreign_keys=["group_id"])
    subject_id: Mapped[str] = mapped_column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    subject: Mapped[Subject] = relationship(back_populates="lessons", foreign_keys=["subject_id"])
    bell_id: Mapped[str] = mapped_column(Integer, ForeignKey("bells.id", ondelete="CASCADE"))
    bell: Mapped[Bell] = relationship(back_populates="lessons", foreign_keys=["bell_id"])
    type: Mapped[LessonsTypes] = mapped_column(SQLEnum(*get_args(LessonsTypes), name="lesson_type_enum"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    __table_args__ = (
        UniqueConstraint("bell_id", "day", "week", "semester", "year", "teacher_id"),
        UniqueConstraint("bell_id", "day", "week", "semester", "year", "classroom_id"),
        UniqueConstraint("bell_id", "day", "week", "semester", "year", "group_id")
    )