from datetime import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RoomAvailability, Room


router = APIRouter(
    prefix="/api/room-availability",
    tags=["Room Availability"]
)


@router.get("/")
def get_room_availability(db: Session = Depends(get_db)):
    availability = (
        db.query(RoomAvailability)
        .order_by(
            RoomAvailability.room_id,
            RoomAvailability.day,
            RoomAvailability.start_time
        )
        .all()
    )

    return availability


@router.post("/")
def create_room_availability(
    room_id: int,
    day: str,
    start_time: time,
    end_time: time,
    available: bool = True,
    db: Session = Depends(get_db)
):
    # Check that room exists
    room = (
        db.query(Room)
        .filter(Room.id == room_id)
        .first()
    )

    if not room:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
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

    # Check duplicate record
    existing = (
        db.query(RoomAvailability)
        .filter(
            RoomAvailability.room_id == room_id,
            RoomAvailability.day == day,
            RoomAvailability.start_time == start_time,
            RoomAvailability.end_time == end_time
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This room availability record already exists"
        )

    availability_record = RoomAvailability(
        room_id=room_id,
        day=day,
        start_time=start_time,
        end_time=end_time,
        available=available
    )

    db.add(availability_record)
    db.commit()
    db.refresh(availability_record)

    return availability_record