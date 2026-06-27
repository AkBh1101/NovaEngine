# 🏕️ Picnic Quest — Game Theory Board Game

## Overview

**Picnic Quest** is an advanced two-player board game that integrates **Sprague-Grundy game theory** with interactive gameplay mechanics. Players navigate a 36-cell board using probabilistic dice rolls while making strategic decisions to reach the finish line. The engine computes optimal moves using Grundy numbers, making it an excellent platform for learning combinatorial game theory and competitive programming algorithms.

### Key Features

✨ **Game-Theoretic Engine:** Computes Grundy numbers (nim-values) for optimal move selection  
🎲 **Complex Mechanics:** Dice rolls, card draws, cell effects (money, jumps, turn modifiers)  
⚡ **Real-Time Performance:** Sub-200ms response time for move evaluation  
🔍 **Algorithm Showcase:** 7+ algorithms integrated (Minimax, BFS, Dijkstra, Binary Search, Prefix Sum, DP, Bitmask)  
🎯 **AI Tournament:** Round-robin tournament framework to compare strategies  
📊 **Interactive UI:** Streamlit-based web interface with visualization & replay  
📈 **Performance Analysis:** Built-in benchmarking and profiling tools

---

## Quick Start

### Installation

```bash
# Clone or download project
cd picnic_quest/

# Verify g++ is available
g++ --version

# Run the setup script (auto-compiles and launches web UI)
bash run.sh
```

**First run will:**
1. Compile C++ engine (game_engine.cpp → picnic_engine.exe)
2. Install Python dependencies (streamlit, plotly, pandas)
3. Launch interactive web interface at `http://localhost:8501`

### Your First Game

1. **Open browser:** `http://localhost:8501`
2. **Enter state:** Position = 0 (start), Money = 10, Die Level = 0
3. **Click "Compute Moves":** See all 6 possible dice outcomes
4. **Run Simulation:** Watch 2 AI players compete
5. **View Grundy:** Highlight winning vs. losing positions

---
## Game Mechanics

### Board

- **Size:** 36 cells (0 = start, 35 = finish)
- **Cell Types:** 11 types with different effects
- **Win Condition:** Reach cell 35

### Player State

```
Position: 0-35 (current board cell)
Money:    0-∞  (accumulated currency)
Die:      0-5  (upgrade level, affects roll range)
```

### Cell Types

| Type             | Effect                 | Example                  |
|------------------|------------------------|--------------------------|
| **Normal**       | No effect              | Safe passage             |
| **Money Gain**   | +N coins               | Landing bonus            |
| **Money Loss**   | -N coins               | Penalty fee              |
| **Die Upgrade**  | Increase die level     | Roll 1d(4+die) next turn |
| **Jump Forward** | +N positions           | Advance board            |
| **Jump Back**    | -N positions           | Retreat board            |
| **Skip Turn**    | Skip next turn         | Opponent plays twice     |
| **Extra Turn**   | Roll again immediately | Chain moves              |
| **Card**         | Draw special card      | Random effect            |
| **Start**        | Game start (pos=0)     | Initial state            |
| **Finish**       | Win (pos=35)           | Victory                  |

### Dice & Upgrades

```
Base die:       roll 1d6 (outcomes 1-6)
Each upgrade:   +1 bonus (die level 0: 1-6, die level 1: 2-7, ..., level 5: 6-11)
Probability:    Die 0: uniform 1/6 each outcome
                Die 5: uniform 1/6 each outcome (shifted)
Expected value: 3.5 + die_level
```

### Strategic Elements

- **Money:** Required to afford certain moves / unlocks upgrades
- **Die Level:** Higher die = faster completion but more randomness
- **Position:** Close to finish = limited options = lower Grundy variance
- **Timing:** Collect early upgrades vs. safe late-game play

---

## Usage Guide

### Web UI (Streamlit)

After running `bash run.sh`, navigate to `http://localhost:8501`

#### 1. **Move Calculator**

**Input:**
- Position (0-35)
- Money (0-100)
- Die Level (0-5)

**Output:**
- All 6 possible dice rolls
- Resulting position, money, die after each roll
- Grundy number of resulting state
- Cell effects and card outcomes

**Example:**
```
Position 10, Money 20, Die 1

Roll 1 → Position 11, Money 21, Die 1, Grundy 4, [Money Gain +1]
Roll 2 → Position 12, Money 18, Die 1, Grundy 2, [Money Loss -2]
Roll 3 → Position 13, Money 22, Die 1, Grundy 5, [Normal]
...
Roll 6 → Position 16, Money 19, Die 1, Grundy 3, [Jump Forward +2]
```

#### 2. **Grundy Analyzer**

**Purpose:** Show which moves lead to winning/losing positions

**Output:**
```
Current State Grundy: 7 (WINNING - you can force a win)

Winning Moves (Lead to Grundy = 0):
  → Roll 3: Position 13, Grundy 0  ✓ Play here to win

Neutral Moves (Lead to Grundy ≠ 0):
  → Roll 1: Position 11, Grundy 4
  → Roll 2: Position 12, Grundy 2
  ...
```

#### 3. **Game Simulation**

**Setup:**
- Choose 2 players (AI strategies or human)
- Optional: Set starting positions/money

**Playback:**
- Step-by-step replay with board visualization
- Move highlights and card effects
- Winner determination

**Statistics:**
- Total turns played
- Money per player
- Die upgrades collected
- Critical decision points

#### 4. **Algorithm Benchmark**

**Measures:**
- Grundy computation time
- Minimax evaluation time
- BFS shortest path time
- Dijkstra risk analysis time
- Prefix sum calculation time
- Overall wall-clock time

**Output:**
```
Grundy (Sprague-Grundy):           150µs  [Grundy = 5]
Minimax (depth=2):                  80µs  [Best move: roll 3]
BFS (shortest path):                 3µs  [Min 4 more moves to finish]
Dijkstra (risk-weighted):           12µs  [Safest path risk = -5]
Prefix Sum (cumulative money):       1µs  [Total money 0→pos = 120]
Binary Search (min coins):          45µs  [Min coins to win = 8]
Bitmask DP (state encoding):        0.5µs [State hash collision = 0]
```

#### 5. **Tournament Mode**

**Format:**
- Round-robin: each AI plays every other AI
- Multiple games per matchup
- Statistics: win rate, avg turns, avg ending money

**Strategies:**
- **Greedy:** Maximize money each turn
- **Minimax:** 2-ply lookahead
- **Grundy-Optimal:** Full Grundy computation
- **Random:** Random legal moves
- **Balanced:** Hybrid (heuristics + Grundy)

**Results Table:**
```
Strategy              Wins  Games  Win%  Avg Turns  Avg Money
─────────────────────────────────────────────────────────────
Grundy-Optimal         78    100   78%       71.2       520
Minimax (d=2)          62    100   62%       76.5       480
Balanced               55    100   55%       79.1       460
Greedy (Max Money)     45    100   45%       82.3       450
Random                 25    100   25%       95.7       380
```
---
