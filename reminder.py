import tkinter as tk
from datetime import datetime, timedelta
import time
import threading
import json
from plyer import notification
import winsound

FILE_NAME = "reminders.json"
reminders = []

# Load reminders
def load_reminders():
    global reminders
    try:
        with open(FILE_NAME, "r") as file:
            reminders = json.load(file)
            refresh_list()
    except:
        reminders = []

# Save reminders
def save_reminders():
    with open(FILE_NAME, "w") as file:
        json.dump(reminders, file)

# Refresh listbox
def refresh_list(data=None):
    listbox.delete(0, tk.END)
    display = data if data else reminders
    for r in display:
        status = "✔" if r.get("done") else ""
        listbox.insert(tk.END, f"{r['task']} at {r['time']} {status}")

# Add reminder
def add_reminder():
    task = entry_task.get()
    time_input = entry_time.get()

    try:
        datetime.strptime(time_input, "%I:%M %p")
    except:
        status_label.config(text="⚠ Use HH:MM AM/PM")
        return

    reminders.append({"task": task, "time": time_input, "done": False})
    save_reminders()
    refresh_list()

    entry_task.delete(0, tk.END)
    entry_time.delete(0, tk.END)
    status_label.config(text="✅ Added")

# Delete
def delete_reminder():
    selected = listbox.curselection()
    if selected:
        reminders.pop(selected[0])
        save_reminders()
        refresh_list()
        status_label.config(text="🗑 Deleted")

# Clear all
def clear_all():
    reminders.clear()
    save_reminders()
    refresh_list()
    status_label.config(text="🧹 Cleared")

# Mark completed
def mark_done():
    selected = listbox.curselection()
    if selected:
        reminders[selected[0]]["done"] = True
        save_reminders()
        refresh_list()
        status_label.config(text="✔ Completed")

# Search
def search_task():
    keyword = search_entry.get().lower()
    filtered = [r for r in reminders if keyword in r["task"].lower()]
    refresh_list(filtered)

# Snooze
def snooze(task):
    new_time = (datetime.now() + timedelta(minutes=5)).strftime("%I:%M %p")
    reminders.append({"task": task, "time": new_time, "done": False})
    save_reminders()
    refresh_list()

# Popup
def show_popup(task):
    popup = tk.Toplevel()
    popup.title("Reminder")
    popup.geometry("250x120")

    tk.Label(popup, text=task).pack(pady=10)

    tk.Button(popup, text="Snooze",
              command=lambda: [snooze(task), popup.destroy()]).pack(pady=5)
    tk.Button(popup, text="Dismiss",
              command=popup.destroy).pack()

# Check reminders
def check_reminders():
    while True:
        now = datetime.now().strftime("%I:%M %p")

        for r in reminders[:]:
            if r["time"] == now and not r["done"]:
                notification.notify(
                    title="Reminder",
                    message=r["task"],
                    timeout=10
                )
                winsound.Beep(1000, 500)
                root.after(0, show_popup, r["task"])

                reminders.remove(r)
                save_reminders()

        time.sleep(30)

# GUI
root = tk.Tk()
root.title("Reminder App")
root.geometry("380x500")

tk.Label(root, text="Reminder App", font=("Arial", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack()

tk.Label(frame, text="Task").pack()
entry_task = tk.Entry(frame, width=30)
entry_task.pack(pady=5)

tk.Label(frame, text="Time (HH:MM AM/PM)").pack()
entry_time = tk.Entry(frame, width=30)
entry_time.pack(pady=5)

tk.Button(frame, text="Add Reminder", command=add_reminder).pack(pady=5)

# Search
search_entry = tk.Entry(frame, width=30)
search_entry.pack(pady=5)
tk.Button(frame, text="Search", command=search_task).pack()

listbox = tk.Listbox(frame, width=45, height=12)
listbox.pack(pady=10)

tk.Button(frame, text="Mark Completed", command=mark_done).pack(pady=2)
tk.Button(frame, text="Delete Selected", command=delete_reminder).pack(pady=2)
tk.Button(frame, text="Clear All", command=clear_all).pack(pady=2)

status_label = tk.Label(root, text="", fg="green")
status_label.pack()

load_reminders()

thread = threading.Thread(target=check_reminders)
thread.daemon = True
thread.start()

root.mainloop()