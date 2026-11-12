
import pygame
import sys
import random
import math

pygame.init()

# -------------------- CONFIGURATION --------------------

WIDTH, HEIGHT = 1000, 720
FPS = 60

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT), pygame.RESIZABLE
)
pygame.display.set_caption("NEON TIC TAC TOE")

clock = pygame.time.Clock()

# Colors
WHITE = (245, 245, 255)
MUTED = (160, 170, 195)
BG_TOP = (13, 15, 38)
BG_BOTTOM = (35, 17, 65)
PURPLE = (166, 90, 255)
CYAN = (45, 220, 255)
PINK = (255, 80, 170)
GREEN = (80, 255, 180)
DARK = (20, 23, 48)

# Fonts
def font(size, bold=False):
    return pygame.font.SysFont(
        "segoeui", size, bold=bold
    )


# -------------------- GAME VARIABLES --------------------

board = [""] * 9
scores = {"X": 0, "O": 0, "Draw": 0}

current_player = "X"
game_mode = None
difficulty = "Impossible"
game_state = "menu"

winner = None
winning_line = None

animations = {}
message = "Choose your game mode"

# -------------------- BACKGROUND --------------------

def draw_background():
    for y in range(HEIGHT):
        ratio = y / max(HEIGHT, 1)

        r = int(BG_TOP[0] * (1-ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1-ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1-ratio) + BG_BOTTOM[2] * ratio)

        pygame.draw.line(
            screen, (r, g, b), (0, y), (WIDTH, y)
        )

    # Decorative glowing circles
    for x, y, radius, color in [
        (100, 100, 150, PURPLE),
        (900, 580, 180, CYAN),
        (500, 350, 100, PINK)
    ]:
        glow = pygame.Surface(
            (radius * 2, radius * 2), pygame.SRCALPHA
        )

        pygame.draw.circle(
            glow, (*color, 15),
            (radius, radius), radius
        )

        screen.blit(glow, (x-radius, y-radius))


# -------------------- TEXT --------------------

def draw_text(text, size, color, center, bold=False):
    surface = font(size, bold).render(
        str(text), True, color
    )

    rect = surface.get_rect(center=center)
    screen.blit(surface, rect)


# -------------------- GLASS CARD --------------------

def glass_card(rect, border_color=PURPLE, radius=22):
    x, y, w, h = rect

    shadow = pygame.Surface(
        (w + 20, h + 20), pygame.SRCALPHA
    )

    pygame.draw.rect(
        shadow, (*border_color, 25),
        (10, 10, w, h), border_radius=radius
    )

    screen.blit(shadow, (x-10, y-10))

    card = pygame.Surface((w, h), pygame.SRCALPHA)

    pygame.draw.rect(
        card, (255, 255, 255, 17),
        (0, 0, w, h), border_radius=radius
    )

    pygame.draw.rect(
        card, (*border_color, 100),
        (0, 0, w, h), 1, border_radius=radius
    )

    screen.blit(card, (x, y))


# -------------------- BUTTON --------------------

def draw_button(text, rect, color=PURPLE):
    mouse = pygame.mouse.get_pos()

    hovering = pygame.Rect(rect).collidepoint(mouse)

    current_color = (
        CYAN if hovering else color
    )

    glass_card(rect, current_color, 15)

    draw_text(
        text, 20, WHITE,
        pygame.Rect(rect).center, True
    )


# -------------------- WIN CHECK --------------------

WIN_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]


def check_winner(state):
    for combo in WIN_COMBINATIONS:
        a, b, c = combo

        if (
            state[a] != ""
            and state[a] == state[b] == state[c]
        ):
            return state[a], combo

    if "" not in state:
        return "Draw", None

    return None, None


# -------------------- MINIMAX AI --------------------

def minimax(state, is_maximizing, depth=0):
    result, _ = check_winner(state)

    if result == "O":
        return 10 - depth

    if result == "X":
        return depth - 10

    if result == "Draw":
        return 0

    if is_maximizing:
        best_score = -math.inf

        for i in range(9):
            if state[i] == "":
                state[i] = "O"

                score = minimax(
                    state, False, depth + 1
                )

                state[i] = ""
                best_score = max(best_score, score)

        return best_score

    else:
        best_score = math.inf

        for i in range(9):
            if state[i] == "":
                state[i] = "X"

                score = minimax(
                    state, True, depth + 1
                )

                state[i] = ""
                best_score = min(best_score, score)

        return best_score


def impossible_ai():
    best_score = -math.inf
    best_move = None

    for i in range(9):
        if board[i] == "":
            board[i] = "O"

            score = minimax(board, False)

            board[i] = ""

            if score > best_score:
                best_score = score
                best_move = i

    return best_move


# -------------------- EASY AI --------------------

def easy_ai():
    available = [
        i for i in range(9) if board[i] == ""
    ]

    return random.choice(available) if available else None


# -------------------- MEDIUM AI --------------------

def medium_ai():
    # Try to win
    for i in range(9):
        if board[i] == "":
            board[i] = "O"

            result, _ = check_winner(board)
            board[i] = ""

            if result == "O":
                return i

    # Block the opponent
    for i in range(9):
        if board[i] == "":
            board[i] = "X"

            result, _ = check_winner(board)
            board[i] = ""

            if result == "X":
                return i

    # Prefer center
    if board[4] == "":
        return 4

    # Prefer corners
    corners = [
        i for i in [0, 2, 6, 8]
        if board[i] == ""
    ]

    if corners:
        return random.choice(corners)

    return easy_ai()


# -------------------- AI MOVE --------------------

def computer_move():
    if difficulty == "Easy":
        move = easy_ai()

    elif difficulty == "Medium":
        move = medium_ai()

    else:
        move = impossible_ai()

    if move is not None:
        make_move(move, "O")


# -------------------- GAME LOGIC --------------------

def make_move(index, player):
    global current_player
    global winner, winning_line, game_state, message

    if board[index] != "" or winner is not None:
        return

    board[index] = player
    animations[index] = pygame.time.get_ticks()

    result, line = check_winner(board)

    if result:
        winner = result
        winning_line = line
        game_state = "over"

        if result == "Draw":
            scores["Draw"] += 1
            message = "IT'S A DRAW!"
        else:
            scores[result] += 1
            message = f"PLAYER {result} WINS!"

        return

    current_player = "O" if player == "X" else "X"


def reset_game():
    global board, winner, winning_line
    global current_player, game_state, message

    board = [""] * 9
    animations.clear()

    winner = None
    winning_line = None

    current_player = "X"
    game_state = "playing"
    message = "PLAYER X'S TURN"


def reset_scores():
    scores["X"] = 0
    scores["O"] = 0
    scores["Draw"] = 0


# -------------------- DRAW BOARD --------------------

def draw_board():
    board_size = min(420, WIDTH - 80, HEIGHT - 240)
    board_size = max(180, board_size)

    cell = board_size // 3

    start_x = (WIDTH - board_size) // 2
    start_y = (HEIGHT - board_size) // 2 + 35

    glass_card(
        (start_x - 12, start_y - 12,
         board_size + 24, board_size + 24),
        CYAN, 25
    )

    mouse = pygame.mouse.get_pos()

    for row in range(3):
        for col in range(3):
            index = row * 3 + col

            x = start_x + col * cell
            y = start_y + row * cell

            rect = pygame.Rect(
                x + 5, y + 5, cell - 10, cell - 10
            )

            hovering = rect.collidepoint(mouse)

            color = (
                (50, 65, 105, 120)
                if hovering else (255, 255, 255, 13)
            )

            cell_surface = pygame.Surface(
                (rect.width, rect.height), pygame.SRCALPHA
            )

            pygame.draw.rect(
                cell_surface, color,
                cell_surface.get_rect(),
                border_radius=17
            )

            screen.blit(cell_surface, rect.topleft)

            if board[index]:
                draw_symbol(
                    board[index], rect.center,
                    cell, index
                )

    # Winning cells
    if winning_line:
        for index in winning_line:
            row, col = divmod(index, 3)

            center = (
                start_x + col * cell + cell // 2,
                start_y + row * cell + cell // 2
            )

            pygame.draw.circle(
                screen, GREEN, center,
                max(4, cell // 2 - 8), 3
            )

    return start_x, start_y, cell


# -------------------- SYMBOL DESIGN --------------------

def draw_symbol(symbol, center, cell, index):
    elapsed = (
        pygame.time.get_ticks()
        - animations.get(index, pygame.time.get_ticks())
    )

    progress = min(1, elapsed / 220)

    scale = 0.5 + 0.5 * progress
    size = int(cell * 0.65 * scale)

    color = CYAN if symbol == "X" else PINK

    # Neon glow
    glow = pygame.Surface(
        (cell, cell), pygame.SRCALPHA
    )

    pygame.draw.circle(
        glow, (*color, 28),
        (cell // 2, cell // 2),
        int(cell * 0.36 * scale)
    )

    screen.blit(
        glow,
        (center[0] - cell // 2,
         center[1] - cell // 2)
    )

    if symbol == "X":
        offset = size // 3
        width = max(3, int(size * 0.09))

        pygame.draw.line(
            screen, color,
            (center[0]-offset, center[1]-offset),
            (center[0]+offset, center[1]+offset),
            width
        )

        pygame.draw.line(
            screen, color,
            (center[0]+offset, center[1]-offset),
            (center[0]-offset, center[1]+offset),
            width
        )

    else:
        pygame.draw.circle(
            screen, color, center,
            size // 3, max(3, size // 12)
        )


# -------------------- GAME SCREEN --------------------

def draw_game():
    draw_background()

    draw_text(
        "NEON TIC TAC TOE",
        38, WHITE, (WIDTH // 2, 45), True
    )

    draw_text(
        message, 22,
        GREEN if winner and winner != "Draw" else CYAN,
        (WIDTH // 2, 100), True
    )

    # Scoreboard
    glass_card(
        (WIDTH // 2 - 210, 125, 420, 65),
        PURPLE
    )

    draw_text(
        f"X: {scores['X']}     O: {scores['O']}     DRAWS: {scores['Draw']}",
        18, WHITE, (WIDTH // 2, 158), True
    )

    draw_board()

    # Bottom controls
    button_y = HEIGHT - 75

    draw_button(
        "RESTART",
        (WIDTH // 2 - 175, button_y, 145, 48),
        PURPLE
    )

    draw_button(
        "MAIN MENU",
        (WIDTH // 2 + 30, button_y, 145, 48),
        CYAN
    )

    if winner:
        draw_text(
            "Click RESTART to play again",
            16, MUTED,
            (WIDTH // 2, HEIGHT - 110)
        )


# -------------------- MENU SCREEN --------------------

def draw_menu():
    draw_background()

    draw_text(
        "NEON TIC TAC TOE",
        55, WHITE, (WIDTH // 2, 125), True
    )

    draw_text(
        "A CLASSIC GAME. A NEW DIMENSION.",
        17, CYAN, (WIDTH // 2, 180)
    )

    buttons = [
        ("PLAYER VS PLAYER", "pvp"),
        ("PLAYER VS COMPUTER", "pvc")
    ]

    for i, (label, _) in enumerate(buttons):
        y = 270 + i * 90

        draw_button(
            label,
            (WIDTH // 2 - 165, y, 330, 58),
            PURPLE if i == 0 else CYAN
        )

    draw_text(
        "Choose your game mode",
        18, MUTED, (WIDTH // 2, 510)
    )


# -------------------- DIFFICULTY SCREEN --------------------

def draw_difficulty():
    draw_background()

    draw_text(
        "SELECT AI DIFFICULTY",
        38, WHITE, (WIDTH // 2, 140), True
    )

    levels = ["Easy", "Medium", "Impossible"]

    for i, level in enumerate(levels):
        y = 245 + i * 85

        draw_button(
            level.upper(),
            (WIDTH // 2 - 160, y, 320, 58),
            [GREEN, PURPLE, PINK][i]
        )

    draw_text(
        "Impossible AI uses Minimax",
        17, CYAN, (WIDTH // 2, 535)
    )

    draw_button(
        "BACK",
        (WIDTH // 2 - 75, 590, 150, 48),
        CYAN
    )


# -------------------- MAIN LOOP --------------------

running = True

while running:

    clock.tick(FPS)

    # Keep minimum dimensions
    WIDTH, HEIGHT = screen.get_size()

    WIDTH = max(WIDTH, 600)
    HEIGHT = max(HEIGHT, 500)

    screen_width, screen_height = screen.get_size()

    # Adjust logical dimensions to actual window size
    WIDTH, HEIGHT = screen_width, screen_height

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(
                (max(600, event.w), max(500, event.h)),
                pygame.RESIZABLE
            )

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                mx, my = event.pos

                if game_state == "menu":

                    if (
                        WIDTH // 2 - 165 < mx < WIDTH // 2 + 165
                        and 270 < my < 328
                    ):
                        game_mode = "pvp"
                        reset_game()

                    elif (
                        WIDTH // 2 - 165 < mx < WIDTH // 2 + 165
                        and 360 < my < 418
                    ):
                        game_mode = "pvc"
                        game_state = "difficulty"

                elif game_state == "difficulty":

                    if (
                        WIDTH // 2 - 160 < mx < WIDTH // 2 + 160
                    ):
                        for i, level in enumerate(
                            ["Easy", "Medium", "Impossible"]
                        ):
                            y = 245 + i * 85

                            if y < my < y + 58:
                                difficulty = level
                                reset_game()
                                break

                    if 590 < my < 638:
                        game_state = "menu"

                elif game_state in ("playing", "over"):

                    button_y = HEIGHT - 75

                    # Restart
                    if (
                        WIDTH // 2 - 175 < mx < WIDTH // 2 - 30
                        and button_y < my < button_y + 48
                    ):
                        reset_game()

                    # Main menu
                    elif (
                        WIDTH // 2 + 30 < mx < WIDTH // 2 + 175
                        and button_y < my < button_y + 48
                    ):
                        game_state = "menu"

                    elif game_state == "playing":

                        if (
                            game_mode == "pvp"
                            or current_player == "X"
                        ):
                            start_x, start_y, cell = (
                                (WIDTH - min(420, WIDTH - 80,
                                             HEIGHT - 240)) // 2,
                                (HEIGHT - min(420, WIDTH - 80,
                                              HEIGHT - 240)) // 2 + 35,
                                min(420, WIDTH - 80,
                                    HEIGHT - 240) // 3
                            )

                            if (
                                start_x <= mx < start_x + cell * 3
                                and start_y <= my < start_y + cell * 3
                            ):
                                col = (mx - start_x) // cell
                                row = (my - start_y) // cell

                                index = row * 3 + col

                                if board[index] == "":
                                    make_move(index, current_player)

    # Computer turn
    if (
        game_state == "playing"
        and game_mode == "pvc"
        and current_player == "O"
        and winner is None
    ):
        pygame.time.wait(180)
        computer_move()

    # Keyboard shortcuts
    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        if game_state == "playing" or game_state == "over":
            game_state = "menu"

    # Render screens
    if game_state == "menu":
        draw_menu()

    elif game_state == "difficulty":
        draw_difficulty()

    elif game_state in ("playing", "over"):
        draw_game()

    pygame.display.flip()

pygame.quit()
sys.exit()
