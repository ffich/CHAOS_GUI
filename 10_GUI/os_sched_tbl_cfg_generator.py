# os_sched_tbl_cfg_generator.py

import re
from pathlib import Path
from typing import List, Dict


def _replace_define(text: str, name: str, value: str) -> str:
    """
    Sostituisce la riga:
        #define NAME <qualcosa>
    con:
        #define NAME value
    lasciando il resto del file invariato.
    """
    pattern = rf"(^\s*#define\s+{name}\s+).*$"
    replacement = rf"\g<1>{value}"  # importante usare \g<1> !
    return re.sub(pattern, replacement, text, flags=re.MULTILINE)


def generate_os_sched_tbl_cfg(
    template_h: str,
    template_c: str,
    output_h: str,
    output_c: str,
    schedule_entries: List[Dict[str, int]],
) -> None:
    """
    template_h: path al template os_sched_tbl_cfg.h
    template_c: path al template os_sched_tbl_cfg.c
    output_h:   path del .h generato
    output_c:   path del .c generato
    schedule_entries: lista di dict:
        [{\"task_id\": int, \"period_ms\": int}, ...]
    """

    # Normalizza: garantiamo int
    norm_entries = []
    for e in schedule_entries:
        try:
            tid = int(e.get("task_id", 0))
        except ValueError:
            tid = 0
        try:
            per = int(e.get("period_ms", 0))
        except ValueError:
            per = 0
        norm_entries.append({"task_id": tid, "period_ms": per})

    evt_n = len(norm_entries)

    # -------------------------------------------------------------------------
    # HEADER: os_sched_tbl_cfg.h  (solo SCHED_EVT_NUMBER)
    # -------------------------------------------------------------------------
    h_text = Path(template_h).read_text(encoding="utf-8")
    h_text = _replace_define(h_text, "SCHED_EVT_NUMBER", f"{evt_n}u")

    out_h_path = Path(output_h)
    out_h_path.parent.mkdir(parents=True, exist_ok=True)
    out_h_path.write_text(h_text, encoding="utf-8")

    # -------------------------------------------------------------------------
    # SOURCE: os_sched_tbl_cfg.c  (SchedTblType SchedTable[...] = { ... })
    # -------------------------------------------------------------------------
    c_text = Path(template_c).read_text(encoding="utf-8")
    c_lines = c_text.splitlines(keepends=True)

    # Trova la dichiarazione dell'array SchedTable
    array_idx = None
    brace_open_idx = None
    brace_close_idx = None

    for i, line in enumerate(c_lines):
        if "SchedTblType SchedTable" in line:
            array_idx = i
            break

    if array_idx is None:
        raise RuntimeError("Impossibile trovare 'SchedTblType SchedTable' nel template .c")

    # Trova la riga con '{'
    for j in range(array_idx, len(c_lines)):
        if "{" in c_lines[j]:
            brace_open_idx = j
            break

    if brace_open_idx is None:
        raise RuntimeError("Impossibile trovare '{' per SchedTable nel template .c")

    # Trova la riga con '};'
    for k in range(brace_open_idx + 1, len(c_lines)):
        if c_lines[k].strip().startswith("};"):
            brace_close_idx = k
            break

    if brace_close_idx is None:
        raise RuntimeError("Impossibile trovare '};' per SchedTable nel template .c")

    # Corpo array: lo rigeneriamo
    body_lines = []
    body_lines.append("  /* ------------------------------------------------ */\n")
    body_lines.append("  /* TaskID          Counter          Timeout  */\n")
    body_lines.append("  /* ------------------------------------------------ */   \n")
    body_lines.append("  /* ----------------- Sched. Table ----------------- */   \n")

    for e in norm_entries:
        body_lines.append(
            f"  {{{e['task_id']},     COUNTER_INIT,    {e['period_ms']}}}, \n"
        )

    body_lines.append("  /* ------------------------------------------------ */\n")

    # Sostituisci tutto tra '{' e '};' (esclusi)
    c_lines = (
        c_lines[:brace_open_idx + 1] +
        body_lines +
        c_lines[brace_close_idx:]
    )

    out_c_path = Path(output_c)
    out_c_path.parent.mkdir(parents=True, exist_ok=True)
    out_c_path.write_text("".join(c_lines), encoding="utf-8")
