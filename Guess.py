import random
import os
os.environ['TCL_LIBRARY'] = r'C:\Users\zacca\AppData\Local\Programs\Python\Python313\tcl\tcl8.6'
os.environ['TK_LIBRARY']  = r'C:\Users\zacca\AppData\Local\Programs\Python\Python313\tcl\tk8.6'
import tkinter as tk

DIFFICULTY_PRESETS = {
    "Easy":   {"low": 1, "high": 50,  "max_chances": 8,  "hints": 1},
    "Medium": {"low": 1, "high": 100, "max_chances": 7,  "hints": 1},
    "Hard":   {"low": 1, "high": 500, "max_chances": 7,  "hints": 0},
}

COLOR = {
    "bg":         "#0f0f0f",
    "surface":    "#1a1a1a",
    "border":     "#2e2e2e",
    "accent":     "#e8ff47",
    "text":       "#f0f0f0",
    "muted":      "#888888",
    "success":    "#4ade80",
    "danger":     "#f87171",
    "warn":       "#facc15",
    "info":       "#60a5fa",
}


class GuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.configure(bg=COLOR["bg"])
        self.root.resizable(False, False)

        self.secret_number = 0
        self.chances_left = 0
        self.max_chances = 0
        self.hints_left = 0
        self.guess_count = 0
        self.range_low = 0
        self.range_high = 0
        self.session_score = 0
        self.session_wins = 0
        self.session_games = 0

        self.selected_difficulty = tk.StringVar(value="Medium")

        self.build_ui()
        self.show_setup_screen()

    def build_ui(self):
        self.root.geometry("480x620")

        self.header_label = tk.Label(
            self.root, text="GUESS THE NUMBER",
            bg=COLOR["bg"], fg=COLOR["accent"],
            font=("Courier", 18, "bold"), pady=20
        )
        self.header_label.pack()

        self.setup_frame = tk.Frame(self.root, bg=COLOR["bg"])
        self.game_frame  = tk.Frame(self.root, bg=COLOR["bg"])
        self.result_frame = tk.Frame(self.root, bg=COLOR["bg"])

        self.build_setup_frame()
        self.build_game_frame()
        self.build_result_frame()

    def build_setup_frame(self):
        tk.Label(
            self.setup_frame, text="Select difficulty",
            bg=COLOR["bg"], fg=COLOR["muted"], font=("Courier", 11)
        ).pack(pady=(0, 12))

        for name in DIFFICULTY_PRESETS:
            self.create_difficulty_button(name)

        self.start_button = tk.Button(
            self.setup_frame, text="START GAME",
            bg=COLOR["accent"], fg=COLOR["bg"],
            font=("Courier", 12, "bold"),
            relief="flat", cursor="hand2",
            padx=30, pady=10,
            command=self.start_game
        )
        self.start_button.pack(pady=24)

        self.session_label = tk.Label(
            self.setup_frame, text="",
            bg=COLOR["bg"], fg=COLOR["muted"], font=("Courier", 10)
        )
        self.session_label.pack()

    def create_difficulty_button(self, name):
        preset = DIFFICULTY_PRESETS[name]
        desc = f"1–{preset['high']}  ·  {preset['max_chances']} chances"

        btn = tk.Radiobutton(
            self.setup_frame, text=f"  {name}   {desc}",
            variable=self.selected_difficulty, value=name,
            bg=COLOR["surface"], fg=COLOR["text"],
            selectcolor=COLOR["surface"],
            activebackground=COLOR["surface"],
            activeforeground=COLOR["accent"],
            font=("Courier", 11),
            indicatoron=False,
            relief="flat", cursor="hand2",
            padx=16, pady=10,
            width=34,
        )
        btn.pack(pady=4)

    def build_game_frame(self):
        stats_row = tk.Frame(self.game_frame, bg=COLOR["bg"])
        stats_row.pack(fill="x", padx=20, pady=(0, 12))

        self.chances_stat = self.create_stat_card(stats_row, "CHANCES", "—")
        self.score_stat   = self.create_stat_card(stats_row, "SCORE",   "0")
        self.hints_stat   = self.create_stat_card(stats_row, "HINTS",   "—")

        self.progress_canvas = tk.Canvas(
            self.game_frame, height=6,
            bg=COLOR["border"], highlightthickness=0
        )
        self.progress_canvas.pack(fill="x", padx=20, pady=(0, 12))

        self.hot_cold_label = tk.Label(
            self.game_frame, text="",
            bg=COLOR["bg"], fg=COLOR["warn"], font=("Courier", 11)
        )
        self.hot_cold_label.pack()

        self.log_frame = tk.Frame(
            self.game_frame, bg=COLOR["surface"],
            highlightbackground=COLOR["border"], highlightthickness=1
        )
        self.log_frame.pack(fill="both", expand=True, padx=20, pady=(6, 12))

        self.log_text = tk.Text(
            self.log_frame, height=10, width=44,
            bg=COLOR["surface"], fg=COLOR["text"],
            font=("Courier", 10), relief="flat",
            state="disabled", wrap="word",
            padx=10, pady=8, cursor="arrow"
        )
        self.log_text.pack(fill="both", expand=True)

        self.log_text.tag_config("correct", foreground=COLOR["success"])
        self.log_text.tag_config("high",    foreground=COLOR["danger"])
        self.log_text.tag_config("low",     foreground=COLOR["info"])
        self.log_text.tag_config("hint",    foreground=COLOR["warn"])
        self.log_text.tag_config("system",  foreground=COLOR["muted"])

        input_row = tk.Frame(self.game_frame, bg=COLOR["bg"])
        input_row.pack(padx=20, fill="x", pady=(0, 16))

        self.guess_entry = tk.Entry(
            input_row,
            bg=COLOR["surface"], fg=COLOR["accent"],
            insertbackground=COLOR["accent"],
            font=("Courier", 16, "bold"),
            relief="flat", justify="center",
            highlightbackground=COLOR["border"],
            highlightthickness=1, width=10
        )
        self.guess_entry.pack(side="left", ipady=8, padx=(0, 8))
        self.guess_entry.bind("<Return>", lambda e: self.submit_guess())

        self.guess_button = tk.Button(
            input_row, text="GUESS",
            bg=COLOR["accent"], fg=COLOR["bg"],
            font=("Courier", 11, "bold"),
            relief="flat", cursor="hand2",
            padx=14, pady=8,
            command=self.submit_guess
        )
        self.guess_button.pack(side="left", padx=(0, 8))

        self.hint_button = tk.Button(
            input_row, text="HINT",
            bg=COLOR["surface"], fg=COLOR["warn"],
            font=("Courier", 11),
            relief="flat", cursor="hand2",
            padx=14, pady=8,
            command=self.use_hint
        )
        self.hint_button.pack(side="left")

    def create_stat_card(self, parent, label_text, initial_value):
        card = tk.Frame(parent, bg=COLOR["surface"], padx=14, pady=10)
        card.pack(side="left", expand=True, fill="x", padx=4)

        value_label = tk.Label(
            card, text=initial_value,
            bg=COLOR["surface"], fg=COLOR["text"],
            font=("Courier", 20, "bold")
        )
        value_label.pack()

        tk.Label(
            card, text=label_text,
            bg=COLOR["surface"], fg=COLOR["muted"],
            font=("Courier", 9)
        ).pack()

        return value_label

    def build_result_frame(self):
        self.result_icon  = tk.Label(self.result_frame, text="", bg=COLOR["bg"], font=("Courier", 40))
        self.result_title = tk.Label(self.result_frame, text="", bg=COLOR["bg"], fg=COLOR["text"],   font=("Courier", 18, "bold"))
        self.result_sub   = tk.Label(self.result_frame, text="", bg=COLOR["bg"], fg=COLOR["muted"],  font=("Courier", 11))
        self.result_score = tk.Label(self.result_frame, text="", bg=COLOR["bg"], fg=COLOR["accent"], font=("Courier", 24, "bold"))
        self.result_hist  = tk.Label(self.result_frame, text="", bg=COLOR["bg"], fg=COLOR["muted"],  font=("Courier", 10))

        for widget in (self.result_icon, self.result_title, self.result_sub,
                       self.result_score, self.result_hist):
            widget.pack(pady=4)

        tk.Button(
            self.result_frame, text="PLAY AGAIN",
            bg=COLOR["accent"], fg=COLOR["bg"],
            font=("Courier", 12, "bold"),
            relief="flat", cursor="hand2",
            padx=30, pady=10,
            command=self.show_setup_screen
        ).pack(pady=20)


    def show_setup_screen(self):
        self.game_frame.pack_forget()
        self.result_frame.pack_forget()
        self.update_session_label()
        self.setup_frame.pack(fill="both", expand=True)

    def show_game_screen(self):
        self.setup_frame.pack_forget()
        self.result_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        self.guess_entry.focus_set()

    def show_result_screen(self, player_won):
        self.game_frame.pack_forget()
        self.setup_frame.pack_forget()
        self.populate_result_screen(player_won)
        self.result_frame.pack(fill="both", expand=True)

    def start_game(self):
        preset = DIFFICULTY_PRESETS[self.selected_difficulty.get()]
        self.range_low    = preset["low"]
        self.range_high   = preset["high"]
        self.max_chances  = preset["max_chances"]
        self.hints_left   = preset["hints"]
        self.chances_left = self.max_chances
        self.guess_count  = 0
        self.secret_number = random.randint(self.range_low, self.range_high)

        self.clear_log()
        self.hot_cold_label.config(text="")
        self.update_stats_display()
        self.draw_progress_bar()

        self.log(f"Guess a number between {self.range_low} and {self.range_high}.", "system")
        self.show_game_screen()

    def submit_guess(self):
        raw = self.guess_entry.get().strip()
        self.guess_entry.delete(0, "end")

        if not self.is_valid_integer(raw):
            self.log("Enter a valid number.", "hint")
            return

        guess = int(raw)
        self.guess_count += 1
        self.chances_left -= 1

        self.update_hot_cold_label(guess)

        if guess == self.secret_number:
            self.log(f"Correct! {self.secret_number} was the number. Guessed in {self.guess_count} attempt(s).", "correct")
            self.finish_game(player_won=True)
            return

        if self.chances_left == 0:
            self.log(f"Out of chances! The number was {self.secret_number}.", "high")
            self.finish_game(player_won=False)
            return

        direction = "too high" if guess > self.secret_number else "too low"
        tag       = "high"     if guess > self.secret_number else "low"
        self.log(f"{guess} is {direction}. {self.chances_left} chance(s) left.", tag)

        self.update_stats_display()
        self.draw_progress_bar()

    def use_hint(self):
        if self.hints_left <= 0:
            self.log("No hints remaining.", "hint")
            return

        self.hints_left -= 1
        midpoint = (self.range_low + self.range_high) // 2
        half_range = f"{self.range_low}–{midpoint}" if self.secret_number <= midpoint else f"{midpoint + 1}–{self.range_high}"
        parity = "even" if self.secret_number % 2 == 0 else "odd"

        self.log(f"Hint: the number is {parity} and in {half_range}.", "hint")
        self.update_stats_display()

    def finish_game(self, player_won):
        earned_score = self.calculate_score(player_won)
        self.session_score += earned_score
        self.session_games += 1
        if player_won:
            self.session_wins += 1

        self.update_stats_display()
        self.show_result_screen(player_won)

    def calculate_score(self, player_won):
        if not player_won:
            return 0
        return max(10, round(100 * (self.chances_left + 1) / self.max_chances))

    def populate_result_screen(self, player_won):
        last_score = self.calculate_score(player_won) if player_won else 0

        self.result_icon.config(text="🎉" if player_won else "😔")
        self.result_title.config(text="You got it!" if player_won else "Better luck next time!")
        self.result_sub.config(
            text=f"Guessed {self.secret_number} in {self.guess_count} attempt(s)."
                 if player_won else f"The number was {self.secret_number}."
        )
        self.result_score.config(text=f"+{last_score} pts" if player_won else "+0 pts")
        self.result_hist.config(
            text=f"Session: {self.session_score} pts  ·  {self.session_wins}/{self.session_games} wins"
        )

    def update_stats_display(self):
        self.chances_stat.config(text=str(self.chances_left))
        self.score_stat.config(text=str(self.session_score))
        self.hints_stat.config(text=str(self.hints_left))

    def draw_progress_bar(self):
        self.progress_canvas.update_idletasks()
        total_width = self.progress_canvas.winfo_width()
        fill_ratio  = self.chances_left / self.max_chances
        fill_width  = int(total_width * fill_ratio)

        bar_color = (
            COLOR["success"] if fill_ratio > 0.6 else
            COLOR["warn"]    if fill_ratio > 0.3 else
            COLOR["danger"]
        )

        self.progress_canvas.delete("all")
        self.progress_canvas.create_rectangle(0, 0, fill_width, 6, fill=bar_color, outline="")

    def update_hot_cold_label(self, guess):
        distance = abs(guess - self.secret_number)
        range_size = self.range_high - self.range_low
        proximity  = distance / range_size

        if   proximity < 0.05: label, color = "🔥 Burning hot!",  COLOR["danger"]
        elif proximity < 0.12: label, color = "♨️ Very warm",     COLOR["warn"]
        elif proximity < 0.25: label, color = "☀️ Warm",          COLOR["warn"]
        elif proximity < 0.45: label, color = "💧 Cold",          COLOR["info"]
        else:                  label, color = "❄️ Freezing cold", COLOR["info"]

        self.hot_cold_label.config(text=label, fg=color)

    def update_session_label(self):
        if self.session_games == 0:
            self.session_label.config(text="")
            return
        self.session_label.config(
            text=f"Session: {self.session_score} pts  ·  {self.session_wins}/{self.session_games} wins"
        )

    def log(self, message, tag="system"):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"  {message}\n", tag)
        self.log_text.config(state="disabled")
        self.log_text.see("end")

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    @staticmethod
    def is_valid_integer(value):
        return value.lstrip("-").isdigit()


def main():
    root = tk.Tk()
    GuessingGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()