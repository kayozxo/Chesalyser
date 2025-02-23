import streamlit as st
import chess
import chess.pgn
import chess.engine
import chess.svg
from io import StringIO
import numpy as np
import random
import pathlib

st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="Chesalyser", page_icon="logos/small.png")

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

    st.logo("logos/big.png", icon_image="logos/small.png")
    file_path = pathlib.Path("style.css")
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

    st.title(":material/chess_pawn: Chess Game Analyzer")

    st.markdown("<hr style='margin: 0px 0px 30px 0px;'>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<div style='background-image: linear-gradient(to top right, #00f0ff, #0e6fff, #8f5bff); border-radius: 8px'><h1 style='text-align: center; padding: 10px; margin: 0px 0px 15px 0px; font-weight: 700;'>⚙ SETTINGS</h1></div>", unsafe_allow_html=True)

        engine_path = "/home/kayozxo/Downloads/stockfish-ubuntu-x86-64-sse41-popcnt/stockfish/stockfish-ubuntu-x86-64-sse41-popcnt"

        with st.container(border=True):
            pgn_file = st.file_uploader(":material/upload: Upload PGN file", type="pgn")
            pgn_text = st.text_area(":material/content_paste: Or paste PGN text here")

        with st.container(border=True):
        # Depth selection with cheeky phrases
            depth_options = {
                10: "Beginner mode",
                15: "Casual mode",
                20: "Serious mode",
                25: "Grandmaster mode",
                30: "Stockfish mode"
            }
            depth = st.selectbox(":material/settings: Select Analysis Depth:", options=list(depth_options.keys()), format_func=lambda x: depth_options[x])

    if pgn_file or pgn_text:
        try:
            pgn = StringIO(pgn_text if pgn_text else pgn_file.getvalue().decode())
            game = chess.pgn.read_game(pgn)

            if game is None:
                st.error("Invalid PGN file or text. Please check the format.")
                return


            with st.sidebar:
                if st.button(":material/neurology: ANALYZE GAME", use_container_width=True, key="agame"):
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
                    with st.container(border=True):
                        slider = st.slider("Move Number", 1, st.session_state.num_moves, 1, label_visibility="collapsed") - 1
                    board = game.board()
                    for i in range(slider + 1):
                        board.push(chess.Move.from_uci(st.session_state.analysis[i]['move']))

                    with st.container(border=True):
                        col2, col3 = st.columns(2, vertical_alignment="center", gap="small")

                        with col2:
                            with st.container(border=True):
                                with st.container(border=True):
                                    st.write(f"{game.headers['Black']} ({game.headers['BlackElo']})")
                                svg = chess.svg.board(board=board, size=400)
                                st.image(svg, width=800)
                                with st.container(border=True):
                                    st.write(f"{game.headers['White']} ({game.headers['WhiteElo']})")

                        with col3:
                            with st.container(border=True):
                                result = st.session_state.analysis[slider]
                                st.markdown("<div style='background-image: linear-gradient(to top right, #00f0ff, #0e6fff, #8f5bff); border-radius: 6px'><h3 style='text-align: center; padding: 10px; margin: 10px 10px 15px 34px; font-weight: 700;'>GAME REPORT</h3></div>", unsafe_allow_html=True)
                                st.markdown(f"- **Move**: `{result['move']}`")
                                st.markdown(f"- **Win Probability**: `{(result['score'] * 100):.2f}%`")
                                st.markdown(f"- **Best move**: `{result['best_move']}`")
                                st.markdown(
                                    f"- **Move Quality**: <span style='color:{result['color']}; font-weight:bold;'>{result['quality']}</span>",
                                    unsafe_allow_html=True
                                )
                                st.markdown(f"- **Expected Points Lost**: `{result['expected_points_lost']:.3f}`")



        except Exception as e:
            st.error(f"Error analyzing game: {str(e)}")

if __name__ == "__main__":
    main()
