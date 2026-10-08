from datetime import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TimeSlot


router = APIRouter(
    prefix="/api/time-slots",
    tags=["Time Slots"]
)


@router.get("/")
def get_time_slots(db: Session = Depends(get_db)):
    time_slots = (
        db.query(TimeSlot)
        .order_by(
            TimeSlot.day,
            TimeSlot.slot_number
        )
        .all()
    )

    return time_slots


@router.post("/")
def create_time_slot(
    day: str,
    start_time: str,
    end_time: str,
    slot_number: int,
    db: Session = Depends(get_db)
):
    # Convert HH:MM:SS strings to Python time objects
    try:
        parsed_start_time = time.fromisoformat(start_time)
        parsed_end_time = time.fromisoformat(end_time)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Time must be in HH:MM or HH:MM:SS format"
        )

    if parsed_start_time >= parsed_end_time:
        raise HTTPException(
            status_code=400,
            detail="Start time must be before end time"
        )

    if slot_number <= 0:
        raise HTTPException(
            status_code=400,
            detail="Slot number must be greater than 0"
        )

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

    existing_slot = (
        db.query(TimeSlot)
        .filter(
            TimeSlot.day == day,
            TimeSlot.slot_number == slot_number
        )
        .first()
    )

    if existing_slot:
        raise HTTPException(
            status_code=400,
            detail="A time slot with this day and slot number already exists"
        )

    time_slot = TimeSlot(
        day=day,
        start_time=parsed_start_time,
        end_time=parsed_end_time,
        slot_number=slot_number
    )

    db.add(time_slot)
    db.commit()
    db.refresh(time_slot)

    return time_slot