from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FacultySubject, Faculty, Course

router = APIRouter(
    prefix="/api/faculty-subjects",
    tags=["Faculty Subjects"]
)


@router.get("/")
def get_faculty_subjects(db: Session = Depends(get_db)):
    assignments = db.query(FacultySubject).all()
    return assignments


@router.post("/")
def create_faculty_subject(
    faculty_id: int,
    course_id: int,
    db: Session = Depends(get_db)
):
    # Check faculty exists
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()

    if not faculty:
        raise HTTPException(
            status_code=404,
            detail="Faculty not found"
        )

    # Check course exists
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Check duplicate assignment
    existing = (
        db.query(FacultySubject)
        .filter(
            FacultySubject.faculty_id == faculty_id,
            FacultySubject.course_id == course_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This faculty is already assigned to this course"
        )

    assignment = FacultySubject(
        faculty_id=faculty_id,
        course_id=course_id
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment