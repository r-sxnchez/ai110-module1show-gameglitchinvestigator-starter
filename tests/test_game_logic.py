"""
Comprehensive edge-case tests for game logic functions in app.py.

Imports are done by mocking streamlit so we can test pure logic
without launching a Streamlit server.
"""
import sys
from unittest.mock import MagicMock

# Mock streamlit before importing app so module-level st.* calls don't fail.
# Several return values must be configured to avoid KeyError / unpack errors.
_st_mock = MagicMock()
_st_mock.sidebar.selectbox.return_value = "Normal"   # used as a dict key
_st_mock.columns.return_value = [MagicMock(), MagicMock()]  # col1, col2 = st.columns(2)
_st_mock.button.return_value = False          # don't trigger new-game branch
_st_mock.form_submit_button.return_value = False  # don't trigger submit branch
_st_mock.checkbox.return_value = False
sys.modules["streamlit"] = _st_mock

from app import get_range_for_difficulty, parse_guess, check_guess, update_score


# ─────────────────────────────────────────
# get_range_for_difficulty
# ─────────────────────────────────────────

class TestGetRangeForDifficulty:
    def test_easy(self):
        assert get_range_for_difficulty("Easy") == (1, 20)

    def test_normal(self):
        assert get_range_for_difficulty("Normal") == (1, 100)

    def test_hard(self):
        assert get_range_for_difficulty("Hard") == (1, 200)

    def test_unknown_difficulty_falls_back_to_normal_range(self):
        # Any unrecognised string should fall back to (1, 100)
        assert get_range_for_difficulty("Impossible") == (1, 100)

    def test_empty_string_falls_back(self):
        assert get_range_for_difficulty("") == (1, 100)

    def test_case_sensitive_easy(self):
        # "easy" (lowercase) is NOT "Easy" – should fall back
        assert get_range_for_difficulty("easy") == (1, 100)

    def test_case_sensitive_hard(self):
        assert get_range_for_difficulty("HARD") == (1, 100)

    def test_none_falls_back(self):
        # None is not a recognised difficulty
        assert get_range_for_difficulty(None) == (1, 100)  # type: ignore


# ─────────────────────────────────────────
# parse_guess
# ─────────────────────────────────────────

class TestParseGuess:
    # --- valid inputs ---
    def test_valid_integer_string(self):
        ok, value, err = parse_guess("42")
        assert ok is True
        assert value == 42
        assert err is None

    def test_valid_zero(self):
        ok, value, _ = parse_guess("0")
        assert ok is True
        assert value == 0

    def test_valid_negative(self):
        ok, value, _ = parse_guess("-5")
        assert ok is True
        assert value == -5

    def test_valid_large_number(self):
        ok, value, _ = parse_guess("999999")
        assert ok is True
        assert value == 999_999

    def test_float_string_truncates_to_int(self):
        # "3.9" should parse as 3, not round to 4
        ok, value, _ = parse_guess("3.9")
        assert ok is True
        assert value == 3  # truncation, not rounding

    def test_float_string_exactly_on_boundary(self):
        ok, value, _ = parse_guess("50.0")
        assert ok is True
        assert value == 50

    def test_negative_float_string(self):
        ok, value, _ = parse_guess("-2.7")
        assert ok is True
        assert value == -2

    # --- invalid / empty inputs ---
    def test_none_returns_error(self):
        ok, value, err = parse_guess(None)
        assert ok is False
        assert value is None
        assert err == "Enter a guess."

    def test_empty_string_returns_error(self):
        ok, value, err = parse_guess("")
        assert ok is False
        assert value is None
        assert err == "Enter a guess."

    def test_alphabetic_string_returns_error(self):
        ok, value, err = parse_guess("abc")
        assert ok is False
        assert value is None
        assert err == "That is not a number."

    def test_special_characters(self):
        ok, _, err = parse_guess("!@#")
        assert ok is False
        assert err == "That is not a number."

    def test_whitespace_only(self):
        # " " is not a number and not "" so should hit the except branch
        ok, _, err = parse_guess("  ")
        assert ok is False
        assert err == "That is not a number."

    def test_mixed_alphanumeric(self):
        ok, _, err = parse_guess("12abc")
        assert ok is False
        assert err == "That is not a number."

    def test_number_with_leading_whitespace(self):
        # Python int(" 5 ") works fine, so this should parse
        ok, value, _ = parse_guess(" 5 ")
        # int(" 5 ") == 5 in Python, so this is actually valid
        assert ok is True
        assert value == 5


# ─────────────────────────────────────────
# check_guess
# ─────────────────────────────────────────

class TestCheckGuess:
    # --- exact match ---
    def test_win(self):
        outcome, _ = check_guess(50, 50)
        assert outcome == "Win"

    def test_win_message(self):
        _, message = check_guess(50, 50)
        assert "Correct" in message

    def test_win_at_lower_bound(self):
        outcome, _ = check_guess(1, 1)
        assert outcome == "Win"

    def test_win_at_upper_bound(self):
        outcome, _ = check_guess(200, 200)
        assert outcome == "Win"


    # --- too high ---
    def test_too_high(self):
        outcome, _ = check_guess(60, 50)
        assert outcome == "Too High"

    def test_too_high_message(self):
        _, message = check_guess(60, 50)
        assert "LOWER" in message

    def test_one_above_secret(self):
        outcome, _ = check_guess(51, 50)
        assert outcome == "Too High"

    def test_far_above_secret(self):
        outcome, _ = check_guess(200, 1)
        assert outcome == "Too High"

    # --- too low ---
    def test_too_low(self):
        outcome, _ = check_guess(40, 50)
        assert outcome == "Too Low"

    def test_too_low_message(self):
        _, message = check_guess(40, 50)
        assert "HIGHER" in message

    def test_one_below_secret(self):
        outcome, _ = check_guess(49, 50)
        assert outcome == "Too Low"

    def test_far_below_secret(self):
        outcome, _ = check_guess(1, 200)
        assert outcome == "Too Low"

    # --- edge: negative numbers ---
    def test_negative_guess_equal(self):
        outcome, _ = check_guess(-10, -10)
        assert outcome == "Win"

    def test_negative_guess_too_low(self):
        outcome, _ = check_guess(-20, -10)
        assert outcome == "Too Low"

    def test_negative_guess_too_high(self):
        outcome, _ = check_guess(-5, -10)
        assert outcome == "Too High"

    # --- edge: zero ---
    def test_zero_equal(self):
        outcome, _ = check_guess(0, 0)
        assert outcome == "Win"

    def test_zero_vs_positive(self):
        outcome, _ = check_guess(0, 1)
        assert outcome == "Too Low"

    # --- BUG PROBE: TypeError fallback path ---
    def test_none_guess_does_not_silently_win(self):
        """
        If guess is None the TypeError branch fires.
        str(None) == "None"; "None" != any int secret, so it should NOT win.
        However the subsequent comparisons `"None" > secret` will raise another
        TypeError in Python 3 (can't compare str > int), so this tests that
        the function either raises or returns a non-Win outcome.
        """
        try:
            outcome, _ = check_guess(None, 50)
            assert outcome != "Win"
        except TypeError:
            pass  # acceptable – the fallback path is broken for None inputs


# ─────────────────────────────────────────
# update_score
# ─────────────────────────────────────────

class TestUpdateScore:
    # --- win scoring ---
    def test_win_attempt_1(self):
        # 100 - 10*1 = 90 points
        score = update_score(0, "Win", 1)
        assert score == 90

    def test_win_attempt_5(self):
        # 100 - 10*5 = 50 points
        score = update_score(0, "Win", 5)
        assert score == 50

    def test_win_attempt_9_floor(self):
        # 100 - 10*9 = 10 points (exactly at floor)
        score = update_score(0, "Win", 9)
        assert score == 10

    def test_win_attempt_10_hits_floor(self):
        # 100 - 10*10 = 0 → floored to 10
        score = update_score(0, "Win", 10)
        assert score == 10

    def test_win_attempt_100_still_gets_minimum(self):
        # Very late win still grants at least 10 points
        score = update_score(0, "Win", 100)
        assert score == 10

    def test_win_adds_to_existing_score(self):
        score = update_score(200, "Win", 1)
        assert score == 290  # 200 + 90

    # --- BUG PROBE: attempt 0 ---
    def test_win_attempt_0_gives_100_points(self):
        """
        Attempt 0 would give 100 - 0 = 100 points. In the UI attempts is
        incremented BEFORE this call, so attempt 0 should never occur in
        normal play – but worth documenting the behaviour.
        """
        score = update_score(0, "Win", 0)
        assert score == 100

    # --- wrong guess scoring ---
    def test_too_high_deducts_5(self):
        score = update_score(100, "Too High", 1)
        assert score == 95

    def test_too_low_deducts_5(self):
        score = update_score(100, "Too Low", 1)
        assert score == 95

    def test_score_can_go_negative(self):
        """
        There is no floor on wrong-guess deductions; repeated wrong guesses
        will push the score below zero.
        """
        score = update_score(0, "Too High", 1)
        assert score == -5  # no floor enforced

    def test_score_goes_very_negative(self):
        score = update_score(-100, "Too Low", 3)
        assert score == -105

    def test_unknown_outcome_no_change(self):
        score = update_score(50, "Unknown", 5)
        assert score == 50

    def test_empty_outcome_no_change(self):
        score = update_score(50, "", 5)
        assert score == 50

    # --- attempt_number does NOT affect wrong-guess deduction ---
    def test_too_high_deduction_same_regardless_of_attempt(self):
        assert update_score(100, "Too High", 1) == update_score(100, "Too High", 99)
