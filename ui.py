"""
ui.py — All UI rendering functions for Glitchy Guesser.

Each function is responsible for one visual section of the app.
app.py calls these functions in order; no game logic lives here.
"""

from pathlib import Path
import streamlit as st


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mono(text: str, color: str = "#64748b", size: str = "0.78rem") -> str:
    """Return an inline-styled monospace span."""
    return (
        f"<span style='font-family:JetBrains Mono,monospace;"
        f"font-size:{size};color:{color}'>{text}</span>"
    )


def _label(text: str) -> str:
    return f"<div class='fb-label'>{text}</div>"


def _value(text: str) -> str:
    return f"<div class='fb-value'>{text}</div>"


# ── CSS ───────────────────────────────────────────────────────────────────────

def inject_css() -> None:
    """Read styles.css and inject it into the Streamlit page."""
    css_path = Path(__file__).parent / "styles.css"
    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar_controls() -> tuple[str, bool]:
    """
    Render the difficulty selector and hint toggle.
    Call this first to get `difficulty`, then compute range/limit,
    then call render_sidebar_info() with the computed values.

    Returns:
        difficulty (str): selected difficulty level
        show_hint (bool): whether directional hints are enabled
    """
    st.sidebar.markdown(
        "<h2 style='font-family:Orbitron,sans-serif;font-size:1rem;"
        "letter-spacing:0.12em;color:#e2e8f0;margin-bottom:0.5rem'>⚙ SETTINGS</h2>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        "<hr style='border-color:#2a2a4a;margin:0.4rem 0 0.8rem'>",
        unsafe_allow_html=True,
    )

    difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Normal", "Hard"], index=1)

    try:
        show_hint = st.sidebar.toggle("Show directional hints", value=True)
    except AttributeError:
        show_hint = st.sidebar.checkbox("Show directional hints", value=True)

    return difficulty, show_hint


def render_sidebar_info(low: int, high: int, attempt_limit: int) -> None:
    """Render the range/attempts info card in the sidebar."""
    st.sidebar.markdown(
        f"""
        <div class="game-card" style="margin-top:0.8rem">
          {_label("Range")}
          <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;
                      color:#00d4aa;font-weight:600;margin-bottom:0.8rem">
            {low} &rarr; {high}
          </div>
          {_label("Max Attempts")}
          <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;
                      color:#00d4aa;font-weight:600">
            {attempt_limit}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Header ────────────────────────────────────────────────────────────────────

def render_header() -> None:
    """Render the hero title card."""
    st.markdown(
        """
        <div class="game-card" style="text-align:center;border-color:#00d4aa40;margin-bottom:1.2rem">
          <h1>GLITCHY GUESSER</h1>
          <p style="color:#64748b;font-family:'JetBrains Mono',monospace;
                     font-size:0.82rem;margin:0.4rem 0 0">
            Something is off. Find the number.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Stats row ─────────────────────────────────────────────────────────────────

def render_stats(score: int, attempts: int, attempt_limit: int, low: int, high: int) -> None:
    """Render the three metric cards (score / attempts / range)."""
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("SCORE", score)
    with c2:
        st.metric("ATTEMPTS", f"{attempts} / {attempt_limit}")
    with c3:
        st.metric("RANGE", f"{low} – {high}")


# ── Progress bar ──────────────────────────────────────────────────────────────

def render_progress(attempts: int, attempt_limit: int) -> None:
    """Render the attempts-used progress bar."""
    st.progress(min(attempts / attempt_limit, 1.0))
    remaining = attempt_limit - attempts
    st.markdown(
        f"<p style='font-family:JetBrains Mono,monospace;font-size:0.7rem;"
        f"color:#64748b;text-align:right;margin-top:-0.5rem'>"
        f"{remaining} attempt(s) remaining</p>",
        unsafe_allow_html=True,
    )


# ── Game-over screens ─────────────────────────────────────────────────────────

def render_win_screen(secret: int, score: int) -> None:
    """Render the win banner."""
    st.markdown(
        f"""
        <div class="fb-win">
          {_label("You cracked it!")}
          {_value("YOU WIN 🎉")}
          <p style="color:#64748b;font-family:'JetBrains Mono',monospace;
                    font-size:0.78rem;margin:0.4rem 0 0">
            The number was
            <strong style="color:#00d4aa">{secret}</strong>
            &nbsp;·&nbsp; Final score:
            <strong style="color:#00d4aa">{score}</strong>
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_loss_screen(secret: int, score: int) -> None:
    """Render the game-over banner."""
    st.markdown(
        f"""
        <div class="fb-loss">
          {_label("Out of attempts")}
          {_value("GAME OVER 💀")}
          <p style="color:#64748b;font-family:'JetBrains Mono',monospace;
                    font-size:0.78rem;margin:0.4rem 0 0">
            The number was
            <strong style="color:#ef4444">{secret}</strong>
            &nbsp;·&nbsp; Score:
            <strong style="color:#ef4444">{score}</strong>
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Input card ────────────────────────────────────────────────────────────────

def render_input_card(difficulty: str, low: int, high: int) -> tuple[str, bool, bool]:
    """
    Render the guess form and New Game button inside a card.

    Returns:
        raw_guess (str): the text the user typed
        submit (bool): True if the Submit button was clicked
        new_game (bool): True if the New Game button was clicked
    """
    st.markdown('<div class="game-card">', unsafe_allow_html=True)

    st.markdown(
        "<h3 style='font-size:0.85rem;letter-spacing:0.14em;"
        "color:#64748b;margin:0 0 0.8rem'>MAKE YOUR GUESS</h3>",
        unsafe_allow_html=True,
    )

    with st.form("guess_form"):
        raw_guess = st.text_input(
            "Enter your guess:",
            key=f"guess_input_{difficulty}",
            placeholder=f"Any number from {low} to {high}…",
        )
        submit = st.form_submit_button("SUBMIT GUESS →")

    btn_col, _ = st.columns([1, 2])
    with btn_col:
        new_game = st.button("↺  NEW GAME")

    st.markdown("</div>", unsafe_allow_html=True)

    return raw_guess, submit, new_game


# ── Guess feedback ────────────────────────────────────────────────────────────

def render_feedback(guess_int: int, message: str, show_hint: bool, outcome: str) -> None:
    """Render the 'you guessed X' label and optional directional hint card."""
    st.markdown(
        f"<p style='font-family:JetBrains Mono,monospace;font-size:0.78rem;"
        f"color:#64748b;margin-bottom:0.3rem'>"
        f"YOU GUESSED &nbsp;<strong style='color:#e2e8f0'>{guess_int}</strong></p>",
        unsafe_allow_html=True,
    )

    if show_hint and outcome != "Win":
        st.markdown(
            f"""
            <div class="fb-hint">
              <span style="font-family:'JetBrains Mono',monospace;
                           color:#f59e0b;font-size:0.95rem;font-weight:600">
                {message}
              </span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Guess history ─────────────────────────────────────────────────────────────

def render_history(history: list, secret: int) -> None:
    """Render color-coded guess history pills."""
    if not history:
        return

    st.markdown(
        "<p style='font-family:JetBrains Mono,monospace;font-size:0.72rem;"
        "letter-spacing:0.1em;color:#64748b;text-transform:uppercase;"
        "margin:0.6rem 0 0.3rem'>Guess History</p>",
        unsafe_allow_html=True,
    )

    pills_html = '<div class="pill-row">'
    for g in history:
        if g == secret:
            css = "win"
        elif isinstance(g, int) and g > secret:
            css = "high"
        elif isinstance(g, int) and g < secret:
            css = "low"
        else:
            css = ""
        pills_html += f'<span class="guess-pill {css}">{g}</span>'
    pills_html += "</div>"

    st.markdown(pills_html, unsafe_allow_html=True)


# ── Debug expander ────────────────────────────────────────────────────────────

def render_debug(secret: int, attempts: int, score: int, difficulty: str, history: list) -> None:
    """Render the collapsible debug info expander."""
    with st.expander("Debug Info"):
        st.write("Secret:", secret)
        st.write("Attempts:", attempts)
        st.write("Score:", score)
        st.write("Difficulty:", difficulty)
        st.write("History:", history)


# ── Footer ────────────────────────────────────────────────────────────────────

def render_footer() -> None:
    """Render the bottom footer line."""
    st.markdown(
        """
        <div style="text-align:center;color:#2a2a4a;font-family:'JetBrains Mono',monospace;
                    font-size:0.7rem;letter-spacing:0.12em;padding:2rem 0 1rem">
          BUILT BY AN AI THAT CLAIMS THIS CODE IS PRODUCTION-READY
        </div>
        """,
        unsafe_allow_html=True,
    )
