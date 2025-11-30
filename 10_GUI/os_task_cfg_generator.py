# os_task_cfg_generator.py

from pathlib import Path
from typing import List, Dict


def generate_os_task_cfg(
    template_h: str,
    template_c: str,
    output_h: str,
    output_c: str,
    tasks: List[Dict[str, str]],
) -> None:
    """
    template_h: path al template os_task_cfg.h
    template_c: path al template os_task_cfg.c
    output_h:   path del .h generato
    output_c:   path del .c generato
    tasks: lista di dict con almeno: {"name": str, "priority": str}
    """

    # Normalizza i dati task: usa l'ID configurato nella GUI
    normalized_tasks = []
    for t in tasks:
        name = (t.get("name") or "").strip()
        if not name:
            continue  # salta righe senza nome

        # ID preso dalla tabella (colonna Task ID)
        id_str = (t.get("id") or "").strip()
        try:
            tid = int(id_str)
        except ValueError:
            # fallback: se qualcosa è andato storto, metti 0 o len(normalized_tasks)
            tid = 0

        prio_str = (t.get("priority") or "1").strip()
        try:
            prio = int(prio_str)
        except ValueError:
            prio = 1

        normalized_tasks.append(
            {
                "id": tid,       # <-- qui ora è l'ID della GUI, non idx
                "name": name,
                "priority": prio,
            }
        )


    # -------------------------------------------------------------------------
    # HEADER: os_task_cfg.h  (blocca solo Task IDs)
    # -------------------------------------------------------------------------
    h_text = Path(template_h).read_text(encoding="utf-8")
    h_lines = h_text.splitlines(keepends=True)

    # 1) Trova la sezione "EXPORTED Defines"
    exported_def_idx = None
    for i, line in enumerate(h_lines):
        if "EXPORTED Defines" in line:
            exported_def_idx = i
            break

    if exported_def_idx is None:
        raise RuntimeError("Impossibile trovare 'EXPORTED Defines' in os_task_cfg.h template")

    # 2) Trova il blocco Task IDs (se c'è)
    start_idx = None
    for i in range(exported_def_idx + 1, len(h_lines)):
        if "Task IDs" in h_lines[i]:
            start_idx = i
            break

    # 3) Trova la fine del blocco (prossima riga di sezione /************************************************************************)
    if start_idx is not None:
        for j in range(start_idx + 1, len(h_lines)):
            if h_lines[j].startswith("/************************************************************************"):
                end_idx = j
                break
        else:
            end_idx = len(h_lines)
    else:
        # Se non esiste il commento Task IDs, inseriamo il blocco subito dopo EXPORTED Defines
        start_idx = exported_def_idx + 1
        for j in range(start_idx, len(h_lines)):
            if h_lines[j].startswith("/************************************************************************"):
                end_idx = j
                break
        else:
            end_idx = len(h_lines)

    # 4) Costruisci il nuovo blocco di define
    define_lines = []
    if "Task IDs" in h_lines[start_idx]:
        define_lines.append(h_lines[start_idx])
    else:
        define_lines.append("/* Task IDs */\n")

    for task in normalized_tasks:
        define_lines.append(
            f"#define {task['name']}_ID                                              {task['id']}u\n"
        )

    # 5) Sostituisci il blocco nel file
    new_h_lines = (
        h_lines[:start_idx] +
        define_lines +
        h_lines[end_idx:]
    )

    out_h_path = Path(output_h)
    out_h_path.parent.mkdir(parents=True, exist_ok=True)
    out_h_path.write_text("".join(new_h_lines), encoding="utf-8")

    # -------------------------------------------------------------------------
    # SOURCE: os_task_cfg.c
    # -------------------------------------------------------------------------
    c_text = Path(template_c).read_text(encoding="utf-8")
    c_lines = c_text.splitlines(keepends=True)

    # ===================== 1) blocco extern void ...  ======================

    # Struttura del template:
    # /************************************************************************
    # * TASK List
    # ************************************************************************/
    # extern void MyTask_1 (void);
    #
    # /************************************************************************
    # * GLOBAL Variables
    # ************************************************************************/

    extern_start = None
    extern_end = None

    task_list_line = None
    for i, line in enumerate(c_lines):
        if "TASK List" in line:
            task_list_line = i
            break

    if task_list_line is not None:
        # blocco commento TASK List:
        # task_list_line-1: /*********
        # task_list_line:   * TASK List
        # task_list_line+1: *********/
        # prima riga utile dopo il blocco = task_list_line + 2
        extern_start = task_list_line + 2

        for j in range(extern_start, len(c_lines)):
            if c_lines[j].startswith("/************************************************************************"):
                extern_end = j
                break

    if extern_start is not None and extern_end is not None:
        extern_lines = []
        for task in normalized_tasks:
            extern_lines.append(f"extern void {task['name']} (void);\n")
        extern_lines.append("\n")
        c_lines = c_lines[:extern_start] + extern_lines + c_lines[extern_end:]
    # Se non troviamo il blocco, NON alziamo eccezione: lasciamo gli extern originali

    # ===================== 2) blocco TbcType Tasks[] =======================

    # Template:
    # /************************************************************************
    # * GLOBAL Variables
    # ************************************************************************/
    # TbcType Tasks[] =
    # {
    #   ...
    # };

    # 2.a: trova la sezione GLOBAL Variables
    global_vars_idx = None
    for i, line in enumerate(c_lines):
        if "GLOBAL Variables" in line:
            global_vars_idx = i
            break

    if global_vars_idx is None:
        raise RuntimeError("Impossibile trovare 'GLOBAL Variables' in os_task_cfg.c template")

    # 2.b: a partire da GLOBAL Variables, trova la riga con la dichiarazione dell'array Tasks
    tasks_array_idx = None
    for i in range(global_vars_idx, len(c_lines)):
        line = c_lines[i]
        if "TbcType" in line and "Tasks" in line:
            tasks_array_idx = i
            break

    if tasks_array_idx is None:
        raise RuntimeError("Impossibile trovare dichiarazione 'TbcType Tasks' dopo 'GLOBAL Variables'")

    # 2.c: trova '{' dopo la riga dell'array
    brace_open_idx = None
    for j in range(tasks_array_idx, len(c_lines)):
        if "{" in c_lines[j]:
            brace_open_idx = j
            break

    if brace_open_idx is None:
        raise RuntimeError("Impossibile trovare '{' per TbcType Tasks[] in os_task_cfg.c template")

    # 2.d: trova '};' che chiude l'array
    brace_close_idx = None
    for k in range(brace_open_idx + 1, len(c_lines)):
        if c_lines[k].strip().startswith("};"):
            brace_close_idx = k
            break

    if brace_close_idx is None:
        raise RuntimeError("Impossibile trovare '};' per TbcType Tasks[] in os_task_cfg.c template")

    # 2.e: genera il corpo dell'array
    body_lines = []
    body_lines.append("  /* -------------------------------------------------------------------- */\n")
    body_lines.append("  /* ID                    Task              State           Priority     */\n")
    body_lines.append("  /* -------------------------------------------------------------------- */   \n")
    body_lines.append("  /* --------------------------------- Tasks ---------------------------- */   \n")

    for task in normalized_tasks:
        body_lines.append(
            f"  {{{task['name']}_ID,           {task['name']},         IDLE,           {task['priority']}}},\n"
        )

    body_lines.append("  /* -------------------------------------------------------------------- */\n")

    # 2.f: sostituisci tutto tra '{' e '};' esclusi
    c_lines = (
        c_lines[:brace_open_idx + 1] +
        body_lines +
        c_lines[brace_close_idx:]
    )

    out_c_path = Path(output_c)
    out_c_path.parent.mkdir(parents=True, exist_ok=True)
    out_c_path.write_text("".join(c_lines), encoding="utf-8")
