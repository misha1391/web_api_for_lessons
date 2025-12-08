import sqlite3
from datetime import datetime
import os

DEF_DB_FILE = "database.db"

def init(db_file: str):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS classes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code TEXT NOT NULL,
            student TEXT NOT NULL,
            year TEXT NOT NULL,
            super_teacher TEXT NOT NULL
        )""") # classes
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
        print(f"INSERT INTO {where} ({strNames}) VALUES ({strQues})", data)
        cursor.execute(f"INSERT INTO {where} ({strNames}) VALUES ({strQues})", tuple([data for key in data]))
        conn.commit()
def get_all(db_file: str, where: str):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {where}")
        tasks = tuple(cursor.fetchall())
        return tasks
def get_by_id(db_file: str, where: str, id: int):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {where} WHERE id = ?", (id,)) # Нужен кортеж, заменяет все "?" в комманде
        tasks = cursor.fetchall()
        return tasks
def override_by_id(db_file: str, where: str, id: int, data: tuple):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {where}")
        names = [""] * (len(cursor.description) - 1)
        for i, desk in enumerate(cursor.description):
            if i != 0:
                names[i - 1] += desk[0]
        strNames = ""
        for name in names:
            strNames += name + " = ?, "
        strNames = strNames[0:-2]
        # print(f"UPDATE {where} SET {strNames} WHERE id = {id}")
        cursor.execute(f"UPDATE {where} SET {strNames} WHERE id = {id}", data)
        conn.commit()
def override(db_file: str, where: str, data: tuple):
    for dat in data:
        override_by_id(db_file, where, dat[0], dat[1:])
def delete(db_file: str, where: str, task_id: int):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {where} WHERE id = {task_id}") # Писать так или как ниже без разницы
        deleted_data = cursor.fetchall()
        cursor.execute(f"DELETE FROM {where} WHERE id = ?", (task_id,))  # Нужен кортеж, заменяет все "?" в комманде
        conn.commit()
        return deleted_data
if __name__ == "__main__":
    init("todo.db")
    add("todo.db", "users", ("Лол", "ХОЛ", "safddsg"))
    add("todo.db", "users", ("Кек", "ХОЛ", "fdg"))
    override_by_id("todo.db", "users", 0, ("Лол2", "ХОЛ2", "safddsg2"))
    all = list(get_all("todo.db", "users"))
    all[0] = [0, "Лох3", "ХОЛ3", "dsfgd3"]
    override("todo.db", "users", all)
    # print("deleted data:", delete("todo.db", "users", 1))
    print(get_all("todo.db", "users"))
