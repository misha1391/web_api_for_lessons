import sqlite3
from typing import Dict, Any, List
from datetime import datetime
import json
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
def add(db_file: str, where: str, data: Dict[str, Any]):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        strNames = ""
        for key in data:
            strNames += key + ", "
        strNames = strNames[0:-2]
        values = ()
        print("data:", data)
        for key in data:
            print("Key:", key)
            print("Value:", data[key])
            values += (data[key],)
        strQues = ", ".join("?" * (len(data)))
        print(f"INSERT INTO {where} ({strNames}) VALUES ({strQues})", values)
        cursor.execute(f"INSERT INTO {where} ({strNames}) VALUES ({strQues})", values)
        conn.commit()
def add_multiple(db_file: str, where: str, data: List[Dict[str, Any]]):
    for i in data:
        for key, val in i.items():
            if type(val) == list:
                for dat in val:
                    datToAdd = i
                    datToAdd[key] = dat
                    add(db_file, where, datToAdd)
            else:
                print("Error: userdb::add_multiple(), given data haven`t got list in it")
def get_all(db_file: str, table: str):
    with sqlite3.connect(db_file) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        returnable = [dict(row) for row in rows]
        print("get_all returns:", returnable)
        return returnable
# def get_all(db_file: str, where: str):
#     with sqlite3.connect(db_file) as conn:
#         cursor = conn.cursor()
#         conn.row_factory = sqlite3.Row
#         cursor.execute(f"SELECT * FROM {where}")
#         print("userdb::get_all()::cursor.desciption =", cursor.description)
#         keys = [i[0] for i in cursor.description]
#         values = cursor.fetchall() # fetchall можно вызвать только 1 раз!
#         print("values:", values)
#         print("keys:", keys)
#         items = []
#         for iv in range(len(values)):
#             item = {keys[ik]: values[iv][ik] for ik in range(len(keys))}
#             print("item:", item)
#             items.append(item)
#         return items
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
    add("todo.db", "users", {"name": "Лол", "hashedPassword": "ХОЛ", "class_code": "safddsg"})
    add("todo.db", "users", {"name": "Кек", "hashedPassword": "ХОЛ", "class_code": "fdg"})
    override_by_id("todo.db", "users", 0, ("Лол2", "ХОЛ2", "safddsg2"))
    all = list(get_all("todo.db", "users"))
    print("all:", all)
    # all[0] = [0, "Лох3", "ХОЛ3", "dsfgd3"]
    override("todo.db", "users", all)
    # print("deleted data:", delete("todo.db", "users", 1))
    print(get_all("todo.db", "users"))
