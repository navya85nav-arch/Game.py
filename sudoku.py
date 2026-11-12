
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time
import json
import os

# ---------------- CONFIGURATION ----------------

BG = "#101027"
PANEL = "#1D1D3B"
WHITE = "#FFFFFF"
CYAN = "#00F5FF"
PURPLE = "#B44CFF"
PINK = "#FF4FD8"
GREEN = "#39FF88"
YELLOW = "#FFE66D"

FONT = "Segoe UI"

root = tk.Tk()
root.title("NEON SUDOKU")
root.geometry("1100x760")
root.minsize(950, 700)
root.configure(bg=BG)

score = 0
mistakes = 0
start_time = time.time()
selected = None
current_player = 1
game_mode = "Player vs Computer"
difficulty = "Easy"
solution = []
board = []
fixed = []
leaderboard_file = "sudoku_leaderboard.json"

# ---------------- LEADERBOARD ----------------

def load_leaderboard():
    if os.path.exists(leaderboard_file):
        try:
            with open(leaderboard_file, "r") as f:
                return json.load(f)
        except:
            pass
    return []

leaderboard = load_leaderboard()

def save_score():
    global leaderboard
    name = simpledialog.askstring("Winner", "Enter your name:")
    if not name:
        name = "Player"
    leaderboard.append({"name": name, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    leaderboard = leaderboard[:10]

    with open(leaderboard_file, "w") as f:
        json.dump(leaderboard, f, indent=4)

# ---------------- SUDOKU LOGIC ----------------

def valid(grid, r, c, n):
    if n in grid[r]:
        return False

    if any(grid[i][c] == n for i in range(9)):
        return False

    br, bc = (r // 3) * 3, (c // 3) * 3

    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if grid[i][j] == n:
                return False

    return True


def solve(grid):
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                numbers = list(range(1, 10))
                random.shuffle(numbers)

                for n in numbers:
                    if valid(grid, r, c, n):
                        grid[r][c] = n

                        if solve(grid):
                            return True

                        grid[r][c] = 0

                return False

    return True


def generate_sudoku():
    global board, solution, fixed

    grid = [[0] * 9 for _ in range(9)]
    solve(grid)

    solution = [row[:] for row in grid]
    board = [row[:] for row in grid]

    blanks = {
        "Easy": 35,
        "Medium": 45,
        "Hard": 55
    }[difficulty]

    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    for r, c in positions[:blanks]:
        board[r][c] = 0

    fixed = [[board[r][c] != 0 for c in range(9)]
             for r in range(9)]


# ---------------- MAIN INTERFACE ----------------

header = tk.Frame(root, bg=BG)
header.pack(fill="x", pady=15)

tk.Label(
    header,
    text="✦ NEON SUDOKU ✦",
    font=(FONT, 28, "bold"),
    fg=CYAN,
    bg=BG
).pack()

tk.Label(
    header,
    text="THINK • SOLVE • WIN",
    font=(FONT, 10, "bold"),
    fg=PINK,
    bg=BG
).pack(pady=3)

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=25, pady=10)

left = tk.Frame(main, bg=PANEL, padx=15, pady=15)
left.pack(side="left", padx=10)

right = tk.Frame(main, bg=PANEL, padx=20, pady=20)
right.pack(side="right", fill="both", expand=True, padx=10)

# ---------------- GAME INFORMATION ----------------

tk.Label(
    right,
    text="GAME CONTROL",
    font=(FONT, 17, "bold"),
    fg=CYAN,
    bg=PANEL
).pack(pady=10)

score_label = tk.Label(
    right, text="SCORE: 0",
    font=(FONT, 15, "bold"),
    fg=GREEN, bg=PANEL
)
score_label.pack(pady=8)

mistake_label = tk.Label(
    right, text="MISTAKES: 0",
    font=(FONT, 13),
    fg=PINK, bg=PANEL
)
mistake_label.pack(pady=5)

timer_label = tk.Label(
    right, text="TIME: 00:00",
    font=(FONT, 13),
    fg=YELLOW, bg=PANEL
)
timer_label.pack(pady=5)

player_label = tk.Label(
    right, text="PLAYER 1",
    font=(FONT, 13, "bold"),
    fg=CYAN, bg=PANEL
)
player_label.pack(pady=10)

# ---------------- SUDOKU GRID ----------------

cells = []

grid_frame = tk.Frame(left, bg=CYAN, padx=3, pady=3)
grid_frame.pack()

def draw_grid():
    global cells
    cells = []

    for r in range(9):
        row = []

        for c in range(9):
            cell = tk.Label(
                grid_frame,
                text=str(board[r][c]) if board[r][c] else "",
                width=3,
                height=1,
                font=(FONT, 17, "bold"),
                bg="#242449",
                fg=CYAN if fixed[r][c] else WHITE,
                relief="flat",
                bd=0,
                padx=3,
                pady=5,
                cursor="hand2"
            )

            cell.grid(
                row=r,
                column=c,
                padx=(2 if c % 3 == 0 else 1),
                pady=(2 if r % 3 == 0 else 1)
            )

            cell.bind(
                "<Button-1>",
                lambda e, rr=r, cc=c: select_cell(rr, cc)
            )

            row.append(cell)

        cells.append(row)


def refresh_grid():
    for r in range(9):
        for c in range(9):
            cells[r][c].config(
                text=str(board[r][c]) if board[r][c] else "",
                fg=CYAN if fixed[r][c] else WHITE,
                bg="#30305C" if (r, c) == selected else "#242449"
            )


def select_cell(r, c):
    global selected

    if fixed[r][c]:
        return

    selected = (r, c)
    refresh_grid()


# ---------------- NUMBER INPUT ----------------

def enter_number(n):
    global score, mistakes, current_player

    if selected is None:
        messagebox.showinfo("Select Cell", "Please select an empty cell first!")
        return

    r, c = selected

    if fixed[r][c]:
        return

    if n == solution[r][c]:
        board[r][c] = n
        score += 10
        score_label.config(text=f"SCORE: {score}")

        refresh_grid()

        if all(board[i][j] == solution[i][j]
               for i in range(9) for j in range(9)):
            messagebox.showinfo("YOU WIN!", f"Congratulations! Score: {score}")
            save_score()
            show_leaderboard()

        else:
            if game_mode == "Player vs Player":
                current_player = 2 if current_player == 1 else 1
                player_label.config(text=f"PLAYER {current_player}")

    else:
        mistakes += 1
        mistake_label.config(text=f"MISTAKES: {mistakes}")
        messagebox.showwarning("Incorrect", "Try another number!")


def erase_cell():
    global selected

    if selected:
        r, c = selected
        if not fixed[r][c]:
            board[r][c] = 0
            refresh_grid()


# ---------------- NUMBER BUTTONS ----------------

tk.Label(
    right,
    text="SELECT NUMBER",
    font=(FONT, 13, "bold"),
    fg=WHITE,
    bg=PANEL
).pack(pady=15)

number_frame = tk.Frame(right, bg=PANEL)
number_frame.pack()

for n in range(1, 10):
    btn = tk.Button(
        number_frame,
        text=str(n),
        font=(FONT, 14, "bold"),
        bg="#34345F",
        fg=CYAN,
        activebackground=PURPLE,
        activeforeground=WHITE,
        width=4,
        relief="flat",
        command=lambda x=n: enter_number(x)
    )

    btn.grid(row=(n-1)//3, column=(n-1)%3, padx=5, pady=5)


# ---------------- TIMER ----------------

def update_timer():
    elapsed = int(time.time() - start_time)
    mins, secs = divmod(elapsed, 60)

    timer_label.config(
        text=f"TIME: {mins:02}:{secs:02}"
    )

    root.after(1000, update_timer)


# ---------------- GAME SETTINGS ----------------

def new_game():
    global score, mistakes, start_time, selected

    score = 0
    mistakes = 0
    selected = None
    start_time = time.time()

    score_label.config(text="SCORE: 0")
    mistake_label.config(text="MISTAKES: 0")

    generate_sudoku()
    draw_grid()


def choose_difficulty(level):
    global difficulty
    difficulty = level
    new_game()


def choose_mode(mode):
    global game_mode
    game_mode = mode

    messagebox.showinfo(
        "Game Mode",
        f"Mode selected: {mode}"
    )

    new_game()


# ---------------- BUTTON DESIGN ----------------

def make_button(parent, text, color, command):
    return tk.Button(
        parent,
        text=text,
        font=(FONT, 11, "bold"),
        bg=color,
        fg=WHITE,
        activebackground=CYAN,
        activeforeground=BG,
        relief="flat",
        width=22,
        pady=8,
        cursor="hand2",
        command=command
    )


tk.Label(
    right,
    text="GAME SETTINGS",
    font=(FONT, 13, "bold"),
    fg=PURPLE,
    bg=PANEL
).pack(pady=12)

make_button(right, "NEW GAME", "#5555B8", new_game).pack(pady=5)

make_button(
    right, "EASY", "#247A66",
    lambda: choose_difficulty("Easy")
).pack(pady=3)

make_button(
    right, "MEDIUM", "#98602B",
    lambda: choose_difficulty("Medium")
).pack(pady=3)

make_button(
    right, "HARD", "#963C72",
    lambda: choose_difficulty("Hard")
).pack(pady=3)

make_button(
    right, "PLAYER VS PLAYER",
    "#6650B8",
    lambda: choose_mode("Player vs Player")
).pack(pady=3)

make_button(
    right, "PLAYER VS COMPUTER",
    "#306A9C",
    lambda: choose_mode("Player vs Computer")
).pack(pady=3)

make_button(
    right, "ERASE NUMBER",
    "#A13E56",
    erase_cell
).pack(pady=3)


# ---------------- HOW TO PLAY ----------------

def how_to_play():
    messagebox.showinfo(
        "HOW TO PLAY",
        "1. Select an empty Sudoku cell.\n\n"
        "2. Choose a number from 1 to 9.\n\n"
        "3. Each row must contain numbers 1-9.\n\n"
        "4. Each column must contain numbers 1-9.\n\n"
        "5. Each 3x3 box must contain numbers 1-9.\n\n"
        "6. Complete the board to win!\n\n"
        "Correct answer = +10 points."
    )


make_button(
    right, "HOW TO PLAY",
    "#7C438D",
    how_to_play
).pack(pady=5)


# ---------------- LEADERBOARD ----------------

def show_leaderboard():
    window = tk.Toplevel(root)
    window.title("Leaderboard")
    window.geometry("350x420")
    window.configure(bg=BG)

    tk.Label(
        window,
        text="🏆 LEADERBOARD",
        font=(FONT, 20, "bold"),
        fg=YELLOW,
        bg=BG
    ).pack(pady=20)

    for i, item in enumerate(leaderboard):
        tk.Label(
            window,
            text=f"{i+1}. {item['name']}  -  {item['score']} PTS",
            font=(FONT, 12, "bold"),
            fg=WHITE,
            bg=PANEL,
            width=30,
            pady=8
        ).pack(pady=4)


make_button(
    right, "LEADERBOARD",
    "#A77B29",
    show_leaderboard
).pack(pady=5)


# ---------------- EXIT ----------------

def exit_game():
    if messagebox.askyesno(
        "Exit Game",
        "Are you sure you want to exit?"
    ):
        root.destroy()


make_button(
    right, "EXIT GAME",
    "#B13B55",
    exit_game
).pack(pady=12)


# ---------------- START ----------------

generate_sudoku()
draw_grid()
update_timer()

root.mainloop()
