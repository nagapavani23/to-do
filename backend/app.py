from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# -----------------------------
# Determine SQLite path
# -----------------------------
# Use /app/data/tasks.db inside Kubernetes (volume mount)
# Use ./db/tasks.db locally
if "KUBERNETES_SERVICE_HOST" in os.environ:
    DB_DIR = "/app/data"
else:
    DB_DIR = os.path.join(os.path.dirname(__file__), "db")

os.makedirs(DB_DIR, exist_ok=True)  # ensure folder exists
DB_PATH = os.path.join(DB_DIR, "tasks.db")

# -----------------------------
# Enable CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Connect to SQLite
# -----------------------------
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

# Create tasks table
cur.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    datetime TEXT NOT NULL
)
""")
conn.commit()

# -----------------------------
# Pydantic model
# -----------------------------
class Task(BaseModel):
    description: str
    datetime: str  # Format: YYYY-MM-DDTHH:MM

# -----------------------------
# Endpoints
# -----------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the To-Do API"}

@app.post("/add")
def add_task(task: Task):
    cur.execute(
        "INSERT INTO tasks (description, datetime) VALUES (?, ?)",
        (task.description, task.datetime)
    )
    conn.commit()
    task_id = cur.lastrowid
    return {"id": task_id, "description": task.description, "datetime": task.datetime}

@app.get("/tasks")
def get_tasks():
    cur.execute("SELECT * FROM tasks ORDER BY datetime")
    rows = cur.fetchall()
    return [{"id": r[0], "description": r[1], "datetime": r[2]} for r in rows]

@app.put("/update/{task_id}")
def update_task(task_id: int, task: Task):
    cur.execute(
        "UPDATE tasks SET description=?, datetime=? WHERE id=?",
        (task.description, task.datetime, task_id)
    )
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": task_id, "description": task.description, "datetime": task.datetime}

@app.delete("/delete/{task_id}")
def delete_task(task_id: int):
    cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}
