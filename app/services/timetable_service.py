from app.models import (
    AcademicYear,
    Course,
    Faculty,
    Room,
    StudentGroup,
    TimeSlot,
    FacultySubject,
    CourseStudentGroup,
    FacultyAvailability,
    RoomAvailability,
    RoomEquipment,
    TimetableAllocation,
)

from app.solver.timetable_solver import solve_timetable


def generate_and_save_timetable(db, academic_year_id: int):
    academic_year = (
        db.query(AcademicYear)
        .filter(AcademicYear.id == academic_year_id)
        .first()
    )

    if not academic_year:
        raise ValueError(
            f"Academic year with id {academic_year_id} was not found."
        )

    courses = db.query(Course).all()
    faculty = db.query(Faculty).all()
    rooms = db.query(Room).all()
    student_groups = db.query(StudentGroup).all()
    time_slots = db.query(TimeSlot).all()

    faculty_subjects = db.query(FacultySubject).all()
    course_student_groups = db.query(CourseStudentGroup).all()

    faculty_availability = db.query(FacultyAvailability).all()
    room_availability = db.query(RoomAvailability).all()
    room_equipment = db.query(RoomEquipment).all()

    if not courses:
        raise ValueError("No courses are available.")

    if not faculty:
        raise ValueError("No faculty members are available.")

    if not rooms:
        raise ValueError("No rooms are available.")

    if not student_groups:
        raise ValueError("No student groups are available.")

    if not time_slots:
        raise ValueError("No time slots are available.")

    result = solve_timetable(
        courses=courses,
        faculty=faculty,
        rooms=rooms,
        student_groups=student_groups,
        time_slots=time_slots,
        faculty_subjects=faculty_subjects,
        course_student_groups=course_student_groups,
        faculty_availability=faculty_availability,
        room_availability=room_availability,
        room_equipment=room_equipment,
    )

    if result["status"] == "INFEASIBLE":
        return {
            "status": "INFEASIBLE",
            "allocations": [],
        }

    # Verify that every course/group combination received
    # exactly the requested number of weekly sessions.
    generated_counts = {}

    for allocation in result["allocations"]:
        key = (
            allocation["course_id"],
            allocation["student_group_id"],
        )

        generated_counts[key] = generated_counts.get(key, 0) + 1

    for course in courses:
        groups = [
            group
            for group in student_groups
            if any(
                csg.course_id == course.id
                and csg.student_group_id == group.id
                for csg in course_student_groups
            )
        ]

        for group in groups:
            key = (course.id, group.id)
            actual_count = generated_counts.get(key, 0)

            if actual_count != course.hours_per_week:
                raise ValueError(
                    f"Course {course.course_code} for group "
                    f"{group.group_code} requires "
                    f"{course.hours_per_week} sessions, but "
                    f"{actual_count} were generated."
                )

    # Remove any previously generated timetable for this
    # academic year before saving the new one.
    (
        db.query(TimetableAllocation)
        .filter(
            TimetableAllocation.academic_year_id
            == academic_year_id
        )
        .delete(synchronize_session=False)
    )

    saved_allocations = []

    for allocation in result["allocations"]:
        record = TimetableAllocation(
            academic_year_id=academic_year_id,
            course_id=allocation["course_id"],
            faculty_id=allocation["faculty_id"],
            room_id=allocation["room_id"],
            student_group_id=allocation["student_group_id"],
            time_slot_id=allocation["time_slot_id"],
        )

        db.add(record)
        saved_allocations.append(record)

    db.commit()

    for record in saved_allocations:
        db.refresh(record)

    return {
        "status": result["status"],
        "allocations": [
            {
                "id": record.id,
                "academic_year_id": record.academic_year_id,
                "course_id": record.course_id,
                "faculty_id": record.faculty_id,
                "room_id": record.room_id,
                "student_group_id": record.student_group_id,
                "time_slot_id": record.time_slot_id,
            }
            for record in saved_allocations
        ],
    }
