from abc import ABC, abstractmethod
from typing import List, Optional


class Person(ABC):
    def __init__(self, name: str, age: int, email: str):
        self.__name = name
        self.__age = age
        self.__email = email

    @property
    def name(self): return self.__name
    @property
    def age(self): return self.__age
    @property
    def email(self): return self.__email

    @name.setter
    def name(self, v):
        if not v.strip(): raise ValueError("Имя не может быть пустым.")
        self.__name = v.strip()

    @age.setter
    def age(self, v):
        if not (1 <= v <= 120): raise ValueError("Возраст: 1–120.")
        self.__age = v

    @email.setter
    def email(self, v):
        if "@" not in v: raise ValueError("Некорректный email.")
        self.__email = v

    @abstractmethod
    def get_info(self) -> dict:
        pass


class Student(Person):
    def __init__(self, name: str, age: int, email: str, student_id: str, year: int):
        super().__init__(name, age, email)
        self.__student_id = student_id
        self.year = year
        self.__courses: List["Course"] = []

    @property
    def student_id(self): return self.__student_id
    @property
    def year(self): return self.__year
    @property
    def courses(self): return list(self.__courses)

    @year.setter
    def year(self, v):
        if not (1 <= v <= 6): raise ValueError("Курс: 1–6.")
        self.__year = v

    def enroll(self, course: "Course") -> bool:
        if any(c.course_id == course.course_id for c in self.__courses):
            return False
        self.__courses.append(course)
        course.add_student(self)
        return True

    def drop_course(self, course_id: str) -> bool:
        idx = next((i for i, c in enumerate(self.__courses) if c.course_id == course_id), -1)
        if idx == -1: return False
        course = self.__courses.pop(idx)
        course.remove_student(self.__student_id)
        return True

    def get_info(self) -> dict:
        return {
            "type": "student",
            "student_id": self.__student_id,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "year": self.__year,
            "courses": [{"course_id": c.course_id, "title": c.title} for c in self.__courses],
        }


class Teacher(Person):
    def __init__(self, name: str, age: int, email: str,
                 teacher_id: str, department: str, salary: float):
        super().__init__(name, age, email)
        self.__teacher_id = teacher_id
        self.__department = department
        self.salary = salary
        self.__courses: List["Course"] = []

    @property
    def teacher_id(self): return self.__teacher_id
    @property
    def department(self): return self.__department
    @property
    def salary(self): return self.__salary
    @property
    def courses(self): return list(self.__courses)

    @salary.setter
    def salary(self, v):
        if v < 0: raise ValueError("Зарплата не может быть отрицательной.")
        self.__salary = v

    def assign_course(self, course: "Course"):
        if not any(c.course_id == course.course_id for c in self.__courses):
            self.__courses.append(course)

    def get_info(self) -> dict:
        return {
            "type": "teacher",
            "teacher_id": self.__teacher_id,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "department": self.__department,
            "salary": self.__salary,
            "courses": [{"course_id": c.course_id, "title": c.title} for c in self.__courses],
        }


class Course:
    def __init__(self, course_id: str, title: str, credits: int, teacher: Teacher):
        self.__course_id = course_id
        self.__title = title
        self.__credits = credits
        self.__teacher = teacher
        self.__students: List[Student] = []
        teacher.assign_course(self)

    @property
    def course_id(self): return self.__course_id
    @property
    def title(self): return self.__title
    @property
    def credits(self): return self.__credits
    @property
    def teacher(self): return self.__teacher
    @property
    def students(self): return list(self.__students)

    def add_student(self, student: Student):
        if not any(s.student_id == student.student_id for s in self.__students):
            self.__students.append(student)

    def remove_student(self, student_id: str):
        self.__students = [s for s in self.__students if s.student_id != student_id]

    def get_info(self) -> dict:
        return {
            "course_id": self.__course_id,
            "title": self.__title,
            "credits": self.__credits,
            "teacher": {"teacher_id": self.__teacher.teacher_id, "name": self.__teacher.name},
            "students": [{"student_id": s.student_id, "name": s.name} for s in self.__students],
        }


class Department:
    def __init__(self, dept_id: str, name: str):
        self.__dept_id = dept_id
        self.__name = name
        self.__teachers: List[Teacher] = []
        self.__courses: List[Course] = []

    @property
    def dept_id(self): return self.__dept_id
    @property
    def name(self): return self.__name

    def add_teacher(self, teacher: Teacher):
        if not any(t.teacher_id == teacher.teacher_id for t in self.__teachers):
            self.__teachers.append(teacher)

    def add_course(self, course: Course):
        if not any(c.course_id == course.course_id for c in self.__courses):
            self.__courses.append(course)

    def get_info(self) -> dict:
        return {
            "dept_id": self.__dept_id,
            "name": self.__name,
            "teachers": [{"teacher_id": t.teacher_id, "name": t.name} for t in self.__teachers],
            "courses": [{"course_id": c.course_id, "title": c.title} for c in self.__courses],
        }


class University:
    def __init__(self, name: str):
        self.__name = name
        self.__students: List[Student] = []
        self.__teachers: List[Teacher] = []
        self.__courses: List[Course] = []
        self.__departments: List[Department] = []

    @property
    def name(self): return self.__name

    def add_student(self, s: Student): self.__students.append(s)
    def add_teacher(self, t: Teacher): self.__teachers.append(t)
    def add_course(self, c: Course):   self.__courses.append(c)
    def add_department(self, d: Department): self.__departments.append(d)

    def remove_student(self, student_id: str) -> bool:
        student = self.find_student(student_id)
        if not student: return False
        for course in list(student.courses):
            student.drop_course(course.course_id)
        self.__students = [s for s in self.__students if s.student_id != student_id]
        return True

    def find_student(self, student_id: str) -> Optional[Student]:
        return next((s for s in self.__students if s.student_id == student_id), None)

    def find_teacher(self, teacher_id: str) -> Optional[Teacher]:
        return next((t for t in self.__teachers if t.teacher_id == teacher_id), None)

    def find_course(self, course_id: str) -> Optional[Course]:
        return next((c for c in self.__courses if c.course_id == course_id), None)

    def find_department(self, dept_id: str) -> Optional[Department]:
        return next((d for d in self.__departments if d.dept_id == dept_id), None)

    def get_all_data(self) -> dict:
        return {
            "university": self.__name,
            "students":    [s.get_info() for s in sorted(self.__students, key=lambda x: x.name)],
            "teachers":    [t.get_info() for t in self.__teachers],
            "courses":     [c.get_info() for c in sorted(self.__courses, key=lambda x: x.credits, reverse=True)],
            "departments": [d.get_info() for d in self.__departments],
        }


# ── Начальные данные ──────────────────────────

def create_default_university() -> University:
    uni = University("КГТУ им. И. Раззакова")

    t1 = Teacher("Айбек Марипов",   45, "maripov@kgtu.kg",  "T01", "Программирование", 55000)
    t2 = Teacher("Гүлнара Асанова", 38, "asanova@kgtu.kg",  "T02", "Математика",       48000)
    t3 = Teacher("Нурлан Токтосун", 52, "toktosun@kgtu.kg", "T03", "Экономика",        50000)

    c1 = Course("C01", "Python ООП",             4, t1)
    c2 = Course("C02", "Алгоритмы и структуры", 5, t2)
    c3 = Course("C03", "Макроэкономика",         3, t3)
    c4 = Course("C04", "Базы данных",            4, t1)

    s1 = Student("Азамат Бектенов",  20, "azamat@mail.kg", "S001", 2)
    s2 = Student("Айпери Жолдошева", 19, "aiperi@mail.kg", "S002", 1)
    s3 = Student("Тимур Садыков",    21, "timur@mail.kg",  "S003", 3)
    s4 = Student("Зарина Омурова",   22, "zarina@mail.kg", "S004", 2)
    s5 = Student("Бекзат Усупов",    20, "bekzat@mail.kg", "S005", 1)

    for t in [t1, t2, t3]: uni.add_teacher(t)
    for c in [c1, c2, c3, c4]: uni.add_course(c)
    for s in [s1, s2, s3, s4, s5]: uni.add_student(s)

    s1.enroll(c1); s1.enroll(c2)
    s2.enroll(c1); s2.enroll(c4)
    s3.enroll(c2); s3.enroll(c3)
    s4.enroll(c1); s4.enroll(c3)
    s5.enroll(c4)

    d1 = Department("D01", "Факультет ИТ")
    d2 = Department("D02", "Экономический факультет")
    d1.add_teacher(t1); d1.add_teacher(t2)
    d1.add_course(c1);  d1.add_course(c2); d1.add_course(c4)
    d2.add_teacher(t3); d2.add_course(c3)
    uni.add_department(d1); uni.add_department(d2)

    return uni