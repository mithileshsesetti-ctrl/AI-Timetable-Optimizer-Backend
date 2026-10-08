from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from app.database import get_db
from app.models import Course, Department
from app.models.models import CourseType, RoomType

router = APIRouter(
    prefix="/api/courses",
    tags=["Courses"]
)


@router.get("/")
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return courses


@router.post("/")
def create_course(
    course_code: str,
    name: str,
    department_id: int,
    year: int,
    semester: str,
    credits: int,
    hours_per_week: int,
    course_type: CourseType,
    required_room_type: RoomType | None = None,
    required_equipment: str | None = None,
    db: Session = Depends(get_db)
):
    # Check department
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    # Check duplicate course code
    existing_course = (
        db.query(Course)
        .filter(Course.course_code == course_code)
        .first()
    )

    if existing_course:
        raise HTTPException(
            status_code=400,
            detail="Course with this code already exists"
        )

    # Validate credits
    if credits <= 0:
        raise HTTPException(
            status_code=400,
            detail="Credits must be greater than 0"
        )

    # Validate weekly hours
    if hours_per_week <= 0:
        raise HTTPException(
            status_code=400,
            detail="Hours per week must be greater than 0"
        )

    course = Course(
        course_code=course_code,
        name=name,
        department_id=department_id,
        year=year,
        semester=semester,
        credits=credits,
        hours_per_week=hours_per_week,
        course_type=course_type,
        required_room_type=required_room_type,
        required_equipment=required_equipment
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return course