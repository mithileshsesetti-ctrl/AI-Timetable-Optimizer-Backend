from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Faculty, Department


router = APIRouter(
    prefix="/api/faculty",
    tags=["Faculty"]
)


@router.get("/")
def get_faculty(db: Session = Depends(get_db)):
    faculty = db.query(Faculty).all()
    return faculty


@router.post("/")
def create_faculty(
    faculty_code: str,
    name: str,
    department_id: int,
    max_classes_per_day: int = 0,
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

    # Check duplicate faculty code
    existing_faculty = (
        db.query(Faculty)
        .filter(Faculty.faculty_code == faculty_code)
        .first()
    )

    if existing_faculty:
        raise HTTPException(
            status_code=400,
            detail="Faculty with this code already exists"
        )

    # Validate maximum classes
    if max_classes_per_day < 0:
        raise HTTPException(
            status_code=400,
            detail="max_classes_per_day cannot be negative"
        )

    faculty_member = Faculty(
        faculty_code=faculty_code,
        name=name,
        department_id=department_id,
        max_classes_per_day=max_classes_per_day
    )

    db.add(faculty_member)
    db.commit()
    db.refresh(faculty_member)

    return faculty_member