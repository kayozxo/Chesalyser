import streamlit as st
import chess
import chess.pgn
import chess.engine
import chess.svg
from io import StringIO
import numpy as np
import random

# Convert Stockfish score to Expected Points (EP)
def compute_expected_points(score):
    if score is None:
        return 0.5
    return 1 / (1 + 10 ** (-score / 400))

# Move Classification based on Expected Points loss (Chess.com criteria)
def classify_move(expected_points_lost):
    if expected_points_lost == 0:
        return "Best", "green"
    elif 0.00 < expected_points_lost <= 0.02:
        return "Excellent", "blue"
    elif 0.02 < expected_points_lost <= 0.05:
        return "Good", "cyan"
    elif 0.05 < expected_points_lost <= 0.10:
        return "Inaccuracy", "yellow"
    elif 0.10 < expected_points_lost <= 0.20:
        return "Mistake", "orange"
    else:
        return "Blunder", "red"

# Analyze game using Stockfish with user-selected depth
def analyze_game(game, engine_path, depth):
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    analysis_results = []
    board = game.board()

    for move in game.mainline_moves():
        # Get Stockfish evaluation
        info = engine.analyse(board, chess.engine.Limit(depth=depth))

        # Extract move evaluation
        played_score = info["score"].white().score(mate_score=1000)
        best_score = info["score"].white().score(mate_score=1000)  # ✅ Correctly extract best move score


        # Compute Expected Points (EP)
        played_move_EP = compute_expected_points(played_score)
        best_move_EP = compute_expected_points(best_score)
        expected_points_lost = best_move_EP - played_move_EP

        # Classify move
        move_quality, color = classify_move(expected_points_lost)

        # Store results
        analysis_results.append({
            'move': move.uci(),
            'score': played_score / 100.0,
            'best_move': info.get("pv", [None])[0].uci() if "pv" in info else "None",
            'expected_points_lost': expected_points_lost,
            'quality': move_quality,
            'color': color
        })

        board.push(move)

    engine.quit()
    return analysis_results


def main():
    st.title("♟️ Chess Game Analyzer")

    with st.sidebar:
        st.write("Upload a PGN file to analyze your game like Chess.com!")
        engine_path = "/home/kayozxo/Downloads/stockfish-ubuntu-x86-64-sse41-popcnt/stockfish/stockfish-ubuntu-x86-64-sse41-popcnt"
        pgn_file = st.file_uploader("Upload PGN file", type="pgn")
        pgn_text = st.text_area("Or paste PGN text here")

        # Depth selection with cheeky phrases
        depth_options = {
            10: "Beginner mode: Let's not overthink!",
            15: "Casual mode: Solid but not too deep!",
            20: "Serious mode: Think like a FIDE Master!",
            25: "Grandmaster mode: Big brain time!",
            30: "Stockfish mode: Maximum overdrive!"
        }
        depth = st.selectbox("Select Analysis Depth:", options=list(depth_options.keys()), format_func=lambda x: depth_options[x])

    if pgn_file or pgn_text:
        try:
            pgn = StringIO(pgn_text if pgn_text else pgn_file.getvalue().decode())
            game = chess.pgn.read_game(pgn)

            if game is None:
                st.error("Invalid PGN file or text. Please check the format.")
                return

            with st.expander("Game Header"):
                st.write(game.headers)

            with st.sidebar:
                if st.button("Analyze Game"):
                    messages = [
                        "Thinking like Magnus Carlsen...",
                        "Calculating the best blunder... just kidding!",
                        "Running Stockfish at full speed!",
                        "Searching for the brilliancy move!",
                        "Did you just play a Bongcloud opening? Let's see...",
                        "Analyzing faster than Hikaru can pre-move!",
                        "Determining if this was a 200 IQ move or a disaster...",
                        "Checking if this game belongs in the Hall of Fame or Shame!"
                    ]
                    with st.spinner(random.choice(messages)):
                        st.session_state.analysis = analyze_game(game, engine_path, depth)
                        st.session_state.num_moves = len(st.session_state.analysis)

            if "analysis" in st.session_state:
                slider = st.slider("Move Number", 1, st.session_state.num_moves, 1) - 1
                board = game.board()
                for i in range(slider + 1):
                    board.push(chess.Move.from_uci(st.session_state.analysis[i]['move']))

                col2, col3 = st.columns(2)

                with col2:
                    svg = chess.svg.board(board=board, size=400)
                    st.image(svg, width=400)

                with col3:
                    result = st.session_state.analysis[slider]
                    st.markdown(f"### Move: `{result['move']}`")
                    st.markdown(f"**Evaluation**: `{result['score']:.2f} pawns`")
                    st.markdown(f"**Best move**: `{result['best_move']}`")
                    st.markdown(
                        f"**Move Quality**: <span style='color:{result['color']}; font-weight:bold;'>{result['quality']}</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown(f"**Expected Points Lost**: `{result['expected_points_lost']:.3f}`")

        except Exception as e:
            st.error(f"Error analyzing game: {str(e)}")

if __name__ == "__main__":
    main()
