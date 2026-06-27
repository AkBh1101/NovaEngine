"""
quest_board.py — Picnic Board Game UI
Supports Human vs Human, Human vs AI, and AI vs AI modes.
"""

import math
import os
import random
import sys
import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Bootstrap ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🏕️ Picnic Quest",
    page_icon="🏕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_interface as eng

GRID_SIZE     = eng.BOARD_SIZE
START_COINS   = eng.INITIAL_MONEY

# ══════════════════════════════════════════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════════════════════════════════════════

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700&display=swap');

:root{
  --bg:#0d1117; --surface:#161b22; --surface2:#21262d;
  --border:#30363d; --accent:#58a6ff;
  --green:#3fb950; --red:#f85149; --yellow:#d29922;
  --orange:#db6d28; --purple:#bc8cff; --teal:#39d353;
  --text:#e6edf3; --muted:#8b949e;
  --p1:#f85149; --p2:#58a6ff;
  --card-sh: 0 8px 32px rgba(0,0,0,0.5);
}
html,body,[class*="css"]{
  font-family:'DM Sans',sans-serif!important;
  background:var(--bg)!important;
  color:var(--text)!important;
}
[data-testid="stSidebar"]{
  background:var(--surface)!important;
  border-right:1px solid var(--border)!important;
}
#MainMenu,footer,[data-testid="stToolbar"]{display:none!important}

.card{background:var(--surface);border:1px solid var(--border);
      border-radius:16px;padding:20px 24px;margin-bottom:16px;
      box-shadow:var(--card-sh);}
.card-accent{border-color:var(--accent);}

.game-title{font-family:'Baloo 2',cursive;font-size:3rem;font-weight:800;
  background:linear-gradient(135deg,#58a6ff,#3fb950,#d29922);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  line-height:1.1;margin-bottom:4px;}
.section-title{font-family:'Baloo 2',cursive;font-size:1.4rem;
  font-weight:700;color:var(--accent);margin-bottom:10px;}
.sub-title{color:var(--muted);font-size:1rem;margin-bottom:16px;}

.stButton>button{
  font-family:'Baloo 2',cursive!important;font-size:1rem!important;
  border-radius:10px!important;border:1px solid var(--border)!important;
  background:var(--surface2)!important;color:var(--text)!important;
  padding:10px 24px!important;transition:all .18s!important;
  box-shadow:0 2px 8px rgba(0,0,0,0.3)!important;
}
.stButton>button:hover{
  border-color:var(--accent)!important;color:var(--accent)!important;
  transform:translateY(-1px)!important;
  box-shadow:0 4px 16px rgba(88,166,255,0.3)!important;}

.btn-primary .stButton>button{
  background:linear-gradient(135deg,#1f6feb,#388bfd)!important;
  color:#fff!important;border:none!important;font-size:1.1rem!important;
  padding:12px 32px!important;}
.btn-roll .stButton>button{
  background:linear-gradient(135deg,#b45309,#d97706)!important;
  color:#fff!important;border:none!important;font-size:1.3rem!important;
  padding:14px 0!important;width:100%!important;letter-spacing:.03em;}
.btn-ai .stButton>button{
  background:linear-gradient(135deg,#6e40c9,#9f6eff)!important;
  color:#fff!important;border:none!important;font-size:1.15rem!important;
  padding:12px 28px!important;}

.mbox{background:var(--surface2);border:1px solid var(--border);
      border-radius:12px;padding:12px 16px;text-align:center;}
.mbox-val{font-family:'Baloo 2',cursive;font-size:2rem;font-weight:800;
          color:var(--accent);line-height:1;}
.mbox-lbl{font-size:.7rem;color:var(--muted);text-transform:uppercase;
          letter-spacing:.08em;font-weight:600;margin-top:4px;}

.pcard{border-radius:14px;padding:14px 16px;margin-bottom:10px;
       border:2px solid transparent;transition:all .2s;}
.pcard.p1{background:linear-gradient(135deg,#1e0d0d,#2d1515);}
.pcard.p2{background:linear-gradient(135deg,#0d1520,#0d2137);}
.pcard.active{border-color:var(--yellow)!important;
              box-shadow:0 0 0 3px rgba(210,153,34,.25)!important;}
.ptok{display:inline-flex;align-items:center;justify-content:center;
      width:32px;height:32px;border-radius:50%;font-weight:800;
      font-size:.75rem;border:2px solid rgba(255,255,255,.3);}
.ptok.p1{background:var(--p1);}
.ptok.p2{background:var(--p2);}

.grundy-panel{background:var(--surface2);border:1px solid var(--border);
              border-radius:16px;padding:18px;}
.grundy-num{font-family:'JetBrains Mono',monospace;font-size:3rem;
            font-weight:700;line-height:1;}
.winning{color:var(--green)!important;}
.losing{color:var(--red)!important;}
.move-row{display:flex;align-items:center;gap:10px;padding:8px 12px;
          border-radius:10px;margin:4px 0;font-size:.88rem;cursor:default;}
.move-row.win{background:rgba(63,185,80,.12);border:1px solid rgba(63,185,80,.3);}
.move-row.loss{background:rgba(139,148,158,.06);border:1px solid rgba(139,148,158,.15);}
.move-row .badge{font-family:'JetBrains Mono',monospace;font-size:.75rem;
                 padding:2px 8px;border-radius:6px;font-weight:700;}
.badge-win{background:rgba(63,185,80,.2);color:var(--green);}
.badge-loss{background:rgba(139,148,158,.15);color:var(--muted);}
.badge-g{background:rgba(88,166,255,.15);color:var(--accent);}

.ev{border-radius:12px;padding:12px 18px;font-size:.97rem;
    font-weight:600;margin:10px 0;border-left:4px solid;}
.ev-gain{background:rgba(63,185,80,.1);border-color:var(--green);color:var(--green);}
.ev-loss{background:rgba(248,81,73,.1);border-color:var(--red);color:var(--red);}
.ev-jump{background:rgba(88,166,255,.1);border-color:var(--accent);color:var(--accent);}
.ev-card{background:rgba(188,140,255,.1);border-color:var(--purple);color:var(--purple);}
.ev-skip{background:rgba(210,153,34,.1);border-color:var(--yellow);color:var(--yellow);}
.ev-extra{background:rgba(63,185,80,.1);border-color:var(--teal);color:var(--teal);}
.ev-reset{background:rgba(219,109,40,.1);border-color:var(--orange);color:var(--orange);}
.ev-normal{background:rgba(139,148,158,.08);border-color:var(--muted);color:var(--muted);}
.ev-upgrade{background:rgba(188,140,255,.12);border-color:var(--purple);color:var(--purple);}

.log-entry{font-family:'JetBrains Mono',monospace;font-size:.78rem;
           padding:5px 10px;border-radius:6px;margin:2px 0;
           background:rgba(255,255,255,.03);color:var(--muted);}
.log-entry.hl{background:rgba(88,166,255,.08);color:var(--text);}

.rule-row{display:flex;gap:14px;align-items:flex-start;
          padding:12px 0;border-bottom:1px solid var(--border);}
.rule-icon{font-size:1.5rem;min-width:36px;}
.rule-body{font-size:.93rem;line-height:1.55;}

.win-screen{background:linear-gradient(135deg,#0d2137,#0d1117);
            border:2px solid var(--accent);border-radius:24px;
            padding:48px;text-align:center;}
.win-name{font-family:'Baloo 2',cursive;font-size:3.5rem;font-weight:800;
          background:linear-gradient(135deg,var(--yellow),var(--orange));
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;}

.sim-step-card{background:var(--surface2);border:1px solid var(--border);
               border-radius:12px;padding:12px 16px;margin:6px 0;}
.sim-step-card.p1-step{border-left:3px solid var(--p1);}
.sim-step-card.p2-step{border-left:3px solid var(--p2);}
.sim-step-card.active-step{background:rgba(88,166,255,.07);
                            border-color:var(--accent)!important;}

.stTabs [data-baseweb="tab-list"]{
  background:var(--surface2)!important;border-radius:10px!important;
  border:1px solid var(--border)!important;padding:3px!important;}
.stTabs [data-baseweb="tab"]{font-family:'DM Sans',sans-serif!important;
  font-weight:600!important;color:var(--muted)!important;border-radius:8px!important;}
.stTabs [aria-selected="true"]{background:var(--accent)!important;color:#000!important;}

.stTextInput input,.stNumberInput input{
  background:var(--surface2)!important;border:1px solid var(--border)!important;
  color:var(--text)!important;border-radius:10px!important;
  font-family:'DM Sans',sans-serif!important;}
.stRadio label{color:var(--text)!important;}

.prog-wrap{background:var(--surface2);border-radius:20px;height:12px;
           overflow:hidden;margin:6px 0;}
.prog-bar{height:100%;border-radius:20px;transition:width .4s ease;}
.prog-p1{background:linear-gradient(90deg,var(--p1),#ff6b6b);}
.prog-p2{background:linear-gradient(90deg,var(--p2),#7ec8f5);}

@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.pulse{animation:pulse 1.5s infinite;}
@keyframes pop{0%{transform:scale(.8);opacity:0}80%{transform:scale(1.05)}100%{transform:scale(1);opacity:1}}
.pop{animation:pop .3s ease;}
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

_STATE_DEFAULTS = {
    "screen": "rulebook", "compiled": False, "compile_err": "",
    "p1_name": "Player 1", "p2_name": "Player 2",
    "p1_pos": 0, "p2_pos": 0,
    "p1_money": START_COINS, "p2_money": START_COINS,
    "p1_die": 0, "p2_die": 0,
    "p1_skip": False, "p2_skip": False,
    "p1_extra": False, "p2_extra": False,
    "cur": 1, "winner": None,
    "game_log": [], "last_ev": None, "last_roll": None,
    "play_mode": "Human vs Human",
    "cells": None, "edges": None,
    "sim_steps": [], "sim_end": {}, "sim_winner": (None, None), "sim_idx": 0,
    "grundy_cache": {}, "p1_mask": 0, "p2_mask": 0,
}

for _k, _v in _STATE_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _build_engine():
    """Compile C++ engine if not already done. Returns True on success."""
    if st.session_state.compiled:
        return True
    ok, err = eng.compile_engine()
    st.session_state.compiled = ok
    st.session_state.compile_err = err
    return ok


def _append_log(entry: str):
    st.session_state.game_log.append(entry)
    if len(st.session_state.game_log) > 60:
        st.session_state.game_log = st.session_state.game_log[-60:]


def _cell_label(pos: int) -> str:
    if pos == 0:
        return "🏠 Start"
    if pos >= GRID_SIZE - 1:
        return "🏁 Finish!"
    return f"Cell {pos}"


def _die_label(die_type: int) -> str:
    return "12-sided 🎲" if die_type else "6-sided 🎲"


def _write_player_state(pid, pos, money, die, skip=False, extra=False):
    st.session_state[f"p{pid}_pos"]   = pos
    st.session_state[f"p{pid}_money"] = money
    st.session_state[f"p{pid}_die"]   = die
    st.session_state[f"p{pid}_skip"]  = skip
    st.session_state[f"p{pid}_extra"] = extra


def _detect_winner() -> bool:
    for pid in [1, 2]:
        if st.session_state[f"p{pid}_pos"] >= GRID_SIZE - 1:
            st.session_state.winner = pid
            st.session_state.screen = "results"
            return True
    return False


def _advance_turn():
    pid = st.session_state.cur
    if st.session_state.get(f"p{pid}_extra", False):
        st.session_state[f"p{pid}_extra"] = False
        return
    st.session_state.cur = 3 - pid
    opp = 3 - pid
    if st.session_state.get(f"p{opp}_skip", False):
        st.session_state[f"p{opp}_skip"] = False
        _append_log(f"⏭️ {st.session_state[f'p{opp}_name']} skips their turn!")
        st.session_state.cur = pid


# ── Item (power-up) definitions ───────────────────────────────────────────────
_POWERUPS = [
    {"cell": 5,  "name": "Compass",        "bonus": 2, "emoji": "🧭"},
    {"cell": 11, "name": "Sunscreen",       "bonus": 2, "emoji": "🧴"},
    {"cell": 17, "name": "Water Bottle",    "bonus": 3, "emoji": "💧"},
    {"cell": 21, "name": "Picnic Blanket",  "bonus": 2, "emoji": "🧺"},
    {"cell": 29, "name": "Trail Map",       "bonus": 3, "emoji": "🗺️"},
]


def _handle_powerup(pid: int, item_name: str, current_money: int) -> int:
    """Apply item bonus via bitmask if not already collected. Returns updated money."""
    mask_key = f"p{pid}_mask"
    for idx, item in enumerate(_POWERUPS):
        if item["name"] == item_name:
            already = (st.session_state.get(mask_key, 0) >> idx) & 1
            if not already:
                current_money = min(30, current_money + item["bonus"])
                st.session_state[mask_key] = st.session_state.get(mask_key, 0) | (1 << idx)
            break
    return current_money


def _classify_event(pid, name, pos, money, result):
    """Return (css_class, message) for the event card."""
    np, nm, nd = result["pos"], result["money"], result["die"]
    delta = nm - money
    skip_t  = result.get("skip", False)
    extra_t = result.get("extra", False)
    cell    = result.get("cell", "")
    card_n  = result.get("card_name", "")
    card_d  = result.get("card_desc", "")

    if np == 0 and pos != 0:
        cls = "ev-reset"
        msg = f"😱 {name} went broke and resets to Start! Money restored to {START_COINS}"
    elif delta > 0:
        cls = "ev-gain"
        msg = f"💰 {name} → {cell} · +{delta} coins! ({nm} total)"
    elif delta < 0:
        cls = "ev-loss"
        msg = f"💸 {name} → {cell} · {delta} coins! ({nm} total)"
    elif skip_t:
        cls = "ev-skip"
        msg = f"🚦 {name} lands on {cell} · Skip next turn!"
    elif extra_t:
        cls = "ev-extra"
        msg = f"🍀 {name} lands on {cell} · Extra turn!"
    elif nd != result.get("_prev_die", nd):
        cls = "ev-upgrade"
        msg = f"🎰 {name} lands on {cell} · Die upgraded to 12-sided!"
    elif np > pos + result.get("_roll", 0):
        cls = "ev-jump"
        msg = f"⏩ {name} jumps to cell {np}! ({cell})"
    elif np < pos + result.get("_roll", 0) and np != 0:
        cls = "ev-jump"
        msg = f"⏪ {name} sent back to cell {np}! ({cell})"
    else:
        cls = "ev-normal"
        msg = f"🌿 {name} moves to {cell}"

    if card_n:
        msg += f" · 🃏 {card_n}: {card_d}"
    return cls, msg


def execute_roll(roll: int):
    """Apply a dice roll for the current player and update all state."""
    pid   = st.session_state.cur
    pos   = st.session_state[f"p{pid}_pos"]
    money = st.session_state[f"p{pid}_money"]
    die   = st.session_state[f"p{pid}_die"]
    name  = st.session_state[f"p{pid}_name"]
    st.session_state.last_roll = roll

    result = eng.apply_move(pos, money, die, roll)

    if "error" in result:
        st.session_state.last_ev = {
            "cls": "ev-skip",
            "msg": (f"🎲 {name} rolled {roll} — overshoots the finish! "
                    f"Turn skipped. (Need ≤{GRID_SIZE - 1 - pos} to move)"),
        }
        _append_log(f"T{len(st.session_state.game_log)+1} · P{pid} rolled {roll} · Overshoot! Turn skipped.")
        _advance_turn()
        return

    result["_prev_die"] = die
    result["_roll"]     = roll
    np, nm, nd = result["pos"], result["money"], result["die"]
    skip_t  = result.get("skip",  False)
    extra_t = result.get("extra", False)

    cls, msg = _classify_event(pid, name, pos, money, result)

    item_nm = result.get("item_name", "")
    if item_nm:
        nm = _handle_powerup(pid, item_nm, nm)
        msg += f" · 🎒 Found {item_nm}!"

    st.session_state.last_ev = {"cls": cls, "msg": msg}
    _append_log(f"T{len(st.session_state.game_log)+1} · P{pid} rolled {roll} · {msg}")
    _write_player_state(pid, np, nm, nd, skip_t, extra_t)

    if not _detect_winner():
        if not extra_t:
            _advance_turn()

# ══════════════════════════════════════════════════════════════════════════════
# BOARD FIGURE
# ══════════════════════════════════════════════════════════════════════════════

_TILE_FILL = {
    "start": "#388bfd", "finish": "#a371f7",
    "money_gain": "#3fb950", "money_loss": "#f85149",
    "die_upgrade": "#a371f7", "jump_forward": "#79c0ff",
    "jump_back": "#db6d28", "skip_turn": "#d29922",
    "extra_turn": "#56d364", "card": "#d2a8ff", "normal": "#30363d",
}
_TILE_STROKE = {
    "start": "#58a6ff", "finish": "#d2a8ff",
    "money_gain": "#56d364", "money_loss": "#ff6b6b",
    "die_upgrade": "#d2a8ff", "jump_forward": "#a8d8f0",
    "jump_back": "#ffa657", "skip_turn": "#e3b341",
    "extra_turn": "#3fb950", "card": "#bc8cff", "normal": "#484f58",
}
_COLS = 6


def _grid_coords(idx: int):
    col = idx % _COLS
    row = idx // _COLS
    if row % 2 == 1:
        col = _COLS - 1 - col
    return col * 1.6, -row * 1.6


def _build_board_figure(cells, p1_pos, p2_pos, p1_name, p2_name, edges=None):
    n_rows = math.ceil(len(cells) / _COLS)
    xs, ys, fills, strokes, labels, tips = [], [], [], [], [], []

    for cell in cells:
        i  = cell["id"]
        cx, cy = _grid_coords(i)
        xs.append(cx); ys.append(cy)
        ct = cell["type"]
        fills.append(_TILE_FILL.get(ct, "#30363d"))

        if i == p1_pos and i == p2_pos:   brd = "#ffffff"
        elif i == p1_pos:                  brd = "#f85149"
        elif i == p2_pos:                  brd = "#58a6ff"
        else:                              brd = _TILE_STROKE.get(ct, "#484f58")
        strokes.append(brd)
        labels.append(cell["emoji"])

        tip = f"<b>{cell['emoji']} {cell['name']}</b><br>Cell {i}<br>{cell['desc']}"
        if cell["value"] != 0:
            tip += f"<br>{'+' if cell['value'] > 0 else ''}{cell['value']}"
        tips.append(tip)

    fig = go.Figure()

    # Road layers (dark asphalt → surface → kerb → dashes)
    for i in range(len(cells) - 1):
        x0, y0 = xs[i], ys[i]
        x1, y1 = xs[i + 1], ys[i + 1]
        for width, color in [
            (22, "#1c1f26"),
            (16, "#2b3040"),
            (18, "rgba(255,255,255,0.18)"),
            (14, "#2b3040"),
        ]:
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1], mode="lines",
                line=dict(color=color, width=width),
                hoverinfo="none", showlegend=False))
        for d in range(3):
            t0 = d / 3 + 0.05
            t1 = min(d / 3 + 0.22, (d + 1) / 3 - 0.05)
            fig.add_trace(go.Scatter(
                x=[x0 + t0 * (x1 - x0), x0 + t1 * (x1 - x0)],
                y=[y0 + t0 * (y1 - y0), y0 + t1 * (y1 - y0)],
                mode="lines",
                line=dict(color="rgba(255,210,50,0.7)", width=2, dash="solid"),
                hoverinfo="none", showlegend=False))

    # Special edges
    if edges:
        for e in [e for e in edges if e["label"] != "normal"]:
            fi, ti = e["from"], e["to"]
            if fi < len(cells) and ti < len(cells):
                fx, fy = xs[fi], ys[fi]
                tx, ty = xs[ti], ys[ti]
                mx, my = (fx + tx) / 2 + 0.7, (fy + ty) / 2 + 0.8
                cx_pts, cy_pts = [fx, mx, tx], [fy, my, ty]
                for width, color in [
                    (10, "rgba(163,113,247,0.18)"),
                    (5,  "rgba(90,50,160,0.75)"),
                ]:
                    fig.add_trace(go.Scatter(
                        x=cx_pts, y=cy_pts, mode="lines",
                        line=dict(color=color, width=width),
                        hoverinfo="none", showlegend=False))
                fig.add_trace(go.Scatter(
                    x=cx_pts, y=cy_pts, mode="lines",
                    line=dict(color="rgba(210,168,255,0.9)", width=1, dash="dot"),
                    hoverinfo="none", showlegend=False))
                fig.add_annotation(
                    x=mx, y=my,
                    text=f"✦ {e['label'][:14]}", showarrow=False,
                    font=dict(size=8, color="#d2a8ff", family="DM Sans"),
                    bgcolor="rgba(13,17,23,0.85)",
                    bordercolor="#6e40c9", borderwidth=1, borderpad=3)

    # Cell tiles
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text",
        marker=dict(size=62, color=fills, symbol="square",
                    line=dict(width=3, color=strokes), opacity=0.95),
        text=labels, textposition="middle center",
        textfont=dict(color="white", size=22,
                      family="Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, DM Sans"),
        hovertext=tips, hoverinfo="text", showlegend=False))

    # Cell index badges
    fig.add_trace(go.Scatter(
        x=[x + 0.34 for x in xs], y=[y - 0.34 for y in ys], mode="markers+text",
        marker=dict(size=21, color="rgba(13,17,23,0.78)", symbol="circle",
                    line=dict(width=1, color="rgba(255,255,255,0.45)")),
        text=[str(c["id"]) for c in cells], textposition="middle center",
        textfont=dict(color="#ffffff", size=9, family="JetBrains Mono, DM Sans"),
        hoverinfo="none", showlegend=False))

    # Player tokens
    def _token(pid, pos, name, color):
        tx, ty = _grid_coords(pos)
        off = (-0.25, +0.25) if pid == 1 else (+0.25, -0.25)
        fig.add_trace(go.Scatter(
            x=[tx + off[0]], y=[ty + off[1]], mode="markers+text",
            marker=dict(size=26, color=color, symbol="circle",
                        line=dict(width=2, color="white")),
            text=[name[:2].upper()],
            textfont=dict(color="white", size=8, family="Baloo 2"),
            textposition="middle center",
            name=f"{'🔴' if pid==1 else '🔵'} {name}", hoverinfo="name"))

    _token(1, p1_pos, p1_name, "#f85149")
    _token(2, p2_pos, p2_name, "#58a6ff")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,17,23,0.6)",
        xaxis=dict(visible=False, range=[-0.9, (_COLS - 1) * 1.6 + 0.9]),
        yaxis=dict(visible=False, range=[-(n_rows - 1) * 1.6 - 0.9, 1.0]),
        margin=dict(l=10, r=10, t=10, b=10),
        height=max(320, n_rows * 115),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                    font=dict(family="DM Sans", size=13, color="#e6edf3"),
                    bgcolor="rgba(22,27,34,0.9)", bordercolor="#30363d", borderwidth=1),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# GRUNDY ANALYSIS PANEL
# ══════════════════════════════════════════════════════════════════════════════

def _progress_bars(name_a, pos_a, color_a, name_b, pos_b, color_b):
    pct_a = int(pos_a / (GRID_SIZE - 1) * 100)
    pct_b = int(pos_b / (GRID_SIZE - 1) * 100)
    st.markdown(
        f'<div style="margin-top:14px;font-size:.82rem;color:var(--muted);font-weight:600">'
        f'📍 Board Progress</div>'
        f'<div>{name_a[:10]} <span style="color:{color_a}">{pct_a}%</span></div>'
        f'<div class="prog-wrap"><div class="prog-bar prog-p1" style="width:{pct_a}%"></div></div>'
        f'<div>{name_b[:10]} <span style="color:{color_b}">{pct_b}%</span></div>'
        f'<div class="prog-wrap"><div class="prog-bar prog-p2" style="width:{pct_b}%"></div></div>',
        unsafe_allow_html=True)


def render_grundy_panel(active_player: int):
    pid  = active_player
    opp  = 3 - pid
    pos  = st.session_state[f"p{pid}_pos"]
    mon  = st.session_state[f"p{pid}_money"]
    die  = st.session_state[f"p{pid}_die"]
    opos = st.session_state[f"p{opp}_pos"]
    omon = st.session_state[f"p{opp}_money"]
    odie = st.session_state[f"p{opp}_die"]
    nm   = st.session_state[f"p{pid}_name"]
    onm  = st.session_state[f"p{opp}_name"]

    g_cur = eng.compute_grundy(pos, mon, die)
    g_opp = eng.compute_grundy(opos, omon, odie)

    gv   = g_cur.get("grundy", 0) or 0
    gs   = g_cur.get("state", "LOSING")
    gvo  = g_opp.get("grundy", 0) or 0
    gso  = g_opp.get("state", "LOSING")

    c_cur = "winning" if gs  == "WINNING" else "losing"
    c_opp = "winning" if gso == "WINNING" else "losing"

    st.markdown('<div class="grundy-panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧠 Sprague–Grundy Analysis</div>', unsafe_allow_html=True)

    if gs == "WINNING" and gso != "WINNING":
        headline = f"<span style='color:var(--green);font-weight:700'>🏆 {nm} is in a WINNING position!</span>"
    elif gso == "WINNING" and gs != "WINNING":
        headline = f"<span style='color:var(--red);font-weight:700'>⚠️ {onm} has the strategic advantage!</span>"
    else:
        headline = "<span style='color:var(--yellow);font-weight:700'>⚖️ Both players in equal (losing) positions — depends on dice!</span>"
    st.markdown(f'<div style="margin-bottom:14px;font-size:.95rem">{headline}</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    for col, name, val, state, css in [
        (col_a, nm[:8],  gv,  gs,  c_cur),
        (col_b, onm[:8], gvo, gso, c_opp),
    ]:
        color_word = "green" if state == "WINNING" else "red"
        col.markdown(
            f'<div class="mbox"><div class="mbox-val {css}">{val}</div>'
            f'<div class="mbox-lbl">G({name})</div>'
            f'<div style="font-size:.8rem;margin-top:4px;color:var(--{color_word})">'
            f'{"✅ WINNING" if state=="WINNING" else "❌ LOSING"}</div></div>',
            unsafe_allow_html=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:.8rem;color:var(--muted);margin-bottom:8px">'
        'G=0 → losing position (with optimal opponent play). '
        'G≠0 → winning — there exists a move to force G=0 on the opponent.</div>',
        unsafe_allow_html=True)

    moves = g_cur.get("moves", [])
    if moves:
        st.markdown(
            '<div style="font-weight:600;margin-bottom:6px;font-size:.9rem">🎯 Recommended Moves for You:</div>',
            unsafe_allow_html=True)
        win_moves = [m for m in moves if m["outcome"] == "WIN"]
        if win_moves:
            st.markdown(
                '<div style="font-size:.78rem;color:var(--green);margin-bottom:4px">'
                '✅ These moves put the opponent in a LOSING position (G=0 for them):</div>',
                unsafe_allow_html=True)
            for m in win_moves[:4]:
                st.markdown(
                    f'<div class="move-row win">'
                    f'<span class="badge badge-win">Roll {m["roll"]}</span>'
                    f'<span>→ {m["cell_emoji"]} <b>{m["cell_name"]}</b> (cell {m["npos"]})</span>'
                    f'<span class="badge badge-g" style="margin-left:auto">G={m["grundy"]}</span>'
                    f'</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="font-size:.78rem;color:var(--yellow);margin-bottom:4px">'
                '⚠️ No winning move exists this turn. Pick the highest-G move:</div>',
                unsafe_allow_html=True)
            for m in moves[:4]:
                st.markdown(
                    f'<div class="move-row loss">'
                    f'<span class="badge badge-loss">Roll {m["roll"]}</span>'
                    f'<span>→ {m["cell_emoji"]} <b>{m["cell_name"]}</b> (cell {m["npos"]})</span>'
                    f'<span class="badge badge-g" style="margin-left:auto">G={m["grundy"]}</span>'
                    f'</div>', unsafe_allow_html=True)

        _progress_bars(nm, pos, "var(--p1)", onm, opos, "var(--p2)")

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar():
    pid = st.session_state.cur
    with st.sidebar:
        st.markdown(
            '<div style="font-family:Baloo 2,cursive;font-size:1.6rem;'
            'font-weight:800;color:#58a6ff">🏕️ Picnic Quest</div>',
            unsafe_allow_html=True)
        st.markdown(
            f'<div style="color:var(--muted);font-size:.85rem;margin-bottom:12px">'
            f'{st.session_state.play_mode}</div>', unsafe_allow_html=True)
        st.divider()

        for pn in [1, 2]:
            nm    = st.session_state[f"p{pn}_name"]
            pos   = st.session_state[f"p{pn}_pos"]
            coins = st.session_state[f"p{pn}_money"]
            die   = st.session_state[f"p{pn}_die"]
            skip  = st.session_state.get(f"p{pn}_skip", False)
            is_active = (pn == pid)
            acls  = "active" if is_active else ""
            tok   = f"p{pn}"
            turn_badge = ("<span style='color:#d29922;font-size:.75rem;margin-left:auto'>◀ YOUR TURN</span>"
                          if is_active else "")
            skip_line = "<br>⏭️ <i>Skipping next</i>" if skip else ""
            progress = int(pos / (GRID_SIZE - 1) * 100)
            st.markdown(
                f'<div class="pcard p{pn} {acls}">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">'
                f'<span class="ptok {tok}">{nm[:2].upper()}</span>'
                f'<b style="font-size:.97rem">{nm}</b>{turn_badge}</div>'
                f'<div style="font-size:.85rem;color:var(--muted);line-height:1.6">'
                f'📍 {_cell_label(pos)}<br>💰 {coins} coins &nbsp;·&nbsp; {_die_label(die)}'
                f'{skip_line}</div>'
                f'<div class="prog-wrap" style="margin-top:8px">'
                f'<div class="prog-bar prog-p{pn}" style="width:{progress}%"></div>'
                f'</div></div>', unsafe_allow_html=True)

        st.divider()
        if st.button("🔄 Restart", use_container_width=True):
            for k, v in _STATE_DEFAULTS.items():
                if k not in ("compiled", "compile_err", "cells", "edges",
                             "play_mode", "p1_name", "p2_name"):
                    st.session_state[k] = v
            st.session_state.screen = "setup"
            st.rerun()
        if st.button("📖 Rules", use_container_width=True):
            st.session_state.screen = "rulebook"
            st.rerun()

        st.divider()
        st.markdown(
            '<div style="font-size:.8rem;font-weight:600;color:var(--muted);margin-bottom:6px">'
            '📜 RECENT LOG</div>', unsafe_allow_html=True)
        for entry in reversed(st.session_state.game_log[-10:]):
            st.markdown(f'<div class="log-entry">{entry}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: RULEBOOK
# ══════════════════════════════════════════════════════════════════════════════

_RULES = [
    ("🎯", "Objective",   "Be first to land **exactly** on cell 35 (Finish). Overshooting is illegal — you simply don't move."),
    ("🎲", "Dice",        "Start with a 6-sided die. Hit special ⭐ or 🎰 cells to permanently upgrade to a 12-sided die."),
    ("💰", "Coins",       "Begin with 10 coins. Gain and lose coins on special cells. Your wealth matters — it affects resets!"),
    ("🔁", "Reset Rule",  "Drop to 0 coins or less → instantly sent back to Start with 10 coins. Die type stays the same."),
    ("⏩⏪","Jumps",       "Some cells teleport you forward (🚗🛫) or backward (🚌🌧️) — plan your path carefully!"),
    ("🃏", "Event Cards", "Land on 🃏 cells to draw a card: gain coins, lose coins, jump, skip, or get an extra turn."),
    ("🚦", "Skip Turn",   "Land on 🚦 or 😴 → your NEXT turn is skipped. The opponent can exploit this!"),
    ("🍀", "Extra Turn",  "Land on 🍀 or ⚡ → roll again immediately in the same turn."),
    ("🧠", "Game Theory", "The Sprague–Grundy theorem labels every position. G=0 means you're in a LOSING position; "
                          "G≠0 means you can force a win. The AI panel shows you these values and the best moves to make."),
]

_CELL_LEGEND = [
    ("🏠",           "#388bfd", "Start — Home base"),
    ("🏁",           "#a371f7", "Finish — Win!"),
    ("💰 🍔 🎯 🎁",  "#3fb950", "Money Gain (+coins)"),
    ("💸 🍕 🚕 ⏳",  "#f85149", "Money Loss (−coins)"),
    ("🎰 ⭐",        "#a371f7", "Die Upgrade → 12-sided"),
    ("🚗 🛫",        "#79c0ff", "Jump Forward"),
    ("🚌 🌧️",       "#db6d28", "Jump Backward"),
    ("🚦 😴",        "#d29922", "Skip Turn"),
    ("🍀 ⚡",        "#56d364", "Extra Turn"),
    ("🃏",           "#d2a8ff", "Event Card"),
]

def screen_rulebook():
    st.markdown('<div class="game-title">🏕️ Picnic Quest</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">A dynamic board game powered by the Sprague–Grundy theorem</div>',
        unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        st.markdown('<div class="section-title">📖 How to Play</div>', unsafe_allow_html=True)
        for em, title, desc in _RULES:
            st.markdown(
                f'<div class="rule-row"><div class="rule-icon">{em}</div>'
                f'<div class="rule-body"><b>{title}</b><br>{desc}</div></div>',
                unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🗺️ Cell Types</div>', unsafe_allow_html=True)
        for em, color, lbl in _CELL_LEGEND:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;padding:7px 0;'
                f'border-bottom:1px solid #30363d;">'
                f'<div style="background:{color}22;border:1px solid {color};border-radius:8px;'
                f'padding:3px 8px;color:{color};font-size:.9rem;min-width:90px;text-align:center">{em}</div>'
                f'<div style="font-size:.88rem;color:var(--text)">{lbl}</div>'
                f'</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card" style="margin-top:0">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚡ Quick Facts</div>', unsafe_allow_html=True)
        for icon, fact in [
            ("📐", "36 cells, 0–35"), ("👥", "2 players"),
            ("💰", "Start: 10 coins"), ("🎲", "6-sided → upgrades to 12"),
            ("🧠", "Grundy AI hints every turn"), ("🃏", "8 event card types"),
        ]:
            st.markdown(f'<div style="padding:4px 0;color:var(--text)">{icon} {fact}</div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    _, btn_c, _ = st.columns([3, 2, 3])
    with btn_c:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("🚀 Let's Play!", use_container_width=True):
            with st.spinner("Compiling game engine..."):
                ok = _build_engine()
            if ok:
                st.session_state.screen = "setup"
                st.rerun()
            else:
                st.error(f"Compile error:\n{st.session_state.compile_err}")
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: SETUP
# ══════════════════════════════════════════════════════════════════════════════

_MODE_DESCS = {
    "Human vs Human": "Both players roll manually.",
    "Human vs AI":    "You play vs an AI that uses Grundy-optimal moves.",
    "AI vs AI":       "Watch two AIs play and analyze the game.",
}

def screen_setup():
    st.markdown('<div class="game-title">👤 Player Setup</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Configure your game before the adventure begins</div>',
        unsafe_allow_html=True)
    st.divider()

    c1, c2, c3 = st.columns(3, gap="large")

    def _name_card(col, pnum, color_var, default_key):
        with col:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### {'🔴' if pnum==1 else '🔵'} Player {pnum}")
            val = st.text_input("Name",
                                value=st.session_state[f"p{pnum}_name"],
                                max_chars=18, key=default_key)
            display = val or f"Player {pnum}"
            tok = f"p{pnum}"
            st.markdown(
                f'<div style="margin-top:8px;display:flex;align-items:center;gap:8px">'
                f'<span class="ptok {tok}">{display[:2].upper()}</span>'
                f'<span style="color:{color_var};font-weight:700">{display}</span>'
                f'</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            return val

    p1 = _name_card(c1, 1, "var(--p1)", "sp1")
    p2 = _name_card(c2, 2, "var(--p2)", "sp2")

    with c3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Game Mode")
        modes = list(_MODE_DESCS.keys())
        mode = st.radio("Mode", modes,
                        index=modes.index(st.session_state.play_mode),
                        label_visibility="collapsed")
        st.markdown(
            f'<div style="color:var(--muted);font-size:.85rem;margin-top:8px">'
            f'{_MODE_DESCS[mode]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    cb, cs, _ = st.columns([2, 2, 4])
    with cb:
        if st.button("← Back"):
            st.session_state.screen = "rulebook"
            st.rerun()
    with cs:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("🎮 Begin!", use_container_width=True):
            for k, v in _STATE_DEFAULTS.items():
                if k not in ("compiled", "compile_err"):
                    st.session_state[k] = v
            st.session_state.p1_name  = p1 or "Player 1"
            st.session_state.p2_name  = p2 or "Player 2"
            st.session_state.play_mode = mode
            st.session_state.p1_money = START_COINS
            st.session_state.p2_money = START_COINS
            try:
                st.session_state.cells = eng.get_board_cells()
                st.session_state.edges = eng.get_graph_edges()
            except Exception:
                pass
            if mode == "AI vs AI":
                steps, end, winner = eng.run_simulation(0, START_COINS, 0)
                st.session_state.sim_steps  = steps
                st.session_state.sim_end    = end
                st.session_state.sim_winner = winner
                st.session_state.sim_idx    = 0
            st.session_state.screen = "game"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: HUMAN vs HUMAN / HUMAN vs AI
# ══════════════════════════════════════════════════════════════════════════════

_BOARD_LEGEND = [
    ("💰", "#3fb950", "Gain"),
    ("💸", "#f85149", "Loss"),
    ("🎰", "#a371f7", "Upgrade"),
    ("⏩", "#79c0ff", "Jump Fwd"),
    ("⏪", "#db6d28", "Jump Back"),
    ("🃏", "#d2a8ff", "Card"),
]
_DICE_ICONS = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]


def _render_dice_animation(faces: int) -> int:
    roll = random.randint(1, faces)
    ph = st.empty()
    for _ in range(6):
        ph.markdown(
            f'<div style="font-size:5rem;text-align:center;margin:8px">'
            f'{random.choice(_DICE_ICONS)}</div>', unsafe_allow_html=True)
        time.sleep(0.06)
    ph.markdown(
        f'<div style="font-size:5rem;text-align:center;margin:8px;animation:pop .3s ease">'
        f'{_DICE_ICONS[min(roll, 6) - 1] if roll <= 6 else "🎲"}</div>',
        unsafe_allow_html=True)
    time.sleep(0.2)
    ph.empty()
    return roll


def _render_move_detail_tab(pid: int):
    pos   = st.session_state[f"p{pid}_pos"]
    money = st.session_state[f"p{pid}_money"]
    die   = st.session_state[f"p{pid}_die"]

    g_data = eng.compute_grundy(pos, money, die)
    gv     = g_data.get("grundy", 0) or 0
    gs     = g_data.get("state", "LOSING")
    sc     = "var(--green)" if gs == "WINNING" else "var(--red)"

    st.markdown(
        f'<div class="card" style="padding:16px 18px;margin-bottom:14px">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'gap:14px;flex-wrap:wrap">'
        f'<div><div class="section-title" style="margin-bottom:2px">Current State Analysis</div>'
        f'<div style="color:var(--muted);font-size:.86rem">'
        f'Cell {pos} · {money} coins · {_die_label(die)}</div></div>'
        f'<div style="display:flex;gap:10px;align-items:center">'
        f'<div class="mbox" style="min-width:92px;margin:0">'
        f'<div class="mbox-val" style="color:{sc}">{gv}</div>'
        f'<div class="mbox-lbl">Grundy</div></div>'
        f'<div class="mbox" style="min-width:110px;margin:0">'
        f'<div class="mbox-val" style="font-size:1.35rem;color:{sc}">{gs}</div>'
        f'<div class="mbox-lbl">Position</div></div>'
        f'</div></div></div>', unsafe_allow_html=True)

    moves = eng.get_moves(pos, money, die)
    if moves:
        st.markdown(
            '<div style="font-weight:700;font-size:.95rem;color:var(--text);margin-bottom:8px">'
            'Best legal moves from this state</div>', unsafe_allow_html=True)
        for rank, m in enumerate(moves[:6], start=1):
            item_tag = f"🎒{m.get('item_name','')}" if m.get("collected_item") else ""
            row_bg   = "rgba(63,185,80,.12)" if rank == 1 else ""
            tag      = "Best" if rank == 1 else f"#{rank}"
            outcome_cls = "win" if m["outcome"] == "WIN" else "loss"
            badge_cls   = "badge-win" if m["outcome"] == "WIN" else "badge-loss"
            st.markdown(
                f'<div class="move-row {outcome_cls}" style="background:{row_bg}">'
                f'<span class="badge badge-g">{tag}</span>'
                f'<span class="badge {badge_cls}">Roll {m["roll"]}</span>'
                f'<span>→ {m["cell_emoji"]} <b>{m["cell_name"]}</b></span>'
                f'<span style="font-size:.75rem;color:var(--muted)">{item_tag}</span>'
                f'<span class="badge badge-g" style="margin-left:auto">G={m["grundy"]}</span>'
                f'<span style="font-size:.72rem;color:var(--muted);margin-left:6px">'
                f'MM={m.get("minimax_val",0)}</span>'
                f'</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="ev ev-normal">No legal moves available from this state.</div>',
            unsafe_allow_html=True)


def screen_game():
    render_sidebar()
    mode = st.session_state.play_mode

    if mode == "AI vs AI":
        screen_ai_vs_ai()
        return

    cells = st.session_state.cells
    edges = st.session_state.edges
    pid   = st.session_state.cur
    p1n   = st.session_state.p1_name
    p2n   = st.session_state.p2_name

    if not cells:
        st.error("Board unavailable. Engine may not be compiled.")
        return

    fig = _build_board_figure(
        cells, st.session_state.p1_pos, st.session_state.p2_pos, p1n, p2n, edges)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    lcols = st.columns(6)
    for col, (em, c, lbl) in zip(lcols, _BOARD_LEGEND):
        col.markdown(
            f'<div style="display:flex;align-items:center;gap:4px;font-size:.76rem">'
            f'<div style="width:10px;height:10px;background:{c};border-radius:3px"></div>'
            f'{em} {lbl}</div>', unsafe_allow_html=True)

    st.markdown("---")

    nm    = st.session_state[f"p{pid}_name"]
    pos   = st.session_state[f"p{pid}_pos"]
    money = st.session_state[f"p{pid}_money"]
    die   = st.session_state[f"p{pid}_die"]
    faces = 12 if die else 6
    color = "var(--p1)" if pid == 1 else "var(--p2)"
    tok   = f"p{pid}"

    col_ctrl, col_grundy = st.columns([3, 2], gap="large")

    with col_ctrl:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">'
            f'<span class="ptok {tok}" style="width:40px;height:40px;font-size:.9rem">'
            f'{nm[:2].upper()}</span>'
            f'<div><div style="font-family:Baloo 2,cursive;font-size:1.6rem;'
            f'font-weight:800;color:{color}">{nm}\'s Turn</div>'
            f'<div style="color:var(--muted);font-size:.85rem">'
            f'{_die_label(die)} · {faces} possible moves</div>'
            f'</div></div>', unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="mbox"><div class="mbox-val">{pos}</div>'
                    '<div class="mbox-lbl">Cell</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="mbox"><div class="mbox-val">{money}</div>'
                    '<div class="mbox-lbl">Coins 💰</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="mbox"><div class="mbox-val">{faces}</div>'
                    '<div class="mbox-lbl">Die Faces</div></div>', unsafe_allow_html=True)

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

        is_ai_turn = (mode == "Human vs AI" and pid == 2)

        if is_ai_turn:
            st.markdown(
                f'<div class="ev ev-normal pulse">🤖 <b>{nm} (AI)</b> is computing optimal move...</div>',
                unsafe_allow_html=True)
            st.markdown('<div class="btn-ai">', unsafe_allow_html=True)
            if st.button("▶️ Execute AI Move", use_container_width=True):
                with st.spinner("AI thinking with Grundy..."):
                    ai_moves = eng.get_moves(pos, money, die)
                if ai_moves:
                    best = ai_moves[0]
                    execute_roll(best["roll"])
                    _append_log(f"🤖 AI: roll {best['roll']} (G={best['grundy']}, {best['outcome']})")
                else:
                    st.warning("AI has no valid moves!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="btn-roll">', unsafe_allow_html=True)
            if st.button(f"🎲 Roll {faces}-sided Die", use_container_width=True):
                roll = _render_dice_animation(faces)
                execute_roll(roll)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        ev = st.session_state.last_ev
        if ev:
            st.markdown(f'<div class="ev {ev["cls"]} pop">{ev["msg"]}</div>',
                        unsafe_allow_html=True)

    with col_grundy:
        render_grundy_panel(pid)

    st.markdown("---")
    tab1, tab2 = st.tabs(["🧠 Grundy Details", "⚙️ Algorithm Dashboard"])
    with tab1:
        _render_move_detail_tab(pid)
    with tab2:
        render_algo_dashboard(pid)

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: AI vs AI
# ══════════════════════════════════════════════════════════════════════════════

def _replay_positions(steps, up_to_idx):
    """Compute board state by replaying steps[0..up_to_idx]."""
    p1_pos = p2_pos = 0
    p1_mon = p2_mon = START_COINS
    p1_die = p2_die = 0
    for step in steps[:up_to_idx + 1]:
        if step.get("skip_only"):
            continue
        if step["player"] == 1:
            p1_pos, p1_mon, p1_die = step["npos"], step["nmoney"], step["ndie"]
        else:
            p2_pos, p2_mon, p2_die = step["npos"], step["nmoney"], step["ndie"]
    return p1_pos, p1_mon, p1_die, p2_pos, p2_mon, p2_die


def screen_ai_vs_ai():
    cells   = st.session_state.cells
    edges   = st.session_state.edges
    steps   = st.session_state.sim_steps
    winner  = st.session_state.sim_winner
    p1n     = st.session_state.p1_name
    p2n     = st.session_state.p2_name

    if not steps:
        st.warning("No simulation data. Please go back to setup.")
        return

    total = len(steps)
    idx   = st.session_state.sim_idx
    cur   = steps[idx]

    p1_pos, p1_mon, _, p2_pos, p2_mon, _ = _replay_positions(steps, idx)

    st.markdown(
        '<div class="section-title">🤖 AI vs AI — Optimal Play Simulation</div>',
        unsafe_allow_html=True)

    if winner[0]:
        wname  = p1n if winner[0] == 1 else p2n
        wcolor = "var(--p1)" if winner[0] == 1 else "var(--p2)"
        st.markdown(
            f'<div style="background:rgba(88,166,255,.07);border:1px solid var(--border);'
            f'border-radius:12px;padding:12px 18px;margin-bottom:12px;">'
            f'🏆 <b style="color:{wcolor}">{wname}</b> wins in {winner[1]} turns '
            f'with optimal Grundy play!</div>', unsafe_allow_html=True)

    if cells:
        fig = _build_board_figure(cells, p1_pos, p2_pos, p1n, p2n, edges)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    col_slider, col_btn = st.columns([5, 1])
    with col_slider:
        new_idx = st.slider("Step", 0, total - 1, idx,
                            key="sim_slider", label_visibility="collapsed")
        if new_idx != idx:
            st.session_state.sim_idx = new_idx
            st.rerun()
    with col_btn:
        if st.button("⏭️", help="Next step") and idx < total - 1:
            st.session_state.sim_idx = idx + 1
            st.rerun()

    st.markdown(f'<div style="color:var(--muted);font-size:.82rem;margin-bottom:12px">'
                f'Step {idx + 1} of {total}</div>', unsafe_allow_html=True)

    if not cur.get("skip_only"):
        pname  = p1n if cur["player"] == 1 else p2n
        pcolor = "var(--p1)" if cur["player"] == 1 else "var(--p2)"
        ev_cls = "ev-gain" if cur["outcome"] == "WIN" else "ev-loss"
        card_str = f"· 🃏 {cur['card']}" if cur["card"] else ""
        st.markdown(
            f'<div class="ev {ev_cls}">'
            f'<b style="color:{pcolor}">{pname}</b> · Turn {cur["turn"]} · '
            f'Roll <b>{cur["roll"]}</b> · {cur["pos"]}→<b>{cur["npos"]}</b> · '
            f'💰{cur["nmoney"]} · {cur["cell"]} {card_str} · G={cur["gval"]}'
            f'</div>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    for col, val, lbl, color in [
        (m1, cur.get("turn", 0),             "Turn",          "var(--accent)"),
        (m2, p1_pos,                          p1n[:8],         "var(--p1)"),
        (m3, p2_pos,                          p2n[:8],         "var(--p2)"),
        (m4, f"{p1_mon}💰",                   f"{p1n[:6]} coins", "var(--p1)"),
        (m5, f"{p2_mon}💰",                   f"{p2n[:6]} coins", "var(--p2)"),
    ]:
        col.markdown(
            f'<div class="mbox"><div class="mbox-val" style="color:{color}">{val}</div>'
            f'<div class="mbox-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col_log, col_chart = st.columns([2, 3])

    with col_log:
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem">📜 Move Log</div>',
            unsafe_allow_html=True)
        log_parts = []
        for i, step in enumerate(steps):
            if step.get("skip_only"):
                log_parts.append(f'<div class="log-entry">T{step["turn"]} P{step["player"]} SKIP</div>')
                continue
            hl   = "hl" if i == idx else ""
            pc   = "p1" if step["player"] == 1 else "p2"
            nm   = (p1n if step["player"] == 1 else p2n)[:6]
            oc   = "✅" if step["outcome"] == "WIN" else "·"
            log_parts.append(
                f'<div class="log-entry {hl}">'
                f'<span style="color:var(--{pc})">{nm}</span> '
                f'T{step["turn"]} r{step["roll"]} {step["pos"]}→{step["npos"]} '
                f'G={step["gval"]} {oc}</div>')
        st.markdown("".join(log_parts), unsafe_allow_html=True)

    with col_chart:
        pos_data, g_data = [], []
        cp1 = cp2 = 0
        for i, step in enumerate(steps[:idx + 1]):
            if step.get("skip_only"):
                continue
            if step["player"] == 1:
                cp1 = step["npos"]
            else:
                cp2 = step["npos"]
            pos_data.append({"Step": i + 1, p1n: cp1, p2n: cp2})
            g_data.append({
                "Step": i + 1, "Grundy": step["gval"],
                "Player": p1n if step["player"] == 1 else p2n,
            })

        _chart_layout = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(22,27,34,.6)",
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(font=dict(color="#e6edf3")),
        )

        if pos_data:
            df = pd.DataFrame(pos_data)
            fig2 = px.line(df, x="Step", y=[p1n, p2n], markers=True,
                           color_discrete_map={p1n: "#f85149", p2n: "#58a6ff"},
                           title="Board Position Over Time", template="plotly_dark")
            fig2.update_layout(**_chart_layout, height=300)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        if g_data:
            dfg = pd.DataFrame(g_data)
            fig3 = px.bar(dfg, x="Step", y="Grundy", color="Player", barmode="group",
                          color_discrete_map={p1n: "#f85149", p2n: "#58a6ff"},
                          title="Grundy Value per Move", template="plotly_dark")
            fig3.update_layout(**_chart_layout, height=250)
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: RESULTS
# ══════════════════════════════════════════════════════════════════════════════

def screen_results():
    with st.sidebar:
        st.markdown(
            '<div style="font-family:Baloo 2,cursive;font-size:1.4rem;color:#58a6ff">'
            '🏕️ Game Over!</div>', unsafe_allow_html=True)
        if st.button("🔄 Play Again", use_container_width=True):
            for k, v in _STATE_DEFAULTS.items():
                if k not in ("compiled", "compile_err", "cells", "edges"):
                    st.session_state[k] = v
            st.session_state.screen = "setup"
            st.rerun()

    w  = st.session_state.winner
    wn = st.session_state[f"p{w}_name"]
    wm = st.session_state[f"p{w}_money"]
    ln = st.session_state[f"p{3-w}_name"]
    lm = st.session_state[f"p{3-w}_money"]

    st.markdown(
        f'<div class="win-screen">'
        f'<div style="font-size:5rem">🏆</div>'
        f'<div class="win-name">{wn} Wins!</div>'
        f'<div style="font-size:1.1rem;color:var(--muted);margin-top:8px">'
        f'Reached the finish with {wm} coins remaining</div>'
        f'</div>', unsafe_allow_html=True)

    st.markdown("")
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        f'<div class="mbox"><div class="mbox-val">{len(st.session_state.game_log)}</div>'
        '<div class="mbox-lbl">Total Turns</div></div>', unsafe_allow_html=True)
    c2.markdown(
        f'<div class="mbox"><div class="mbox-val" style="color:var(--green)">{wm}</div>'
        f'<div class="mbox-lbl">{wn[:10]} Coins</div></div>', unsafe_allow_html=True)
    c3.markdown(
        f'<div class="mbox"><div class="mbox-val" style="color:var(--red)">{lm}</div>'
        f'<div class="mbox-lbl">{ln[:10]} Coins</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    ca, cb, _ = st.columns([2, 2, 3])
    with ca:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("🔄 Play Again", use_container_width=True):
            for k, v in _STATE_DEFAULTS.items():
                if k not in ("compiled", "compile_err", "cells", "edges"):
                    st.session_state[k] = v
            st.session_state.screen = "setup"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with cb:
        if st.button("📖 Rules", use_container_width=True):
            st.session_state.screen = "rulebook"
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-title">📜 Full Game Log</div>', unsafe_allow_html=True)
    for entry in st.session_state.game_log:
        st.markdown(f'<div class="log-entry hl">{entry}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ALGORITHM DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

_ALGO_ICON = {
    "Grundy": "🧠", "Binary Search": "🔍", "Prefix Sum": "📊",
    "BFS": "🗺️", "Minimax": "♟️", "Dijkstra": "🧭",
}
_COMPLEXITY_COLOR = {
    "O(1)": "#3fb950", "O(N)": "#3fb950", "O(N log": "#3fb950",
    "O(V+E)": "#58a6ff", "O(B*M": "#d29922", "O(log M": "#d29922",
    "O(D^": "#f85149", "O(E log": "#58a6ff",
}


def _complexity_color(cplx: str) -> str:
    for prefix, color in _COMPLEXITY_COLOR.items():
        if cplx.startswith(prefix):
            return color
    return "#58a6ff"


def _format_us(us: int) -> str:
    if us == 0:     return "< 1 µs"
    if us < 1000:   return f"{us} µs"
    return f"{us / 1000:.1f} ms"


def _timing_table(timings, wall_ms: float):
    rows = [
        '<div style="overflow-x:auto;border:1px solid var(--border);'
        'border-radius:10px;background:var(--surface);">',
        '<table style="width:100%;border-collapse:collapse;font-size:.82rem;'
        'font-family:JetBrains Mono,monospace">',
        '<thead><tr style="border-bottom:2px solid var(--border);'
        'background:rgba(88,166,255,.06)">',
    ]
    for hdr in ["Algorithm", "Time Complexity", "C++ Time", "Result"]:
        align = "right" if hdr == "C++ Time" else "left"
        rows.append(f'<th style="text-align:{align};padding:10px 12px;'
                    f'color:var(--accent)">{hdr}</th>')
    rows.append('</tr></thead><tbody>')

    for t in timings:
        icon = next((v for k, v in _ALGO_ICON.items() if k in t["name"]), "")
        rows.append(
            f'<tr style="border-bottom:1px solid rgba(48,54,61,0.5)">'
            f'<td style="padding:9px 12px;color:var(--text)">{icon} {t["name"]}</td>'
            f'<td style="padding:9px 12px;color:{_complexity_color(t["complexity"])}">'
            f'{t["complexity"]}</td>'
            f'<td style="padding:9px 12px;text-align:right;color:var(--yellow)">'
            f'{_format_us(t["time_us"])}</td>'
            f'<td style="padding:9px 12px;color:var(--muted)">{t["result"]}</td>'
            f'</tr>')

    rows.append(
        f'<tr style="border-top:2px solid var(--border);'
        f'background:rgba(88,166,255,.06)">'
        f'<td colspan="2" style="padding:9px 12px;color:var(--muted)">'
        f'Total wall time (Python call)</td>'
        f'<td style="padding:9px 12px;text-align:right;color:var(--accent);'
        f'font-weight:700">{wall_ms:.1f} ms</td>'
        f'<td></td></tr>')
    rows.append('</tbody></table></div>')
    return "".join(rows)


def render_algo_dashboard(cur_player: int):
    pid   = cur_player
    pos   = st.session_state[f"p{pid}_pos"]
    money = st.session_state[f"p{pid}_money"]
    die   = st.session_state[f"p{pid}_die"]

    st.markdown('<div class="section-title">⚙️ Algorithm Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color:var(--muted);font-size:.82rem;margin-bottom:16px">'
        'Live execution times and results for the core CP algorithms at current position.</div>',
        unsafe_allow_html=True)

    with st.spinner("Running all algorithms..."):
        timings, wall_ms = eng.get_algo_timings(pos, money, die)

    st.markdown(
        '<div style="font-weight:700;font-size:.95rem;color:var(--text);margin-bottom:10px">'
        '📋 Algorithm Performance Table</div>', unsafe_allow_html=True)
    st.markdown(_timing_table(timings, wall_ms), unsafe_allow_html=True)
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns(2, gap="large")

    # ── Left column: BFS, Dijkstra, Binary Search ─────────────────────────────
    with col_left:
        # BFS
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem">'
            '🗺️ BFS: Min Moves to Finish</div>', unsafe_allow_html=True)
        bfs_dist, bfs_ms = eng.get_bfs_distances()
        d = bfs_dist.get(pos, -1)
        d_color = "#3fb950" if d <= 3 else "#d29922" if d <= 6 else "#f85149"
        st.markdown(
            f'<div class="mbox" style="margin-bottom:12px">'
            f'<div class="mbox-val" style="color:{d_color}">{d if d >= 0 else "?"}</div>'
            f'<div class="mbox-lbl">Min dice rolls from cell {pos} to finish</div>'
            f'<div style="font-size:.72rem;color:var(--muted);margin-top:4px">'
            f'BFS computed in {bfs_ms:.1f}ms · O(V+E)</div></div>',
            unsafe_allow_html=True)

        bar_html = ""
        for cell_idx in range(0, GRID_SIZE, 5):
            cd  = bfs_dist.get(cell_idx, -1)
            w   = max(0, min(100, int((1 - cd / 12) * 100))) if cd >= 0 else 0
            brd = "border:2px solid var(--yellow);" if cell_idx == pos else ""
            bar_color = "var(--accent)" if cell_idx == pos else "#30363d"
            bar_html += (
                f'<div style="display:flex;align-items:center;gap:6px;margin:3px 0;{brd}">'
                f'<span style="font-size:.7rem;width:40px;color:var(--muted)">Cell {cell_idx}</span>'
                f'<div style="flex:1;height:8px;background:var(--surface2);border-radius:4px">'
                f'<div style="width:{w}%;height:100%;background:{bar_color};border-radius:4px">'
                f'</div></div>'
                f'<span style="font-size:.7rem;width:20px;color:var(--text)">{cd}</span>'
                f'</div>')
        st.markdown(bar_html, unsafe_allow_html=True)

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

        # Dijkstra
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem">'
            '🧭 Dijkstra: Minimum-Risk Path</div>', unsafe_allow_html=True)
        risk_dist, risk_ms = eng.get_dijkstra_risks()
        risk = risk_dist.get(pos, -1)
        r_color = "#3fb950" if 0 <= risk <= 8 else "#d29922" if 0 <= risk <= 16 else "#f85149"
        st.markdown(
            f'<div class="mbox" style="margin-bottom:12px">'
            f'<div class="mbox-val" style="color:{r_color}">{risk if risk >= 0 else "?"}</div>'
            f'<div class="mbox-lbl">Minimum weighted risk from cell {pos}</div>'
            f'<div style="font-size:.72rem;color:var(--muted);margin-top:4px">'
            f'Cell penalties are weighted · Dijkstra O(E log V) · {risk_ms:.1f}ms</div></div>',
            unsafe_allow_html=True)

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

        # Binary Search
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem">'
            '🔍 Binary Search: Min Winning Coins</div>', unsafe_allow_html=True)
        min_coins, bs_ms = eng.get_binary_search_coins(pos, die)
        has_enough = money >= min_coins
        coin_color = "#3fb950" if has_enough else "#f85149"
        st.markdown(
            f'<div class="mbox">'
            f'<div class="mbox-val" style="color:{coin_color}">{min_coins}</div>'
            f'<div class="mbox-lbl">Min coins for a winning position</div>'
            f'<div style="font-size:.72rem;color:var(--muted);margin-top:4px">'
            f'Binary search on [1..30] · {bs_ms:.1f}ms</div></div>',
            unsafe_allow_html=True)
        ev_cls = "ev-gain" if has_enough else "ev-loss"
        msg = (f"✅ You have {money} coins — above the {min_coins} threshold!"
               if has_enough
               else f"⚠️ You only have {money} coins — need {min_coins} for a guaranteed win!")
        st.markdown(f'<div class="ev {ev_cls}" style="margin-top:8px">{msg}</div>',
                    unsafe_allow_html=True)

    # ── Right column: Prefix Sum ───────────────────────────────────────────────
    with col_right:
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem">'
            '📊 Prefix Sum: Cell Range Money</div>', unsafe_allow_html=True)
        prefix_gains, pfx_ms = eng.get_prefix_gains()
        gain_to_end = prefix_gains.get(GRID_SIZE - 1, 0) - prefix_gains.get(pos, 0)
        g_color = "var(--green)" if gain_to_end >= 0 else "var(--red)"
        st.markdown(
            f'<div class="mbox" style="margin-bottom:12px">'
            f'<div class="mbox-val" style="color:{g_color}">{gain_to_end:+}</div>'
            f'<div class="mbox-lbl">Expected coins if you reach finish from cell {pos}</div>'
            f'<div style="font-size:.72rem;color:var(--muted);margin-top:4px">'
            f'Prefix sum query O(1) · built in {pfx_ms:.1f}ms</div></div>',
            unsafe_allow_html=True)

        cell_html = ""
        for i in range(GRID_SIZE):
            pg        = prefix_gains.get(i, 0)
            prev_pg   = prefix_gains.get(i - 1, 0) if i > 0 else 0
            cell_gain = pg - prev_pg
            if cell_gain > 0:      bg, fg = "#1a3320", "#3fb950"
            elif cell_gain < 0:    bg, fg = "#2d1515", "#f85149"
            else:                  bg, fg = "var(--surface2)", "var(--muted)"
            border = "2px solid var(--yellow)" if i == pos else "1px solid transparent"
            label  = str(cell_gain) if cell_gain != 0 else "·"
            cell_html += (
                f'<span title="Cell {i}: {cell_gain:+}" '
                f'style="display:inline-block;width:20px;height:20px;margin:1px;'
                f'border-radius:3px;background:{bg};color:{fg};font-size:.58rem;'
                f'text-align:center;line-height:20px;border:{border}">{label}</span>')
        st.markdown(
            f'<div style="line-height:1.2">{cell_html}</div>'
            f'<div style="font-size:.7rem;color:var(--muted);margin-top:4px">'
            f'Each cell shows net coin change. Yellow outline = your position.</div>',
            unsafe_allow_html=True)

    # ── Bitmask power-up tracker ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div class="section-title" style="font-size:1.1rem">'
        '🎒 Bitmask: Power-up Tracker</div>', unsafe_allow_html=True)

    mask        = st.session_state.get(f"p{pid}_mask", 0)
    total_bonus = 0
    item_parts  = [
        '<div style="display:grid;grid-template-columns:'
        'repeat(auto-fit,minmax(220px,1fr));gap:8px">']

    for i, item in enumerate(_POWERUPS):
        collected = (mask >> i) & 1
        if collected:
            total_bonus += item["bonus"]
        bg     = "rgba(63,185,80,.15)"  if collected else "rgba(139,148,158,.06)"
        border = "var(--green)"         if collected else "var(--border)"
        status = "✅ Collected"         if collected else f"📍 At cell {item['cell']}"
        item_parts.append(
            f'<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;'
            f'border-radius:10px;background:{bg};border:1px solid {border}">'
            f'<span style="font-size:1.2rem">{item["emoji"]}</span>'
            f'<div><b style="font-size:.88rem">{item["name"]}</b>'
            f'<span style="color:var(--green);margin-left:8px;font-size:.8rem">'
            f'+{item["bonus"]}</span>'
            f'<div style="font-size:.72rem;color:var(--muted)">{status}</div></div>'
            f'<span style="margin-left:auto;font-size:.7rem;'
            f'font-family:JetBrains Mono,monospace;color:var(--muted)">'
            f'bit {i} = {(mask >> i) & 1}</span></div>')
    item_parts.append('</div>')
    st.markdown("".join(item_parts), unsafe_allow_html=True)
    st.markdown(
        f'<div style="margin-top:10px;font-size:.8rem;color:var(--muted)">'
        f'Bitmask: <span style="font-family:JetBrains Mono;color:var(--accent)">'
        f'{bin(mask)} ({mask})</span> · Bonus: <span style="color:var(--green)">'
        f'+{total_bonus}</span></div>', unsafe_allow_html=True)

    # ── Tournament results ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div class="section-title" style="font-size:1.1rem">'
        '🏁 AI Tournament: Strategy Comparison</div>', unsafe_allow_html=True)

    tour_rows, tour_ms = eng.get_tournament_results()
    if tour_rows:
        tour_rows = sorted(tour_rows, key=lambda r: r["win_rate"], reverse=True)
        t_parts = [
            '<div style="overflow-x:auto;border:1px solid var(--border);'
            'border-radius:10px;background:var(--surface)">',
            '<table style="width:100%;border-collapse:collapse;font-size:.82rem;'
            'font-family:JetBrains Mono,monospace">',
            '<thead><tr style="border-bottom:2px solid var(--border);'
            'background:rgba(88,166,255,.06)">',
        ]
        for hdr, align in [
            ("Rank", "left"), ("Strategy", "left"), ("Win Rate", "right"),
            ("Wins/Games", "right"), ("Avg Turns", "right"), ("Avg Money", "right"),
        ]:
            t_parts.append(
                f'<th style="text-align:{align};padding:9px 12px;'
                f'color:var(--accent)">{hdr}</th>')
        t_parts.append('</tr></thead><tbody>')

        for rank, row in enumerate(tour_rows, start=1):
            color = "#3fb950" if rank == 1 else "#58a6ff" if rank == 2 else "var(--muted)"
            t_parts.append(
                f'<tr style="border-bottom:1px solid rgba(48,54,61,0.5)">'
                f'<td style="padding:9px 12px;color:{color}">#{rank}</td>'
                f'<td style="padding:9px 12px;color:var(--text)">{row["strategy"]}</td>'
                f'<td style="padding:9px 12px;text-align:right;color:{color}">'
                f'{row["win_rate"]:.1f}%</td>'
                f'<td style="padding:9px 12px;text-align:right;color:var(--muted)">'
                f'{row["wins"]}/{row["games"]}</td>'
                f'<td style="padding:9px 12px;text-align:right;color:var(--muted)">'
                f'{row["avg_turns"]:.1f}</td>'
                f'<td style="padding:9px 12px;text-align:right;color:var(--muted)">'
                f'{row["avg_money"]:.1f}</td>'
                f'</tr>')
        t_parts.append('</tbody></table></div>')
        st.markdown("".join(t_parts), unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:.72rem;color:var(--muted);margin-top:6px">'
            f'Round-robin simulation in C++ · Random vs Greedy vs Minimax vs Grundy '
            f'· {tour_ms:.1f}ms</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════

if "p1_mask" not in st.session_state:
    st.session_state["p1_mask"] = 0
if "p2_mask" not in st.session_state:
    st.session_state["p2_mask"] = 0

_SCREENS = {
    "rulebook": screen_rulebook,
    "setup":    screen_setup,
    "game":     screen_game,
    "results":  screen_results,
}

_current = st.session_state.screen
handler  = _SCREENS.get(_current)
if handler:
    handler()
else:
    st.session_state.screen = "rulebook"
    st.rerun()
