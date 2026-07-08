import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

FILE = "tasks.json"


class TodoApp:

    def __init__(self, root):

        self.root = root
        self.root.title("To-Do Manager")
        self.root.geometry("950x720")
        self.root.configure(bg="#eef1f7")

        self.tasks = []

        self.load_tasks()

        self.build_ui()

        self.refresh_tasks()

    def build_ui(self):

        header = tk.Label(
            self.root,
            text="📋 Smart To-Do Manager",
            font=("Helvetica", 22, "bold"),
            bg="#6c5ce7",
            fg="white",
            pady=12
        )
        header.pack(fill="x")

        form = tk.Frame(self.root, bg="#eef1f7")
        form.pack(pady=15)

        tk.Label(form, text="Task", bg="#eef1f7").grid(row=0, column=0)

        self.task_var = tk.StringVar()
        tk.Entry(form, textvariable=self.task_var, width=30).grid(row=0, column=1, padx=8)

        tk.Label(form, text="Priority", bg="#eef1f7").grid(row=0, column=2)

        self.priority = ttk.Combobox(
            form,
            values=["High", "Medium", "Low"],
            width=10
        )
        self.priority.set("Medium")
        self.priority.grid(row=0, column=3, padx=8)

        tk.Label(form, text="Due Date", bg="#eef1f7").grid(row=0, column=4)

        self.due = tk.Entry(form, width=12)
        self.due.insert(0, "YYYY-MM-DD")
        self.due.grid(row=0, column=5, padx=8)

        tk.Button(
            form,
            text="Add Task",
            bg="#00b894",
            fg="white",
            command=self.add_task
        ).grid(row=0, column=6, padx=10)

        search_frame = tk.Frame(self.root, bg="#eef1f7")
        search_frame.pack()

        tk.Label(search_frame, text="Search", bg="#eef1f7").pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.refresh_tasks())

        tk.Entry(search_frame, textvariable=self.search_var).pack(side="left", padx=10)

        columns = ("Task", "Priority", "Due Date", "Status")

        self.tree = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings",
            height=10
        )

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column("Task", width=400)
        self.tree.column("Priority", width=100, anchor="center")
        self.tree.column("Due Date", width=120, anchor="center")
        self.tree.column("Status", width=100, anchor="center")

        self.tree.pack(pady=10)

        btn = tk.Frame(self.root, bg="#eef1f7")
        btn.pack()

        tk.Button(
            btn,
            text="✔ Complete",
            bg="#2ecc71",
            fg="white",
            command=self.complete_task
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            btn,
            text="🗑 Delete",
            bg="#e74c3c",
            fg="white",
            command=self.delete_task
        ).grid(row=0, column=1, padx=6)

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress.pack(pady=10)

        self.chart_frame = tk.LabelFrame(
            self.root,
            text="📊 Analytics Dashboard",
            font=("Helvetica", 12, "bold")
        )

        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=20)


    def add_task(self):

        task = self.task_var.get().strip()

        if not task:
            messagebox.showwarning("Warning", "Enter a task")
            return

        due = self.due.get()

        self.tasks.append({
            "task": task,
            "priority": self.priority.get(),
            "due": due,
            "status": "Pending"
        })

        self.task_var.set("")

        self.save_tasks()

        self.refresh_tasks()

    def complete_task(self):

        selected = self.tree.selection()

        if not selected:
            return

        index = self.tree.index(selected[0])

        self.tasks[index]["status"] = "Done"

        self.save_tasks()

        self.refresh_tasks()

    def delete_task(self):

        selected = self.tree.selection()

        if not selected:
            return

        index = self.tree.index(selected[0])

        del self.tasks[index]

        self.save_tasks()

        self.refresh_tasks()


    def save_tasks(self):

        with open(FILE, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def load_tasks(self):

        if os.path.exists(FILE):

            with open(FILE, "r") as f:
                self.tasks = json.load(f)


    def draw_analytics(self):

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not self.tasks:
            return

        df = pd.DataFrame(self.tasks)

        fig, ax = plt.subplots(1, 2, figsize=(7, 3))

        sns.countplot(
            x="status",
            data=df,
            palette="pastel",
            ax=ax[0]
        )

        ax[0].set_title("Task Status")

        sns.countplot(
            x="priority",
            data=df,
            palette="Set2",
            ax=ax[1]
        )

        ax[1].set_title("Priority Distribution")

        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()


    def refresh_tasks(self):

        self.tree.delete(*self.tree.get_children())

        query = self.search_var.get().lower()

        for task in self.tasks:

            if query and query not in task["task"].lower():
                continue

            self.tree.insert(
                "",
                "end",
                values=(
                    task["task"],
                    task["priority"],
                    task["due"],
                    task["status"]
                )
            )

        total = len(self.tasks)

        done = len([t for t in self.tasks if t["status"] == "Done"])

        percent = (done / total * 100) if total else 0

        self.progress["value"] = percent

        self.draw_analytics()


root = tk.Tk()

app = TodoApp(root)

root.mainloop()