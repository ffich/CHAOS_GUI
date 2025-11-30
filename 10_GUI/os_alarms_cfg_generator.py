# os_alarms_cfg_generator.py

from pathlib import Path
from typing import List, Dict
import re


def _replace_define(text: str, name: str, value: str) -> str:
    """
    Sostituisce:
        #define NAME <qualcosa>
    con:
        #define NAME value
    lasciando invariato il resto.
    """
    pattern = rf"(^\s*#define\s+{name}\s+).*$"
    replacement = rf"\g<1>{value}"
    return re.sub(pattern, replacement, text, flags=re.MULTILINE)


def generate_os_alarms_cfg(
    template_h: str,
    template_c: str,
    output_h: str,
    output_c: str,
    alarms: List[Dict],
) -> None:
    """
    template_h: path al template os_alarms_cfg.h
    template_c: path al template os_alarms_cfg.c
    output_h:   path del .h generato
    output_c:   path del .c generato
    alarms: lista di dict provenienti da get_alarms(), es:
        {
            "alarm_id": int,
            "alarm_type": "ONE_SHOT" | "CYCLIC",
            "alarm_action": "ACTIVATE_TASK" | "TRIGGER_CALLBACK",
            "period_ms": int,
            "task_id": int | None,
            "callback": str | None,
        }
    """

    # Normalizza
    norm_alarms = []
    for a in alarms:
        try:
            alarm_id = int(a.get("alarm_id", 0))
        except ValueError:
            alarm_id = 0

        alarm_type = a.get("alarm_type") or "ONE_SHOT"
        alarm_action = a.get("alarm_action") or "ACTIVATE_TASK"
        try:
            period_ms = int(a.get("period_ms", 0))
        except ValueError:
            period_ms = 0

        task_id = a.get("task_id")
        if task_id is None:
            task_id_expr = "0"
        else:
            try:
                task_id_expr = str(int(task_id))
            except ValueError:
                task_id_expr = "0"

        callback = a.get("callback")
        if callback:
            callback_expr = callback
        else:
            callback_expr = "NULL"

        norm_alarms.append({
            "alarm_id": alarm_id,
            "alarm_type": alarm_type,
            "alarm_action": alarm_action,
            "period_ms": period_ms,
            "task_id_expr": task_id_expr,
            "callback_expr": callback_expr,
        })

    # ---------------------------------------------------------------------
    # HEADER: os_alarms_cfg.h (solo ALARMS_NUMB)
    # ---------------------------------------------------------------------
    h_text = Path(template_h).read_text(encoding="utf-8")
    h_text = _replace_define(h_text, "ALARMS_NUMB", f"{len(norm_alarms)}u")

    out_h_path = Path(output_h)
    out_h_path.parent.mkdir(parents=True, exist_ok=True)
    out_h_path.write_text(h_text, encoding="utf-8")

    # ---------------------------------------------------------------------
    # SOURCE: os_alarms_cfg.c
    # ---------------------------------------------------------------------
    c_text = Path(template_c).read_text(encoding="utf-8")
    c_lines = c_text.splitlines(keepends=True)

    # =================== 1) Blocchi AlarmType Alarm_ID_X ==================

    # Nel template abbiamo:
    # /* Alarm structure initialization */
    # AlarmType MyAlarm =
    #   ...
    #   {};
    #   /* ----------------------------------------------------------------------------------------- */
    #
    # AlarmListType AlarmList[ALARMS_NUMB] = ...

    start_struct_idx = None
    alarm_list_decl_idx = None

    for i, line in enumerate(c_lines):
        if "Alarm structure initialization" in line:
            start_struct_idx = i
        if "AlarmListType AlarmList" in line:
            alarm_list_decl_idx = i
            break

    if start_struct_idx is None or alarm_list_decl_idx is None:
        raise RuntimeError("Impossibile trovare blocco 'Alarm structure initialization' o 'AlarmListType AlarmList' in os_alarms_cfg.c template")

    # Genera i blocchi AlarmType Alarm_ID_X
    struct_lines = []

    for a in norm_alarms:
        aid = a["alarm_id"]
        name = f"Alarm_ID_{aid}"
        action = a["alarm_action"]
        alarm_type = a["alarm_type"]
        timeout = a["period_ms"]
        counter = "COUNTER_INIT"
        task_id_expr = a["task_id_expr"]
        callback_expr = a["callback_expr"]

        struct_lines.append("/* Alarm structure initialization */\n")
        struct_lines.append(f"AlarmType {name} =\n\n")
        struct_lines.append("  /* --------------------------------------- Alarm ------------------------------------------- */     \n")
        struct_lines.append("  /* ----------------------------------------------------------------------------------------- */\n")
        struct_lines.append("  /* Action          Counter          Timeout           Type          TaskID          Callback */\n")
        struct_lines.append("  /* ----------------------------------------------------------------------------------------- */   \n")
        struct_lines.append(
            f"  {{{action},   {counter},    {timeout},           {alarm_type},          {task_id_expr},          {callback_expr}}};   \n"
        )
        struct_lines.append("  /* ----------------------------------------------------------------------------------------- */\n\n")

    # Sostituisci blocco da start_struct_idx fino alla riga prima di AlarmList
    c_lines = c_lines[:start_struct_idx] + struct_lines + c_lines[alarm_list_decl_idx:]

    # =================== 2) Array AlarmList[ALARMS_NUMB] ==================

    # Riloccalizza indice dichiarazione AlarmList dopo la modifica
    for i, line in enumerate(c_lines):
        if "AlarmListType AlarmList" in line:
            alarm_list_decl_idx = i
            break

    if alarm_list_decl_idx is None:
        raise RuntimeError("Impossibile trovare 'AlarmListType AlarmList' dopo la sostituzione in os_alarms_cfg.c")

    # Trova '{' e '};'
    brace_open_idx = None
    brace_close_idx = None

    for j in range(alarm_list_decl_idx, len(c_lines)):
        if "{" in c_lines[j]:
            brace_open_idx = j
            break

    if brace_open_idx is None:
        raise RuntimeError("Impossibile trovare '{' per AlarmList in os_alarms_cfg.c")

    for k in range(brace_open_idx + 1, len(c_lines)):
        if c_lines[k].strip().startswith("};"):
            brace_close_idx = k
            break

    if brace_close_idx is None:
        raise RuntimeError("Impossibile trovare '};' per AlarmList in os_alarms_cfg.c")

    # Corpo dell'array
    body_lines = []
    body_lines.append("  /* ---------------- Alarm List --------------- */   \n")
    body_lines.append("  /* ------------------------------------------- */\n")
    body_lines.append("  /* AlarmID         AlarmState         AlarmPtr */\n")
    body_lines.append("  /* ------------------------------------------- */     \n")

    for a in norm_alarms:
        aid = a["alarm_id"]
        body_lines.append(
            f"  {{{aid},         ALARM_ACTIVE,      &Alarm_ID_{aid}}},\n"
        )

    body_lines.append("  /* ------------------------------------------- */\n")

    # Sostituisci il contenuto tra '{' e '};'
    c_lines = (
        c_lines[:brace_open_idx + 1] +
        body_lines +
        c_lines[brace_close_idx:]
    )

    out_c_path = Path(output_c)
    out_c_path.parent.mkdir(parents=True, exist_ok=True)
    out_c_path.write_text("".join(c_lines), encoding="utf-8")
