#!/bin/bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$DIR/picnic_engine"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   🏕️  Picnic Quest — Game Theory Board Game  v2     ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Check g++
if ! command -v g++ &>/dev/null; then
  echo "❌  g++ not found."
  echo "    Ubuntu: sudo apt install build-essential"
  echo "    macOS:  xcode-select --install"
  exit 1
fi
echo "✅  Compiler: $(g++ --version | head -1)"

# Compile
echo "🔨  Compiling C++ engine..."
g++ -O2 -std=c++17 -o "$BIN" "$DIR/game_engine.cpp"
echo "✅  Engine compiled → $BIN"

# Self-test
COUNT=$(./picnic_engine cellinfo | grep -c "^CELL|" || true)
echo "✅  Board loaded: $COUNT cells"

# Python deps
echo "📦  Installing Python packages..."
pip install -q streamlit plotly pandas 2>/dev/null || pip3 install -q streamlit plotly pandas
echo "✅  Packages ready"

echo ""
echo "🚀  Launching at http://localhost:8501"
echo "    Press Ctrl+C to quit"
echo ""

streamlit run "$DIR/app.py" \
  --server.port 8501 \
  --server.headless false \
  --theme.base dark \
  --theme.primaryColor "#58a6ff" \
  --theme.backgroundColor "#0d1117" \
  --theme.secondaryBackgroundColor "#161b22" \
  --theme.textColor "#e6edf3"
