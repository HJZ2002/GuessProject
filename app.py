import random
import streamlit as st

DIFFICULTY_PRESETS = {
    "Easy":   {"low": 1, "high": 50,  "max_chances": 8, "hints": 1},
    "Medium": {"low": 1, "high": 100, "max_chances": 7, "hints": 1},
    "Hard":   {"low": 1, "high": 500, "max_chances": 7, "hints": 0},
}


def init_session():
    defaults = {
        "screen":        "setup",
        "secret_number": 0,
        "chances_left":  0,
        "max_chances":   0,
        "hints_left":    0,
        "guess_count":   0,
        "range_low":     0,
        "range_high":    0,
        "log":           [],
        "player_won":    False,
        "session_score": 0,
        "session_wins":  0,
        "session_games": 0,
        "last_score":    0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_game(difficulty):
    preset = DIFFICULTY_PRESETS[difficulty]
    st.session_state.range_low    = preset["low"]
    st.session_state.range_high   = preset["high"]
    st.session_state.max_chances  = preset["max_chances"]
    st.session_state.chances_left = preset["max_chances"]
    st.session_state.hints_left   = preset["hints"]
    st.session_state.guess_count  = 0
    st.session_state.secret_number = random.randint(preset["low"], preset["high"])
    st.session_state.log = [
        ("system", f"Guess a number between {preset['low']} and {preset['high']}. "
                   f"You have {preset['max_chances']} chances.")
    ]
    st.session_state.screen = "game"


def submit_guess(guess):
    st.session_state.guess_count  += 1
    st.session_state.chances_left -= 1

    secret = st.session_state.secret_number

    if guess == secret:
        score = calculate_score(player_won=True)
        st.session_state.last_score     = score
        st.session_state.session_score += score
        st.session_state.session_wins  += 1
        st.session_state.session_games += 1
        st.session_state.player_won     = True
        st.session_state.log.append(
            ("correct", f"Correct! {secret} was the number. "
                        f"Guessed in {st.session_state.guess_count} attempt(s).")
        )
        st.session_state.screen = "result"
        return

    if st.session_state.chances_left == 0:
        st.session_state.last_score     = 0
        st.session_state.session_games += 1
        st.session_state.player_won     = False
        st.session_state.log.append(("high", f"Out of chances! The number was {secret}."))
        st.session_state.screen = "result"
        return

    direction = "too high" if guess > secret else "too low"
    tag       = "high"     if guess > secret else "low"
    st.session_state.log.append(
        (tag, f"{guess} is {direction}. {st.session_state.chances_left} chance(s) left.")
    )


def use_hint():
    if st.session_state.hints_left <= 0:
        st.session_state.log.append(("hint", "No hints remaining."))
        return

    st.session_state.hints_left -= 1
    secret  = st.session_state.secret_number
    low     = st.session_state.range_low
    high    = st.session_state.range_high
    midpoint = (low + high) // 2
    half     = f"{low}–{midpoint}" if secret <= midpoint else f"{midpoint + 1}–{high}"
    parity   = "even" if secret % 2 == 0 else "odd"
    st.session_state.log.append(("hint", f"Hint: the number is {parity} and in {half}."))


def calculate_score(player_won):
    if not player_won:
        return 0
    return max(10, round(100 * (st.session_state.chances_left + 1) / st.session_state.max_chances))


def get_hot_cold_label(guess):
    secret     = st.session_state.secret_number
    range_size = st.session_state.range_high - st.session_state.range_low
    proximity  = abs(guess - secret) / range_size

    if   proximity < 0.05: return "🔥 Burning hot!"
    elif proximity < 0.12: return "♨️ Very warm"
    elif proximity < 0.25: return "☀️ Warm"
    elif proximity < 0.45: return "💧 Cold"
    else:                  return "❄️ Freezing cold"


def render_log_tag_color(tag):
    return {"correct": "green", "high": "red", "low": "blue", "hint": "orange", "system": "gray"}.get(tag, "gray")


def render_setup_screen():
    st.title("🎯 Number Guessing Game")
    st.write("Select a difficulty and start guessing!")

    difficulty = st.radio(
        "Difficulty",
        options=list(DIFFICULTY_PRESETS.keys()),
        horizontal=True
    )

    preset = DIFFICULTY_PRESETS[difficulty]
    st.caption(f"Range: {preset['low']}–{preset['high']}  ·  {preset['max_chances']} chances  ·  {preset['hints']} hint(s)")

    if st.button("Start Game", use_container_width=True, type="primary"):
        start_game(difficulty)
        st.rerun()

    if st.session_state.session_games > 0:
        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Session Score", st.session_state.session_score)
        col2.metric("Wins",  st.session_state.session_wins)
        col3.metric("Games", st.session_state.session_games)


def render_game_screen():
    st.title("🎯 Number Guessing Game")

    col1, col2, col3 = st.columns(3)
    col1.metric("Chances Left", st.session_state.chances_left)
    col2.metric("Score",        st.session_state.session_score)
    col3.metric("Hints Left",   st.session_state.hints_left)

    progress = st.session_state.chances_left / st.session_state.max_chances
    st.progress(progress)

    st.divider()

    for tag, message in st.session_state.log:
        color = render_log_tag_color(tag)
        st.markdown(f":{color}[{message}]")

    st.divider()

    with st.form("guess_form", clear_on_submit=True):
        guess = st.number_input(
            "Your guess",
            min_value=st.session_state.range_low,
            max_value=st.session_state.range_high,
            step=1,
            label_visibility="collapsed"
        )
        col_guess, col_hint = st.columns([3, 1])

        with col_guess:
            guessed = st.form_submit_button("Guess", use_container_width=True, type="primary")
        with col_hint:
            hinted = st.form_submit_button("Hint", use_container_width=True)

    if guessed:
        hot_cold = get_hot_cold_label(int(guess))
        st.info(hot_cold)
        submit_guess(int(guess))
        st.rerun()

    if hinted:
        use_hint()
        st.rerun()


def render_result_screen():
    st.title("🎯 Number Guessing Game")

    if st.session_state.player_won:
        st.success(f"🎉 You got it! Guessed {st.session_state.secret_number} "
                   f"in {st.session_state.guess_count} attempt(s).")
    else:
        st.error(f"😔 Out of chances! The number was {st.session_state.secret_number}.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Points Earned",  f"+{st.session_state.last_score}")
    col2.metric("Session Score",  st.session_state.session_score)
    col3.metric("Win Rate",
                f"{round(st.session_state.session_wins / st.session_state.session_games * 100)}%")

    st.divider()

    for tag, message in st.session_state.log:
        color = render_log_tag_color(tag)
        st.markdown(f":{color}[{message}]")

    st.divider()

    if st.button("Play Again", use_container_width=True, type="primary"):
        st.session_state.screen = "setup"
        st.rerun()


def main():
    st.set_page_config(page_title="Number Guessing Game", page_icon="🎯", layout="centered")
    init_session()

    screens = {
        "setup":  render_setup_screen,
        "game":   render_game_screen,
        "result": render_result_screen,
    }
    screens[st.session_state.screen]()


main()
