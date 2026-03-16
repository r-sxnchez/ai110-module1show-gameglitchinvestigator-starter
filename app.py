import random
import streamlit as st

from ui import (
    inject_css,
    render_sidebar_controls,
    render_sidebar_info,
    render_header,
    render_stats,
    render_progress,
    render_win_screen,
    render_loss_screen,
    render_input_card,
    render_feedback,
    render_history,
    render_debug,
    render_footer,
)


# ── Core game logic ───────────────────────────────────────────────────────────

def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def parse_guess(raw: str):
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        if guess > secret:
            return "Too High", "📉 Go LOWER!"
        else:
            return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * attempt_number
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


# ── App setup ─────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮", layout="centered")
inject_css()

# ── Sidebar (difficulty + hint toggle) ────────────────────────────────────────

attempt_limit_map = {"Easy": 6, "Normal": 8, "Hard": 5}

difficulty, show_hint = render_sidebar_controls()

attempt_limit = attempt_limit_map[difficulty]
low, high = get_range_for_difficulty(difficulty)

render_sidebar_info(low=low, high=high, attempt_limit=attempt_limit)

# ── Session state ─────────────────────────────────────────────────────────────

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# Stores the last guess result so it survives reruns and renders in the right place.
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None  # dict | None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _reset_game():
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.score = 0
    st.session_state.last_feedback = None


# ── Main layout ───────────────────────────────────────────────────────────────

render_header()
render_stats(st.session_state.score, st.session_state.attempts, attempt_limit, low, high)
render_progress(st.session_state.attempts, attempt_limit)

# ── Game-over screens (New Game button always reachable) ──────────────────────

if st.session_state.status == "won":
    render_win_screen(st.session_state.secret, st.session_state.score)
    if st.button("↺  NEW GAME", key="new_game_win"):
        _reset_game()
        st.rerun()
    st.stop()

if st.session_state.status == "lost":
    render_loss_screen(st.session_state.secret, st.session_state.score)
    if st.button("↺  NEW GAME", key="new_game_loss"):
        _reset_game()
        st.rerun()
    st.stop()

# ── Persistent feedback from last guess ──────────────────────────────────────

if st.session_state.last_feedback:
    fb = st.session_state.last_feedback
    render_feedback(fb["guess"], fb["message"], show_hint, fb["outcome"])

# ── Input card ────────────────────────────────────────────────────────────────

raw_guess, submit, new_game = render_input_card(difficulty, low, high)

# ── Button handlers ───────────────────────────────────────────────────────────

if new_game:
    _reset_game()
    st.rerun()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.session_state.last_feedback = None
        st.error(err)
        st.rerun()
    else:
        st.session_state.history.append(guess_int)

        outcome, message = check_guess(guess_int, st.session_state.secret)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        # Save feedback to session state so it renders above the input card
        # on the next rerun with the updated stats/progress bar.
        st.session_state.last_feedback = {
            "guess": guess_int,
            "message": message,
            "outcome": outcome,
        }

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"

        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"

        st.rerun()

# ── History + debug + footer ──────────────────────────────────────────────────

render_history(st.session_state.history, st.session_state.secret)
render_debug(
    st.session_state.secret,
    st.session_state.attempts,
    st.session_state.score,
    difficulty,
    st.session_state.history,
)
render_footer()
