from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from models import University, Student, Teacher, Course, Department, create_default_university

app = FastAPI(title="UniSystem API")

# ── Единственный экземпляр университета ──────
uni: University = create_default_university()


# ── Pydantic-схемы для входящих данных ───────

class StudentIn(BaseModel):
    name: str
    age: int
    email: str
    student_id: str
    year: int

class TeacherIn(BaseModel):
    name: str
    age: int
    email: str
    teacher_id: str
    department: str
    salary: float

class CourseIn(BaseModel):
    course_id: str
    title: str
    credits: int
    teacher_id: str

class DepartmentIn(BaseModel):
    dept_id: str
    name: str

class EnrollIn(BaseModel):
    student_id: str
    course_id: str


# ── API маршруты ──────────────────────────────

@app.get("/api/data")
def get_all():
    """Вернуть все данные университета одним запросом."""
    return uni.get_all_data()


# Students
@app.post("/api/students", status_code=201)
def add_student(data: StudentIn):
    if uni.find_student(data.student_id):
        raise HTTPException(400, "Студент с таким ID уже существует.")
    try:
        s = Student(data.name, data.age, data.email, data.student_id, data.year)
        uni.add_student(s)
        return s.get_info()
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.delete("/api/students/{student_id}")
def remove_student(student_id: str):
    if not uni.remove_student(student_id):
        raise HTTPException(404, "Студент не найден.")
    return {"ok": True}


# Teachers
@app.post("/api/teachers", status_code=201)
def add_teacher(data: TeacherIn):
    if uni.find_teacher(data.teacher_id):
        raise HTTPException(400, "Преподаватель с таким ID уже существует.")
    try:
        t = Teacher(data.name, data.age, data.email,
                    data.teacher_id, data.department, data.salary)
        uni.add_teacher(t)
        return t.get_info()
    except ValueError as e:
        raise HTTPException(400, str(e))


# Courses
@app.post("/api/courses", status_code=201)
def add_course(data: CourseIn):
    if uni.find_course(data.course_id):
        raise HTTPException(400, "Курс с таким ID уже существует.")
    teacher = uni.find_teacher(data.teacher_id)
    if not teacher:
        raise HTTPException(404, "Преподаватель не найден.")
    try:
        c = Course(data.course_id, data.title, data.credits, teacher)
        uni.add_course(c)
        return c.get_info()
    except ValueError as e:
        raise HTTPException(400, str(e))


# Departments
@app.post("/api/departments", status_code=201)
def add_department(data: DepartmentIn):
    if uni.find_department(data.dept_id):
        raise HTTPException(400, "Факультет с таким ID уже существует.")
    d = Department(data.dept_id, data.name)
    uni.add_department(d)
    return d.get_info()


# Enroll / Drop
@app.post("/api/enroll")
def enroll(data: EnrollIn):
    student = uni.find_student(data.student_id)
    course  = uni.find_course(data.course_id)
    if not student: raise HTTPException(404, "Студент не найден.")
    if not course:  raise HTTPException(404, "Курс не найден.")
    if not student.enroll(course):
        raise HTTPException(400, "Студент уже записан на этот курс.")
    return {"ok": True}

@app.delete("/api/enroll/{student_id}/{course_id}")
def drop(student_id: str, course_id: str):
    student = uni.find_student(student_id)
    if not student: raise HTTPException(404, "Студент не найден.")
    if not student.drop_course(course_id):
        raise HTTPException(400, "Студент не записан на этот курс.")
    return {"ok": True}


# ── Отдаём фронтенд ───────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")


# ── Локальный запуск ──────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)