# pages/page_alarm_configuration.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QComboBox
)
from PySide6.QtCore import Qt


class AlarmConfigurationPage(QWidget):
    def __init__(self):
        super().__init__()

        self.tasks = []  # lista di dict: [{"id": "0", "name": "MyTask_0", "priority": "1"}, ...]

        layout = QVBoxLayout(self)

        # --- Title ---
        title_label = QLabel("Alarm Configuration")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title_label)

        # --- Table ---
        # Colonne:
        # 0: Alarm ID       (incrementale da 0, non editabile)
        # 1: Alarm Type     (ONE_SHOT / CYCLIC)
        # 2: Alarm Action   (ACTIVATE_TASK / TRIGGER_CALLBACK)
        # 3: Period [ms]
        # 4: Task Name      (dropdown con tutti i task)
        # 5: Task ID        (auto da Task Name, non editabile)
        # 6: Callback       (MyAlarmCallback_N, solo per TRIGGER_CALLBACK)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Alarm ID",
            "Alarm Type",
            "Alarm Action",
            "Period [ms]",
            "Task Name",
            "Task ID",
            "Callback",
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # --- Buttons ---
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Add Alarm")
        self.btn_add.clicked.connect(self.add_row)
        btn_layout.addWidget(self.btn_add)

        self.btn_delete = QPushButton("Delete Selected Alarm")
        self.btn_delete.clicked.connect(self.delete_selected_row)
        btn_layout.addWidget(self.btn_delete)

        layout.addLayout(btn_layout)

    # ------------------------------------------------------------------
    # Chiamato dal wizard per passare la lista dei task
    # tasks: [{"id": "0", "name": "Task_0", "priority": "1"}, ...]
    # ------------------------------------------------------------------
    def set_task_list(self, tasks):
        self.tasks = tasks or []

        # Aggiorna eventuali combo Task Name già presenti
        for row in range(self.table.rowCount()):
            task_combo = self.table.cellWidget(row, 4)
            if not isinstance(task_combo, QComboBox):
                continue

            current_id = None
            task_id_item = self.table.item(row, 5)
            if task_id_item:
                current_id = task_id_item.text().strip()

            task_combo.blockSignals(True)
            task_combo.clear()
            for t in self.tasks:
                task_combo.addItem(t["name"], t["id"])  # nome visibile, id in userData
            task_combo.blockSignals(False)

            if current_id is not None:
                for i in range(task_combo.count()):
                    if str(task_combo.itemData(i)) == current_id:
                        task_combo.setCurrentIndex(i)
                        break

            self.update_alarm_row_state(row)

    # ------------------------------------------------------------------
    # Aggiunge una nuova riga di allarme
    # ------------------------------------------------------------------
    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Alarm ID (incrementale da 0, non editabile)
        alarm_id_item = QTableWidgetItem(str(row))
        alarm_id_item.setTextAlignment(Qt.AlignCenter)
        alarm_id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(row, 0, alarm_id_item)

        # Alarm Type dropdown
        alarm_type_cb = QComboBox()
        alarm_type_cb.addItems(["ONE_SHOT", "CYCLIC"])
        self.table.setCellWidget(row, 1, alarm_type_cb)

        # Alarm Action dropdown
        alarm_action_cb = QComboBox()
        alarm_action_cb.addItems(["ACTIVATE_TASK", "TRIGGER_CALLBACK"])
        self.table.setCellWidget(row, 2, alarm_action_cb)

        # Period [ms] (default 100)
        period_item = QTableWidgetItem("100")
        period_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, period_item)

        # Task Name (dropdown con lista task)
        task_combo = QComboBox()
        for t in self.tasks:
            task_combo.addItem(t["name"], t["id"])
        self.table.setCellWidget(row, 4, task_combo)

        # Task ID (auto da Task Name, non editabile)
        task_id_item = QTableWidgetItem("")
        task_id_item.setTextAlignment(Qt.AlignCenter)
        task_id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(row, 5, task_id_item)

        # Callback (numerato, ma abilitato solo per TRIGGER_CALLBACK)
        callback_item = QTableWidgetItem(f"MyAlarmCallback_{row}")
        callback_item.setFlags(Qt.NoItemFlags)
        self.table.setItem(row, 6, callback_item)

        # Collega il cambio di Action e Task Name all'update della riga
        alarm_action_cb.currentIndexChanged.connect(
            lambda idx, r=row: self.update_alarm_row_state(r)
        )
        task_combo.currentIndexChanged.connect(
            lambda idx, r=row: self.update_alarm_row_state(r)
        )

        # Inizializza stato riga
        self.update_alarm_row_state(row)

    # ------------------------------------------------------------------
    # Aggiorna Task Name/Task ID/Callback in base ad Alarm Action
    # ------------------------------------------------------------------
    def update_alarm_row_state(self, row: int):
        """
        - Se Alarm Action == TRIGGER_CALLBACK:
            - Task Name combo disabilitato
            - Task ID vuoto e disabilitato
            - Callback = 'MyAlarmCallback_<row>' e editabile
        - Se Alarm Action == ACTIVATE_TASK:
            - Task Name combo abilitato
            - Task ID = id del task selezionato (o 0) e abilitato
            - Callback vuoto e disabilitato
        """
        action_cb = self.table.cellWidget(row, 2)
        task_combo = self.table.cellWidget(row, 4)
        task_id_item = self.table.item(row, 5)
        callback_item = self.table.item(row, 6)

        if not action_cb or not task_combo or not task_id_item or not callback_item:
            return

        action = action_cb.currentText()

        if action == "TRIGGER_CALLBACK":
            # Task disabilitato
            task_combo.setEnabled(False)

            # Task ID disabilitato e vuoto
            task_id_item.setText("")
            task_id_item.setFlags(Qt.NoItemFlags)

            # Callback abilitato e numerato
            callback_item.setText(f"MyAlarmCallback_{row}")
            callback_item.setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
            )
        else:
            # ACTIVATE_TASK
            # Task combo abilitato
            task_combo.setEnabled(True)

            # Task ID aggiornato dal combo
            idx = task_combo.currentIndex()
            if idx >= 0 and task_combo.count() > 0:
                tid = task_combo.itemData(idx)
                task_id_item.setText(str(tid))
            else:
                task_id_item.setText("0")

            task_id_item.setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsEnabled
            )

            # Callback disabilitato e vuoto
            callback_item.setText("")
            callback_item.setFlags(Qt.NoItemFlags)

        self.table.viewport().update()

    # ------------------------------------------------------------------
    # Cancella la riga selezionata
    # ------------------------------------------------------------------
    def delete_selected_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
            # Nota: non rinumeriamo Alarm ID / callback qui.

    # ------------------------------------------------------------------
    # Ritorna la lista di allarmi configurati
    # ------------------------------------------------------------------
    def get_alarms(self):
        """
        Ritorna una lista di dizionari:
        [
          {
            "alarm_id": int,
            "alarm_type": str,
            "alarm_action": str,
            "period_ms": int,
            "task_id": int | None,
            "callback": str | None,
          },
          ...
        ]
        """
        alarms = []
        for row in range(self.table.rowCount()):
            alarm_id_item = self.table.item(row, 0)
            type_cb = self.table.cellWidget(row, 1)
            action_cb = self.table.cellWidget(row, 2)
            period_item = self.table.item(row, 3)
            task_id_item = self.table.item(row, 5)
            callback_item = self.table.item(row, 6)

            # Alarm ID
            try:
                alarm_id = int(alarm_id_item.text()) if alarm_id_item else row
            except ValueError:
                alarm_id = row

            alarm_type = type_cb.currentText() if type_cb else "ONE_SHOT"
            alarm_action = action_cb.currentText() if action_cb else "ACTIVATE_TASK"

            # Period
            try:
                period_ms = int(period_item.text()) if period_item else 0
            except ValueError:
                period_ms = 0

            # Task ID valido solo se la cella è abilitata
            if task_id_item and (task_id_item.flags() & Qt.ItemIsEnabled):
                txt = task_id_item.text().strip()
                try:
                    task_id = int(txt) if txt else 0
                except ValueError:
                    task_id = 0
            else:
                task_id = None

            # Callback valida solo se editabile
            if callback_item and (callback_item.flags() & Qt.ItemIsEditable):
                cb_text = callback_item.text().strip()
                callback = cb_text if cb_text else None
            else:
                callback = None

            alarms.append({
                "alarm_id": alarm_id,
                "alarm_type": alarm_type,
                "alarm_action": alarm_action,
                "period_ms": period_ms,
                "task_id": task_id,
                "callback": callback,
            })

        return alarms

    def set_alarms(self, alarms):
        """
        alarms: lista di dict come quelli restituiti da get_alarms()
        """
        self.table.setRowCount(0)

        if not alarms:
            return

        for a in alarms:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Alarm ID
            alarm_id_item = QTableWidgetItem(str(a.get("alarm_id", row)))
            alarm_id_item.setTextAlignment(Qt.AlignCenter)
            alarm_id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(row, 0, alarm_id_item)

            # Alarm Type
            type_cb = QComboBox()
            type_cb.addItems(["ONE_SHOT", "CYCLIC"])
            self.table.setCellWidget(row, 1, type_cb)
            t_val = a.get("alarm_type", "ONE_SHOT")
            idx = type_cb.findText(t_val)
            if idx >= 0:
                type_cb.setCurrentIndex(idx)

            # Alarm Action
            action_cb = QComboBox()
            action_cb.addItems(["ACTIVATE_TASK", "TRIGGER_CALLBACK"])
            self.table.setCellWidget(row, 2, action_cb)
            act_val = a.get("alarm_action", "ACTIVATE_TASK")
            idx = action_cb.findText(act_val)
            if idx >= 0:
                action_cb.setCurrentIndex(idx)

            # Period
            period_item = QTableWidgetItem(str(a.get("period_ms", 0)))
            period_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, period_item)

            # Task Name combo
            task_combo = QComboBox()
            for t in self.tasks:
                task_combo.addItem(t["name"], t["id"])
            self.table.setCellWidget(row, 4, task_combo)

            # Task ID cell
            task_id_item = QTableWidgetItem("")
            task_id_item.setTextAlignment(Qt.AlignCenter)
            task_id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(row, 5, task_id_item)

            # Callback cell
            callback_item = QTableWidgetItem("")
            self.table.setItem(row, 6, callback_item)

            # connect signals
            action_cb.currentIndexChanged.connect(
                lambda idx, r=row: self.update_alarm_row_state(r)
            )
            task_combo.currentIndexChanged.connect(
                lambda idx, r=row: self.update_alarm_row_state(r)
            )

            # ripristina Task selezionato se ACTIVATE_TASK
            task_id_saved = a.get("task_id", None)
            if task_id_saved is not None:
                target_id = str(task_id_saved)
                for i in range(task_combo.count()):
                    if str(task_combo.itemData(i)) == target_id:
                        task_combo.setCurrentIndex(i)
                        break

            # ripristina callback se TRIGGER_CALLBACK
            cb_val = a.get("callback", None)
            if cb_val:
                callback_item.setText(cb_val)

            # stato finale coerente con Action
            self.update_alarm_row_state(row)
