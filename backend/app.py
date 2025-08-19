from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the To-Do API"}


# CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "tasksdb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")

# Connect to SQLite (database file will be tasks.db)
conn = sqlite3.connect("tasks.db", check_same_thread=False)  # check_same_thread=False is needed for FastAPI
cur = conn.cursor()

# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    task_date TEXT NOT NULL,
    task_time TEXT NOT NULL
)
""")
conn.commit()


class Task(BaseModel):
    description: str
    task_date: str   # YYYY-MM-DD
    task_time: str   # HH:MM

# Add task
@app.post("/add")
def add_task(task: Task):
    cur.execute(
        "INSERT INTO tasks (description, task_date, task_time) VALUES (?, ?, ?)",
        (task.description, task.task_date, task.task_time)
    )
    conn.commit()
    return {"message": "Task added successfully"}

# Get tasks
@app.get("/tasks")
def get_tasks():
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    return [
        {"id": r[0], "description": r[1], "task_date": r[2], "task_time": r[3]}
        for r in rows
    ]

# Update task
@app.put("/update/{task_id}")
def update_task(task_id: int, task: Task):
    cur.execute(
        "UPDATE tasks SET description=?, task_date=?, task_time=? WHERE id=?",
        (task.description, task.task_date, task.task_time, task_id)
    )
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated"}

# Delete task
@app.delete("/delete/{task_id}")
def delete_task(task_id: int):
    cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

# Search task
@app.get("/search/{name}")
def search_task(name: str):
    cur.execute("SELECT * FROM tasks WHERE description LIKE ?", (f"%{name}%",))
    rows = cur.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Task not found")
    return [
        {"id": r[0], "description": r[1], "task_date": r[2], "task_time": r[3]}
        for r in rows
    ]
