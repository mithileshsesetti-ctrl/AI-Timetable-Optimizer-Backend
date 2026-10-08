from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Department

router = APIRouter(
    prefix="/api/departments",
    tags=["Departments"]
)


@router.get("/")
def get_departments(db: Session = Depends(get_db)):
    departments = db.query(Department).all()

    return departments


@router.post("/")
def create_department(
    name: str,
    code: str,
    db: Session = Depends(get_db)
):
    existing_department = (
        db.query(Department)
        .filter(Department.code == code)
        .first()
    )

    if existing_department:
        raise HTTPException(
            status_code=400,
            detail="Department with this code already exists"
        )

    department = Department(
        name=name,
        code=code
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return department