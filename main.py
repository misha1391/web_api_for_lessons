from typing import Dict, Any
from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
import user as userdb
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import hashlib
import secrets

app = FastAPI()
templates = Jinja2Templates(directory="templates")

userdb.init("database.db")

# Именно так можно сворачивать в VSCode
# region Jsons
JSON_FILE = "jsons/grades.json"
CLASSES_FILE = "jsons/classes.json"
EVENTS_FILE = "jsons/events.json"
LESSONS_FILE = "jsons/lessons.json"
USERS_FILE = "jsons/users.json"
# endregion

# region Helpers
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
def generate_token() -> str:
    return secrets.token_hex(32)

# Хранилище активных сессий (token -> username)
active_sessions = {}
def check_auth(token: str = None):
    if not token:
        return None
    return active_sessions.get(token)
# endregion

# region api запросы
# region Работа с аккаунтами
@app.post("/api/register")
async def register(data: Dict[str, Any]):
    users = userdb.get_all(userdb.DEF_DB_FILE, "users")

    username   = data.get("username", "").strip()
    password   = data.get("password", "")
    class_code = data.get("class_code")
    email      = data.get("email", "")

    if not (username and password and class_code and email):
        return {"success": False, "error": "Заполните все поля"}

    # Проверка существующего пользователя
    for user in users:
        if user["name"] == username:
            return {"success": False, "error": "Пользователь уже существует"}

    # Создание нового пользователя
    new_user = {
        "name": username,
        "hashedPassword": hash_password(password),
        "email": email,
        "class_code": class_code
    }
    userdb.add("database.db", "users", new_user)

    return {"success": True}
@app.post("/api/login")
async def login(data: Dict[str, Any], response: Response):
    users = userdb.get_all(userdb.DEF_DB_FILE, "users")

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return {"success": False, "error": "Заполните все поля"}

    # Поиск пользователя
    hashed_password = hash_password(password)
    for user in users:
        if user["name"] == username and user["hashedPassword"] == hashed_password:
            # Создание сессии
            token = generate_token()
            active_sessions[token] = username

            response.set_cookie(key="session_token", value=token, httponly=True)
            return {"success": True}

    return {"success": False, "error": "Неверное имя пользователя или пароль"}
@app.post("/api/logout")
async def logout(response: Response, session_token: str = Cookie(None)):
    if session_token and session_token in active_sessions:
        del active_sessions[session_token]

    response.delete_cookie("session_token")
    return RedirectResponse(url="/login", status_code=302)
@app.post("/api/deleteAcc")
async def deleteAcc(response: Response, session_token: str = Cookie(None)):
    if session_token and session_token in active_sessions:
        userdb.delete_by_item(userdb.DEF_DB_FILE, "users", "name", active_sessions[session_token])
        del active_sessions[session_token]
    response.delete_cookie("session_token")
    return RedirectResponse(url="/login", status_code=302)
@app.post("api/changePassword")
async def changePass(rsponse: Response, session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}
    
# endregion
# region Оценки
@app.get("/api/grades")
def get_grades(session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}
    test = userdb.get_all(userdb.DEF_DB_FILE, "grades")
    return test
@app.post("/api/grades")
def add_grade(data: Dict[str, Any], session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    new_grade = {
        "name": data["name"],
        "class_code": data["class_code"],
        "subject": data["subject"],
        "grade": data["grade"],
        "date": data["date"],
        "teacher": data["teacher"]
    }
    userdb.add(userdb.DEF_DB_FILE, "grades", new_grade)
    return {"Success": True, "grade": new_grade}
@app.delete("/api/grades/{grade_id}")
def delete_grade(grade_id: int, session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    deleted_grade = userdb.delete(userdb.DEF_DB_FILE, "grades", grade_id)
    if deleted_grade:
        return deleted_grade
    return {"ERROR": "Нет такой оценки"}
@app.get("/api/grades/{grade_id}")
def get_grade_by_id(grade_id: int, session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    grade = userdb.get_by_id(userdb.DEF_DB_FILE, "grades", grade_id)
    if grade:
        return grade
    return {"ERROR": "Нет такой оценки"}
# endregion
# region Классы
@app.get("/api/classes")
def all_classes(session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}
    answer = []
    class_codes = []
    for i in userdb.get_all(userdb.DEF_DB_FILE, "classes"):
        i["student"] = [i["student"]]
        if i["class_code"] not in class_codes:
            class_codes.append(i["class_code"])
            answer.append(i)
        else:
            for i2 in range(len(answer)):
                if answer[i2]["class_code"] == i["class_code"]:
                    answer[i2]["student"].append(i["student"][0])
    return answer
@app.get("/api/classes/{class_id}")
def get_class_by_id(class_id: int, session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    clas = userdb.get_by_id(userdb.DEF_DB_FILE, "classes", class_id)
    if clas:
        return clas
    return {"ERROR": "Нет такого класса"}
@app.post("/api/classes")
def add_class(data: Dict[str, Any], session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}
    new_class = {
        "class_code": data["class_code"],
        "student": data["students"],
        "year": data["year"],
        "super_teacher": data["super_teacher"]
    }
    userdb.add_multiple(userdb.DEF_DB_FILE, "classes", new_class)
    return {"Success": True, "class": new_class}
@app.delete("/api/classes/{class_id}")
def delete_class_by_id(class_id: int, session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    deleted_class = userdb.delete(userdb.DEF_DB_FILE, "classes", class_id)
    if deleted_class:
        return deleted_class
    return {"ERROR": "Нет такого класса"}
# endregion
# region События
@app.get("/api/events")
def get_events(session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}
    return userdb.get_all(userdb.DEF_DB_FILE, "events")
@app.post("/api/events")
def add_event(data: Dict[str, Any], session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}
    new_event = {
        "class_code": data["class_code"],
        "title": data["title"],
        "date": data["date"],
        "time": data["time"],
        "type": data["type"],
        "description": data["description"]
    }
    userdb.add(userdb.DEF_DB_FILE, "events", new_event)
    return {"Success": True, "class": new_event}
@app.delete("/api/events/{event_id}")
def delete_event(event_id: int, session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    deleted_event = userdb.delete(userdb.DEF_DB_FILE, "events", event_id)
    if deleted_event:
        return deleted_event
    return {"ERROR": "Нет такого класса"}
# endregion
# region Уроки
@app.get("/api/lessons")
def get_lessons(session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}
    return userdb.get_all(userdb.DEF_DB_FILE, "lessons")
@app.post("/api/lessons")
def add_lesson(data: Dict[str, Any], session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    new_lesson = {
        "class_code": data["class_code"],
        "day": data["day"],
        "subject": data["subject"],
        "time_from": data["time_from"],
        "time_to": data["time_to"],
        "type": data["type"]
    }
    userdb.add(userdb.DEF_DB_FILE, "lessons", new_lesson)
    return {"Success": True, "class": new_lesson}
@app.delete("/api/lessons/{lesson_id}")
def delete_lesson(lesson_id: int, session_token: str = Cookie(None)):
    if not check_auth(session_token):
        return {"error": "Не авторизован"}

    deleted_lesson = userdb.delete(userdb.DEF_DB_FILE, "lessons", lesson_id)
    if deleted_lesson:
        return deleted_lesson
    return {"ERROR": "Нет такого класса"}
# endregion
# region Проверка авторизации для API
@app.get("/api/check-auth")
async def check_auth_endpoint(session_token: str = Cookie(None)):
    username = check_auth(session_token)
    if username:
        return {"authenticated": True, "username": username}
    return {"authenticated": False}
# endregion
# endregion

# region Все страницы
# region Страницы аутентификации
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
# endregion
# region Веб-страницы (с проверкой авторизации)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session_token: str = Cookie(None)):
    username = check_auth(session_token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, "username": username})
@app.get("/account", response_class=HTMLResponse)
async def account_page(request: Request, session_token: str = Cookie(None)):
    username = check_auth(session_token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    acounts = userdb.get_all_items(userdb.DEF_DB_FILE, "users", "name, email")
    email = "error"
    for i in acounts:
        if i["name"] == username:
            email = i["email"]
    return templates.TemplateResponse("account.html", {"request": request, "username": username, "email": email})
@app.get("/grades", response_class=HTMLResponse)
async def grades_page(request: Request, session_token: str = Cookie(None)):
    username = check_auth(session_token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("grades.html", {"request": request, "username": username})
@app.get("/classes", response_class=HTMLResponse)
async def classes_page(request: Request, session_token: str = Cookie(None)):
    username = check_auth(session_token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("classes.html", {"request": request, "username": username})
@app.get("/events", response_class=HTMLResponse)
async def events_page(request: Request, session_token: str = Cookie(None)):
    username = check_auth(session_token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("events.html", {"request": request, "username": username})
@app.get("/lessons", response_class=HTMLResponse)
# endregion
# endregion

async def lessons_page(request: Request, session_token: str = Cookie(None)):
    username = check_auth(session_token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("lessons.html", {"request": request, "username": username})
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")