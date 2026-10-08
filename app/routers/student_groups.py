from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import StudentGroup, Department


router = APIRouter(
    prefix="/api/student-groups",
    tags=["Student Groups"]
)


@router.get("/")
def get_student_groups(db: Session = Depends(get_db)):
    student_groups = db.query(StudentGroup).all()
    return student_groups


@router.post("/")
def create_student_group(
    group_code: str,
    department_id: int,
    year: int,
    section: str,
    student_count: int,
    db: Session = Depends(get_db)
):
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

    existing_group = (
        db.query(StudentGroup)
        .filter(StudentGroup.group_code == group_code)
        .first()
    )

    if existing_group:
        raise HTTPException(
            status_code=400,
            detail="Student group with this code already exists"
        )

    if student_count <= 0:
        raise HTTPException(
            status_code=400,
            detail="Student count must be greater than 0"
        )

    student_group = StudentGroup(
        group_code=group_code,
        department_id=department_id,
        year=year,
        section=section,
        student_count=student_count
    )

    db.add(student_group)
    db.commit()
    db.refresh(student_group)

    return student_group