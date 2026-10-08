from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Room, Department
from app.models.models import RoomType


router = APIRouter(
    prefix="/api/rooms",
    tags=["Rooms"]
)


@router.get("/")
def get_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).all()
    return rooms


@router.post("/")
def create_room(
    room_code: str,
    name: str,
    room_type: RoomType,
    capacity: int,
    department_id: int | None = None,
    db: Session = Depends(get_db)
):
    # Check department if one was provided
    if department_id is not None:
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

    # Check duplicate room code
    existing_room = (
        db.query(Room)
        .filter(Room.room_code == room_code)
        .first()
    )

    if existing_room:
        raise HTTPException(
            status_code=400,
            detail="Room with this code already exists"
        )

    # Validate capacity
    if capacity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Room capacity must be greater than 0"
        )

    room = Room(
        room_code=room_code,
        name=name,
        room_type=room_type,
        capacity=capacity,
        department_id=department_id
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return room