from datetime import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FacultyAvailability, Faculty


router = APIRouter(
    prefix="/api/faculty-availability",
    tags=["Faculty Availability"]
)


@router.get("/")
def get_faculty_availability(db: Session = Depends(get_db)):
    availability = (
        db.query(FacultyAvailability)
        .order_by(
            FacultyAvailability.faculty_id,
            FacultyAvailability.day,
            FacultyAvailability.start_time
        )
        .all()
    )

    return availability


@router.post("/")
def create_faculty_availability(
    faculty_id: int,
    day: str,
    start_time: time,
    end_time: time,
    available: bool = True,
    db: Session = Depends(get_db)
):
    # Check that faculty exists
    faculty = (
        db.query(Faculty)
        .filter(Faculty.id == faculty_id)
        .first()
    )

    if not faculty:
        raise HTTPException(
            status_code=404,
            detail="Faculty not found"
        )

    # Validate time
    if start_time >= end_time:
        raise HTTPException(
            status_code=400,
            detail="Start time must be before end time"
        )

    # Validate day
    valid_days = {
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday"
    }

    if day not in valid_days:
        raise HTTPException(
            status_code=400,
            detail="Day must be Monday, Tuesday, Wednesday, Thursday, Friday, or Saturday"
        )

    # Check duplicate availability record
    existing = (
        db.query(FacultyAvailability)
        .filter(
            FacultyAvailability.faculty_id == faculty_id,
            FacultyAvailability.day == day,
            FacultyAvailability.start_time == start_time,
            FacultyAvailability.end_time == end_time
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This faculty availability record already exists"
        )

    availability_record = FacultyAvailability(
        faculty_id=faculty_id,
        day=day,
        start_time=start_time,
        end_time=end_time,
        available=available
    )

    db.add(availability_record)
    db.commit()
    db.refresh(availability_record)

    return availability_record