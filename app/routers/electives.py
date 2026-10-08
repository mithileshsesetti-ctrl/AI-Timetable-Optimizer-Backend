from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Elective, Course, ElectiveStudentGroup, StudentGroup


router = APIRouter(
    prefix="/api/electives",
    tags=["Electives"]
)


@router.get("/")
def get_electives(db: Session = Depends(get_db)):
    electives = db.query(Elective).all()
    return electives


@router.post("/")
def create_elective(
    course_id: int,
    elective_name: str,
    multidisciplinary: bool = False,
    db: Session = Depends(get_db)
):
    # Check course exists
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

    elective_name = elective_name.strip()

    if not elective_name:
        raise HTTPException(
            status_code=400,
            detail="Elective name cannot be empty"
        )

    elective = Elective(
        course_id=course_id,
        elective_name=elective_name,
        multidisciplinary=multidisciplinary
    )

    db.add(elective)
    db.commit()
    db.refresh(elective)

    return elective


@router.get("/{elective_id}/student-groups")
def get_elective_student_groups(
    elective_id: int,
    db: Session = Depends(get_db)
):
    elective = (
        db.query(Elective)
        .filter(Elective.id == elective_id)
        .first()
    )

    if not elective:
        raise HTTPException(
            status_code=404,
            detail="Elective not found"
        )

    mappings = (
        db.query(ElectiveStudentGroup)
        .filter(ElectiveStudentGroup.elective_id == elective_id)
        .all()
    )

    return mappings


@router.post("/{elective_id}/student-groups")
def add_student_group_to_elective(
    elective_id: int,
    student_group_id: int,
    db: Session = Depends(get_db)
):
    # Check elective exists
    elective = (
        db.query(Elective)
        .filter(Elective.id == elective_id)
        .first()
    )

    if not elective:
        raise HTTPException(
            status_code=404,
            detail="Elective not found"
        )

    # Check student group exists
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
        db.query(ElectiveStudentGroup)
        .filter(
            ElectiveStudentGroup.elective_id == elective_id,
            ElectiveStudentGroup.student_group_id == student_group_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This student group is already assigned to this elective"
        )

    mapping = ElectiveStudentGroup(
        elective_id=elective_id,
        student_group_id=student_group_id
    )

    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    return mapping
