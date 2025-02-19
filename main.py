import streamlit as st
import chess
import chess.pgn
import chess.engine
import chess.svg
from io import StringIO
import numpy as np
import random

# Move Classification based on Expected Points loss (Chess.com criteria)
def classify_move(score_change):
    if score_change == 0:
        return "Best Move", "green"
    elif 0 < score_change < 50:
        return "Good Move", "blue"
    elif 50 <= score_change < 150:
        return "Inaccuracy", "yellow"
    elif 150 <= score_change < 300:
        return "Mistake", "orange"
    else:
        return "Blunder", "red"


def analyze_game(game, engine_path, depth):
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    analysis_results = []
    board = game.board()

    pre_eval = 0
    for move in game.mainline_moves():
        # Get Stockfish evaluation for the current position
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        played_score = info["score"].white().score(mate_score=1000)

        score_change = abs(played_score - pre_eval)
        win_probability = 1 / (1 + 10 ** (-played_score / 400))


        # Classify move based on Expected Points loss
        move_quality, color = classify_move(score_change)

        best_move = info.get("pv", [None])[0]

        # Store results
        analysis_results.append({
            'move': move.uci(),
            'score': win_probability,
            'best_move': best_move.uci() if best_move else "None",
            'expected_points_lost': score_change,
            'quality': move_quality,
            'color': color
        })

        pre_eval = played_score
        board.push(move)  # Push the actual played move


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
                    st.markdown(f"**Win Probability**: `{(result['score'] * 100):.2f}%`")
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
