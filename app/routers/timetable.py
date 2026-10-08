from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.timetable_service import generate_and_save_timetable


router = APIRouter(
    prefix="/api/timetable",
    tags=["Timetable"]
)


@router.post("/generate/{academic_year_id}")
def generate_timetable_api(
    academic_year_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = generate_and_save_timetable(
            db=db,
            academic_year_id=academic_year_id
        )

        # ---------------------------------------------------------
        # INFEASIBLE TIMETABLE
        # ---------------------------------------------------------
        if result["status"] == "INFEASIBLE":
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "INFEASIBLE",
                    "message": (
                        "No feasible timetable could be generated "
                        "with the current constraints."
                    ),
                    "reason": (
                        "One or more hard constraints cannot be "
                        "satisfied with the available resources."
                    )
                }
            )

        return result

    except HTTPException:
        # Keep the original HTTP error status.
        raise

    except ValueError as e:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Timetable generation failed: {str(e)}"
        )


@router.get("/")
def get_timetable(
    academic_year_id: int,
    db: Session = Depends(get_db)
):
    from app.models import TimetableAllocation

    allocations = (
        db.query(TimetableAllocation)
        .filter(
            TimetableAllocation.academic_year_id == academic_year_id
        )
        .all()
    )

    return allocations