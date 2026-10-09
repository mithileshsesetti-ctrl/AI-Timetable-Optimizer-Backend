from datetime import datetime, time
from enum import Enum

from sqlalchemy import (
    DateTime,
    Boolean,
    Column,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


# ============================================================
# ENUMS
# ============================================================

class CourseType(str, Enum):
    REGULAR = "REGULAR"
    ELECTIVE = "ELECTIVE"
    LAB = "LAB"


class RoomType(str, Enum):
    CLASSROOM = "CLASSROOM"
    LAB = "LAB"
    HALL = "HALL"


# ============================================================
# ACADEMIC YEAR
# ============================================================

class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    semester = Column(String, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    allocations = relationship(
        "TimetableAllocation",
        back_populates="academic_year",
        cascade="all, delete-orphan",
    )


# ============================================================
# DEPARTMENT
# ============================================================

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False, index=True)

    courses = relationship("Course", back_populates="department")
    faculty = relationship("Faculty", back_populates="department")
    rooms = relationship("Room", back_populates="department")
    student_groups = relationship(
        "StudentGroup",
        back_populates="department",
    )


# ============================================================
# COURSE
# ============================================================

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False,
    )

    year = Column(Integer, nullable=False)
    semester = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    hours_per_week = Column(Integer, nullable=False)

    course_type = Column(
        SQLEnum(CourseType),
        nullable=False,
    )

    required_room_type = Column(
        SQLEnum(RoomType),
        nullable=True,
    )

    required_equipment = Column(
        String,
        nullable=True,
    )

    department = relationship(
        "Department",
        back_populates="courses",
    )

    faculty_subjects = relationship(
        "FacultySubject",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    student_groups = relationship(
        "CourseStudentGroup",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    electives = relationship(
        "Elective",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    allocations = relationship(
        "TimetableAllocation",
        back_populates="course",
    )


# ============================================================
# FACULTY
# ============================================================

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    faculty_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )
    name = Column(String, nullable=False)

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False,
    )

    max_classes_per_day = Column(
        Integer,
        default=0,
        nullable=False,
    )

    department = relationship(
        "Department",
        back_populates="faculty",
    )

    subjects = relationship(
        "FacultySubject",
        back_populates="faculty",
        cascade="all, delete-orphan",
    )

    availability = relationship(
        "FacultyAvailability",
        back_populates="faculty",
        cascade="all, delete-orphan",
    )

    allocations = relationship(
        "TimetableAllocation",
        back_populates="faculty",
    )


# ============================================================
# ROOM
# ============================================================

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )
    name = Column(String, nullable=False)

    room_type = Column(
        SQLEnum(RoomType),
        nullable=False,
    )

    capacity = Column(Integer, nullable=False)

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=True,
    )

    department = relationship(
        "Department",
        back_populates="rooms",
    )

    availability = relationship(
        "RoomAvailability",
        back_populates="room",
        cascade="all, delete-orphan",
    )

    equipment = relationship(
        "RoomEquipment",
        back_populates="room",
        cascade="all, delete-orphan",
    )

    allocations = relationship(
        "TimetableAllocation",
        back_populates="room",
    )


# ============================================================
# STUDENT GROUP
# ============================================================

class StudentGroup(Base):
    __tablename__ = "student_groups"

    id = Column(Integer, primary_key=True, index=True)
    group_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False,
    )

    year = Column(Integer, nullable=False)
    section = Column(String, nullable=False)
    student_count = Column(Integer, nullable=False)

    department = relationship(
        "Department",
        back_populates="student_groups",
    )

    courses = relationship(
        "CourseStudentGroup",
        back_populates="student_group",
        cascade="all, delete-orphan",
    )

    elective_groups = relationship(
        "ElectiveStudentGroup",
        back_populates="student_group",
        cascade="all, delete-orphan",
    )

    allocations = relationship(
        "TimetableAllocation",
        back_populates="student_group",
    )


# ============================================================
# TIME SLOT
# ============================================================

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)

    day = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_number = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "day",
            "slot_number",
            name="uq_time_slot_day_number",
        ),
    )

    allocations = relationship(
        "TimetableAllocation",
        back_populates="time_slot",
    )


# ============================================================
# FACULTY SUBJECT
# ============================================================

class FacultySubject(Base):
    __tablename__ = "faculty_subjects"

    id = Column(Integer, primary_key=True, index=True)

    faculty_id = Column(
        Integer,
        ForeignKey("faculty.id"),
        nullable=False,
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "faculty_id",
            "course_id",
            name="uq_faculty_course",
        ),
    )

    faculty = relationship(
        "Faculty",
        back_populates="subjects",
    )

    course = relationship(
        "Course",
        back_populates="faculty_subjects",
    )


# ============================================================
# COURSE - STUDENT GROUP
# ============================================================

class CourseStudentGroup(Base):
    __tablename__ = "course_student_groups"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False,
    )

    student_group_id = Column(
        Integer,
        ForeignKey("student_groups.id"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "student_group_id",
            name="uq_course_student_group",
        ),
    )

    course = relationship(
        "Course",
        back_populates="student_groups",
    )

    student_group = relationship(
        "StudentGroup",
        back_populates="courses",
    )


# ============================================================
# FACULTY AVAILABILITY
# ============================================================

class FacultyAvailability(Base):
    __tablename__ = "faculty_availability"

    id = Column(Integer, primary_key=True, index=True)

    faculty_id = Column(
        Integer,
        ForeignKey("faculty.id"),
        nullable=False,
    )

    day = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    available = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "faculty_id",
            "day",
            "start_time",
            "end_time",
            name="uq_faculty_availability",
        ),
    )

    faculty = relationship(
        "Faculty",
        back_populates="availability",
    )


# ============================================================
# ROOM AVAILABILITY
# ============================================================

class RoomAvailability(Base):
    __tablename__ = "room_availability"

    id = Column(Integer, primary_key=True, index=True)

    room_id = Column(
        Integer,
        ForeignKey("rooms.id"),
        nullable=False,
    )

    day = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    available = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "day",
            "start_time",
            "end_time",
            name="uq_room_availability",
        ),
    )

    room = relationship(
        "Room",
        back_populates="availability",
    )


# ============================================================
# ROOM EQUIPMENT
# ============================================================

class RoomEquipment(Base):
    __tablename__ = "room_equipment"

    id = Column(Integer, primary_key=True, index=True)

    room_id = Column(
        Integer,
        ForeignKey("rooms.id"),
        nullable=False,
    )

    equipment_name = Column(
        String,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "equipment_name",
            name="uq_room_equipment",
        ),
    )

    room = relationship(
        "Room",
        back_populates="equipment",
    )


# ============================================================
# ELECTIVE
# ============================================================

class Elective(Base):
    __tablename__ = "electives"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False,
    )

    elective_name = Column(
        String,
        nullable=False,
    )

    multidisciplinary = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    course = relationship(
        "Course",
        back_populates="electives",
    )

    student_groups = relationship(
        "ElectiveStudentGroup",
        back_populates="elective",
        cascade="all, delete-orphan",
    )


# ============================================================
# ELECTIVE - STUDENT GROUP
# ============================================================

class ElectiveStudentGroup(Base):
    __tablename__ = "elective_student_groups"

    id = Column(Integer, primary_key=True, index=True)

    elective_id = Column(
        Integer,
        ForeignKey("electives.id"),
        nullable=False,
    )

    student_group_id = Column(
        Integer,
        ForeignKey("student_groups.id"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "elective_id",
            "student_group_id",
            name="uq_elective_student_group",
        ),
    )

    elective = relationship(
        "Elective",
        back_populates="student_groups",
    )

    student_group = relationship(
        "StudentGroup",
        back_populates="elective_groups",
    )


# ============================================================
# TIMETABLE ALLOCATION
# ============================================================

class TimetableAllocation(Base):
    __tablename__ = "timetable_allocations"

    id = Column(Integer, primary_key=True, index=True)

    academic_year_id = Column(
        Integer,
        ForeignKey("academic_years.id"),
        nullable=False,
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False,
    )

    faculty_id = Column(
        Integer,
        ForeignKey("faculty.id"),
        nullable=False,
    )

    room_id = Column(
        Integer,
        ForeignKey("rooms.id"),
        nullable=False,
    )

    student_group_id = Column(
        Integer,
        ForeignKey("student_groups.id"),
        nullable=False,
    )

    time_slot_id = Column(
        Integer,
        ForeignKey("time_slots.id"),
        nullable=False,
    )

    academic_year = relationship(
        "AcademicYear",
        back_populates="allocations",
    )

    course = relationship(
        "Course",
        back_populates="allocations",
    )

    faculty = relationship(
        "Faculty",
        back_populates="allocations",
    )

    room = relationship(
        "Room",
        back_populates="allocations",
    )

    student_group = relationship(
        "StudentGroup",
        back_populates="allocations",
    )

    time_slot = relationship(
        "TimeSlot",
        back_populates="allocations",
    )


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)