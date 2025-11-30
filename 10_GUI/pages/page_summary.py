# pages/page_summary.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout
)

class SummaryPage(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        # --- Title ---
        title_label = QLabel("Summary")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        main_layout.addWidget(title_label)

        # --- OS Configuration Summary ---
        self.os_group = QGroupBox("OS Configuration")
        os_layout = QFormLayout()
        self.lbl_scheduler_freq = QLabel("0")
        self.lbl_os_tick = QLabel("0")
        os_layout.addRow("Scheduler Timer Frequency (Hz):", self.lbl_scheduler_freq)
        os_layout.addRow("OS Tick (ms):", self.lbl_os_tick)
        self.os_group.setLayout(os_layout)

        # --- Hooks Summary ---
        self.hooks_group = QGroupBox("Hooks")
        hooks_layout = QVBoxLayout()
        self.lbl_hooks = QLabel("")
        hooks_layout.addWidget(self.lbl_hooks)
        self.hooks_group.setLayout(hooks_layout)

        # --- Tasks Summary ---
        self.tasks_group = QGroupBox("Tasks")
        tasks_layout = QFormLayout()
        self.lbl_num_tasks = QLabel("0")
        tasks_layout.addRow("Number of Tasks:", self.lbl_num_tasks)
        self.tasks_group.setLayout(tasks_layout)

        # --- Schedule Table Summary ---
        self.schedule_group = QGroupBox("Schedule Table")
        schedule_layout = QFormLayout()
        self.lbl_num_schedule_events = QLabel("0")
        schedule_layout.addRow("Number of Schedule Table Events:", self.lbl_num_schedule_events)
        self.schedule_group.setLayout(schedule_layout)

        # --- Alarms Summary ---
        self.alarms_group = QGroupBox("Alarms")
        alarms_layout = QFormLayout()
        self.lbl_num_alarms = QLabel("0")
        alarms_layout.addRow("Number of Alarms:", self.lbl_num_alarms)
        self.alarms_group.setLayout(alarms_layout)

        main_layout.addWidget(self.os_group)
        main_layout.addWidget(self.hooks_group)
        main_layout.addWidget(self.tasks_group)
        main_layout.addWidget(self.schedule_group)
        main_layout.addWidget(self.alarms_group)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def update_summary(self, os_config=None, hooks=None, tasks=None, schedule=None, alarms=None):
        if os_config:
            self.lbl_scheduler_freq.setText(str(os_config.get('scheduler_freq', '0')))
            self.lbl_os_tick.setText(str(os_config.get('tick_ms', '0')))
        if hooks:
            self.lbl_hooks.setText(', '.join(hooks) if hooks else 'None')
        if tasks is not None:
            self.lbl_num_tasks.setText(str(tasks))
        if schedule is not None:
            self.lbl_num_schedule_events.setText(str(schedule))
        if alarms is not None:
            self.lbl_num_alarms.setText(str(alarms))