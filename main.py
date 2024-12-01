import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QListWidget,
    QCalendarWidget, QCheckBox, QListWidgetItem, QInputDialog
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QTextCharFormat, QColor



class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo list")
        self.setGeometry(100, 100, 800, 600)
        
        self.tasks = self.load_tasks()
        self.selected_date = QDate.currentDate()  # Current selected date
        
        # Main widget
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()  # Vertical layout for button and content

        # Panel for the "Calendar" button and calendar
        self.calendar_panel = QWidget()
        self.calendar_layout = QVBoxLayout()  # Container for button and calendar

        # Calendar button (collapse/expand)
        self.calendar_toggle_btn = QPushButton("Calendar")
        self.calendar_toggle_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                text-align: center;
                width: 100%;   /* Making the button stretch to its full width */
                height: 40px;   /* Set a fixed height */
            }
        """)
        self.calendar_toggle_btn.clicked.connect(self.toggle_calendar)

        # Placement of the "Calendar" button
        self.calendar_layout.addWidget(self.calendar_toggle_btn)

        # Adding a calendar
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.change_date)
        # Highlight task days
        self.highlight_task_days()
        self.calendar_layout.addWidget(self.calendar)

        self.calendar_panel.setLayout(self.calendar_layout)

        # Task list panel
        self.task_panel = QWidget()
        self.task_layout = QVBoxLayout()

        # Task list
        self.task_list = QListWidget()
        self.update_task_list()
        self.task_layout.addWidget(self.task_list)

        # Add task button
        self.add_task_btn = QPushButton("Add task")
        self.add_task_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                text-align: center;
                width: 100%;   /* The button stretches to full width */
                height: 40px;  /* Setting the height of the button */
            }
        """)
        self.add_task_btn.clicked.connect(self.add_task)
        self.task_layout.addWidget(self.add_task_btn)

        self.task_panel.setLayout(self.task_layout)

        # Adding panels to the main layout
        self.main_layout.addWidget(self.calendar_panel)  # Add a calendar to the top
        self.main_layout.addWidget(self.task_panel)  # Adding a taskbar to the bottom

        # Installing the main widget
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
    
    def toggle_calendar(self):
        """Collapse or expand the calendar."""
        if self.calendar.isVisible():
            self.calendar.hide()
            self.calendar_toggle_btn.setText("Expand calendar")
        else:
            self.calendar.show()
            self.calendar_toggle_btn.setText("Hide calendar")

    def change_date(self, date):
        """Changes the selected date and updates the task list."""
        self.selected_date = date
        self.update_task_list()
    
    def update_task_list(self):
        """Updates the task list, filtering by the selected date."""
        self.task_list.clear()
        selected_date_str = self.selected_date.toString("yyyy-MM-dd")
        
        for task in self.tasks:
            if task["date"] == selected_date_str:
                task_item = QWidget()
                task_layout = QHBoxLayout()

                # Checkbox
                checkbox = QCheckBox(task["title"])
                checkbox.setChecked(task.get("completed", False))
                checkbox.stateChanged.connect(lambda state, task=task: self.toggle_task_state(state, task))
                
                # Description of the task
                task_label = QWidget()
                task_label.setStyleSheet("font-size: 14px; padding-left: 10px;")  # Task text style

                # "Edit" button
                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda _, t=task: self.edit_task(t))

                #"Delete" button
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda _, t=task: self.delete_task(t))

                # Adding elements to the horizontal layout
                task_layout.addWidget(checkbox)
                task_layout.addWidget(task_label)
                task_layout.addWidget(edit_button)
                task_layout.addWidget(delete_button)

                # Placement in list widget
                task_item.setLayout(task_layout)
                list_item = QListWidgetItem()
                self.task_list.addItem(list_item)
                list_item.setSizeHint(task_item.sizeHint())
                self.task_list.setItemWidget(list_item, task_item)
    
    def toggle_task_state(self, state, task):
        """Handles a change in the state of a task."""
        task["completed"] = state == 2  # If the checkbox is checked (state 2)
        self.save_tasks()

    def highlight_task_days(self):
        """Highlights days in the calendar that have tasks."""
        # Reset backlight for the entire calendar
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Save unique dates with tasks
        task_dates = {QDate.fromString(task["date"], "yyyy-MM-dd") for task in self.tasks}
        
        # Format for highlighting
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(245, 245, 220))  # Light beige color

        # Applying format to dates with tasks
        for date in task_dates:
            self.calendar.setDateTextFormat(date, highlight_format)
    
    def add_task(self):
        """Adding a new task via simple input."""
        title, ok = QInputDialog.getText(self, "Add task", "Task name:")
        if ok and title:
            date_str = self.selected_date.toString("yyyy-MM-dd")
            new_task = {"title": title, "date": date_str, "completed": False}
            self.tasks.append(new_task)
            self.save_tasks()
            self.update_task_list()

    def delete_task(self, task):
        """Removes a task from the list."""
        task_to_remove = None
        for t in self.tasks:
            if t["title"] == task["title"] and t["date"] == task["date"]:
                task_to_remove = t
                break

        if task_to_remove:
            self.tasks.remove(task_to_remove)  # Delete the task
            self.save_tasks()  # Save changes
            self.update_task_list()  # Updating the list
        else:
            print("Task not found!")

            # Update highlights after delete
            self.highlight_task_days()



    def edit_task(self, task):
        """Edits a task."""
        new_title, ok = QInputDialog.getText(self, "Edit task", "Task name:", text=task["title"])
        if ok and new_title:
            task["title"] = new_title
            self.save_tasks()
            self.update_task_list()

    def load_tasks(self):
        """Loading tasks from a file."""
        try:
            with open("tasks.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
    
    def save_tasks(self):
        """Saving tasks to a file."""
        with open("tasks.json", "w") as file:
            json.dump(self.tasks, file, indent=4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec())
