![Logo](logos/big.png)

# Chesalyser - Chess Game Analyzer ♟️

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Stockfish](https://img.shields.io/badge/Stockfish-7B61FF?style=for-the-badge&logo=chess.com&logoColor=white)](https://stockfishchess.org/)

A powerful chess game analyzer built with Python and Streamlit, leveraging Stockfish for position evaluation. Provides detailed move analysis, win probability tracking, and interactive game review.

![Chesalyser Demo](logos/ss.png)

## 🌟 Features

- **PGN File Analysis**: Upload games or paste PGN text directly
- **Move Classification**:
  - 🟢 Best Move 🟦 Good Move 🟡 Inaccuracy 🟠 Mistake 🔴 Blunder
- **Interactive Chess Board**: SVG-based board visualization
- **Win Probability Graph**: Track advantage fluctuations through the game
- **Multi-Depth Analysis**: Choose from 5 analysis modes (Beginner to Stockfish)
- **Game Metadata Display**: Player names, Elo ratings, and game results
- **Modern UI**: Gradient headers and responsive design

## ⚙️ Installation

### Prerequisites

- Python 3.9+
- Stockfish binary (included in `stockfish/` folder)

```bash
# Clone repository
git clone https://github.com/yourusername/chesalyser.git
cd chesalyser

# Install dependencies
pip install -r requirements.txt

# Download Stockfish (Linux)
chmod +x stockfish/stockfish-ubuntu-x86-64-sse41-popcnt
```

## 🚀 Usage

1. Start the application:

```bash
streamlit run main.py
```

2. In the sidebar:

   - Upload PGN file or paste game text
   - Select analysis depth (Beginner to Stockfish mode)
   - Click "ANALYZE GAME"

3. Explore results:
   - Interactive move slider
   - Chess board visualization
   - Move quality assessment
   - Win probability graph
   - Best move suggestions

## 📊 Analysis Metrics

| Metric               | Description                                         |
| -------------------- | --------------------------------------------------- |
| Win Probability      | White's winning chances based on current evaluation |
| Centipawn Evaluation | Numeric assessment of position advantage            |
| Score Change         | Difference in evaluation from previous move         |
| Piece Moved          | Type of piece moved (Queen, Knight, etc.)           |
| Capture Detection    | Identifies if move resulted in capture              |

## 🛠️ Customization

Modify these components for different behavior:

1. **Analysis Depth Settings** (in `main.py`):

```python
depth_options = {
    10: "Beginner mode",
    15: "Casual mode",
    20: "Serious mode",
    25: "Grandmaster mode",
    30: "Stockfish mode",
}
```

2. **Move Classification Thresholds** (in `classify_move()` function):

```python
# Adjust these values for different move ratings
if is_capture:
    if score_change < 30:  # Modify these thresholds
        return "Best Move", "green"
```

3. **UI Colors** (in `style.css`):

```css
/* Custom gradient effects */
.gradient-header {
  background-image: linear-gradient(to top right, #00f0ff, #0e6fff, #8f5bff);
}
```

## 🚨 Troubleshooting

**Common Issues**:

1. **Stockfish Not Found**:

   - Verify executable path in sidebar settings
   - Ensure correct permissions: `chmod +x stockfish/...`

2. **PGN Parsing Errors**:

   - Validate PGN format using [PGN Validator](https://www.chess.com/pgn-viewer)
   - Ensure game headers are present

3. **Analysis Timeouts**:
   - Reduce analysis depth
   - Use better hardware for deep analysis

## 📜 License

MIT License - See [LICENSE](LICENSE) for details

## 🤝 Credits

- Chess engine: [Stockfish](https://stockfishchess.org/)
- Chess library: [python-chess](https://python-chess.readthedocs.io/)
- UI Framework: [Streamlit](https://streamlit.io/)

---

**Disclaimer**: This project is not affiliated with Chess.com or Lichess. Intended for educational purposes only. Use at your own risk in competitive environments.
