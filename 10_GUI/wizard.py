# wizard.py

from pathlib import Path

import json

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QProgressBar, QMessageBox, QFileDialog
)

from PySide6.QtCore import QTimer

from pages.page_os_configuration import OSConfigurationPage
from pages.page_task_configuration import TaskConfigurationPage
from pages.page_schedule_table_configuration import ScheduleTableConfigurationPage
from pages.page_alarm_configuration import AlarmConfigurationPage
from pages.page_summary import SummaryPage

from os_cfg_generator import generate_os_cfg
from os_task_cfg_generator import generate_os_task_cfg
from os_sched_tbl_cfg_generator import generate_os_sched_tbl_cfg
from os_alarms_cfg_generator import generate_os_alarms_cfg


class RTOSWizard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CHAOS Configuration Wizard")
        self.resize(800, 300)
        
        self.current_project_path = None

        # Menu File
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        act_save_as = file_menu.addAction("Save Project as...")
        act_load = file_menu.addAction("Load Project")

        act_save_as.triggered.connect(self.save_project_as)
        act_load.triggered.connect(self.load_project)
        
        self.stack = QStackedWidget()

        # Pagine
        self.page_os = OSConfigurationPage()
        self.page_tasks = TaskConfigurationPage()
        self.page_schedule = ScheduleTableConfigurationPage()
        self.page_alarms = AlarmConfigurationPage()
        self.page_summary = SummaryPage()

        # Aggiunta pagine allo stack
        self.stack.addWidget(self.page_os)
        self.stack.addWidget(self.page_tasks)
        self.stack.addWidget(self.page_schedule)
        self.stack.addWidget(self.page_alarms)
        self.stack.addWidget(self.page_summary)

        # Pulsanti di navigazione
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("< Prev")
        self.btn_next = QPushButton("Next >")

        self.btn_prev.clicked.connect(self.go_prev)
        self.btn_next.clicked.connect(self.go_next)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)

        # Progress bar per animazione "Generate"
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.stack)
        layout.addWidget(self.progress_bar)
        layout.addLayout(nav_layout)

        self.setCentralWidget(container)

        # Stato interno per animazione generazione
        self._generation_done = False
        self._progress_value = 0
        self._progress_timer = None

        self.update_buttons()

    # ------------------------------------------------------------------
    # Navigazione avanti
    # ------------------------------------------------------------------
    def go_next(self):
        idx = self.stack.currentIndex()
        last = self.stack.count() - 1

        if idx < last:
            # Prima di entrare in Schedule, aggiorna i task
            if idx + 1 == 2:  # 0: OS, 1: Task, 2: Schedule
                self.page_schedule.set_task_list(self.page_tasks.get_tasks())

            # Prima di entrare in Alarms, aggiorna i task
            if idx + 1 == 3:  # 3: Alarm Configuration
                self.page_alarms.set_task_list(self.page_tasks.get_tasks())

            self.stack.setCurrentIndex(idx + 1)
            if idx + 1 == last:
                self.update_summary()
            self.update_buttons()
        else:
            self.start_generation_animation()

    # ------------------------------------------------------------------
    # Navigazione indietro
    # ------------------------------------------------------------------
    def go_prev(self):
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
        self.update_buttons()

    # ------------------------------------------------------------------
    # Aggiornamento testo / stato dei pulsanti
    # ------------------------------------------------------------------
    def update_buttons(self):
        idx = self.stack.currentIndex()
        last = self.stack.count() - 1

        # Nascondi il pulsante "Prev" nella prima pagina
        if idx == 0:
            self.btn_prev.setVisible(False)
        else:
            self.btn_prev.setVisible(True)

        # Testo del pulsante "Next"
        self.btn_next.setText("Generate" if idx == last else "Next >")


    # ------------------------------------------------------------------
    # Aggiornamento pagina Summary
    # ------------------------------------------------------------------
    def update_summary(self):
        # OS Configuration
        os_config = {
            "scheduler_freq": self.page_os.scheduler_freq.text(),
            "tick_ms": self.page_os.tick_ms.text()
        }
        # Hooks
        hooks = []
        if self.page_os.startup_hook.isChecked():
            hooks.append("Startup Hook")
        if self.page_os.shutdown_hook.isChecked():
            hooks.append("Shutdown Hook")
        if self.page_os.pre_task_hook.isChecked():
            hooks.append("Pre-task Hook")
        if self.page_os.post_task_hook.isChecked():
            hooks.append("Post-task Hook")
        if self.page_os.error_hook.isChecked():
            hooks.append("Error Hook")

        # Number of tasks
        num_tasks = self.page_tasks.table.rowCount()
        # Number of schedule table events
        num_schedule_events = self.page_schedule.table.rowCount()
        # Number of alarms
        num_alarms = self.page_alarms.table.rowCount()

        self.page_summary.update_summary(
            os_config=os_config,
            hooks=hooks,
            tasks=num_tasks,
            schedule=num_schedule_events,
            alarms=num_alarms
        )
        
    def save_project_as(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save CHAOS Project",
            "",
            "CHAOS Config (*.chaos_cfg);;All Files (*.*)",
        )
        if not filename:
            return

        if not filename.endswith(".chaos_cfg"):
            filename += ".chaos_cfg"

        project = {
            "version": 1,
            "os": self.page_os.get_config(),
            "tasks": self.page_tasks.get_tasks(),
            "schedule": self.page_schedule.get_schedule_entries(),
            "alarms": self.page_alarms.get_alarms(),
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(project, f, indent=2)
            self.current_project_path = filename
            QMessageBox.information(self, "Save Project", "Project saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Save Project", f"Error saving project:\n{e}")

    def load_project(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load CHAOS Project",
            "",
            "CHAOS Config (*.chaos_cfg);;All Files (*.*)",
        )
        if not filename:
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                project = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Load Project", f"Error loading project:\n{e}")
            return

        # OS
        os_cfg = project.get("os", {})
        self.page_os.set_config(os_cfg)

        # Tasks
        tasks = project.get("tasks", [])
        self.page_tasks.set_tasks(tasks)

        # aggiorna lista task per schedule/alarms
        self.page_schedule.set_task_list(self.page_tasks.get_tasks())
        self.page_alarms.set_task_list(self.page_tasks.get_tasks())

        # Schedule
        schedule = project.get("schedule", [])
        self.page_schedule.set_schedule_entries(schedule)

        # Alarms
        alarms = project.get("alarms", [])
        self.page_alarms.set_alarms(alarms)

        # aggiorna Summary se siamo sull'ultima pagina
        self.update_summary()
        self.current_project_path = filename
        QMessageBox.information(self, "Load Project", "Project loaded successfully.")
        

    # ------------------------------------------------------------------
    # Avvia animazione e schedula la generazione reale del codice
    # ------------------------------------------------------------------
    def start_generation_animation(self):
        # Disabilita i pulsanti durante la generazione
        self.btn_next.setEnabled(False)
        self.btn_prev.setEnabled(False)

        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        self._generation_done = False
        self._progress_value = 0

        # Timer per animare la progress bar
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_progress_bar)
        self._progress_timer.start(60)  # ogni 60 ms aumenta un po'

        # Schedula la vera generazione del codice dopo un attimo
        # così la UI ha il tempo di ridisegnarsi
        QTimer.singleShot(80, self._run_generate_code)

    def _run_generate_code(self):
        # Esegue la vera generazione (OS, Task, Sched, Alarms)
        self.generate_code()
        # Segnala al timer che la generazione è conclusa
        self._generation_done = True

    def _update_progress_bar(self):
        if not self._generation_done:
            # Finché generate_code() non ha finito, sali fino al 90%
            if self._progress_value < 90:
                self._progress_value += 5
                self.progress_bar.setValue(self._progress_value)
        else:
            # Generazione finita -> porta la barra al 100% e chiudi
            self._progress_timer.stop()
            self.progress_bar.setValue(100)
            QTimer.singleShot(300, self._finish_generation_animation)

    def _finish_generation_animation(self):
        self.progress_bar.setVisible(False)
        self.btn_next.setEnabled(True)
        self.btn_prev.setEnabled(True)

        QMessageBox.information(
            self,
            "Code Generation",
            "Configuration code has been generated in the 'generated' folder."
        )

    # ------------------------------------------------------------------
    # Generazione effettiva dei file di configurazione
    # ------------------------------------------------------------------
    def generate_code(self):
        # ---- OS CONFIGURATION (GUI → dict) ----
        os_config = {
            "scheduler_freq": self.page_os.scheduler_freq.text(),
            "tick_ms": self.page_os.tick_ms.text(),
            "ready_queue": self.page_os.ready_queue.text(),
        }

        hooks = {
            "startup": self.page_os.startup_hook.isChecked(),
            "shutdown": self.page_os.shutdown_hook.isChecked(),
            "pre_task": self.page_os.pre_task_hook.isChecked(),
            "post_task": self.page_os.post_task_hook.isChecked(),
            "error": self.page_os.error_hook.isChecked(),
        }

        # ---------------- OS CFG ----------------
        os_template_path = Path("templates") / "os_cfg.h"
        os_output_path = Path("generated") / "os_cfg.h"

        generate_os_cfg(
            template_path=str(os_template_path),
            output_path=str(os_output_path),
            os_config=os_config,
            hooks=hooks,
        )

        # ---------------- TASK CFG ----------------
        task_rows = self.page_tasks.get_tasks()  # [{id, name, priority}, ...]

        task_template_h = Path("templates") / "os_task_cfg.h"
        task_template_c = Path("templates") / "os_task_cfg.c"
        task_output_h = Path("generated") / "os_task_cfg.h"
        task_output_c = Path("generated") / "os_task_cfg.c"

        generate_os_task_cfg(
            template_h=str(task_template_h),
            template_c=str(task_template_c),
            output_h=str(task_output_h),
            output_c=str(task_output_c),
            tasks=task_rows,
        )

        # ---------------- SCHEDULE TABLE CFG ----------------
        sched_entries = self.page_schedule.get_schedule_entries()
        # [{"task_id": int, "period_ms": int}, ...]

        sched_template_h = Path("templates") / "os_sched_tbl_cfg.h"
        sched_template_c = Path("templates") / "os_sched_tbl_cfg.c"
        sched_output_h = Path("generated") / "os_sched_tbl_cfg.h"
        sched_output_c = Path("generated") / "os_sched_tbl_cfg.c"

        generate_os_sched_tbl_cfg(
            template_h=str(sched_template_h),
            template_c=str(sched_template_c),
            output_h=str(sched_output_h),
            output_c=str(sched_output_c),
            schedule_entries=sched_entries,
        )

        # ---------------- ALARMS CFG ----------------
        alarms = self.page_alarms.get_alarms()

        alarms_template_h = Path("templates") / "os_alarms_cfg.h"
        alarms_template_c = Path("templates") / "os_alarms_cfg.c"
        alarms_output_h = Path("generated") / "os_alarms_cfg.h"
        alarms_output_c = Path("generated") / "os_alarms_cfg.c"

        generate_os_alarms_cfg(
            template_h=str(alarms_template_h),
            template_c=str(alarms_template_c),
            output_h=str(alarms_output_h),
            output_c=str(alarms_output_c),
            alarms=alarms,
        )
