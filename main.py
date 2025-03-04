import streamlit as st
import chess
import chess.pgn
import chess.engine
import chess.svg
from io import StringIO
import random
import pathlib
import pandas as pd
import altair as alt

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_title="Chesalyser",
    page_icon="logos/small.png",
)


def classify_move(score_change, is_capture=False, moved_piece=None):
    if is_capture:
        if score_change < 30:
            return "Best Move", "green"
        elif 30 <= score_change < 80:
            return "Good Move", "blue"
        elif 80 <= score_change < 180:
            return "Inaccuracy", "yellow"
        elif 180 <= score_change < 350:
            return "Mistake", "orange"
        else:
            return "Blunder", "red"

    elif moved_piece == chess.QUEEN:
        if score_change < 40:
            return "Best Move", "green"
        elif 40 <= score_change < 100:
            return "Good Move", "blue"
        elif 100 <= score_change < 200:
            return "Inaccuracy", "yellow"
        elif 200 <= score_change < 400:
            return "Mistake", "orange"
        else:
            return "Blunder", "red"

    else:
        if score_change < 20:
            return "Best Move", "green"
        elif 20 <= score_change < 70:
            return "Good Move", "blue"
        elif 70 <= score_change < 150:
            return "Inaccuracy", "yellow"
        elif 150 <= score_change < 300:
            return "Mistake", "orange"
        else:
            return "Blunder", "red"

def analyze_game(game, engine_path, depth):
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    analysis_results = []
    board = game.board()

    previous_eval = None

    for move_index, move in enumerate(game.mainline_moves()):
        is_capture = board.is_capture(move)

        from_square = move.from_square
        moved_piece = board.piece_type_at(from_square)

        current_position = board.copy()

        board.push(move)

        side_to_move = not board.turn

        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        current_eval = info["score"].white().score(mate_score=10000)

        if previous_eval is None:
            score_change = 0
        else:
            if side_to_move:  # White just moved
                score_change = previous_eval - current_eval
            else:  # Black just moved
                score_change = current_eval - previous_eval

            score_change = abs(score_change)

        previous_eval = current_eval

        win_probability = 1 / (1 + 10 ** (-current_eval / 400))

        move_quality, color = classify_move(score_change, is_capture, moved_piece)

        best_move_info = engine.analyse(current_position, chess.engine.Limit(depth=depth))
        best_move = best_move_info.get("pv", [None])[0]

        analysis_results.append({
            "move": move.uci(),
            "score": round(win_probability, 3),
            "centipawn_eval": current_eval,
            "best_move": best_move.uci() if best_move else "None",
            "score_change": round(score_change, 1),
            "quality": move_quality,
            "color": color,
            "is_capture": is_capture,
            "piece_moved": chess.piece_name(moved_piece) if moved_piece else "None",
        })

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
        st.markdown(
            "<div style='background-image: linear-gradient(to top right, #00f0ff, #0e6fff, #8f5bff); border-radius: 8px'><h1 style='text-align: center; padding: 10px; margin: 0px 0px 15px 0px; font-weight: 700;'>⚙ SETTINGS</h1></div>",
            unsafe_allow_html=True,
        )

        engine_path = "stockfish/stockfish-ubuntu-x86-64-sse41-popcnt"

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
                30: "Stockfish mode",
            }
            depth = st.selectbox(
                ":material/settings: Select Analysis Depth:",
                options=list(depth_options.keys()),
                format_func=lambda x: depth_options[x],
            )

    if pgn_file or pgn_text:
        try:
            pgn = StringIO(pgn_text if pgn_text else pgn_file.getvalue().decode())
            game = chess.pgn.read_game(pgn)

            if game is None:
                st.error("Invalid PGN file or text. Please check the format.")
                return

            with st.sidebar:
                if st.button(
                    ":material/neurology: ANALYZE GAME",
                    use_container_width=True,
                    key="agame",
                ):
                    messages = [
                        "Thinking like Magnus Carlsen...",
                        "Calculating the best blunder... just kidding!",
                        "Running Stockfish at full speed!",
                        "Searching for the brilliancy move!",
                        "Did you just play a Bongcloud opening? Let's see...",
                        "Analyzing faster than Hikaru can pre-move!",
                        "Determining if this was a 200 IQ move or a disaster...",
                        "Checking if this game belongs in the Hall of Fame or Shame!",
                    ]
                    with st.spinner(random.choice(messages)):
                        st.session_state.analysis = analyze_game(
                            game, engine_path, depth
                        )
                        st.session_state.num_moves = len(st.session_state.analysis)

            if "analysis" in st.session_state:
                with st.container(border=True):
                    slider = (
                        st.slider(
                            "Move Number",
                            1,
                            st.session_state.num_moves,
                            1,
                            label_visibility="collapsed",
                        )
                        - 1
                    )
                board = game.board()
                for i in range(slider + 1):
                    board.push(
                        chess.Move.from_uci(st.session_state.analysis[i]["move"])
                    )

                with st.container(border=True):
                    col2, col3 = st.columns(2, vertical_alignment="center", gap="small")

                    with col2:
                        with st.container(border=True):
                            with st.container(border=True):
                                st.write(
                                    f"{game.headers['Black']} ({game.headers['BlackElo']})"
                                )
                            svg = chess.svg.board(board=board, size=400)
                            st.image(svg, width=800)
                            with st.container(border=True):
                                st.write(
                                    f"{game.headers['White']} ({game.headers['WhiteElo']})"
                                )

                    with col3:
                        with st.container(border=True):
                            result = st.session_state.analysis[slider]
                            st.markdown(
                                "<div style='background-image: linear-gradient(to top right, #00f0ff, #0e6fff, #8f5bff); border-radius: 6px'><h3 style='text-align: center; padding: 10px; margin: 10px 10px 15px 34px; font-weight: 700;'>GAME REPORT</h3></div>",
                                unsafe_allow_html=True,
                            )
                            st.markdown(f"- **Move**: `{result['move']}`")
                            st.markdown(
                                f"- **Win Probability**: `{(result['score'] * 100):.2f}%`"
                            )
                            st.markdown(f"- **Best move**: `{result['best_move']}`")
                            st.markdown(
                                f"- **Move Quality**: <span style='color:{result['color']}; font-weight:bold;'>{result['quality']}</span>",
                                unsafe_allow_html=True,
                            )
                            # st.markdown(f"- **Expected Points Lost**: `{result['expected_points_lost']:.3f}`")
                            with st.container(border=True):
                                # Win Probability Chart with Brush Selection
                                win_prob_data = pd.DataFrame(
                                    {
                                        "Move Number": range(
                                            1, len(st.session_state.analysis) + 1
                                        ),
                                        "Win Probability": [
                                            x["score"]
                                            for x in st.session_state.analysis
                                        ],
                                    }
                                )

                                brush = alt.selection_interval(encodings=["x"])

                                win_prob_chart = (
                                    alt.Chart(win_prob_data)
                                    .mark_line()
                                    .encode(
                                        x=alt.X("Move Number:Q", title="Move Number"),
                                        y=alt.Y(
                                            "Win Probability:Q", title="Win Probability"
                                        ),  # Removed format="%"`
                                        tooltip=["Move Number", "Win Probability"],
                                    )
                                    .properties(
                                        title="Win Probability of White Over Time"
                                    )
                                    .add_selection(brush)
                                )

                                st.altair_chart(
                                    win_prob_chart, use_container_width=True
                                )

        except Exception as e:
            st.error(f"Error analyzing game: {str(e)}")

        with st.sidebar:
            st.markdown("###### :gray[Powered by [Stockfish](https://stockfishchess.org/)]")


if __name__ == "__main__":
    main()
