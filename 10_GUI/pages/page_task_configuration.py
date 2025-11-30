# pages/page_task_configuration.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt


class TaskConfigurationPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # --- Title ---
        title_label = QLabel("Task Configuration")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title_label)

        # --- Table ---
        # 0: Task ID
        # 1: Task Name
        # 2: Task Priority
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Task ID", "Task Name", "Task Priority"])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        # --- Buttons ---
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Add Task")
        self.btn_add.clicked.connect(self.add_row)
        btn_layout.addWidget(self.btn_add)

        self.btn_delete = QPushButton("Delete Selected Task")
        self.btn_delete.clicked.connect(self.delete_selected_row)
        btn_layout.addWidget(self.btn_delete)

        layout.addLayout(btn_layout)

    # ------------------------------------------------------------------
    # Funzione interna: crea una riga task con stile uniforme
    # ------------------------------------------------------------------
    def add_task_row(self, task_id, name, priority):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Task ID (centrato)
        id_item = QTableWidgetItem(str(task_id))
        id_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, id_item)

        # Task Name (left, normale)
        name_item = QTableWidgetItem(str(name))
        name_item.setTextAlignment(Qt.AlignLeft)
        self.table.setItem(row, 1, name_item)

        # Task Priority (centrato)
        prio_item = QTableWidgetItem(str(priority))
        prio_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, prio_item)

    # ------------------------------------------------------------------
    # Aggiunge una nuova riga dalla GUI
    # ------------------------------------------------------------------
    def add_row(self):
        next_id = self.table.rowCount()
        self.add_task_row(task_id=next_id, name=f"Task_{next_id}", priority=1)

    # ------------------------------------------------------------------
    # Caricamento da file progetto
    # ------------------------------------------------------------------
    def set_tasks(self, tasks):
        self.table.setRowCount(0)

        for t in tasks:
            tid = t.get("id", 0)
            name = t.get("name", f"Task_{tid}")
            prio = t.get("priority", "1")
            self.add_task_row(tid, name, prio)

    # ------------------------------------------------------------------
    # Cancella riga selezionata
    # ------------------------------------------------------------------
    def delete_selected_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    # ------------------------------------------------------------------
    # Ritorna lista task per salvataggio / codegen
    # ------------------------------------------------------------------
    def get_tasks(self):
        tasks = []
        for row in range(self.table.rowCount()):
            task_id_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)
            prio_item = self.table.item(row, 2)

            tasks.append({
                "id": task_id_item.text().strip() if task_id_item else "",
                "name": name_item.text().strip() if name_item else "",
                "priority": prio_item.text().strip() if prio_item else "",
            })

        return tasks
