import sqlite3
from datetime import datetime
import os

def init(db_file: str):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS classes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code TEXT NOT NULL,
            student TEXT NOT NULL,
            year TEXT NOT NULL,
            super_teacher TEXT NOT NULL
        )""") # class
        cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hashedPassword TEXT NOT NULL,
            class_code TEXT NOT NULL
        )""") # users
        cursor.execute("""CREATE TABLE IF NOT EXISTS lessons(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code TEXT NOT NULL,
            day TEXT NOT NULL,
            subject TEXT NOT NULL,
            time_from TEXT NOT NULL,
            time_to TEXT NOT NULL,
            type TEXT NOT NULL
        )""") # lessons
        cursor.execute("""CREATE TABLE IF NOT EXISTS grades(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code TEXT NOT NULL,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            grade TEXT NOT NULL,
            date TEXT NOT NULL,
            teacher TEXT NOT NULL
        )""") # grades
        cursor.execute("""CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code TEXT NOT NULL,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT NOT NULL
        )""") # events
        conn.commit()
def add(db_file: str, where: str, data: tuple):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * from {where}")
        names = [""] * (len(cursor.description)-1)
        for i, desk in enumerate(cursor.description):
            if i != 0:
                names[i-1] += desk[0]
        strNames = ""
        for name in names:
            strNames += name + ", "
        strNames = strNames[0:-2]
        strQues = ("?, " * (len(cursor.description)-1))[0:-2]
        print(f"INSERT INTO {where} ({strNames}) VALUES ({strQues})")
        cursor.execute(f"INSERT INTO {where} ({strNames}) VALUES ({strQues})", data)
        conn.commit()
def get_all(db_file: str, where: str):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {where}")
        tasks = cursor.fetchall()
        return tasks
def get_by_id(db_file: str, task_id):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) # Нужен кортеж, заменяет все "?" в комманде
        tasks = cursor.fetchall()
        return tasks
def update(title, description, db_file: str, task_id):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET title = ?, description = ? WHERE id = ?", (title, description, task_id))  # Нужен кортеж, заменяет все "?" в комманде
        conn.commit()
def delete(title, description, db_file: str, task_id):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))  # Нужен кортеж, заменяет все "?" в комманде
        conn.commit()

if __name__ == "__main__":
    init("database.db")
    add("database.db", "users", ("Лол", "ХОЛ", "safddsg"))
    add("database.db", "users", ("Кек", "ХОЛ", "fdg"))
    print(get_all("database.db", "users"))
