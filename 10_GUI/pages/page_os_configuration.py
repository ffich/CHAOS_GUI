# pages/page_os_configuration.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QGroupBox
)
from PySide6.QtCore import Qt

class OSConfigurationPage(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        # --- Title ---
        title_label = QLabel("OS Configuration")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        main_layout.addWidget(title_label)

        # --- General Group ---
        general_group = QGroupBox("General")
        general_layout = QFormLayout()
        
        self.scheduler_freq = QLineEdit("1000")
        self.tick_ms = QLineEdit("1")
        self.ready_queue = QLineEdit("100")

        general_layout.addRow("Scheduler Timer Freq (Hz):", self.scheduler_freq)
        general_layout.addRow("Desired OS Tick (ms):", self.tick_ms)
        general_layout.addRow("Ready Task Queue:", self.ready_queue)

        general_group.setLayout(general_layout)

        # --- Hooks Group ---
        hooks_group = QGroupBox("Hooks")
        hooks_layout = QVBoxLayout()

        self.startup_hook = QCheckBox("Enable Startup Hook")
        self.shutdown_hook = QCheckBox("Enable Shutdown Hook")
        self.pre_task_hook = QCheckBox("Enable pre-task Hook")
        self.post_task_hook = QCheckBox("Enable post-task Hook")
        self.error_hook = QCheckBox("Enable Error Hook")

        for hook in [self.startup_hook, self.shutdown_hook, self.pre_task_hook, self.post_task_hook, self.error_hook]:
            hooks_layout.addWidget(hook)

        hooks_group.setLayout(hooks_layout)

        main_layout.addWidget(general_group)
        main_layout.addWidget(hooks_group)

        self.setLayout(main_layout)
        
    # ------------------------------------------------------------------
    # Project save/load helpers
    # ------------------------------------------------------------------
    def get_config(self) -> dict:
        return {
            "scheduler_freq": self.scheduler_freq.text(),
            "tick_ms": self.tick_ms.text(),
            "ready_queue": self.ready_queue.text(),
            "hooks": {
                "startup": self.startup_hook.isChecked(),
                "shutdown": self.shutdown_hook.isChecked(),
                "pre_task": self.pre_task_hook.isChecked(),
                "post_task": self.post_task_hook.isChecked(),
                "error": self.error_hook.isChecked(),
            },
        }

    def set_config(self, data: dict):
        if not data:
            return

        self.scheduler_freq.setText(str(data.get("scheduler_freq", "1000")))
        self.tick_ms.setText(str(data.get("tick_ms", "1")))
        self.ready_queue.setText(str(data.get("ready_queue", "100")))

        hooks = data.get("hooks", {})
        self.startup_hook.setChecked(bool(hooks.get("startup", False)))
        self.shutdown_hook.setChecked(bool(hooks.get("shutdown", False)))
        self.pre_task_hook.setChecked(bool(hooks.get("pre_task", False)))
        self.post_task_hook.setChecked(bool(hooks.get("post_task", False)))
        self.error_hook.setChecked(bool(hooks.get("error", False)))
        