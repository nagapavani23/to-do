const API_URL = "http://backend-service:8000";

async function loadTasks() {
  const res = await fetch(`${API_URL}/tasks`);
  const tasks = await res.json();
  const list = document.getElementById("taskList");
  list.innerHTML = "";
  tasks.forEach(task => {
    const li = document.createElement("li");
    li.innerHTML = `
      ${task.description} 
      <button onclick="deleteTask(${task.id})">Delete</button>
      <button onclick="editTask(${task.id}, '${task.description}')">Update</button>
    `;
    list.appendChild(li);
  });
}

async function addTask() {
  const taskInput = document.getElementById("task");
  if (!taskInput.value.trim()) return;
  await fetch(`${API_URL}/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description: taskInput.value })
  });
  taskInput.value = "";
  loadTasks();
}

async function deleteTask(id) {
  await fetch(`${API_URL}/delete/${id}`, { method: "DELETE" });
  loadTasks();
}

async function editTask(id, oldDescription) {
  const newDescription = prompt("Update task:", oldDescription);
  if (newDescription && newDescription.trim()) {
    await fetch(`${API_URL}/update/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: newDescription })
    });
    loadTasks();
  }
}

loadTasks();
