"""
app.py  — Picnic Board Game 
AI vs AI, two-player, Human vs AI
"""

import streamlit as st, random, time, os, sys, math
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="🏕️ Picnic Quest", page_icon="🏕️",
                   layout="wide", initial_sidebar_state="expanded")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import picnic_bridge as bridge

BOARD_SIZE    = bridge.BOARD_SIZE
INITIAL_MONEY = bridge.INITIAL_MONEY

#  THEME
st.markdown("""
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
/* Sidebar */
[data-testid="stSidebar"]{
  background:var(--surface)!important;
  border-right:1px solid var(--border)!important;
}
/* Hide streamlit chrome */
#MainMenu,footer,[data-testid="stToolbar"]{display:none!important}

/* Cards */
.card{background:var(--surface);border:1px solid var(--border);
      border-radius:16px;padding:20px 24px;margin-bottom:16px;
      box-shadow:var(--card-sh);}
.card-accent{border-color:var(--accent);}

/* Titles */
.game-title{font-family:'Baloo 2',cursive;font-size:3rem;font-weight:800;
  background:linear-gradient(135deg,#58a6ff,#3fb950,#d29922);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  line-height:1.1;margin-bottom:4px;}
.section-title{font-family:'Baloo 2',cursive;font-size:1.4rem;
  font-weight:700;color:var(--accent);margin-bottom:10px;}
.sub-title{color:var(--muted);font-size:1rem;margin-bottom:16px;}

/* Buttons */
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

/* Metric boxes */
.mbox{background:var(--surface2);border:1px solid var(--border);
      border-radius:12px;padding:12px 16px;text-align:center;}
.mbox-val{font-family:'Baloo 2',cursive;font-size:2rem;font-weight:800;
          color:var(--accent);line-height:1;}
.mbox-lbl{font-size:.7rem;color:var(--muted);text-transform:uppercase;
          letter-spacing:.08em;font-weight:600;margin-top:4px;}

/* Player cards */
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

/* Grundy panel */
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

/* Event messages */
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

/* Log */
.log-entry{font-family:'JetBrains Mono',monospace;font-size:.78rem;
           padding:5px 10px;border-radius:6px;margin:2px 0;
           background:rgba(255,255,255,.03);color:var(--muted);}
.log-entry.hl{background:rgba(88,166,255,.08);color:var(--text);}

/* Rulebook */
.rule-row{display:flex;gap:14px;align-items:flex-start;
          padding:12px 0;border-bottom:1px solid var(--border);}
.rule-icon{font-size:1.5rem;min-width:36px;}
.rule-body{font-size:.93rem;line-height:1.55;}

/* Win screen */
.win-screen{background:linear-gradient(135deg,#0d2137,#0d1117);
            border:2px solid var(--accent);border-radius:24px;
            padding:48px;text-align:center;}
.win-name{font-family:'Baloo 2',cursive;font-size:3.5rem;font-weight:800;
          background:linear-gradient(135deg,var(--yellow),var(--orange));
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;}

/* Sim controls */
.sim-step-card{background:var(--surface2);border:1px solid var(--border);
               border-radius:12px;padding:12px 16px;margin:6px 0;}
.sim-step-card.p1-step{border-left:3px solid var(--p1);}
.sim-step-card.p2-step{border-left:3px solid var(--p2);}
.sim-step-card.active-step{background:rgba(88,166,255,.07);
                            border-color:var(--accent)!important;}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
  background:var(--surface2)!important;border-radius:10px!important;
  border:1px solid var(--border)!important;padding:3px!important;}
.stTabs [data-baseweb="tab"]{font-family:'DM Sans',sans-serif!important;
  font-weight:600!important;color:var(--muted)!important;border-radius:8px!important;}
.stTabs [aria-selected="true"]{background:var(--accent)!important;color:#000!important;}

/* Inputs */
.stTextInput input,.stNumberInput input{
  background:var(--surface2)!important;border:1px solid var(--border)!important;
  color:var(--text)!important;border-radius:10px!important;
  font-family:'DM Sans',sans-serif!important;}
.stRadio label{color:var(--text)!important;}

/* Progress bar */
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
""", unsafe_allow_html=True)

#  SESSION STATE
DEFS = {
    "screen":"rulebook","compiled":False,"compile_err":"",
    "p1_name":"Player 1","p2_name":"Player 2",
    "p1_pos":0,"p2_pos":0,
    "p1_money":INITIAL_MONEY,"p2_money":INITIAL_MONEY,
    "p1_die":0,"p2_die":0,
    "p1_skip":False,"p2_skip":False,
    "p1_extra":False,"p2_extra":False,
    "cur":1,"winner":None,
    "game_log":[],"last_ev":None,"last_roll":None,
    "play_mode":"Human vs Human",
    "cells":None,"edges":None,
    "sim_steps":[],"sim_end":{},"sim_winner":(None,None),"sim_idx":0,
    "grundy_cache":{},"p1_mask":0,"p2_mask":0,
}
for k,v in DEFS.items():
    if k not in st.session_state: st.session_state[k]=v

#  HELPERS
def ensure_compiled():
    if st.session_state.compiled: return True
    ok,err = bridge.compile_engine()
    st.session_state.compiled=ok; st.session_state.compile_err=err
    return ok

def add_log(msg): 
    st.session_state.game_log.append(msg)
    if len(st.session_state.game_log)>60:
        st.session_state.game_log=st.session_state.game_log[-60:]

def pos_lbl(pos):
    if pos==0: return "🏠 Start"
    if pos>=BOARD_SIZE-1: return "🏁 Finish!"
    return f"Cell {pos}"

def die_lbl(d): return "12-sided 🎲" if d else "6-sided 🎲"

def apply_state(p,pos,money,die,skip=False,extra=False):
    st.session_state[f"p{p}_pos"]=pos
    st.session_state[f"p{p}_money"]=money
    st.session_state[f"p{p}_die"]=die
    st.session_state[f"p{p}_skip"]=skip
    st.session_state[f"p{p}_extra"]=extra

def check_winner():
    for p in[1,2]:
        if st.session_state[f"p{p}_pos"]>=BOARD_SIZE-1:
            st.session_state.winner=p; st.session_state.screen="results"; return True
    return False

def next_player():
    p=st.session_state.cur
    if st.session_state.get(f"p{p}_extra",False):
        st.session_state[f"p{p}_extra"]=False; return
    st.session_state.cur=3-p
    opp=3-p
    if st.session_state.get(f"p{opp}_skip",False):
        st.session_state[f"p{opp}_skip"]=False
        add_log(f"⏭️ {st.session_state[f'p{opp}_name']} skips their turn!")
        st.session_state.cur=p  # come back to original player

def do_roll(roll:int):
    p=st.session_state.cur
    pos=st.session_state[f"p{p}_pos"]
    money=st.session_state[f"p{p}_money"]
    die=st.session_state[f"p{p}_die"]
    name=st.session_state[f"p{p}_name"]
    st.session_state.last_roll=roll

    result=bridge.apply_move(pos,money,die,roll)
    if "error" in result:
        st.session_state.last_ev={"cls":"ev-skip",
            "msg":f"🎲 {name} rolled {roll} — overshoots the finish! Turn skipped. (Need ≤{BOARD_SIZE-1-pos} to move)"}
        add_log(f"T{len(st.session_state.game_log)+1} · P{p} rolled {roll} · Overshoot! Turn skipped.")
        next_player()
        return

    np,nm,nd=result["pos"],result["money"],result["die"]
    cell=result.get("cell","")
    skip_t=result.get("skip",False)
    extra_t=result.get("extra",False)
    card_n=result.get("card_name","")
    card_d=result.get("card_desc","")
    delta=nm-money

    if np==0 and pos!=0:
        cls,msg="ev-reset",f"😱 {name} went broke and resets to Start! Money restored to {INITIAL_MONEY}"
    elif delta>0:
        cls,msg="ev-gain",f"💰 {name} → {cell} · +{delta} coins! ({nm} total)"
    elif delta<0:
        cls,msg="ev-loss",f"💸 {name} → {cell} · {delta} coins! ({nm} total)"
    elif skip_t:
        cls,msg="ev-skip",f"🚦 {name} lands on {cell} · Skip next turn!"
    elif extra_t:
        cls,msg="ev-extra",f"🍀 {name} lands on {cell} · Extra turn!"
    elif nd!=die:
        cls,msg="ev-upgrade",f"🎰 {name} lands on {cell} · Die upgraded to 12-sided!"
    elif np>pos+roll:
        cls,msg="ev-jump",f"⏩ {name} jumps to cell {np}! ({cell})"
    elif np<pos+roll and np!=0:
        cls,msg="ev-jump",f"⏪ {name} sent back to cell {np}! ({cell})"
    else:
        cls,msg="ev-normal",f"🌿 {name} moves to {cell}"
    if card_n: msg+=f" · 🃏 {card_n}: {card_d}"
    # Power-up item collection (Bitmask)
    item_nm = result.get("item_name","")
    if item_nm:
        ITEMS_CELLS=[5,11,17,21,29]
        ITEMS_NAMES=["Compass","Sunscreen","Water Bottle","Picnic Blanket","Trail Map"]
        ITEMS_BONUS=[2,2,3,2,3]
        for i2,(ic,iname) in enumerate(zip(ITEMS_CELLS,ITEMS_NAMES)):
            if iname==item_nm:
                mask_key=f"p{p}_mask"
                already_collected = (st.session_state.get(mask_key,0) >> i2) & 1
                if not already_collected:
                    nm = min(30, nm + ITEMS_BONUS[i2])
                    st.session_state[mask_key] = st.session_state.get(mask_key,0) | (1<<i2)
                break
        msg+=f" · 🎒 Found {item_nm}!"

    st.session_state.last_ev={"cls":cls,"msg":msg}
    add_log(f"T{len(st.session_state.game_log)+1} · P{p} rolled {roll} · {msg}")
    apply_state(p,np,nm,nd,skip_t,extra_t)
    if not check_winner():
        if not extra_t: next_player()

#  BOARD FIGURE
CELL_COLORS={
    "start":"#388bfd","finish":"#a371f7","money_gain":"#3fb950",
    "money_loss":"#f85149","die_upgrade":"#a371f7","jump_forward":"#79c0ff",
    "jump_back":"#db6d28","skip_turn":"#d29922","extra_turn":"#56d364",
    "card":"#d2a8ff","normal":"#30363d",
}
CELL_BORDER={
    "start":"#58a6ff","finish":"#d2a8ff","money_gain":"#56d364",
    "money_loss":"#ff6b6b","die_upgrade":"#d2a8ff","jump_forward":"#a8d8f0",
    "jump_back":"#ffa657","skip_turn":"#e3b341","extra_turn":"#3fb950",
    "card":"#bc8cff","normal":"#484f58",
}

def board_figure(cells, p1_pos, p2_pos, p1_name, p2_name, edges=None):
    N=len(cells); COLS=6
    rows=math.ceil(N/COLS)
    xs,ys,colors,borders,texts,hovers=[],[],[],[],[],[]

    for cell in cells:
        i=cell["id"]
        col=i%COLS; row=i//COLS
        if row%2==1: col=COLS-1-col
        xs.append(col*1.6); ys.append(-row*1.6)
        ct=cell["type"]
        colors.append(CELL_COLORS.get(ct,"#30363d"))
        if i==p1_pos and i==p2_pos: brd="#ffffff"
        elif i==p1_pos: brd="#f85149"
        elif i==p2_pos: brd="#58a6ff"
        else: brd=CELL_BORDER.get(ct,"#484f58")
        borders.append(brd)
        lbl=cell["emoji"]
        texts.append(lbl)
        tip=f"<b>{cell['emoji']} {cell['name']}</b><br>Cell {i}<br>{cell['desc']}"
        if cell["value"]!=0:
            tip+=f"<br>{'+'if cell['value']>0 else ''}{cell['value']}"
        hovers.append(tip)

    fig=go.Figure()

    # ── ROADS: draw segment by segment so each straight piece looks like a road ──
    # Layer 1: wide dark asphalt base
    for i in range(N-1):
        fig.add_trace(go.Scatter(
            x=[xs[i],xs[i+1]], y=[ys[i],ys[i+1]],
            mode="lines",
            line=dict(color="#1c1f26", width=22),
            hoverinfo="none", showlegend=False))

    # Layer 2: road surface (slightly lighter asphalt)
    for i in range(N-1):
        fig.add_trace(go.Scatter(
            x=[xs[i],xs[i+1]], y=[ys[i],ys[i+1]],
            mode="lines",
            line=dict(color="#2b3040", width=16),
            hoverinfo="none", showlegend=False))

    # Layer 3: white edge lines (road kerb) — two thin lines flanking
    for i in range(N-1):
        fig.add_trace(go.Scatter(
            x=[xs[i],xs[i+1]], y=[ys[i],ys[i+1]],
            mode="lines",
            line=dict(color="rgba(255,255,255,0.18)", width=18),
            hoverinfo="none", showlegend=False))
        fig.add_trace(go.Scatter(
            x=[xs[i],xs[i+1]], y=[ys[i],ys[i+1]],
            mode="lines",
            line=dict(color="#2b3040", width=14),
            hoverinfo="none", showlegend=False))

    # Layer 4: yellow center dashed line (drawn as short segments)
    for i in range(N-1):
        x0,y0,x1r,y1r = xs[i],ys[i],xs[i+1],ys[i+1]
        # interpolate dashes: 3 dashes per segment
        for d in range(3):
            t0 = d/3 + 0.05
            t1 = d/3 + 0.22
            t1 = min(t1, (d+1)/3 - 0.05)
            fig.add_trace(go.Scatter(
                x=[x0+t0*(x1r-x0), x0+t1*(x1r-x0)],
                y=[y0+t0*(y1r-y0), y0+t1*(y1r-y0)],
                mode="lines",
                line=dict(color="rgba(255,210,50,0.7)", width=2, dash="solid"),
                hoverinfo="none", showlegend=False))

    if edges:
        spec=[e for e in edges if e["label"]!="normal"]
        for e in spec:
            fi,ti=e["from"],e["to"]
            if fi<N and ti<N:
                fx,fy=xs[fi],ys[fi]
                tx,ty=xs[ti],ys[ti]
                mx=(fx+tx)/2 + 0.7
                my=(fy+ty)/2 + 0.8
                cx=[fx,mx,tx]; cy=[fy,my,ty]
                # Glow outer
                fig.add_trace(go.Scatter(x=cx,y=cy,mode="lines",
                    line=dict(color="rgba(163,113,247,0.18)",width=10),
                    hoverinfo="none",showlegend=False))
                # Road surface
                fig.add_trace(go.Scatter(x=cx,y=cy,mode="lines",
                    line=dict(color="rgba(90,50,160,0.75)",width=5),
                    hoverinfo="none",showlegend=False))
                # Centre stripe
                fig.add_trace(go.Scatter(x=cx,y=cy,mode="lines",
                    line=dict(color="rgba(210,168,255,0.9)",width=1,dash="dot"),
                    hoverinfo="none",showlegend=False))
                # Label at midpoint
                fig.add_annotation(x=mx,y=my,
                    text=f"✦ {e['label'][:14]}",
                    showarrow=False,
                    font=dict(size=8,color="#d2a8ff",family="DM Sans"),
                    bgcolor="rgba(13,17,23,0.85)",
                    bordercolor="#6e40c9",borderwidth=1,borderpad=3)

    # Cells
    fig.add_trace(go.Scatter(x=xs,y=ys,mode="markers+text",
        marker=dict(size=62,color=colors,symbol="square",
                    line=dict(width=3,color=borders),opacity=0.95),
        text=texts,textposition="middle center",
        textfont=dict(color="white",size=22,family="Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, DM Sans"),
        hovertext=hovers,hoverinfo="text",showlegend=False))

    fig.add_trace(go.Scatter(x=[x+0.34 for x in xs],y=[y-0.34 for y in ys],mode="markers+text",
        marker=dict(size=21,color="rgba(13,17,23,0.78)",symbol="circle",
                    line=dict(width=1,color="rgba(255,255,255,0.45)")),
        text=[str(c["id"]) for c in cells],
        textposition="middle center",
        textfont=dict(color="#ffffff",size=9,family="JetBrains Mono, DM Sans"),
        hoverinfo="none",showlegend=False))

    # Player tokens
    def get_xy(pos):
        col=pos%COLS; row=pos//COLS
        if row%2==1: col=COLS-1-col
        return col*1.6, -row*1.6

    x1,y1=get_xy(p1_pos)
    x2,y2=get_xy(p2_pos)
    fig.add_trace(go.Scatter(x=[x1-0.25],y=[y1+0.25],mode="markers+text",
        marker=dict(size=26,color="#f85149",symbol="circle",
                    line=dict(width=2,color="white")),
        text=[p1_name[:2].upper()],
        textfont=dict(color="white",size=8,family="Baloo 2"),
        textposition="middle center",name=f"🔴 {p1_name}",hoverinfo="name"))
    fig.add_trace(go.Scatter(x=[x2+0.25],y=[y2-0.25],mode="markers+text",
        marker=dict(size=26,color="#58a6ff",symbol="circle",
                    line=dict(width=2,color="white")),
        text=[p2_name[:2].upper()],
        textfont=dict(color="white",size=8,family="Baloo 2"),
        textposition="middle center",name=f"🔵 {p2_name}",hoverinfo="name"))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,17,23,0.6)",
        xaxis=dict(visible=False,range=[-0.9,(COLS-1)*1.6+0.9]),
        yaxis=dict(visible=False,range=[-(rows-1)*1.6-0.9,1.0]),
        margin=dict(l=10,r=10,t=10,b=10),
        height=max(320,rows*115),
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="left",x=0,
                    font=dict(family="DM Sans",size=13,color="#e6edf3"),
                    bgcolor="rgba(22,27,34,0.9)",bordercolor="#30363d",borderwidth=1),
    )
    return fig

#  GRUNDY PANEL
def render_grundy_panel(cur_player):
    p=cur_player
    pos=st.session_state[f"p{p}_pos"]
    money=st.session_state[f"p{p}_money"]
    die=st.session_state[f"p{p}_die"]
    opp=3-p
    opp_pos=st.session_state[f"p{opp}_pos"]
    opp_money=st.session_state[f"p{opp}_money"]
    opp_die=st.session_state[f"p{opp}_die"]

    g_cur = bridge.compute_grundy(pos,money,die)
    g_opp = bridge.compute_grundy(opp_pos,opp_money,opp_die)

    g_val=g_cur.get("grundy",0) or 0
    g_state=g_cur.get("state","LOSING")
    g_opp_val=g_opp.get("grundy",0) or 0
    g_opp_state=g_opp.get("state","LOSING")

    nm=st.session_state[f"p{p}_name"]
    opp_nm=st.session_state[f"p{opp}_name"]
    col_cls="winning" if g_state=="WINNING" else "losing"
    opp_cls="winning" if g_opp_state=="WINNING" else "losing"

    st.markdown('<div class="grundy-panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧠 Sprague–Grundy Analysis</div>', unsafe_allow_html=True)

    if g_state=="WINNING" and g_opp_state!="WINNING":
        headline=f"<span style='color:var(--green);font-weight:700'>🏆 {nm} is in a WINNING position!</span>"
    elif g_opp_state=="WINNING" and g_state!="WINNING":
        headline=f"<span style='color:var(--red);font-weight:700'>⚠️ {opp_nm} has the strategic advantage!</span>"
    else:
        headline="<span style='color:var(--yellow);font-weight:700'>⚖️ Both players in equal (losing) positions — depends on dice!</span>"
    st.markdown(f'<div style="margin-bottom:14px;font-size:.95rem">{headline}</div>',
                unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1:
        st.markdown(
            f'<div class="mbox"><div class="mbox-val {col_cls}">{g_val}</div>'
            f'<div class="mbox-lbl">G({nm[:8]})</div>'
            f'<div style="font-size:.8rem;margin-top:4px;color:var(--{"green" if g_state=="WINNING" else "red"})">'
            f'{"✅ WINNING" if g_state=="WINNING" else "❌ LOSING"}</div></div>',
            unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<div class="mbox"><div class="mbox-val {opp_cls}">{g_opp_val}</div>'
            f'<div class="mbox-lbl">G({opp_nm[:8]})</div>'
            f'<div style="font-size:.8rem;margin-top:4px;color:var(--{"green" if g_opp_state=="WINNING" else "red"})">'
            f'{"✅ WINNING" if g_opp_state=="WINNING" else "❌ LOSING"}</div></div>',
            unsafe_allow_html=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    st.markdown(f'<div style="font-size:.8rem;color:var(--muted);margin-bottom:8px">'
                f'G=0 → losing position (with optimal opponent play). '
                f'G≠0 → winning — there exists a move to force G=0 on the opponent.</div>',
                unsafe_allow_html=True)

    moves=g_cur.get("moves",[])
    if moves:
        st.markdown('<div style="font-weight:600;margin-bottom:6px;font-size:.9rem">🎯 Recommended Moves for You:</div>',
                    unsafe_allow_html=True)
        win_moves=[m for m in moves if m["outcome"]=="WIN"]
        if win_moves:
            st.markdown('<div style="font-size:.78rem;color:var(--green);margin-bottom:4px">✅ These moves put the opponent in a LOSING position (G=0 for them):</div>',
                        unsafe_allow_html=True)
            for m in win_moves[:4]:
                st.markdown(
                    f'<div class="move-row win">'
                    f'<span class="badge badge-win">Roll {m["roll"]}</span>'
                    f'<span>→ {m["cell_emoji"]} <b>{m["cell_name"]}</b> (cell {m["npos"]})</span>'
                    f'<span class="badge badge-g" style="margin-left:auto">G={m["grundy"]}</span>'
                    f'</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:.78rem;color:var(--yellow);margin-bottom:4px">⚠️ No winning move exists this turn. Pick the highest-G move:</div>',
                        unsafe_allow_html=True)
            for m in moves[:4]:
                st.markdown(
                    f'<div class="move-row loss">'
                    f'<span class="badge badge-loss">Roll {m["roll"]}</span>'
                    f'<span>→ {m["cell_emoji"]} <b>{m["cell_name"]}</b> (cell {m["npos"]})</span>'
                    f'<span class="badge badge-g" style="margin-left:auto">G={m["grundy"]}</span>'
                    f'</div>', unsafe_allow_html=True)

        pct_cur=int(pos/(BOARD_SIZE-1)*100)
        pct_opp=int(opp_pos/(BOARD_SIZE-1)*100)
        st.markdown('<div style="margin-top:14px;font-size:.82rem;color:var(--muted);font-weight:600">📍 Board Progress</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<div>{nm[:10]} <span style="color:var(--p1)">{pct_cur}%</span></div>'
            f'<div class="prog-wrap"><div class="prog-bar prog-p1" style="width:{pct_cur}%"></div></div>'
            f'<div>{opp_nm[:10]} <span style="color:var(--p2)">{pct_opp}%</span></div>'
            f'<div class="prog-wrap"><div class="prog-bar prog-p2" style="width:{pct_opp}%"></div></div>',
            unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

#  SIDEBAR
def render_sidebar():
    p=st.session_state.cur
    with st.sidebar:
        st.markdown('<div style="font-family:Baloo 2,cursive;font-size:1.6rem;'
                    'font-weight:800;color:#58a6ff">🏕️ Picnic Quest</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div style="color:var(--muted);font-size:.85rem;margin-bottom:12px">'
                    f'{st.session_state.play_mode}</div>', unsafe_allow_html=True)
        st.divider()

        for pn in[1,2]:
            nm=st.session_state[f"p{pn}_name"]
            pos=st.session_state[f"p{pn}_pos"]
            mon=st.session_state[f"p{pn}_money"]
            die=st.session_state[f"p{pn}_die"]
            skip=st.session_state.get(f"p{pn}_skip",False)
            active=(pn==p)
            acls="active" if active else ""
            tok="p1" if pn==1 else "p2"
            st.markdown(
                f'<div class="pcard p{pn} {acls}">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">'
                f'<span class="ptok {tok}">{nm[:2].upper()}</span>'
                f'<b style="font-size:.97rem">{nm}</b>'
                f'{"<span style=\'color:#d29922;font-size:.75rem;margin-left:auto\'>◀ YOUR TURN</span>" if active else ""}'
                f'</div>'
                f'<div style="font-size:.85rem;color:var(--muted);line-height:1.6">'
                f'📍 {pos_lbl(pos)}<br>'
                f'💰 {mon} coins &nbsp;·&nbsp; {die_lbl(die)}'
                f'{"<br>⏭️ <i>Skipping next</i>" if skip else ""}'
                f'</div>'
                f'<div class="prog-wrap" style="margin-top:8px">'
                f'<div class="prog-bar prog-p{pn}" style="width:{int(pos/(BOARD_SIZE-1)*100)}%"></div>'
                f'</div>'
                f'</div>', unsafe_allow_html=True)

        st.divider()
        if st.button("🔄 Restart",use_container_width=True):
            for k,v in DEFS.items():
                if k not in("compiled","compile_err","cells","edges","play_mode","p1_name","p2_name"):
                    st.session_state[k]=v
            st.session_state.screen="setup"; st.rerun()
        if st.button("📖 Rules",use_container_width=True):
            st.session_state.screen="rulebook"; st.rerun()

        st.divider()
        st.markdown('<div style="font-size:.8rem;font-weight:600;color:var(--muted);margin-bottom:6px">📜 RECENT LOG</div>',
                    unsafe_allow_html=True)
        for e in reversed(st.session_state.game_log[-10:]):
            st.markdown(f'<div class="log-entry">{e}</div>', unsafe_allow_html=True)

#  SCREEN: RULEBOOK
def screen_rulebook():
    st.markdown('<div class="game-title">🏕️ Picnic Quest</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">A dynamic board game powered by the Sprague–Grundy theorem</div>',
                unsafe_allow_html=True)
    col_l,col_r=st.columns([3,2],gap="large")

    with col_l:
        st.markdown('<div class="section-title">📖 How to Play</div>', unsafe_allow_html=True)
        rules=[
            ("🎯","Objective","Be first to land **exactly** on cell 35 (Finish). Overshooting is illegal — you simply don't move."),
            ("🎲","Dice","Start with a 6-sided die. Hit special ⭐ or 🎰 cells to permanently upgrade to a 12-sided die."),
            ("💰","Coins","Begin with 10 coins. Gain and lose coins on special cells. Your wealth matters — it affects resets!"),
            ("🔁","Reset Rule","Drop to 0 coins or less → instantly sent back to Start with 10 coins. Die type stays the same."),
            ("⏩⏪","Jumps","Some cells teleport you forward (🚗🛫) or backward (🚌🌧️) — plan your path carefully!"),
            ("🃏","Event Cards","Land on 🃏 cells to draw a card: gain coins, lose coins, jump, skip, or get an extra turn."),
            ("🚦","Skip Turn","Land on 🚦 or 😴 → your NEXT turn is skipped. The opponent can exploit this!"),
            ("🍀","Extra Turn","Land on 🍀 or ⚡ → roll again immediately in the same turn."),
            ("🧠","Game Theory","The Sprague–Grundy theorem labels every position. G=0 means you're in a LOSING position; G≠0 means you can force a win. The AI panel shows you these values and the best moves to make."),
        ]
        for em,title,desc in rules:
            st.markdown(
                f'<div class="rule-row"><div class="rule-icon">{em}</div>'
                f'<div class="rule-body"><b>{title}</b><br>{desc}</div></div>',
                unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🗺️ Cell Types</div>', unsafe_allow_html=True)
        legend=[
            ("🏠","#388bfd","Start — Home base"),
            ("🏁","#a371f7","Finish — Win!"),
            ("💰 🍔 🎯 🎁","#3fb950","Money Gain (+coins)"),
            ("💸 🍕 🚕 ⏳","#f85149","Money Loss (−coins)"),
            ("🎰 ⭐","#a371f7","Die Upgrade → 12-sided"),
            ("🚗 🛫","#79c0ff","Jump Forward"),
            ("🚌 🌧️","#db6d28","Jump Backward"),
            ("🚦 😴","#d29922","Skip Turn"),
            ("🍀 ⚡","#56d364","Extra Turn"),
            ("🃏","#d2a8ff","Event Card"),
        ]
        for em,c,lbl in legend:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;padding:7px 0;'
                f'border-bottom:1px solid #30363d;">'
                f'<div style="background:{c}22;border:1px solid {c};border-radius:8px;'
                f'padding:3px 8px;color:{c};font-size:.9rem;min-width:90px;text-align:center">{em}</div>'
                f'<div style="font-size:.88rem;color:var(--text)">{lbl}</div>'
                f'</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card" style="margin-top:0">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚡ Quick Facts</div>', unsafe_allow_html=True)
        facts=[("📐","36 cells, 0–35"),("👥","2 players"),
               ("💰","Start: 10 coins"),("🎲","6-sided → upgrades to 12"),
               ("🧠","Grundy AI hints every turn"),("🃏","8 event card types")]
        for icon,fact in facts:
            st.markdown(f'<div style="padding:4px 0;color:var(--text)">{icon} {fact}</div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    _,btn_c,_=st.columns([3,2,3])
    with btn_c:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("🚀 Let's Play!",use_container_width=True):
            with st.spinner("Compiling game engine..."):
                ok=ensure_compiled()
            if ok: st.session_state.screen="setup"; st.rerun()
            else: st.error(f"Compile error:\n{st.session_state.compile_err}")
        st.markdown('</div>', unsafe_allow_html=True)

#  SCREEN: SETUP
def screen_setup():
    st.markdown('<div class="game-title">👤 Player Setup</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Configure your game before the adventure begins</div>',
                unsafe_allow_html=True)
    st.divider()

    c1,c2,c3=st.columns(3,gap="large")
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔴 Player 1")
        p1=st.text_input("Name",value=st.session_state.p1_name,max_chars=18,key="sp1")
        st.markdown(f'<div style="margin-top:8px;display:flex;align-items:center;gap:8px">'
                    f'<span class="ptok p1">{(p1 or "P1")[:2].upper()}</span>'
                    f'<span style="color:var(--p1);font-weight:700">{p1 or "Player 1"}</span>'
                    f'</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔵 Player 2")
        p2=st.text_input("Name",value=st.session_state.p2_name,max_chars=18,key="sp2")
        st.markdown(f'<div style="margin-top:8px;display:flex;align-items:center;gap:8px">'
                    f'<span class="ptok p2">{(p2 or "P2")[:2].upper()}</span>'
                    f'<span style="color:var(--p2);font-weight:700">{p2 or "Player 2"}</span>'
                    f'</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Game Mode")
        mode=st.radio("Mode",["Human vs Human","Human vs AI","AI vs AI"],
                      index=["Human vs Human","Human vs AI","AI vs AI"].index(
                          st.session_state.play_mode),label_visibility="collapsed")
        mode_descs={"Human vs Human":"Both players roll manually.",
                    "Human vs AI":"You play vs an AI that uses Grundy-optimal moves.",
                    "AI vs AI":"Watch two AIs play and analyze the game."}
        st.markdown(f'<div style="color:var(--muted);font-size:.85rem;margin-top:8px">{mode_descs[mode]}</div>',
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    cb,cs,_=st.columns([2,2,4])
    with cb:
        if st.button("← Back"):
            st.session_state.screen="rulebook"; st.rerun()
    with cs:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("🎮 Begin!",use_container_width=True):
            for k,v in DEFS.items():
                if k not in("compiled","compile_err"):
                    st.session_state[k]=v
            st.session_state.p1_name=p1 or "Player 1"
            st.session_state.p2_name=p2 or "Player 2"
            st.session_state.play_mode=mode
            st.session_state.p1_money=INITIAL_MONEY
            st.session_state.p2_money=INITIAL_MONEY
            # Load board data
            try:
                st.session_state.cells=bridge.get_board_cells()
                st.session_state.edges=bridge.get_graph_edges()
            except: pass
            # AI vs AI: pre-run
            if mode=="AI vs AI":
                steps,end,winner=bridge.run_simulation(0,INITIAL_MONEY,0)
                st.session_state.sim_steps=steps
                st.session_state.sim_end=end
                st.session_state.sim_winner=winner
                st.session_state.sim_idx=0
            st.session_state.screen="game"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

#  Human vs Human / Human vs AI
def screen_game():
    render_sidebar()
    mode=st.session_state.play_mode

    if mode=="AI vs AI":
        screen_ai_vs_ai(); return

    cells=st.session_state.cells
    edges=st.session_state.edges
    p=st.session_state.cur
    p1n=st.session_state.p1_name; p2n=st.session_state.p2_name

    # Board
    if cells:
        fig=board_figure(cells,st.session_state.p1_pos,st.session_state.p2_pos,
                         p1n,p2n,edges)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    else:
        st.error("Board unavailable. Engine may not be compiled.")
        return

    lcols=st.columns(6)
    leg=[("💰","#3fb950","Gain"),("💸","#f85149","Loss"),
         ("🎰","#a371f7","Upgrade"),("⏩","#79c0ff","Jump Fwd"),
         ("⏪","#db6d28","Jump Back"),("🃏","#d2a8ff","Card")]
    for lc,(em,c,lbl) in zip(lcols,leg):
        lc.markdown(f'<div style="display:flex;align-items:center;gap:4px;font-size:.76rem">'
                    f'<div style="width:10px;height:10px;background:{c};border-radius:3px"></div>'
                    f'{em} {lbl}</div>', unsafe_allow_html=True)

    st.markdown("---")

    nm=st.session_state[f"p{p}_name"]
    pos=st.session_state[f"p{p}_pos"]
    money=st.session_state[f"p{p}_money"]
    die=st.session_state[f"p{p}_die"]
    faces=12 if die else 6
    color=("var(--p1)" if p==1 else "var(--p2)")

    col_ctrl,col_grundy=st.columns([3,2],gap="large")

    with col_ctrl:
        tok="p1" if p==1 else "p2"
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">'
            f'<span class="ptok {tok}" style="width:40px;height:40px;font-size:.9rem">{nm[:2].upper()}</span>'
            f'<div><div style="font-family:Baloo 2,cursive;font-size:1.6rem;font-weight:800;color:{color}">'
            f'{nm}\'s Turn</div>'
            f'<div style="color:var(--muted);font-size:.85rem">{die_lbl(die)} · {faces} possible moves</div>'
            f'</div></div>', unsafe_allow_html=True)

        m1,m2,m3=st.columns(3)
        m1.markdown(f'<div class="mbox"><div class="mbox-val">{pos}</div>'
                    '<div class="mbox-lbl">Cell</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="mbox"><div class="mbox-val">{money}</div>'
                    '<div class="mbox-lbl">Coins 💰</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="mbox"><div class="mbox-val">{faces}</div>'
                    '<div class="mbox-lbl">Die Faces</div></div>', unsafe_allow_html=True)

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

        is_ai_turn = (mode=="Human vs AI" and p==2)

        if is_ai_turn:
            st.markdown(f'<div class="ev ev-normal pulse">🤖 <b>{nm} (AI)</b> is computing optimal move...</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="btn-ai">', unsafe_allow_html=True)
            if st.button("▶️ Execute AI Move",use_container_width=True):
                with st.spinner("AI thinking with Grundy..."):
                    moves=bridge.get_moves(pos,money,die)
                if moves:
                    best=moves[0]
                    do_roll(best["roll"])
                    add_log(f"🤖 AI: roll {best['roll']} (G={best['grundy']}, {best['outcome']})")
                else:
                    st.warning("AI has no valid moves!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="btn-roll">', unsafe_allow_html=True)
            if st.button(f"🎲 Roll {faces}-sided Die",use_container_width=True):
                roll=random.randint(1,faces)
                # Brief animation
                ph=st.empty()
                dice_icons=["⚀","⚁","⚂","⚃","⚄","⚅"]
                for _ in range(6):
                    ph.markdown(f'<div style="font-size:5rem;text-align:center;margin:8px">'
                                f'{random.choice(dice_icons)}</div>',unsafe_allow_html=True)
                    time.sleep(0.06)
                ph.markdown(f'<div style="font-size:5rem;text-align:center;margin:8px;'
                            f'animation:pop .3s ease">'
                            f'{dice_icons[min(roll,6)-1] if roll<=6 else "🎲"}</div>',
                            unsafe_allow_html=True)
                time.sleep(0.2)
                ph.empty()
                do_roll(roll)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        ev=st.session_state.last_ev
        if ev:
            st.markdown(f'<div class="ev {ev["cls"]} pop">{ev["msg"]}</div>',
                        unsafe_allow_html=True)

    with col_grundy:
        render_grundy_panel(p)

    st.markdown("---")
    tab1, tab2 = st.tabs(["🧠 Grundy Details", "⚙️ Algorithm Dashboard"])
    with tab1:
        g_data = bridge.compute_grundy(pos, money, die)
        g_val = g_data.get("grundy", 0) or 0
        g_state = g_data.get("state", "LOSING")
        state_color = "var(--green)" if g_state == "WINNING" else "var(--red)"
        st.markdown(
            f'<div class="card" style="padding:16px 18px;margin-bottom:14px">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap">'
            f'<div><div class="section-title" style="margin-bottom:2px">Current State Analysis</div>'
            f'<div style="color:var(--muted);font-size:.86rem">Cell {pos} · {money} coins · {die_lbl(die)}</div></div>'
            f'<div style="display:flex;gap:10px;align-items:center">'
            f'<div class="mbox" style="min-width:92px;margin:0"><div class="mbox-val" style="color:{state_color}">{g_val}</div><div class="mbox-lbl">Grundy</div></div>'
            f'<div class="mbox" style="min-width:110px;margin:0"><div class="mbox-val" style="font-size:1.35rem;color:{state_color}">{g_state}</div><div class="mbox-lbl">Position</div></div>'
            f'</div></div></div>',
            unsafe_allow_html=True)
        moves = bridge.get_moves(pos, money, die)
        if moves:
            st.markdown(
                '<div style="font-weight:700;font-size:.95rem;color:var(--text);margin-bottom:8px">'
                'Best legal moves from this state</div>',
                unsafe_allow_html=True)
            for rank, m in enumerate(moves[:6], start=1):
                item_tag=f"🎒{m.get('item_name','')}" if m.get("collected_item") else ""
                mm_val=m.get("minimax_val",0)
                row_bg = "rgba(63,185,80,.12)" if rank == 1 else ""
                tag = "Best" if rank == 1 else f"#{rank}"
                st.markdown(
                    f'<div class="move-row {"win" if m["outcome"]=="WIN" else "loss"}" style="background:{row_bg}">'
                    f'<span class="badge badge-g">{tag}</span>'
                    f'<span class="badge {"badge-win" if m["outcome"]=="WIN" else "badge-loss"}">Roll {m["roll"]}</span>'
                    f'<span>→ {m["cell_emoji"]} <b>{m["cell_name"]}</b></span>'
                    f'<span style="font-size:.75rem;color:var(--muted)">{item_tag}</span>'
                    f'<span class="badge badge-g" style="margin-left:auto">G={m["grundy"]}</span>'
                    f'<span style="font-size:.72rem;color:var(--muted);margin-left:6px">MM={mm_val}</span>'
                    f'</div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="ev ev-normal">No legal moves available from this state.</div>', unsafe_allow_html=True)
    with tab2:
        render_algo_dashboard(p)
        if False: _old_dashboard_debug = """

        pos = st.session_state[f"p{p}_pos"]
        money = st.session_state[f"p{p}_money"]
        die = st.session_state[f"p{p}_die"]

        timings, wall = bridge.get_algo_timings(pos, money, die)

        st.markdown("#### ⏱️ Algorithm Timings")
        for t in timings:
            st.write(f"{t['name']} → {t['time_us']} μs | {t['complexity']}")

        st.write(f"Total Execution: {round(wall,2)} ms")

        coins, t_bs = bridge.get_binary_search_coins(pos, die)
        st.markdown("#### 🔍 Binary Search")
        st.write("Min coins to guarantee win:", coins)
        st.caption("Time: O(log M × Grundy)")

        dist, t_bfs = bridge.get_bfs_distances()
        st.markdown("#### 📊 BFS Shortest Path")
        st.write("Min moves to finish:", dist.get(35, -1))
        st.caption("Time: O(V + E)")

        pref, t_pref = bridge.get_prefix_gains()
        st.markdown("#### 📈 Prefix Sum")
        st.write("Total gain till current cell:", pref.get(pos, 0))
        st.caption("Time: O(1) query")

        moves = bridge.get_moves(pos, money, die)

        st.markdown("#### 🎯 Move Analysis")
        for m in moves[:5]:
            st.write(
                f"Roll {m['roll']} → {m['cell_name']} | "
                f"G={m['grundy']} | MM={m['minimax_val']} | "
                f"Item={m['item_name']}"
            )
            
        st.markdown("#### Removed Debug Section")
        arr = []
        if arr:
            best = max(sum(arr[i:i+3]) for i in range(len(arr)-2))
            st.write("Best 3-move gain:", best)
            st.caption("Time: O(N)")
        """
            
#  AI vs AI
def screen_ai_vs_ai():
    cells=st.session_state.cells
    edges=st.session_state.edges
    steps=st.session_state.sim_steps
    end=st.session_state.sim_end
    winner=st.session_state.sim_winner
    p1n=st.session_state.p1_name; p2n=st.session_state.p2_name

    if not steps:
        st.warning("No simulation data. Please go back to setup.")
        return

    total=len(steps)
    idx=st.session_state.sim_idx
    s=steps[idx]

    p1_pos=0; p2_pos=0; p1m=INITIAL_MONEY; p2m=INITIAL_MONEY
    p1d=0; p2d=0
    for i,st2 in enumerate(steps[:idx+1]):
        if st2.get("skip_only"): continue
        if st2["player"]==1:
            p1_pos=st2["npos"]; p1m=st2["nmoney"]; p1d=st2["ndie"]
        else:
            p2_pos=st2["npos"]; p2m=st2["nmoney"]; p2d=st2["ndie"]
    if end:
        pass 

    st.markdown('<div class="section-title">🤖 AI vs AI — Optimal Play Simulation</div>',
                unsafe_allow_html=True)

    if winner[0]:
        wname=(p1n if winner[0]==1 else p2n)
        wcolor=("var(--p1)" if winner[0]==1 else "var(--p2)")
        st.markdown(f'<div style="background:rgba(88,166,255,.07);border:1px solid var(--border);'
                    f'border-radius:12px;padding:12px 18px;margin-bottom:12px;">'
                    f'🏆 <b style="color:{wcolor}">{wname}</b> wins in {winner[1]} turns with optimal Grundy play!'
                    f'</div>', unsafe_allow_html=True)

    if cells:
        fig=board_figure(cells,p1_pos,p2_pos,p1n,p2n,edges)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    c_sl,c_btn=st.columns([5,1])
    with c_sl:
        new_idx=st.slider("Step",0,total-1,idx,key="sim_slider",label_visibility="collapsed")
        if new_idx!=idx: st.session_state.sim_idx=new_idx; st.rerun()
    with c_btn:
        if st.button("⏭️",help="Next step"):
            if idx<total-1: st.session_state.sim_idx=idx+1; st.rerun()

    st.markdown(f'<div style="color:var(--muted);font-size:.82rem;margin-bottom:12px">'
                f'Step {idx+1} of {total}</div>', unsafe_allow_html=True)

    if not s.get("skip_only"):
        pcolor=("var(--p1)" if s["player"]==1 else "var(--p2)")
        pname=(p1n if s["player"]==1 else p2n)
        ev_cls="ev-gain" if s["outcome"]=="WIN" else "ev-loss"
        st.markdown(
            f'<div class="ev {ev_cls}">'
            f'<b style="color:{pcolor}">{pname}</b> · Turn {s["turn"]} · '
            f'Roll <b>{s["roll"]}</b> · {s["pos"]}→<b>{s["npos"]}</b> · '
            f'💰{s["nmoney"]} · {s["cell"]}'
            f'{"· 🃏 "+s["card"] if s["card"] else ""}'
            f' · G={s["gval"]}'
            f'</div>', unsafe_allow_html=True)

    m1,m2,m3,m4,m5=st.columns(5)
    m1.markdown(f'<div class="mbox"><div class="mbox-val">{s.get("turn",0)}</div><div class="mbox-lbl">Turn</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="mbox"><div class="mbox-val" style="color:var(--p1)">{p1_pos}</div><div class="mbox-lbl">{p1n[:8]}</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="mbox"><div class="mbox-val" style="color:var(--p2)">{p2_pos}</div><div class="mbox-lbl">{p2n[:8]}</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="mbox"><div class="mbox-val" style="color:var(--p1)">{p1m}💰</div><div class="mbox-lbl">{p1n[:6]} coins</div></div>', unsafe_allow_html=True)
    m5.markdown(f'<div class="mbox"><div class="mbox-val" style="color:var(--p2)">{p2m}💰</div><div class="mbox-lbl">{p2n[:6]} coins</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col_log,col_chart=st.columns([2,3])

    with col_log:
        st.markdown('<div class="section-title" style="font-size:1.1rem">📜 Move Log</div>',
                    unsafe_allow_html=True)
        log_html=""
        for i,s2 in enumerate(steps):
            if s2.get("skip_only"):
                log_html+=f'<div class="log-entry">T{s2["turn"]} P{s2["player"]} SKIP</div>'
                continue
            hl="hl" if i==idx else ""
            pc=("p1" if s2["player"]==1 else "p2")
            oc="✅" if s2["outcome"]=="WIN" else "·"
            nm2=(p1n if s2["player"]==1 else p2n)[:6]
            log_html+=(f'<div class="log-entry {hl}">'
                       f'<span style="color:var(--{pc})">{nm2}</span> '
                       f'T{s2["turn"]} r{s2["roll"]} {s2["pos"]}→{s2["npos"]} '
                       f'G={s2["gval"]} {oc}</div>')
        st.markdown(log_html, unsafe_allow_html=True)

    with col_chart:
        chart_data=[]
        cp1,cp2=0,0; cm1,cm2=INITIAL_MONEY,INITIAL_MONEY
        for i,s2 in enumerate(steps[:idx+1]):
            if s2.get("skip_only"): continue
            if s2["player"]==1: cp1=s2["npos"]; cm1=s2["nmoney"]
            else:               cp2=s2["npos"]; cm2=s2["nmoney"]
            chart_data.append({"Step":i+1,p1n:cp1,p2n:cp2})
        if chart_data:
            df=pd.DataFrame(chart_data)
            fig2=px.line(df,x="Step",y=[p1n,p2n],markers=True,
                         color_discrete_map={p1n:"#f85149",p2n:"#58a6ff"},
                         title="Board Position Over Time",
                         template="plotly_dark")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                               plot_bgcolor="rgba(22,27,34,.6)",
                               margin=dict(l=0,r=0,t=30,b=0),height=300,
                               legend=dict(font=dict(color="#e6edf3")))
            st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})

        g_data=[]
        for i,s2 in enumerate(steps[:idx+1]):
            if not s2.get("skip_only"):
                g_data.append({"Step":i+1,"Grundy":s2["gval"],
                                "Player":(p1n if s2["player"]==1 else p2n)})
        if g_data:
            dfg=pd.DataFrame(g_data)
            fig3=px.bar(dfg,x="Step",y="Grundy",color="Player",barmode="group",
                        color_discrete_map={p1n:"#f85149",p2n:"#58a6ff"},
                        title="Grundy Value per Move",template="plotly_dark")
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                               plot_bgcolor="rgba(22,27,34,.6)",
                               margin=dict(l=0,r=0,t=30,b=0),height=250,
                               legend=dict(font=dict(color="#e6edf3")))
            st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False})

def screen_results():
    with st.sidebar:
        st.markdown('<div style="font-family:Baloo 2,cursive;font-size:1.4rem;color:#58a6ff">🏕️ Game Over!</div>',
                    unsafe_allow_html=True)
        if st.button("🔄 Play Again",use_container_width=True):
            for k,v in DEFS.items():
                if k not in("compiled","compile_err","cells","edges"):
                    st.session_state[k]=v
            st.session_state.screen="setup"; st.rerun()

    w=st.session_state.winner
    wn=st.session_state[f"p{w}_name"]
    wm=st.session_state[f"p{w}_money"]
    ln=st.session_state[f"p{3-w}_name"]
    lm=st.session_state[f"p{3-w}_money"]

    st.markdown(
        f'<div class="win-screen">'
        f'<div style="font-size:5rem">🏆</div>'
        f'<div class="win-name">{wn} Wins!</div>'
        f'<div style="font-size:1.1rem;color:var(--muted);margin-top:8px">'
        f'Reached the finish with {wm} coins remaining</div>'
        f'</div>', unsafe_allow_html=True)

    st.markdown("")
    c1,c2,c3=st.columns(3)
    c1.markdown(f'<div class="mbox"><div class="mbox-val">{len(st.session_state.game_log)}</div>'
                '<div class="mbox-lbl">Total Turns</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="mbox"><div class="mbox-val" style="color:var(--green)">{wm}</div>'
                f'<div class="mbox-lbl">{wn[:10]} Coins</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="mbox"><div class="mbox-val" style="color:var(--red)">{lm}</div>'
                f'<div class="mbox-lbl">{ln[:10]} Coins</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    ca,cb,_=st.columns([2,2,3])
    with ca:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("🔄 Play Again",use_container_width=True):
            for k,v in DEFS.items():
                if k not in("compiled","compile_err","cells","edges"):
                    st.session_state[k]=v
            st.session_state.screen="setup"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with cb:
        if st.button("📖 Rules",use_container_width=True):
            st.session_state.screen="rulebook"; st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-title">📜 Full Game Log</div>', unsafe_allow_html=True)
    for e in st.session_state.game_log:
        st.markdown(f'<div class="log-entry hl">{e}</div>', unsafe_allow_html=True)

def render_algo_dashboard(cur_player):
    p=cur_player
    pos=st.session_state[f"p{p}_pos"]
    money=st.session_state[f"p{p}_money"]
    die=st.session_state[f"p{p}_die"]

    st.markdown('<div class="section-title">⚙️ Algorithm Dashboard</div>',unsafe_allow_html=True)
    st.markdown('<div style="color:var(--muted);font-size:.82rem;margin-bottom:16px">Live execution times and results for the core CP algorithms at current position.</div>',unsafe_allow_html=True)

    # TIMING TABLE
    with st.spinner("Running all algorithms..."):
        timings, wall_ms = bridge.get_algo_timings(pos, money, die)

    ALGO_ICONS = {
        "Grundy":"🧠", "Binary Search":"🔍", "Prefix Sum":"📊",
        "BFS":"🗺️", "Minimax":"♟️", "Dijkstra":"🧭"
    }
    COMPLEXITY_COLOR = {
        "O(1)":"#3fb950", "O(N)":"#3fb950", "O(N log":"#3fb950",
        "O(V+E)":"#58a6ff", "O(B*M":"#d29922", "O(log M":"#d29922",
        "O(D^":"#f85149", "O(E log":"#58a6ff"
    }

    st.markdown('<div style="font-weight:700;font-size:.95rem;color:var(--text);margin-bottom:10px">📋 Algorithm Performance Table</div>',unsafe_allow_html=True)

    table_rows = [
        '<div style="overflow-x:auto;border:1px solid var(--border);border-radius:10px;background:var(--surface);">',
        '<table style="width:100%;border-collapse:collapse;font-size:.82rem;font-family:JetBrains Mono,monospace">',
        '<thead><tr style="border-bottom:2px solid var(--border);background:rgba(88,166,255,.06)">',
        '<th style="text-align:left;padding:10px 12px;color:var(--accent)">Algorithm</th>',
        '<th style="text-align:left;padding:10px 12px;color:var(--accent)">Time Complexity</th>',
        '<th style="text-align:right;padding:10px 12px;color:var(--accent)">C++ Time</th>',
        '<th style="text-align:left;padding:10px 12px;color:var(--accent)">Result</th>',
        '</tr></thead><tbody>',
    ]
    for t in timings:
        name=t["name"]; cplx=t["complexity"]; us=t["time_us"]; res=t["result"]
        icon=""
        for k,v in ALGO_ICONS.items():
            if k in name: icon=v; break
        c_color="#58a6ff"
        for pfx,col in COMPLEXITY_COLOR.items():
            if cplx.startswith(pfx): c_color=col; break
        if us==0: time_str="< 1 µs"
        elif us<1000: time_str=f"{us} µs"
        else: time_str=f"{us/1000:.1f} ms"
        table_rows.append(
            f'<tr style="border-bottom:1px solid rgba(48,54,61,0.5)">'
            f'<td style="padding:9px 12px;color:var(--text)">{icon} {name}</td>'
            f'<td style="padding:9px 12px;color:{c_color}">{cplx}</td>'
            f'<td style="padding:9px 12px;text-align:right;color:var(--yellow)">{time_str}</td>'
            f'<td style="padding:9px 12px;color:var(--muted)">{res}</td>'
            f'</tr>'
        )
    table_rows.append(
        f'<tr style="border-top:2px solid var(--border);background:rgba(88,166,255,.06)">'
        f'<td colspan="2" style="padding:9px 12px;color:var(--muted)">Total wall time (Python call)</td>'
        f'<td style="padding:9px 12px;text-align:right;color:var(--accent);font-weight:700">{wall_ms:.1f} ms</td>'
        f'<td></td></tr>'
    )
    table_rows.append('</tbody></table></div>')
    st.markdown("".join(table_rows), unsafe_allow_html=True)

    st.markdown('<div style="height:20px"></div>',unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    # LEFT: BFS + Binary Search
    with col1:
        st.markdown('<div class="section-title" style="font-size:1.1rem">🗺️ BFS: Min Moves to Finish</div>',unsafe_allow_html=True)
        bfs_dist, bfs_ms = bridge.get_bfs_distances()
        d = bfs_dist.get(pos, -1)
        color = "#3fb950" if d<=3 else "#d29922" if d<=6 else "#f85149"
        st.markdown(
            f'<div class="mbox" style="margin-bottom:12px">'
            f'<div class="mbox-val" style="color:{color}">{d if d>=0 else "?"}</div>'
            f'<div class="mbox-lbl">Min dice rolls from cell {pos} to finish</div>'
            f'<div style="font-size:.72rem;color:var(--muted);margin-top:4px">BFS computed in {bfs_ms:.1f}ms · O(V+E)</div>'
            f'</div>', unsafe_allow_html=True)

        # BFS distance bar
        bar_html=""
        for cell in range(0, BOARD_SIZE, 5):
            cd=bfs_dist.get(cell,-1)
            w=max(0,min(100,int((1-cd/12)*100))) if cd>=0 else 0
            is_cur="border:2px solid var(--yellow);" if cell==pos else ""
            bar_html+=f'<div style="display:flex;align-items:center;gap:6px;margin:3px 0;{is_cur}">'
            bar_html+=f'<span style="font-size:.7rem;width:40px;color:var(--muted)">Cell {cell}</span>'
            bar_html+=f'<div style="flex:1;height:8px;background:var(--surface2);border-radius:4px">'
            bar_html+=f'<div style="width:{w}%;height:100%;background:{"var(--accent)" if cell==pos else "#30363d"};border-radius:4px"></div></div>'
            bar_html+=f'<span style="font-size:.7rem;width:20px;color:var(--text)">{cd}</span></div>'
        st.markdown(bar_html, unsafe_allow_html=True)

        st.markdown('<div style="height:16px"></div>',unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="font-size:1.1rem">🧭 Dijkstra: Minimum-Risk Path</div>',unsafe_allow_html=True)
        risk_dist, risk_ms = bridge.get_dijkstra_risks()
        risk = risk_dist.get(pos, -1)
        risk_color = "#3fb950" if risk>=0 and risk<=8 else "#d29922" if risk>=0 and risk<=16 else "#f85149"
        st.markdown(
            f'<div class="mbox" style="margin-bottom:12px">'
            f'<div class="mbox-val" style="color:{risk_color}">{risk if risk>=0 else "?"}</div>'
            f'<div class="mbox-lbl">Minimum weighted risk from cell {pos}</div>'
            f'<div style="font-size:.72rem;color:var(--muted);margin-top:4px">Cell penalties are weighted · Dijkstra O(E log V) · {risk_ms:.1f}ms</div>'
            f'</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:16px"></div>',unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="font-size:1.1rem">🔍 Binary Search: Min Winning Coins</div>',unsafe_allow_html=True)
        min_coins, bs_ms = bridge.get_binary_search_coins(pos, die)
        has_enough = money >= min_coins
        coin_color = "#3fb950" if has_enough else "#f85149"
        st.markdown(
            f'<div class="mbox">'
            f'<div class="mbox-val" style="color:{coin_color}">{min_coins}</div>'
            f'<div class="mbox-lbl">Min coins for a winning position</div>'
            f'<div style="font-size:.72rem;color:var(--muted);margin-top:4px">Binary search on [1..30] · {bs_ms:.1f}ms</div>'
            f'</div>', unsafe_allow_html=True)
        if has_enough:
            st.markdown(f'<div class="ev ev-gain" style="margin-top:8px">✅ You have {money} coins — above the {min_coins} threshold!</div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ev ev-loss" style="margin-top:8px">⚠️ You only have {money} coins — need {min_coins} for a guaranteed win!</div>',unsafe_allow_html=True)

    # RIGHT: Prefix Sum
    with col2:
        st.markdown('<div class="section-title" style="font-size:1.1rem">📊 Prefix Sum: Cell Range Money</div>',unsafe_allow_html=True)
        prefix_gains, pfx_ms = bridge.get_prefix_gains()
        # Show gain from current pos to finish
        gain_to_end = prefix_gains.get(BOARD_SIZE-1, 0) - prefix_gains.get(pos, 0)
        st.markdown(
            f'<div class="mbox" style="margin-bottom:12px">'
            f'<div class="mbox-val" style="color:{"var(--green)" if gain_to_end>=0 else "var(--red)"}">{gain_to_end:+}</div>'
            f'<div class="mbox-lbl">Expected coins if you reach finish from cell {pos}</div>'
            f'<div style="font-size:.72rem;color:var(--muted);margin-top:4px">Prefix sum query O(1) · built in {pfx_ms:.1f}ms</div>'
            f'</div>', unsafe_allow_html=True)

        # Visualize prefix gains as colored cells
        row_html=""
        for i in range(BOARD_SIZE):
            pg=prefix_gains.get(i,0)
            # relative gain at this cell
            cell_gain = pg - (prefix_gains.get(i-1,0) if i>0 else 0)
            if cell_gain>0: bg="#1a3320"; fg="#3fb950"
            elif cell_gain<0: bg="#2d1515"; fg="#f85149"
            else: bg="var(--surface2)"; fg="var(--muted)"
            brd="2px solid var(--yellow)" if i==pos else "1px solid transparent"
            row_html+=f'<span title="Cell {i}: {cell_gain:+}" style="display:inline-block;width:20px;height:20px;margin:1px;border-radius:3px;background:{bg};color:{fg};font-size:.58rem;text-align:center;line-height:20px;border:{brd}">{cell_gain if cell_gain!=0 else "·"}</span>'
        st.markdown(f'<div style="line-height:1.2">{row_html}</div><div style="font-size:.7rem;color:var(--muted);margin-top:4px">Each cell shows net coin change. Yellow outline = your position.</div>',unsafe_allow_html=True)

    # Bottom: Bitmask Power-ups
    st.markdown("---")
    st.markdown('<div class="section-title" style="font-size:1.1rem">🎒 Bitmask: Power-up Tracker</div>',unsafe_allow_html=True)
    mask=st.session_state.get(f"p{p}_mask",0)
    ITEMS_PY=[
        {"cell":5,"name":"Compass","bonus":2,"emoji":"🧭"},
        {"cell":11,"name":"Sunscreen","bonus":2,"emoji":"🧴"},
        {"cell":17,"name":"Water Bottle","bonus":3,"emoji":"💧"},
        {"cell":21,"name":"Picnic Blanket","bonus":2,"emoji":"🧺"},
        {"cell":29,"name":"Trail Map","bonus":3,"emoji":"🗺️"},
    ]
    item_html='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px">'
    total_bonus=0
    for i,item in enumerate(ITEMS_PY):
        collected=(mask>>i)&1
        if collected: total_bonus+=item["bonus"]
        bg="rgba(63,185,80,.15)" if collected else "rgba(139,148,158,.06)"
        brd="var(--green)" if collected else "var(--border)"
        status="✅ Collected" if collected else f"📍 At cell {item['cell']}"
        item_html+=f'<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:10px;background:{bg};border:1px solid {brd}">'
        item_html+=f'<span style="font-size:1.2rem">{item["emoji"]}</span>'
        item_html+=f'<div><b style="font-size:.88rem">{item["name"]}</b><span style="color:var(--green);margin-left:8px;font-size:.8rem">+{item["bonus"]}</span>'
        item_html+=f'<div style="font-size:.72rem;color:var(--muted)">{status}</div></div>'
        item_html+=f'<span style="margin-left:auto;font-size:.7rem;font-family:JetBrains Mono,monospace;color:var(--muted)">bit {i} = {(mask>>i)&1}</span>'
        item_html+='</div>'
    item_html+='</div>'
    st.markdown(item_html,unsafe_allow_html=True)
    st.markdown(f'<div style="margin-top:10px;font-size:.8rem;color:var(--muted)">Bitmask: <span style="font-family:JetBrains Mono;color:var(--accent)">{bin(mask)} ({mask})</span> · Bonus: <span style="color:var(--green)">+{total_bonus}</span></div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="section-title" style="font-size:1.1rem">🏁 AI Tournament: Strategy Comparison</div>',unsafe_allow_html=True)
    tour_rows, tour_ms = bridge.get_tournament_results()
    if tour_rows:
        tour_rows = sorted(tour_rows, key=lambda r: r["win_rate"], reverse=True)
        rows_html=[
            '<div style="overflow-x:auto;border:1px solid var(--border);border-radius:10px;background:var(--surface)">',
            '<table style="width:100%;border-collapse:collapse;font-size:.82rem;font-family:JetBrains Mono,monospace">',
            '<thead><tr style="border-bottom:2px solid var(--border);background:rgba(88,166,255,.06)">',
            '<th style="text-align:left;padding:9px 12px;color:var(--accent)">Rank</th>',
            '<th style="text-align:left;padding:9px 12px;color:var(--accent)">Strategy</th>',
            '<th style="text-align:right;padding:9px 12px;color:var(--accent)">Win Rate</th>',
            '<th style="text-align:right;padding:9px 12px;color:var(--accent)">Wins/Games</th>',
            '<th style="text-align:right;padding:9px 12px;color:var(--accent)">Avg Turns</th>',
            '<th style="text-align:right;padding:9px 12px;color:var(--accent)">Avg Money</th>',
            '</tr></thead><tbody>',
        ]
        for rank,row in enumerate(tour_rows, start=1):
            color="#3fb950" if rank==1 else "#58a6ff" if rank==2 else "var(--muted)"
            rows_html.append(
                f'<tr style="border-bottom:1px solid rgba(48,54,61,0.5)">'
                f'<td style="padding:9px 12px;color:{color}">#{rank}</td>'
                f'<td style="padding:9px 12px;color:var(--text)">{row["strategy"]}</td>'
                f'<td style="padding:9px 12px;text-align:right;color:{color}">{row["win_rate"]:.1f}%</td>'
                f'<td style="padding:9px 12px;text-align:right;color:var(--muted)">{row["wins"]}/{row["games"]}</td>'
                f'<td style="padding:9px 12px;text-align:right;color:var(--muted)">{row["avg_turns"]:.1f}</td>'
                f'<td style="padding:9px 12px;text-align:right;color:var(--muted)">{row["avg_money"]:.1f}</td>'
                f'</tr>'
            )
        rows_html.append('</tbody></table></div>')
        st.markdown("".join(rows_html), unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:.72rem;color:var(--muted);margin-top:6px">Round-robin simulation in C++ · Random vs Greedy vs Minimax vs Grundy · {tour_ms:.1f}ms</div>', unsafe_allow_html=True)

if "p1_mask" not in st.session_state: st.session_state["p1_mask"]=0
if "p2_mask" not in st.session_state: st.session_state["p2_mask"]=0

sc=st.session_state.screen
if   sc=="rulebook": screen_rulebook()
elif sc=="setup":    screen_setup()
elif sc=="game":     screen_game()
elif sc=="results":  screen_results()
else: st.session_state.screen="rulebook"; st.rerun()