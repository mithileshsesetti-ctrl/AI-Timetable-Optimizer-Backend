from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CourseStudentGroup, Course, StudentGroup


router = APIRouter(
    prefix="/api/course-student-groups",
    tags=["Course Student Groups"]
)


@router.get("/")
def get_course_student_groups(db: Session = Depends(get_db)):
    mappings = (
        db.query(CourseStudentGroup)
        .order_by(
            CourseStudentGroup.course_id,
            CourseStudentGroup.student_group_id
        )
        .all()
    )

    return mappings


@router.post("/")
def create_course_student_group(
    course_id: int,
    student_group_id: int,
    db: Session = Depends(get_db)
):
    # Check that course exists
    course = (
        db.query(Course)
        .filter(Course.id == course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Check that student group exists
    student_group = (
        db.query(StudentGroup)
        .filter(StudentGroup.id == student_group_id)
        .first()
    )

    if not student_group:
        raise HTTPException(
            status_code=404,
            detail="Student group not found"
        )

    # Check duplicate mapping
    existing = (
        db.query(CourseStudentGroup)
        .filter(
            CourseStudentGroup.course_id == course_id,
            CourseStudentGroup.student_group_id == student_group_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This course is already assigned to this student group"
        )

    mapping = CourseStudentGroup(
        course_id=course_id,
        student_group_id=student_group_id
    )

    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    return mapping