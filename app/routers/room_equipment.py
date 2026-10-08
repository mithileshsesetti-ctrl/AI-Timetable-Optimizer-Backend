from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RoomEquipment, Room


router = APIRouter(
    prefix="/api/room-equipment",
    tags=["Room Equipment"]
)


@router.get("/")
def get_room_equipment(db: Session = Depends(get_db)):
    equipment = (
        db.query(RoomEquipment)
        .order_by(
            RoomEquipment.room_id,
            RoomEquipment.equipment_name
        )
        .all()
    )

    return equipment


@router.post("/")
def create_room_equipment(
    room_id: int,
    equipment_name: str,
    db: Session = Depends(get_db)
):
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

    equipment_name = equipment_name.strip()

    if not equipment_name:
        raise HTTPException(
            status_code=400,
            detail="Equipment name cannot be empty"
        )

    existing = (
        db.query(RoomEquipment)
        .filter(
            RoomEquipment.room_id == room_id,
            RoomEquipment.equipment_name == equipment_name
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This equipment is already assigned to this room"
        )

    equipment = RoomEquipment(
        room_id=room_id,
        equipment_name=equipment_name
    )

    db.add(equipment)
    db.commit()
    db.refresh(equipment)

    return equipment