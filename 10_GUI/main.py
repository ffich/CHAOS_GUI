# =============================================================
# Project structure for PySide6 RTOS Configuration Wizard
# =============================================================
# This document contains ALL files as a scaffold.
# You will split them into actual files in your project folder.
# =============================================================

# ----------------------------
# main.py
# ----------------------------
from PySide6.QtWidgets import QApplication, QMainWindow
from wizard import RTOSWizard
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RTOSWizard()
    window.show()
    sys.exit(app.exec())

