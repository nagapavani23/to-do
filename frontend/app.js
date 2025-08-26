 const API_URL = "/api";
//  const API_URL = "http://127.0.0.1:8000";
// const API_URL = "http://48.214.207.181/api"; // For server

// Track reminder counts for tasks
const reminderCounts = {};

// ----------------------
// Render a single task
// ----------------------
function renderTask(task, fromSearch = false) {
  const li = document.createElement("li");
  li.dataset.id = task.id;

  const taskTime = new Date(task.datetime);
  const now = new Date();

  li.innerHTML = `
    <span>
      <strong>${task.description}</strong><br>
      <small>${task.datetime}</small>
    </span>
    <div class="btn-group">
      <button class="btn-update" onclick="editTask(${task.id}, '${task.description}', '${task.datetime}')">Update</button>
      <button class="btn-delete">${fromSearch ? "Remove" : "Delete"}</button>
    </div>
  `;

  li.querySelector(".btn-delete").onclick = () => {
    if (fromSearch) {
      li.remove();
    } else {
      deleteTask(task.id);
    }
  };

  if (taskTime <= now) li.classList.add("highlight");
  return li;
}

// ----------------------
// Load all tasks from backend
// ----------------------
async function loadTasks() {
  try {
    const res = await fetch(`${API_URL}/tasks`);
    const tasks = await res.json();
    const list = document.getElementById("taskList");
    list.innerHTML = "";
    tasks.forEach(task => list.appendChild(renderTask(task)));
  } catch (err) {
    console.error("Error loading tasks:", err);
  }
}

// ----------------------
// Add a new task
// ----------------------
async function addTask() {
  const taskInput = document.getElementById("task");
  const timeInput = document.getElementById("taskTime");

  if (!taskInput.value.trim() || !timeInput.value) {
    return alert("Enter task and datetime");
  }

  try {
    await fetch(`${API_URL}/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        description: taskInput.value,
        datetime: timeInput.value
      })
    });

    taskInput.value = "";
    timeInput.value = "";
    await loadTasks(); // refresh list immediately
  } catch (err) {
    console.error("Error adding task:", err);
  }
}

// ----------------------
// Delete task
// ----------------------
async function deleteTask(id) {
  try {
    await fetch(`${API_URL}/delete/${id}`, { method: "DELETE" });
    await loadTasks();
  } catch (err) {
    console.error("Error deleting task:", err);
  }
}

// ----------------------
// Edit/Update task
// ----------------------
async function editTask(id, oldDescription, oldDatetime) {
  const newDescription = prompt("Update task:", oldDescription);
  const newDatetime = prompt("Update date & time (YYYY-MM-DDTHH:MM):", oldDatetime);

  if (newDescription && newDatetime) {
    try {
      await fetch(`${API_URL}/update/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          description: newDescription,
          datetime: newDatetime
        })
      });

      reminderCounts[id] = 0; // reset reminder
      await loadTasks();
    } catch (err) {
      console.error("Error updating task:", err);
    }
  }
}

// ----------------------
// Search tasks
// ----------------------
async function searchTasks() {
  const query = document.getElementById("searchInput").value.toLowerCase().trim();
  const resultsList = document.getElementById("searchResults");

  // Always clear previous results
  resultsList.innerHTML = "";

  if (!query) return; // <-- If search is empty, stop here

  try {
    const res = await fetch(`${API_URL}/tasks`);
    const tasks = await res.json();

    // Filter tasks that match
    const matched = tasks.filter(task =>
      task.description.toLowerCase().includes(query)
    );

    // Render only the new matched tasks
    matched.forEach(task => {
      if (!resultsList.querySelector(`[data-id="${task.id}"]`)) {
        resultsList.appendChild(renderTask(task, true));
      }
    });
  } catch (err) {
    console.error("Error searching tasks:", err);
  }
}


// ----------------------
// Check reminders & highlight
// ----------------------
async function checkNotifications() {
  try {
    const res = await fetch(`${API_URL}/tasks`);
    const tasks = await res.json();
    const now = new Date();

    const listItems = document.querySelectorAll("#taskList li");
    listItems.forEach(li => {
      const datetimeText = li.querySelector("span small").innerText;
      const taskTime = new Date(datetimeText);
      const taskDescription = li.querySelector("span strong").innerText;
      const taskId = li.dataset.id;

      if (taskTime <= now) li.classList.add("highlight");

      if (!(taskId in reminderCounts)) reminderCounts[taskId] = 0;

      if (
        reminderCounts[taskId] < 3 &&
        Math.abs(taskTime - now) < 60000
      ) {
        alert(`⏰ Reminder: ${taskDescription}`);
        reminderCounts[taskId] += 1;
      }
    });
  } catch (err) {
    console.error("Error checking notifications:", err);
  }
}

// ----------------------
// Initialize on page load
// ----------------------
window.onload = () => {
  loadTasks();
  setInterval(loadTasks, 60000); // refresh tasks every minute
  setInterval(checkNotifications, 30000); // check reminders every 30s

  const searchInput = document.getElementById("searchInput");
  if (searchInput) searchInput.addEventListener("input", searchTasks);
};
