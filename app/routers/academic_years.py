from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AcademicYear


router = APIRouter(
    prefix="/api/academic-years",
    tags=["Academic Years"]
)


@router.get("/")
def get_academic_years(db: Session = Depends(get_db)):
    academic_years = db.query(AcademicYear).all()
    return academic_years


@router.post("/")
def create_academic_year(
    year: int,
    semester: str,
    active: bool = True,
    db: Session = Depends(get_db)
):
    academic_year = AcademicYear(
        year=year,
        semester=semester,
        active=active
    )

    db.add(academic_year)
    db.commit()
    db.refresh(academic_year)

    return academic_year