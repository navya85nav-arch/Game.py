
import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
import time
import datetime

# Optional music support
try:
    import pygame
    pygame.mixer.init()
    MUSIC_AVAILABLE = True
except Exception:
    MUSIC_AVAILABLE = False

# ================= CONFIGURATION =================

root = tk.Tk()
root.title("NEON BRAIN PUZZLE")
root.geometry("1150x780")
root.minsize(950, 680)

FONT = "Segoe UI"

THEMES = {
    "Neon Purple": "#15102D",
    "Ocean Blue": "#071D35",
    "Cyber Pink": "#2B1028",
    "Emerald": "#09271F",
    "Dark Galaxy": "#111323"
}

BG = THEMES["Neon Purple"]
CARD = "#211C40"
CYAN = "#00F5FF"
PINK = "#FF4FD8"
PURPLE = "#A970FF"
GREEN = "#47F59A"
YELLOW = "#FFE66D"
WHITE = "#FFFFFF"
MUTED = "#B8B6D9"

LEADERBOARD_FILE = "puzzle_scores.json"

score = 0
computer_score = 0
player1_score = 0
player2_score = 0
mistakes = 0
round_number = 0

player_name = "Player 1"
second_player = "Player 2"

game_mode = "Single Player"
difficulty = "Beginner"
category = "Random"
game_type = "Practice Mode"

current_player = 1
current_answer = ""
current_question = ""
time_left = 60
game_active = False
music_on = False
selected = None

# ================= DATA =================

def load_scores():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as file:
                return json.load(file)
        except:
            return []
    return []

leaderboard = load_scores()

def save_scores():
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file, indent=4)

def record_score(name, points):
    leaderboard.append({
        "name": name,
        "score": points,
        "date": datetime.date.today().isoformat()
    })

    leaderboard.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    del leaderboard[10:]
    save_scores()

# ================= PUZZLE GENERATOR =================

def generate_puzzle(cat, level, rng=None):
    rng = rng or random.Random()

    levels = {
        "Beginner": (5, 15),
        "Easy": (10, 30),
        "Medium": (20, 60),
        "Hard": (40, 100),
        "Expert": (70, 200)
    }

    low, high = levels[level]

    if cat == "Random":
        cat = rng.choice([
            "Math",
            "Number Pattern",
            "Word Scramble",
            "Logic"
        ])

    # MATH PUZZLE
    if cat == "Math":
        a = rng.randint(low, high)
        b = rng.randint(low, high)
        operation = rng.choice(["+", "-", "*"])

        if operation == "+":
            answer = a + b
        elif operation == "-":
            answer = a - b
        else:
            a = rng.randint(2, max(3, high // 3))
            b = rng.randint(2, 12)
            answer = a * b

        question = f"Solve: {a} {operation} {b} = ?"

    # NUMBER PATTERN
    elif cat == "Number Pattern":
        start = rng.randint(low, high)
        step = rng.randint(2, 10)

        sequence = [
            start + i * step for i in range(5)
        ]

        answer = start + 5 * step
        question = (
            "Find the missing number:\n"
            + "   ".join(map(str, sequence))
            + "   ?"
        )

    # WORD SCRAMBLE
    elif cat == "Word Scramble":
        words = [
            "PYTHON", "PUZZLE", "PLANET",
            "GALAXY", "CODING", "RAINBOW",
            "FLOWER", "COMPUTER", "SCIENCE",
            "JOURNEY", "DIAMOND", "ELEPHANT"
        ]

        word = rng.choice(words)
        scrambled = list(word)

        while True:
            rng.shuffle(scrambled)
            if "".join(scrambled) != word:
                break

        question = (
            "Unscramble this word:\n\n"
            + "   ".join(scrambled)
        )
        answer = word

    # LOGIC PUZZLE
    else:
        puzzles = [
            ("I have hands but cannot clap. What am I?", "CLOCK"),
            ("What has keys but no locks?", "PIANO"),
            ("What gets wetter as it dries?", "TOWEL"),
            ("What has a neck but no head?", "BOTTLE"),
            ("What has one eye but cannot see?", "NEEDLE"),
            ("What has many teeth but cannot bite?", "COMB")
        ]

        question, answer = rng.choice(puzzles)

    return question, str(answer).upper(), cat


# ================= MAIN BACKGROUND =================

root.configure(bg=BG)

canvas = tk.Canvas(
    root,
    bg=BG,
    highlightthickness=0
)
canvas.place(relwidth=1, relheight=1)

def draw_background():
    canvas.delete("all")

    w = root.winfo_width()
    h = root.winfo_height()

    colors = [CYAN, PURPLE, PINK]

    for i in range(18):
        x = random.randint(0, max(1, w))
        y = random.randint(0, max(1, h))
        radius = random.randint(15, 65)

        canvas.create_oval(
            x-radius, y-radius,
            x+radius, y+radius,
            outline=colors[i % 3],
            width=1
        )

def change_theme(theme):
    global BG
    BG = THEMES[theme]
    root.configure(bg=BG)
    canvas.configure(bg=BG)
    draw_background()

# ================= HEADER =================

header = tk.Frame(root, bg=BG)
header.pack(fill="x", pady=15)

tk.Label(
    header,
    text="✦ NEON BRAIN PUZZLE ✦",
    font=(FONT, 29, "bold"),
    fg=CYAN,
    bg=BG
).pack()

tk.Label(
    header,
    text="THINK SMARTER • PLAY BETTER • WIN BIGGER",
    font=(FONT, 10, "bold"),
    fg=PINK,
    bg=BG
).pack(pady=5)

# ================= MAIN LAYOUT =================

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=25, pady=10)

left = tk.Frame(
    main,
    bg=CARD,
    padx=20,
    pady=18,
    highlightbackground=PURPLE,
    highlightthickness=2
)
left.pack(side="left", fill="both", expand=True, padx=10)

right = tk.Frame(
    main,
    bg=CARD,
    padx=18,
    pady=15,
    width=310,
    highlightbackground=CYAN,
    highlightthickness=2
)
right.pack(side="right", fill="y", padx=10)
right.pack_propagate(False)

# ================= REUSABLE BUTTON =================

def make_button(parent, text, color, command, width=23):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=(FONT, 10, "bold"),
        bg=color,
        fg=WHITE,
        activebackground=CYAN,
        activeforeground="#101027",
        relief="flat",
        bd=0,
        width=width,
        pady=9,
        cursor="hand2"
    )

# ================= GAME STATUS =================

tk.Label(
    left,
    text="YOUR PUZZLE ARENA",
    font=(FONT, 19, "bold"),
    bg=CARD,
    fg=CYAN
).pack(pady=8)

name_label = tk.Label(
    left,
    text="PLAYER: Player 1",
    font=(FONT, 11, "bold"),
    bg=CARD,
    fg=WHITE
)
name_label.pack(pady=5)

mode_label = tk.Label(
    left,
    text="MODE: Single Player",
    font=(FONT, 10),
    bg=CARD,
    fg=PINK
)
mode_label.pack()

category_label = tk.Label(
    left,
    text="CATEGORY: Random",
    font=(FONT, 10),
    bg=CARD,
    fg=YELLOW
)
category_label.pack(pady=5)

# ================= SCORE CARDS =================

stats = tk.Frame(left, bg=CARD)
stats.pack(pady=18)

score_label = tk.Label(
    stats,
    text="⭐ SCORE: 0",
    font=(FONT, 14, "bold"),
    fg=GREEN,
    bg="#302750",
    padx=15,
    pady=10
)
score_label.grid(row=0, column=0, padx=5)

mistake_label = tk.Label(
    stats,
    text="❌ MISTAKES: 0",
    font=(FONT, 12, "bold"),
    fg=PINK,
    bg="#302750",
    padx=12,
    pady=10
)
mistake_label.grid(row=0, column=1, padx=5)

# ================= TIMER =================

timer_label = tk.Label(
    left,
    text="⏱ TIME: 00:00",
    font=(FONT, 15, "bold"),
    bg=CARD,
    fg=YELLOW
)
timer_label.pack(pady=10)

# ================= QUESTION =================

question_card = tk.Frame(
    left,
    bg="#302750",
    padx=20,
    pady=25,
    highlightbackground=CYAN,
    highlightthickness=1
)
question_card.pack(fill="x", pady=15)

tk.Label(
    question_card,
    text="BRAIN CHALLENGE",
    font=(FONT, 11, "bold"),
    bg="#302750",
    fg=PURPLE
).pack()

question_label = tk.Label(
    question_card,
    text="Press START GAME to begin!",
    font=(FONT, 18, "bold"),
    bg="#302750",
    fg=WHITE,
    wraplength=500,
    justify="center",
    height=3
)
question_label.pack(pady=12)

# ================= ANSWER INPUT =================

answer_entry = tk.Entry(
    left,
    font=(FONT, 17, "bold"),
    bg="#19152F",
    fg=CYAN,
    insertbackground=WHITE,
    justify="center",
    relief="flat",
    width=20
)
answer_entry.pack(pady=10, ipady=8)

answer_entry.bind(
    "<Return>",
    lambda event: submit_answer()
)

feedback = tk.Label(
    left,
    text="Your answer will appear here.",
    font=(FONT, 11, "bold"),
    bg=CARD,
    fg=MUTED
)
feedback.pack(pady=8)

# ================= GAME ENGINE =================

def next_puzzle():
    global current_question, current_answer, category

    if not game_active:
        return

    rng = None

    if game_type == "Daily Puzzle":
        seed = datetime.date.today().isoformat()
        rng = random.Random(seed)

    current_question, current_answer, actual_category = (
        generate_puzzle(category, difficulty, rng)
    )

    category_label.config(
        text=f"CATEGORY: {actual_category}"
    )

    question_label.config(text=current_question)

    answer_entry.delete(0, tk.END)
    answer_entry.focus_set()


def update_scoreboard():
    score_label.config(text=f"⭐ SCORE: {score}")

    mistake_label.config(
        text=f"❌ MISTAKES: {mistakes}"
    )


def submit_answer():
    global score, mistakes, current_player
    global computer_score, player1_score, player2_score
    global round_number

    if not game_active:
        return

    answer = answer_entry.get().strip().upper()

    if not answer:
        feedback.config(
            text="Please enter an answer!",
            fg=YELLOW
        )
        return

    if answer == current_answer:
        points = {
            "Beginner": 10,
            "Easy": 15,
            "Medium": 20,
            "Hard": 30,
            "Expert": 50
        }[difficulty]

        score += points

        if game_mode == "Player vs Player":
            if current_player == 1:
                player1_score += points
                current_player = 2
            else:
                player2_score += points
                current_player = 1

            name_label.config(
                text=f"{second_player if current_player == 2 else player_name} "
                     f"— NEXT TURN"
            )

        elif game_mode == "Player vs Computer":
            # A simulated computer opponent.
            # Its success chance changes with difficulty.
            chances = {
                "Beginner": 0.85,
                "Easy": 0.75,
                "Medium": 0.60,
                "Hard": 0.45,
                "Expert": 0.30
            }

            if random.random() < chances[difficulty]:
                computer_score += points

        feedback.config(
            text=f"✓ CORRECT! +{points} POINTS",
            fg=GREEN
        )

    else:
        mistakes += 1
        feedback.config(
            text="✗ INCORRECT! TRY THE NEXT PUZZLE",
            fg=PINK
        )

    round_number += 1
    update_scoreboard()

    if round_number >= 10:
        finish_game()
        return

    if game_type == "Daily Puzzle":
        finish_game()
        return

    root.after(900, next_puzzle)


# ================= TIMER SYSTEM =================

def timer_tick():
    global time_left

    if not game_active:
        return

    if game_type == "Time Challenge":
        time_left -= 1

        timer_label.config(
            text=f"⏱ TIME: 00:{max(0, time_left):02}"
        )

        if time_left <= 0:
            finish_game()
            return
    else:
        elapsed = int(time.time() - start_time)
        mins, secs = divmod(elapsed, 60)

        timer_label.config(
            text=f"⏱ TIME: {mins:02}:{secs:02}"
        )

    root.after(1000, timer_tick)


# ================= START GAME =================

def start_game():
    global score, mistakes, time_left
    global game_active, start_time, round_number
    global computer_score, player1_score, player2_score
    global current_player

    score = 0
    mistakes = 0
    time_left = 60
    round_number = 0

    computer_score = 0
    player1_score = 0
    player2_score = 0

    current_player = 1
    start_time = time.time()
    game_active = True

    update_scoreboard()

    mode_label.config(
        text=f"MODE: {game_mode} | {game_type}"
    )

    name_label.config(
        text=f"PLAYER: {player_name}"
    )

    feedback.config(
        text="GOOD LUCK! START SOLVING!",
        fg=GREEN
    )

    next_puzzle()
    timer_tick()


# ================= END GAME =================

def finish_game():
    global game_active

    if not game_active:
        return

    game_active = False

    if game_mode == "Player vs Computer":
        if score > computer_score:
            result = "YOU WIN!"
        elif score < computer_score:
            result = "COMPUTER WINS!"
        else:
            result = "IT'S A DRAW!"
    elif game_mode == "Player vs Player":
        if player1_score > player2_score:
            result = f"{player_name} WINS!"
        elif player2_score > player1_score:
            result = f"{second_player} WINS!"
        else:
            result = "IT'S A DRAW!"
    else:
        result = "CHALLENGE COMPLETED!"

    record_score(player_name, score)

    messagebox.showinfo(
        "GAME FINISHED",
        f"{result}\n\n"
        f"Your Score: {score}\n"
        f"Computer Score: {computer_score}\n"
        f"Mistakes: {mistakes}\n\n"
        "Your score has been saved!"
    )

    question_label.config(
        text="GAME COMPLETED!\nPress START GAME to play again."
    )


# ================= SETTINGS =================

tk.Label(
    right,
    text="⚙ GAME CONTROL",
    font=(FONT, 17, "bold"),
    fg=CYAN,
    bg=CARD
).pack(pady=10)

make_button(
    right,
    "▶ START GAME",
    "#6544B8",
    start_game
).pack(pady=6)

make_button(
    right,
    "⏹ STOP GAME",
    "#A83C61",
    finish_game
).pack(pady=6)

# ================= SELECTIONS =================

def create_selector(title, options, variable, command):
    tk.Label(
        right,
        text=title,
        font=(FONT, 10, "bold"),
        bg=CARD,
        fg=PINK
    ).pack(pady=(9, 3))

    combo = ttk.Combobox(
        right,
        values=options,
        textvariable=variable,
        state="readonly",
        font=(FONT, 10),
        width=25
    )
    combo.pack(pady=3)
    combo.bind("<<ComboboxSelected>>", command)
    return combo


mode_var = tk.StringVar(value=game_mode)
difficulty_var = tk.StringVar(value=difficulty)
category_var = tk.StringVar(value=category)
type_var = tk.StringVar(value=game_type)
theme_var = tk.StringVar(value="Neon Purple")

def mode_changed(event=None):
    global game_mode
    game_mode = mode_var.get()

def difficulty_changed(event=None):
    global difficulty
    difficulty = difficulty_var.get()

def category_changed(event=None):
    global category
    category = category_var.get()

def type_changed(event=None):
    global game_type
    game_type = type_var.get()

def theme_changed(event=None):
    change_theme(theme_var.get())

create_selector(
    "🎮 GAME MODE",
    ["Single Player", "Player vs Player", "Player vs Computer"],
    mode_var,
    mode_changed
)

create_selector(
    "⚡ DIFFICULTY",
    ["Beginner", "Easy", "Medium", "Hard", "Expert"],
    difficulty_var,
    difficulty_changed
)

create_selector(
    "🧩 PUZZLE CATEGORY",
    ["Random", "Math", "Number Pattern", "Word Scramble", "Logic"],
    category_var,
    category_changed
)

create_selector(
    "🏆 CHALLENGE TYPE",
    ["Practice Mode", "Time Challenge", "Daily Puzzle"],
    type_var,
    type_changed
)

create_selector(
    "🎨 BACKGROUND",
    list(THEMES.keys()),
    theme_var,
    theme_changed
)

# ================= PLAYER NAMES =================

def change_names():
    global player_name, second_player

    from tkinter import simpledialog

    name = simpledialog.askstring(
        "Player Name",
        "Enter Player 1 name:",
        parent=root
    )

    if name and name.strip():
        player_name = name.strip()

    if game_mode == "Player vs Player":
        name2 = simpledialog.askstring(
            "Player Name",
            "Enter Player 2 name:",
            parent=root
        )

        if name2 and name2.strip():
            second_player = name2.strip()

    name_label.config(
        text=f"PLAYER: {player_name}"
    )

make_button(
    right,
    "👤 CHANGE PLAYER NAME",
    "#3D779B",
    change_names
).pack(pady=8)

# ================= MUSIC =================

def toggle_music():
    global music_on

    if not MUSIC_AVAILABLE:
        messagebox.showwarning(
            "Music unavailable",
            "Install pygame and add background.mp3 "
            "to the game folder."
        )
        return

    try:
        if not music_on:
            if not os.path.exists("background.mp3"):
                messagebox.showwarning(
                    "Music file missing",
                    "Add background.mp3 to this folder."
                )
                return

            pygame.mixer.music.load("background.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.35)
            music_on = True
            music_button.config(text="🔊 MUSIC: ON")
        else:
            pygame.mixer.music.stop()
            music_on = False
            music_button.config(text="🔇 MUSIC: OFF")

    except Exception as error:
        messagebox.showerror("Music Error", str(error))


music_button = make_button(
    right,
    "🔇 MUSIC: OFF",
    "#67428C",
    toggle_music
)
music_button.pack(pady=5)

# ================= LEADERBOARD =================

def show_leaderboard():
    window = tk.Toplevel(root)
    window.title("TOP 10 PLAYERS")
    window.geometry("430x520")
    window.configure(bg=BG)

    tk.Label(
        window,
        text="🏆 TOP 10 LEADERBOARD",
        font=(FONT, 20, "bold"),
        fg=YELLOW,
        bg=BG
    ).pack(pady=20)

    if not leaderboard:
        tk.Label(
            window,
            text="No scores yet. Start playing!",
            font=(FONT, 12),
            fg=WHITE,
            bg=BG
        ).pack(pady=20)

    for i, item in enumerate(leaderboard):
        tk.Label(
            window,
            text=(
                f"#{i+1}    {item['name']}    "
                f"⭐ {item['score']}"
            ),
            font=(FONT, 12, "bold"),
            bg=CARD,
            fg=CYAN if i == 0 else WHITE,
            width=32,
            pady=10
        ).pack(pady=4)


make_button(
    right,
    "🏆 LEADERBOARD",
    "#9A762E",
    show_leaderboard
).pack(pady=5)

# ================= GAME RULES =================

def show_rules():
    messagebox.showinfo(
        "HOW TO PLAY",
        "✦ NEON BRAIN PUZZLE RULES ✦\n\n"
        "1. Select a game mode.\n\n"
        "2. Choose your difficulty level.\n\n"
        "3. Select a puzzle category.\n\n"
        "4. Read the question carefully.\n\n"
        "5. Enter your answer and press ENTER.\n\n"
        "6. Correct answers earn points.\n\n"
        "7. Complete 10 rounds to finish.\n\n"
        "8. In Time Challenge, solve as many "
        "puzzles as possible in 60 seconds.\n\n"
        "9. Daily Puzzle uses a daily fixed seed.\n\n"
        "10. Try to reach the TOP 10 leaderboard!"
    )


make_button(
    right,
    "📖 HOW TO PLAY / RULES",
    "#7650A8",
    show_rules
).pack(pady=5)

# ================= EXIT =================

def exit_game():
    if messagebox.askyesno(
        "Exit",
        "Are you sure you want to exit?"
    ):
        if MUSIC_AVAILABLE:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except:
                pass
        root.destroy()


make_button(
    right,
    "🚪 EXIT GAME",
    "#A33E51",
    exit_game
).pack(pady=12)

# ================= FOOTER =================

footer = tk.Label(
    root,
    text="NEON BRAIN PUZZLE  •  CHALLENGE YOUR MIND",
    font=(FONT, 9, "bold"),
    bg=BG,
    fg=PURPLE
)
footer.pack(side="bottom", pady=8)

# ================= START APPLICATION =================

draw_background()
root.mainloop()
