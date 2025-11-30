# pages/page_schedule_table_configuration.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QComboBox
)
from PySide6.QtCore import Qt


class ScheduleTableConfigurationPage(QWidget):
    def __init__(self):
        super().__init__()

        self.tasks = []  # lista di dict: [{"id": "0", "name": "TaskA", "priority": "1"}, ...]

        layout = QVBoxLayout(self)

        # --- Title ---
        title_label = QLabel("Schedule Table Configuration")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title_label)

        # --- Table ---
        # Colonne:
        # 0: Task Name (dropdown)
        # 1: Task ID (auto, non editabile)
        # 2: Period [ms]
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Task Name", "Task ID", "Period [ms]"])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        # --- Buttons ---
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Add Scheduling Event")
        self.btn_add.clicked.connect(self.add_row)
        btn_layout.addWidget(self.btn_add)

        self.btn_delete = QPushButton("Remove Scheduling Event")
        self.btn_delete.clicked.connect(self.delete_selected_row)
        btn_layout.addWidget(self.btn_delete)

        layout.addLayout(btn_layout)

    # ------------------------------------------------------------------
    # Richiamato dal wizard per passare la lista dei task
    # ------------------------------------------------------------------
    def set_task_list(self, tasks):
        self.tasks = tasks or []

        # Aggiorna eventuali combo già esistenti
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 0)
            if not isinstance(combo, QComboBox):
                continue

            current_id = None
            id_item = self.table.item(row, 1)
            if id_item:
                current_id = id_item.text().strip()

            combo.blockSignals(True)
            combo.clear()
            for t in self.tasks:
                combo.addItem(t["name"], t["id"])  # SOLO nome, id nascosto
            combo.blockSignals(False)

            if current_id is not None:
                for i in range(combo.count()):
                    if combo.itemData(i) == current_id:
                        combo.setCurrentIndex(i)
                        break

            self.update_task_id_for_row(row)

    # ------------------------------------------------------------------
    # Aggiunge una nuova riga
    # ------------------------------------------------------------------
    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # --- Task Name (dropdown) ---
        combo = QComboBox()
        for t in self.tasks:
            combo.addItem(t["name"], t["id"])

        self.table.setCellWidget(row, 0, combo)

        combo.currentIndexChanged.connect(
            lambda idx, r=row: self.update_task_id_for_row(r)
        )

        # --- Task ID ---
        task_id_item = QTableWidgetItem("")
        task_id_item.setTextAlignment(Qt.AlignCenter)
        task_id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(row, 1, task_id_item)

        # --- Period [ms] ---
        period_item = QTableWidgetItem("10")
        period_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, period_item)

        self.update_task_id_for_row(row)

    # ------------------------------------------------------------------
    # Aggiorna Task ID in base alla selezione del task
    # ------------------------------------------------------------------
    def update_task_id_for_row(self, row):
        combo = self.table.cellWidget(row, 0)
        task_id_item = self.table.item(row, 1)

        if not combo or not task_id_item:
            return

        idx = combo.currentIndex()
        if idx < 0:
            task_id_item.setText("")
        else:
            task_id_item.setText(str(combo.itemData(idx)))

        self.table.viewport().update()

    # ------------------------------------------------------------------
    # Cancella la riga selezionata
    # ------------------------------------------------------------------
    def delete_selected_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    # ------------------------------------------------------------------
    # Recupera le entry configurate
    # ------------------------------------------------------------------
    def get_schedule_entries(self):
        entries = []
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 0)
            task_id_item = self.table.item(row, 1)
            period_item = self.table.item(row, 2)

            if combo and combo.currentIndex() >= 0:
                task_name = combo.currentText()
            else:
                task_name = ""

            try:
                task_id = int(task_id_item.text()) if task_id_item.text() else 0
            except ValueError:
                task_id = 0

            try:
                period_ms = int(period_item.text()) if period_item.text() else 0
            except ValueError:
                period_ms = 0

            entries.append({
                "task_id": task_id,
                "task_name": task_name,
                "period_ms": period_ms,
            })

        return entries

    def set_schedule_entries(self, entries):
        """
        entries: lista di dict [{ "task_id": int, "task_name": str, "period_ms": int }, ...]
        ATTENZIONE: prima di chiamare questo, chiama set_task_list(tasks),
        così i combo sono popolati.
        """
        self.table.setRowCount(0)

        if not entries:
            return

        for e in entries:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Task Name combo
            combo = QComboBox()
            for t in self.tasks:
                combo.addItem(t["name"], t["id"])
            self.table.setCellWidget(row, 0, combo)
            combo.currentIndexChanged.connect(
                lambda idx, r=row: self.update_task_id_for_row(r)
            )

            # Task ID cell
            task_id_item = QTableWidgetItem("")
            task_id_item.setTextAlignment(Qt.AlignCenter)
            task_id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(row, 1, task_id_item)

            # Period
            period_item = QTableWidgetItem(str(e.get("period_ms", 0)))
            period_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, period_item)

            # seleziona il task corretto in base a task_id
            target_id = str(e.get("task_id", 0))
            for i in range(combo.count()):
                if str(combo.itemData(i)) == target_id:
                    combo.setCurrentIndex(i)
                    break

            self.update_task_id_for_row(row)
