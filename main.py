import tkinter as tk
from tkinter import messagebox
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os

config = {}

with open('config.properties', 'r') as file:
    for line in file:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            config[key.strip()] = value.strip()

user = config['user']
password = config['password']
host = config['host']
port = config['port']
database = config['database']

Base = declarative_base()
basedir = os.path.abspath(os.path.dirname(__file__))

class Task(Base):
    __tablename__ = "tasks"

    tid = Column("tid", Integer, primary_key=True)
    title = Column("title", String)
    content = Column("content", String)
    status = Column(Integer, ForeignKey("status.sid"))

    def __init__(self, tid, title, content, status):
        self.tid = tid
        self.title = title
        self.content = content
        self.status = status

    def __repr__(self):
        return f"({self.tid}) {self.title} {self.content} {self.status}"

class Status(Base):
    __tablename__ = "status"

    sid = Column("sid", Integer, primary_key=True)
    state = Column("state", String)

    def __init__(self, sid, state):
        self.sid = sid
        self.state = state

    def __repr__(self):
        return f"({self.sid}) {self.state}"

connection_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_str, echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

# Tkinter UI class
class TodoListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List")

        self.text_intro = tk.Label(root, text="Texto titulo")
        self.text_intro.grid(row=0, column=0, padx=10, pady=5)

        self.task_entry_title_label = tk.Label(root, text="Titulo Tarea")
        self.task_entry_title_label.grid(row=1, column=0, padx=10, pady=5)

        self.task_entry_title = tk.Entry(root, width=50)
        self.task_entry_title.grid(row=2, column=0, padx=10, pady=5)

        self.task_entry_content_label = tk.Label(root, text="Contenido Tarea")
        self.task_entry_content_label.grid(row=3, column=0, padx=10, pady=5)

        self.task_entry_content = tk.Entry(root, width=50)
        self.task_entry_content.grid(row=4, column=0, padx=10, pady=5)

        self.add_button = tk.Button(root, text="Add Task", command=self.add_task)
        self.add_button.grid(row=5, column=0, padx=10, pady=5)

        self.task_listbox = tk.Listbox(root, width=70, height=15, selectmode=tk.SINGLE)
        self.task_listbox.grid(row=6, column=0, padx=10, pady=5)

        self.complete_button = tk.Button(root, text="Mark as Completed", command=self.mark_as_completed)
        self.complete_button.grid(row=7, column=0, padx=10, pady=5)

        self.delete_button = tk.Button(root, text="Delete Task", command=self.delete_task)
        self.delete_button.grid(row=8, column=0, padx=10, pady=5)

        self.export_button_csv = tk.Button(root, text="Export to Csv", command=self.export_csv)
        self.export_button_csv.grid(row=9, column=0, padx=10, pady=5)

        self.export_button_json = tk.Button(root, text="Export to Json", command=self.export_to_json)
        self.export_button_json.grid(row=10, column=0, padx=10, pady=5)

        self.import_entry = tk.Entry(root, width=50)
        self.import_entry.grid(row=11, column=0, padx=10, pady=5)

        self.import_button = tk.Button(root, text="Import Json", command=self.import_from_json)
        self.import_button.grid(row=12, column=0, padx=10, pady=5)

        self.load_tasks()

    def load_tasks(self):
        self.task_listbox.delete(0, tk.END)
        tasks = session.query(Task).all()
        for task in tasks:
            # Invalid conditional operand of type "ColumnElement[bool] | Unkown" error, no se porque pasa ¯\_(ツ)_/¯ 
            status = "[X]" if task.status == 1 else "[ ]"
            self.task_listbox.insert(tk.END, f"{status} | {task.title}: {task.content}")

    def add_task(self):
        title = self.task_entry_title.get().strip()
        content = self.task_entry_content.get().strip()
        if title and content:
            new_task = Task(tid=None, title=title, content=content, status=2)
            session.add(new_task)
            session.commit()
            self.task_entry_title.delete(0, tk.END)
            self.task_entry_content.delete(0, tk.END)
            self.load_tasks()
        else:
            messagebox.showwarning("Input Error", "Task title and content cannot be empty.")

    def mark_as_completed(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_text = self.task_listbox.get(selected_index)
            title = task_text.split(':')[0][4:].strip()
            task = session.query(Task).filter_by(title=title).first()
            if task:
                task.status = 1
                session.commit()
                self.load_tasks()
        else:
            messagebox.showwarning("Selection Error", "Please select a task to mark as completed.")

    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_text = self.task_listbox.get(selected_index)
            title = task_text.split(':')[0][4:].strip()
            task = session.query(Task).filter_by(title=title).first()
            if task:
                session.delete(task)
                session.commit()
                self.load_tasks()
        else:
            messagebox.showwarning("Selection Error", "Please select a task to delete.")

    def export_csv(self):
        results = pd.read_sql_query('SELECT * FROM tasks', engine)
        results.to_csv(os.path.join(basedir, 'mydump.csv'),index = False, sep = ",")

    def export_to_json(self):
        file_path = "tasks.json"
        tasks = session.query(Task).all()
        tasks_data = [
            {
                "tid": task.tid,
                "title": task.title,
                "content": task.content,
                "status": task.status
            }
            for task in tasks
        ]
        df = pd.DataFrame(tasks_data)
        df.to_json(file_path, orient="records", indent=4)
        print(f"Data exported to {file_path}")

    
    def import_from_json(self):
        file_path = self.import_entry.get().strip()
        df = pd.read_json(file_path)
        for _, row in df.iterrows():
            task = Task(tid=row["tid"], title=row["title"], content=row["content"], status=row["status"])
            session.merge(task)  
        session.commit()
        print(f"Data imported from {file_path}")
    

# Main function
def main():
    root = tk.Tk()
    app = TodoListApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
