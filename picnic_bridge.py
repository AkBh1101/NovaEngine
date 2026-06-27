"""
picnic_bridge.py  — Python <-> C++ bridge (v3 Enhanced)
New: Binary Search, Prefix Sum, Bitmask, BFS, Minimax
"""
import subprocess, os, sys, time
import streamlit as st

_DIR     = os.path.dirname(os.path.abspath(__file__))
CPP_SRC  = os.path.join(_DIR, "game_engine.cpp")
CPP_BIN = os.path.join(_DIR, "picnic_engine.exe")

BOARD_SIZE    = 36
INITIAL_MONEY = 10

def compile_engine():
    r = subprocess.run(["g++","-O2","-std=c++17","-o",CPP_BIN,CPP_SRC],
                       capture_output=True, text=True)
    return r.returncode == 0, r.stderr

def _run(mode, stdin_data="", timeout=20):
    try:
        r = subprocess.run([CPP_BIN, mode], input=stdin_data,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="ignore", timeout=timeout)
        return r.stdout, r.stderr
    except subprocess.TimeoutExpired: return "", "TIMEOUT"
    except FileNotFoundError: return "", "Binary not found"

def _run_timed(mode, stdin_data="", timeout=20):
    t0 = time.perf_counter()
    out, err = _run(mode, stdin_data, timeout)
    return out, err, (time.perf_counter()-t0)*1000

CELL_TYPE_NAMES = {0:"normal",1:"money_gain",2:"money_loss",
                   3:"die_upgrade",4:"jump_forward",5:"jump_back",
                   6:"skip_turn",7:"extra_turn",8:"card",9:"start",10:"finish"}
CELL_EMOJIS = {
    "start":"🏠","finish":"🏁","money_gain":"💰","money_loss":"💸",
    "die_upgrade":"🎰","jump_forward":"⏩","jump_back":"⏪",
    "skip_turn":"🚦","extra_turn":"🍀","card":"🃏","normal":"🌿"
}

@st.cache_data
def get_board_cells():
    out, _ = _run("cellinfo")
    cells, active = [], False
    for line in out.splitlines():
        if line == "CELLS_START": active=True; continue
        if line == "CELLS_END": break
        if active and line.startswith("CELL|"):
            p = line.split("|")
            t = CELL_TYPE_NAMES.get(int(p[2]),"normal")
            cells.append({"id":int(p[1]),"type":t,"value":int(p[3]),
                           "emoji":CELL_EMOJIS.get(t,"⬜"),"name":p[5],"desc":p[6]})
    return cells

@st.cache_data
def get_graph_edges():
    out, _ = _run("graph")
    edges, active = [], False
    for line in out.splitlines():
        if line=="GRAPH_START": active=True; continue
        if line=="GRAPH_END": break
        if active and line.startswith("EDGE|"):
            p=line.split("|")
            edges.append({"from":int(p[1]),"to":int(p[2]),"label":p[3]})
    return edges

def parse_moves(output):
    moves, active = [], False
    for line in output.splitlines():
        if line=="MOVES_START": active=True; continue
        if line=="MOVES_END": break
        if active and line.startswith("MOVE|"):
            p=line.split("|")
            moves.append({
                "roll":int(p[1]),"npos":int(p[2]),"nmoney":int(p[3]),
                "ndie":int(p[4]),"grundy":int(p[5]),"outcome":p[6],
                "cell_name":p[7],"cell_emoji":p[8],"cell_desc":p[9],
                "card_name":p[10],"card_desc":p[11],
                "skip":p[12]=="1","extra":p[13]=="1",
                "minimax_val":int(p[14]) if len(p)>14 else 0,
                "collected_item":p[15]=="1" if len(p)>15 else False,
                "item_id":int(p[16]) if len(p)>16 else -1,
                "item_name":p[17] if len(p)>17 else "",
            })
    return moves

def parse_grundy(output):
    d={"grundy":None,"state":None,"moves":[]}
    for line in output.splitlines():
        if line.startswith("GRUNDY|"): d["grundy"]=int(line.split("|")[1])
        elif line.startswith("STATE|"): d["state"]=line.split("|")[1]
    d["moves"]=parse_moves(output)
    return d

def parse_simulate(output):
    steps,end,winner=[],{},(None,None)
    for line in output.splitlines():
        if line.startswith("SIM_STEP|"):
            p=line.split("|")
            steps.append({"turn":int(p[1]),"player":int(p[2]),
                           "pos":int(p[3]),"money":int(p[4]),"die":int(p[5]),
                           "roll":int(p[6]),"npos":int(p[7]),"nmoney":int(p[8]),
                           "ndie":int(p[9]),"outcome":p[10],
                           "cell":p[11],"card":p[12],
                           "skip":p[13]=="1","extra":p[14]=="1","gval":int(p[15])})
        elif line.startswith("SIM_SKIP|"):
            p=line.split("|")
            steps.append({"turn":int(p[1]),"player":int(p[2]),"skip_only":True,
                           "pos":0,"roll":0,"npos":0,"nmoney":0,"ndie":0,
                           "outcome":"SKIP","cell":"Skip Turn","card":"","gval":0})
        elif line.startswith("SIM_WIN|"):
            p=line.split("|"); winner=(int(p[1]),int(p[2]))
        elif line.startswith("SIM_END|"):
            p=line.split("|")
            end={"p1pos":int(p[1]),"p1money":int(p[2]),"p1die":int(p[3]),
                 "p2pos":int(p[4]),"p2money":int(p[5]),"p2die":int(p[6])}
    return steps, end, winner

def parse_apply(output):
    for line in output.splitlines():
        if line.startswith("RESULT|"):
            p=line.split("|")
            return {"pos":int(p[1]),"money":int(p[2]),"die":int(p[3]),
                    "cell":p[4],"desc":p[5],"card_name":p[6],"card_desc":p[7],
                    "skip":p[8]=="1","extra":p[9]=="1",
                    "item_name":p[10] if len(p)>10 else ""}
        elif line.startswith("INVALID|"):
            return {"error":line.split("|")[1]}
    return {}

def parse_timings(output):
    timings=[]
    active=False
    for line in output.splitlines():
        if line=="TIMING_START": active=True; continue
        if line=="TIMING_END": break
        if active and line.startswith("TIMING|"):
            p=line.split("|")
            us_str=p[3].replace("us","")
            timings.append({
                "name":p[1],"complexity":p[2],
                "time_us":int(us_str) if us_str.isdigit() else 0,
                "result":p[4] if len(p)>4 else ""
            })
    return timings

def parse_bfs(output):
    dist={}; active=False
    for line in output.splitlines():
        if line=="BFS_START": active=True; continue
        if line=="BFS_END": break
        if active and line.startswith("BFS|"):
            p=line.split("|"); dist[int(p[1])]=int(p[2])
    return dist

def parse_dijkstra(output):
    dist={}; active=False
    for line in output.splitlines():
        if line=="DIJKSTRA_START": active=True; continue
        if line=="DIJKSTRA_END": break
        if active and line.startswith("DIJKSTRA|"):
            p=line.split("|"); dist[int(p[1])]=int(p[2])
    return dist

def parse_prefix(output):
    gains={}; active=False
    for line in output.splitlines():
        if line=="PREFIX_START": active=True; continue
        if line=="PREFIX_END": break
        if active and line.startswith("PREFIX|"):
            p=line.split("|"); gains[int(p[1])]=int(p[2])
    return gains

def parse_tournament(output):
    rows=[]; active=False
    for line in output.splitlines():
        if line=="TOURNAMENT_START": active=True; continue
        if line=="TOURNAMENT_END": break
        if active and line.startswith("TOURNAMENT|"):
            p=line.split("|")
            rows.append({
                "strategy":p[1],
                "wins":int(p[2]),
                "games":int(p[3]),
                "win_rate":float(p[4]),
                "avg_turns":float(p[5]),
                "avg_money":float(p[6]),
            })
    return rows

# ── Public API ───────────────────────────────────────────────
def compute_grundy(pos, money, die):
    out, err = _run("grundy", f"{pos} {money} {die}\n")
    if err and not out: return {"error":err,"moves":[]}
    return parse_grundy(out)

def get_moves(pos, money, die):
    out, _ = _run("moves", f"{pos} {money} {die}\n")
    return parse_moves(out)

def apply_move(pos, money, die, roll):
    out, err = _run("apply", f"{pos} {money} {die}\n{roll}\n")
    if err and not out: return {"error":err}
    return parse_apply(out)

def run_simulation(p1pos, p1money, p1die, p2pos=0, p2money=10, p2die=0):
    inp = f"{p1pos} {p1money} {p1die} {p2pos} {p2money} {p2die}\n"
    out, err = _run("simulate", inp)
    return parse_simulate(out)

def get_algo_timings(pos, money, die):
    out, err, wall_ms = _run_timed("timings", f"{pos} {money} {die}\n")
    return parse_timings(out), wall_ms

def get_binary_search_coins(pos, die):
    out, err, wall_ms = _run_timed("binsearch", f"{pos} 10 {die}\n")
    for line in out.splitlines():
        if line.startswith("BINSEARCH|"):
            return int(line.split("|")[1]), wall_ms
    return -1, wall_ms

@st.cache_data
def get_bfs_distances():
    out, err, wall_ms = _run_timed("bfs")
    return parse_bfs(out), wall_ms

@st.cache_data
def get_dijkstra_risks():
    out, err, wall_ms = _run_timed("dijkstra")
    return parse_dijkstra(out), wall_ms

@st.cache_data
def get_prefix_gains():
    out, err, wall_ms = _run_timed("prefix")
    return parse_prefix(out), wall_ms

@st.cache_data
def get_tournament_results():
    out, err, wall_ms = _run_timed("tournament", timeout=40)
    return parse_tournament(out), wall_ms
