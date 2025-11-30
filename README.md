# CHAOS GUI
 CHAOS GUI is a desktop application designed to simplify the creation of configuration files for the CHAOS Real-Time Operating System.

▶️ https://github.com/ffich/CHAOS

The tool provides a clean, guided GUI workflow that allows developers to configure all major CHAOS components—OS settings, tasks, scheduling table, and alarms—and automatically generate the corresponding .c and .h files required by the CHAOS build system.

The application is built in Python using PySide6 (Qt for Python) and includes integrated project management, allowing users to save and reload configurations via a portable .chaos_cfg file format.

🚀 Key Features

⚙️ CHAOS OS Configuration
- Configure CHAOS kernel settings:
- Scheduler timer frequency (Hz)
- Desired OS tick period (ms)
- Ready queue size
- User Hooks enabling (Startup, Shutdown, Pre-task, Post-task, Error)

🧵 Task Configuration for CHAOS
- Define tasks through an intuitive table-driven interface:
- Task ID (preserved exactly as configured)
- Task name
- Task priority
- Add/remove tasks dynamically

⏱️ Schedule Table Configuration
- Define periodic scheduling events used by the CHAOS scheduler:
- Select tasks from a dropdown (names mapped automatically to IDs)
- Auto-filled Task ID field
- Event period (ms)
- Add/remove scheduling events

⏰ Alarm Configuration for CHAOS

Configure one-shot or cyclic alarms:
- Alarm type: ONE_SHOT / CYCLIC
- Action: ACTIVATE_TASK or TRIGGER_CALLBACK
- Task selection (auto-enabled only when relevant)
- Auto-generated callback identifiers
- Add/remove alarms easily

📊 Summary Page

The final summary provides a clear overview of:

- Configured OS parameters
- Enabled hooks
- Number of tasks
- Number of scheduling events
- Number of alarms

💾 Project Save / Load

Built-in project manager, supporting:
- Saving complete CHAOS configuration to .chaos_cfg
- Loading saved projects
- Fully restoring all GUI configurations

The .chaos_cfg format is JSON-based, human-readable, and versioned.

🛠️ Code Generation

The wizard generates all required CHAOS configuration files:

- os_cfg.h
- os_task_cfg.h
- os_task_cfg.c
- os_sched_tbl_cfg.h
- os_sched_tbl_cfg.c
- os_alarms_cfg.h
- os_alarms_cfg.c

All outputs are fully consistent with the CHAOS RTOS configuration structure.

📦 Windows Executable Support

A .bat helper script and PyInstaller instructions allow packaging the application into a standalone Windows executable.

🛠️ Tech Stack

- Python 3
- PySide6 (Qt-based GUI)
- JSON configuration format
- PyInstaller (optional EXE generation)

🎯 Purpose

This tool streamlines the creation of complete RTOS configurations for CHAOS, eliminating manual editing of multiple .c and .h files and ensuring consistency across all system components.

Ideal for:

- Embedded engineers using CHAOS in production
- Developers customizing RTOS behavior
- Students and researchers learning how CHAOS works internally
- Anyone wanting a structured, error-free workflow for configuring CHAOS

# Usage Example


https://github.com/user-attachments/assets/1b88606a-9f9e-4ce9-afb3-806dfc62fae6


