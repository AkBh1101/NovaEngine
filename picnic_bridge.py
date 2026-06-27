"""
engine_interface.py — Game engine I/O layer
Handles compilation, process execution, and structured data extraction.
"""

import os
import subprocess
import sys
import time
import streamlit as st

# ── Path resolution ───────────────────────────────────────────────────────────
_ROOT       = os.path.dirname(os.path.abspath(__file__))
_SRC_FILE   = os.path.join(_ROOT, "game_engine.cpp")
_BIN_FILE   = os.path.join(_ROOT, "picnic_engine.exe")

# ── Constants ─────────────────────────────────────────────────────────────────
BOARD_SIZE    = 36
INITIAL_MONEY = 10

# ── Cell metadata ─────────────────────────────────────────────────────────────
_TYPE_MAP = {
    0: "normal",    1: "money_gain", 2: "money_loss",
    3: "die_upgrade", 4: "jump_forward", 5: "jump_back",
    6: "skip_turn", 7: "extra_turn", 8: "card",
    9: "start",    10: "finish",
}

_EMOJI_MAP = {
    "start":        "🏠",
    "finish":       "🏁",
    "money_gain":   "💰",
    "money_loss":   "💸",
    "die_upgrade":  "🎰",
    "jump_forward": "⏩",
    "jump_back":    "⏪",
    "skip_turn":    "🚦",
    "extra_turn":   "🍀",
    "card":         "🃏",
    "normal":       "🌿",
}

# ══════════════════════════════════════════════════════════════════════════════
# Low-level process helpers
# ══════════════════════════════════════════════════════════════════════════════

def compile_engine():
    """Compile the C++ source. Returns (success: bool, stderr: str)."""
    result = subprocess.run(
        ["g++", "-O2", "-std=c++17", "-o", _BIN_FILE, _SRC_FILE],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stderr


def _invoke(mode, payload="", timeout=20):
    """
    Send *payload* to the engine binary under *mode*.
    Returns (stdout, stderr).
    """
    try:
        proc = subprocess.run(
            [_BIN_FILE, mode],
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout,
        )
        return proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT"
    except FileNotFoundError:
        return "", "Binary not found"


def _invoke_timed(mode, payload="", timeout=20):
    """Like _invoke but also returns wall-clock elapsed time in milliseconds."""
    t_start = time.perf_counter()
    stdout, stderr = _invoke(mode, payload, timeout)
    elapsed_ms = (time.perf_counter() - t_start) * 1000
    return stdout, stderr, elapsed_ms


# ══════════════════════════════════════════════════════════════════════════════
# Output parsers — each converts raw stdout lines into Python structures
# ══════════════════════════════════════════════════════════════════════════════

def _extract_block(lines, sentinel_start, sentinel_end, prefix):
    """Yield raw pipe-separated fields for lines between two sentinel markers."""
    inside = False
    for line in lines:
        if line == sentinel_start:
            inside = True
            continue
        if line == sentinel_end:
            return
        if inside and line.startswith(prefix):
            yield line.split("|")


def _parse_move_record(parts):
    return {
        "roll":       int(parts[1]),
        "npos":       int(parts[2]),
        "nmoney":     int(parts[3]),
        "ndie":       int(parts[4]),
        "grundy":     int(parts[5]),
        "outcome":    parts[6],
        "cell_name":  parts[7],
        "cell_emoji": parts[8],
        "cell_desc":  parts[9],
        "card_name":  parts[10],
        "card_desc":  parts[11],
        "skip":       parts[12] == "1",
        "extra":      parts[13] == "1",
        "minimax_val":    int(parts[14]) if len(parts) > 14 else 0,
        "collected_item": parts[15] == "1" if len(parts) > 15 else False,
        "item_id":        int(parts[16]) if len(parts) > 16 else -1,
        "item_name":      parts[17] if len(parts) > 17 else "",
    }


def _extract_moves(output):
    rows = []
    for fields in _extract_block(output.splitlines(), "MOVES_START", "MOVES_END", "MOVE|"):
        rows.append(_parse_move_record(fields))
    return rows


def _extract_grundy(output):
    record = {"grundy": None, "state": None, "moves": []}
    for line in output.splitlines():
        if line.startswith("GRUNDY|"):
            record["grundy"] = int(line.split("|")[1])
        elif line.startswith("STATE|"):
            record["state"] = line.split("|")[1]
    record["moves"] = _extract_moves(output)
    return record


def _extract_simulation(output):
    steps, summary, winner = [], {}, (None, None)

    for line in output.splitlines():
        if line.startswith("SIM_STEP|"):
            p = line.split("|")
            steps.append({
                "turn":    int(p[1]),
                "player":  int(p[2]),
                "pos":     int(p[3]),
                "money":   int(p[4]),
                "die":     int(p[5]),
                "roll":    int(p[6]),
                "npos":    int(p[7]),
                "nmoney":  int(p[8]),
                "ndie":    int(p[9]),
                "outcome": p[10],
                "cell":    p[11],
                "card":    p[12],
                "skip":    p[13] == "1",
                "extra":   p[14] == "1",
                "gval":    int(p[15]),
            })
        elif line.startswith("SIM_SKIP|"):
            p = line.split("|")
            steps.append({
                "turn": int(p[1]), "player": int(p[2]),
                "skip_only": True,
                "pos": 0, "roll": 0, "npos": 0, "nmoney": 0, "ndie": 0,
                "outcome": "SKIP", "cell": "Skip Turn",
                "card": "", "gval": 0,
            })
        elif line.startswith("SIM_WIN|"):
            p = line.split("|")
            winner = (int(p[1]), int(p[2]))
        elif line.startswith("SIM_END|"):
            p = line.split("|")
            summary = {
                "p1pos":   int(p[1]), "p1money": int(p[2]), "p1die": int(p[3]),
                "p2pos":   int(p[4]), "p2money": int(p[5]), "p2die": int(p[6]),
            }

    return steps, summary, winner


def _extract_apply_result(output):
    for line in output.splitlines():
        if line.startswith("RESULT|"):
            p = line.split("|")
            return {
                "pos":       int(p[1]),
                "money":     int(p[2]),
                "die":       int(p[3]),
                "cell":      p[4],
                "desc":      p[5],
                "card_name": p[6],
                "card_desc": p[7],
                "skip":      p[8] == "1",
                "extra":     p[9] == "1",
                "item_name": p[10] if len(p) > 10 else "",
            }
        if line.startswith("INVALID|"):
            return {"error": line.split("|")[1]}
    return {}


def _extract_timings(output):
    rows = []
    for fields in _extract_block(output.splitlines(), "TIMING_START", "TIMING_END", "TIMING|"):
        raw_us = fields[3].replace("us", "")
        rows.append({
            "name":       fields[1],
            "complexity": fields[2],
            "time_us":    int(raw_us) if raw_us.isdigit() else 0,
            "result":     fields[4] if len(fields) > 4 else "",
        })
    return rows


def _extract_bfs(output):
    return {
        int(f[1]): int(f[2])
        for f in _extract_block(output.splitlines(), "BFS_START", "BFS_END", "BFS|")
    }


def _extract_dijkstra(output):
    return {
        int(f[1]): int(f[2])
        for f in _extract_block(output.splitlines(), "DIJKSTRA_START", "DIJKSTRA_END", "DIJKSTRA|")
    }


def _extract_prefix(output):
    return {
        int(f[1]): int(f[2])
        for f in _extract_block(output.splitlines(), "PREFIX_START", "PREFIX_END", "PREFIX|")
    }


def _extract_tournament(output):
    rows = []
    for f in _extract_block(output.splitlines(), "TOURNAMENT_START", "TOURNAMENT_END", "TOURNAMENT|"):
        rows.append({
            "strategy": f[1],
            "wins":     int(f[2]),
            "games":    int(f[3]),
            "win_rate": float(f[4]),
            "avg_turns": float(f[5]),
            "avg_money": float(f[6]),
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# Cached board queries (pure — same args → same result every session)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def get_board_cells():
    stdout, _ = _invoke("cellinfo")
    cells = []
    for fields in _extract_block(stdout.splitlines(), "CELLS_START", "CELLS_END", "CELL|"):
        cell_type = _TYPE_MAP.get(int(fields[2]), "normal")
        cells.append({
            "id":    int(fields[1]),
            "type":  cell_type,
            "value": int(fields[3]),
            "emoji": _EMOJI_MAP.get(cell_type, "⬜"),
            "name":  fields[5],
            "desc":  fields[6],
        })
    return cells


@st.cache_data
def get_graph_edges():
    stdout, _ = _invoke("graph")
    return [
        {"from": int(f[1]), "to": int(f[2]), "label": f[3]}
        for f in _extract_block(stdout.splitlines(), "GRAPH_START", "GRAPH_END", "EDGE|")
    ]


@st.cache_data
def get_bfs_distances():
    stdout, _, elapsed_ms = _invoke_timed("bfs")
    return _extract_bfs(stdout), elapsed_ms


@st.cache_data
def get_dijkstra_risks():
    stdout, _, elapsed_ms = _invoke_timed("dijkstra")
    return _extract_dijkstra(stdout), elapsed_ms


@st.cache_data
def get_prefix_gains():
    stdout, _, elapsed_ms = _invoke_timed("prefix")
    return _extract_prefix(stdout), elapsed_ms


@st.cache_data
def get_tournament_results():
    stdout, _, elapsed_ms = _invoke_timed("tournament", timeout=40)
    return _extract_tournament(stdout), elapsed_ms


# ══════════════════════════════════════════════════════════════════════════════
# Public API — called by the Streamlit UI
# ══════════════════════════════════════════════════════════════════════════════

def compute_grundy(pos, money, die):
    stdout, stderr = _invoke("grundy", f"{pos} {money} {die}\n")
    if stderr and not stdout:
        return {"error": stderr, "moves": []}
    return _extract_grundy(stdout)


def get_moves(pos, money, die):
    stdout, _ = _invoke("moves", f"{pos} {money} {die}\n")
    return _extract_moves(stdout)


def apply_move(pos, money, die, roll):
    stdout, stderr = _invoke("apply", f"{pos} {money} {die}\n{roll}\n")
    if stderr and not stdout:
        return {"error": stderr}
    return _extract_apply_result(stdout)


def run_simulation(p1pos, p1money, p1die, p2pos=0, p2money=10, p2die=0):
    payload = f"{p1pos} {p1money} {p1die} {p2pos} {p2money} {p2die}\n"
    stdout, _ = _invoke("simulate", payload)
    return _extract_simulation(stdout)


def get_algo_timings(pos, money, die):
    stdout, _, elapsed_ms = _invoke_timed("timings", f"{pos} {money} {die}\n")
    return _extract_timings(stdout), elapsed_ms


def get_binary_search_coins(pos, die):
    stdout, _, elapsed_ms = _invoke_timed("binsearch", f"{pos} 10 {die}\n")
    for line in stdout.splitlines():
        if line.startswith("BINSEARCH|"):
            return int(line.split("|")[1]), elapsed_ms
    return -1, elapsed_ms
