from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "postgres-service")
DB_NAME = os.getenv("DB_NAME", "tasksdb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS
    )

class Task(BaseModel):
    description: str

@app.on_event("startup")
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, description TEXT);")
    conn.commit()
    conn.close()

@app.get("/tasks")
def get_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, description FROM tasks;")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "description": r[1]} for r in rows]

@app.post("/add")
def add_task(task: Task):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (description) VALUES (%s);", (task.description,))
    conn.commit()
    conn.close()
    return {"message": "Task added"}

@app.put("/update/{task_id}")
def update_task(task_id: int, task: Task):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET description = %s WHERE id = %s;", (task.description, task_id))
    conn.commit()
    conn.close()
    return {"message": "Task updated"}

@app.delete("/delete/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Task deleted"}
