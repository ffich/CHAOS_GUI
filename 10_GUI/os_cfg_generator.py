# os_cfg_generator.py

import re
from pathlib import Path

def _replace_define(text: str, name: str, value: str) -> str:
    """
    Sostituisce la riga:
        #define NAME <qualcosa>
    con:
        #define NAME value
    mantenendo il resto del file invariato.
    """
    pattern = rf"(^\s*#define\s+{name}\s+).*$"
    # NOTA: usare \g<1> per evitare ambiguità con valori che iniziano per cifra!
    replacement = rf"\g<1>{value}"
    return re.sub(pattern, replacement, text, flags=re.MULTILINE)



def generate_os_cfg(template_path: str, output_path: str,
                    os_config: dict, hooks: dict) -> None:
    """
    template_path: path al template os_cfg.h (quello originale)
    output_path:  path del file generato (può anche essere la cartella del progetto)
    os_config: {
        'scheduler_freq': '1000',
        'tick_ms': '1',
        'ready_queue': '100',
    }
    hooks: {
        'startup': bool,
        'shutdown': bool,
        'pre_task': bool,
        'post_task': bool,
        'error': bool,
    }
    """
    text = Path(template_path).read_text(encoding="utf-8")

    # --- Valori numerici OS ---
    sched_freq = os_config.get("scheduler_freq", "1000")
    tick_ms = os_config.get("tick_ms", "1")
    ready_queue = os_config.get("ready_queue", "100")

    text = _replace_define(
        text,
        "SCHED_TIMER_FREQ_HZ",
        f"((uint16_t)({sched_freq}))",
    )
    text = _replace_define(
        text,
        "DESIRED_SCHED_PERIOD_MS",
        f"((uint16_t)({tick_ms}))",
    )
    text = _replace_define(
        text,
        "MAX_READY_TASKS",
        f"{ready_queue}u",
    )

    # --- Hooks → STD_TRUE / STD_FALSE ---
    def hv(flag: bool) -> str:
        return "STD_TRUE" if flag else "STD_FALSE"

    text = _replace_define(
        text,
        "ENABLE_STARTUP_HOOK",
        hv(hooks.get("startup", False)),
    )
    text = _replace_define(
        text,
        "ENABLE_SHUTDOWN_HOOK",
        hv(hooks.get("shutdown", False)),
    )
    text = _replace_define(
        text,
        "ENABLE_PRE_TASK_HOOK",
        hv(hooks.get("pre_task", False)),
    )
    text = _replace_define(
        text,
        "ENABLE_POST_TASK_HOOK",
        hv(hooks.get("post_task", False)),
    )
    text = _replace_define(
        text,
        "ENABLE_ERROR_HOOK",
        hv(hooks.get("error", False)),
    )

    # Scrivi il file generato
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
