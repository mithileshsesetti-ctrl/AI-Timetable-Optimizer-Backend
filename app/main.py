from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth,
    academic_years,
    courses,
    course_student_groups,
    departments,
    electives,
    faculty,
    faculty_availability,
    faculty_subjects,
    rooms,
    room_availability,
    room_equipment,
    student_groups,
    timetable,
    time_slots,
)

app = FastAPI(
    title="AI Timetable Optimizer",
    description="AI-powered college timetable optimization system",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://pixel-perfect.sesettinagamithilesh.workers.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(academic_years.router)
app.include_router(courses.router)
app.include_router(course_student_groups.router)
app.include_router(departments.router)
app.include_router(electives.router)
app.include_router(faculty.router)
app.include_router(faculty_availability.router)
app.include_router(faculty_subjects.router)
app.include_router(rooms.router)
app.include_router(room_availability.router)
app.include_router(room_equipment.router)
app.include_router(student_groups.router)
app.include_router(timetable.router)
app.include_router(time_slots.router)


@app.get("/")
def root():
    return {
        "message": "AI Timetable Optimizer API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
