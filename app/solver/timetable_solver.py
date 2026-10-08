from ortools.sat.python import cp_model


def solve_timetable(
    courses,
    faculty,
    rooms,
    student_groups,
    time_slots,
    faculty_subjects,
    course_student_groups,
    faculty_availability,
    room_availability,
    room_equipment,
):
    """
    Build and solve the timetable using OR-Tools CP-SAT.

    Returns:
        {
            "status": "OPTIMAL" | "FEASIBLE" | "INFEASIBLE",
            "allocations": [...]
        }
    """

    model = cp_model.CpModel()

    # Candidate allocation variables:
    # (course_id, faculty_id, room_id, group_id, slot_id)
    variables = {}

    # ---------------------------------------------------------
    # Helper functions
    # ---------------------------------------------------------

    def time_overlaps(slot_start, slot_end, avail_start, avail_end):
        return slot_start < avail_end and slot_end > avail_start

    def is_faculty_available(faculty_obj, slot):
        records = [
            a for a in faculty_availability
            if a.faculty_id == faculty_obj.id
            and a.day == slot.day
        ]

        if not records:
            return True

        return any(
            a.available
            and time_overlaps(
                slot.start_time,
                slot.end_time,
                a.start_time,
                a.end_time,
            )
            for a in records
        )

    def is_room_available(room_obj, slot):
        records = [
            a for a in room_availability
            if a.room_id == room_obj.id
            and a.day == slot.day
        ]

        if not records:
            return True

        return any(
            a.available
            and time_overlaps(
                slot.start_time,
                slot.end_time,
                a.start_time,
                a.end_time,
            )
            for a in records
        )

    def room_has_required_equipment(room_obj, course_obj):
        if not course_obj.required_equipment:
            return True

        required = {
            item.strip().lower()
            for item in course_obj.required_equipment.split(",")
            if item.strip()
        }

        available = {
            item.equipment_name.strip().lower()
            for item in room_equipment
            if item.room_id == room_obj.id
        }

        return required.issubset(available)

    def faculty_can_teach(faculty_obj, course_obj):
        return any(
            fs.faculty_id == faculty_obj.id
            and fs.course_id == course_obj.id
            for fs in faculty_subjects
        )

    def group_takes_course(group_obj, course_obj):
        return any(
            csg.course_id == course_obj.id
            and csg.student_group_id == group_obj.id
            for csg in course_student_groups
        )

    # ---------------------------------------------------------
    # Build candidate variables
    # ---------------------------------------------------------

    candidates_by_course = {
        course.id: []
        for course in courses
    }

    for course in courses:
        groups = [
            group
            for group in student_groups
            if group_takes_course(group, course)
        ]

        eligible_faculty = [
            f
            for f in faculty
            if faculty_can_teach(f, course)
        ]

        eligible_rooms = [
            room
            for room in rooms
            if (
                (
                    course.required_room_type is None
                    or room.room_type == course.required_room_type
                )
                and room.capacity >= max(
                    [g.student_count for g in groups],
                    default=0,
                )
                and room_has_required_equipment(room, course)
            )
        ]

        for group in groups:
            for f in eligible_faculty:
                if not all(
                    is_faculty_available(f, slot)
                    for slot in time_slots
                ):
                    pass

                for room in eligible_rooms:
                    for slot in time_slots:
                        if not is_faculty_available(f, slot):
                            continue

                        if not is_room_available(room, slot):
                            continue

                        key = (
                            course.id,
                            f.id,
                            room.id,
                            group.id,
                            slot.id,
                        )

                        variables[key] = model.NewBoolVar(
                            "x_%d_%d_%d_%d_%d" % key
                        )

                        candidates_by_course[course.id].append(key)

    # ---------------------------------------------------------
    # Exact weekly hours for every course/group combination
    # ---------------------------------------------------------

    for course in courses:
        groups = [
            group
            for group in student_groups
            if group_takes_course(group, course)
        ]

        for group in groups:
            group_vars = [
                variables[key]
                for key in candidates_by_course[course.id]
                if key[3] == group.id
            ]

            model.Add(sum(group_vars) == course.hours_per_week)

    # ---------------------------------------------------------
    # Student-group overlap
    # ---------------------------------------------------------

    for group in student_groups:
        for slot in time_slots:
            slot_vars = [
                variables[key]
                for key in variables
                if key[3] == group.id and key[4] == slot.id
            ]

            if slot_vars:
                model.Add(sum(slot_vars) <= 1)

    # ---------------------------------------------------------
    # Faculty overlap
    # ---------------------------------------------------------

    for f in faculty:
        for slot in time_slots:
            slot_vars = [
                variables[key]
                for key in variables
                if key[1] == f.id and key[4] == slot.id
            ]

            if slot_vars:
                model.Add(sum(slot_vars) <= 1)

    # ---------------------------------------------------------
    # Room overlap
    # ---------------------------------------------------------

    for room in rooms:
        for slot in time_slots:
            slot_vars = [
                variables[key]
                for key in variables
                if key[2] == room.id and key[4] == slot.id
            ]

            if slot_vars:
                model.Add(sum(slot_vars) <= 1)

    # ---------------------------------------------------------
    # Same course overlap
    # ---------------------------------------------------------

    for course in courses:
        for slot in time_slots:
            slot_vars = [
                variables[key]
                for key in variables
                if key[0] == course.id and key[4] == slot.id
            ]

            if slot_vars:
                model.Add(sum(slot_vars) <= 1)

    # ---------------------------------------------------------
    # Faculty maximum classes per day
    # ---------------------------------------------------------

    for f in faculty:
        if f.max_classes_per_day and f.max_classes_per_day > 0:
            days = set(slot.day for slot in time_slots)

            for day in days:
                day_vars = [
                    variables[key]
                    for key in variables
                    if key[1] == f.id
                    and next(
                        (
                            slot.day
                            for slot in time_slots
                            if slot.id == key[4]
                        ),
                        None,
                    ) == day
                ]

                if day_vars:
                    model.Add(
                        sum(day_vars) <= f.max_classes_per_day
                    )

    # ---------------------------------------------------------
    # Solve
    # ---------------------------------------------------------

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.INFEASIBLE:
        return {
            "status": "INFEASIBLE",
            "allocations": [],
        }

    if status == cp_model.OPTIMAL:
        status_name = "OPTIMAL"
    elif status == cp_model.FEASIBLE:
        status_name = "FEASIBLE"
    else:
        return {
            "status": "INFEASIBLE",
            "allocations": [],
        }

    allocations = []

    for key, variable in variables.items():
        if solver.Value(variable) == 1:
            course_id, faculty_id, room_id, group_id, slot_id = key

            allocations.append(
                {
                    "course_id": course_id,
                    "faculty_id": faculty_id,
                    "room_id": room_id,
                    "student_group_id": group_id,
                    "time_slot_id": slot_id,
                }
            )

    return {
        "status": status_name,
        "allocations": allocations,
    }
