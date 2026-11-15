
import pygame
import random
import sys
import os
import time
import tkinter as tk
from tkinter import filedialog

pygame.init()

# ==========================================
# 1. WINDOW AND BASIC SETTINGS
# ==========================================

WIDTH, HEIGHT = 1000, 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puzzle Galaxy | Picture Puzzle")

clock = pygame.time.Clock()

# Colours
BG_TOP = (16, 19, 55)
BG_BOTTOM = (45, 25, 90)
WHITE = (255, 255, 255)
PURPLE = (145, 90, 255)
CYAN = (45, 220, 255)
PINK = (255, 90, 190)
GREEN = (65, 230, 165)
DARK = (25, 28, 65)
MUTED = (185, 190, 225)

# Fonts
title_font = pygame.font.SysFont("arial", 48, bold=True)
heading_font = pygame.font.SysFont("arial", 30, bold=True)
font = pygame.font.SysFont("arial", 21, bold=True)
small_font = pygame.font.SysFont("arial", 16)
tiny_font = pygame.font.SysFont("arial", 13)

# ==========================================
# 2. GAME SETTINGS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

CATEGORIES = ["Nature", "Animals", "Cars", "Space"]

LEVELS = {
    "Easy": 3,
    "Medium": 4,
    "Hard": 5
}

selected_category = "Nature"
selected_level = "Easy"
grid_size = 3

image = None
tiles = []
board_rect = pygame.Rect(370, 105, 560, 560)

game_state = "menu"

moves = 0
start_time = 0
paused_time = 0
pause_started = 0

dragging = False
drag_index = None
drag_position = (0, 0)

picture_name = "No picture selected"


# ==========================================
# 3. BACKGROUND
# ==========================================

def create_background():
    background = pygame.Surface((WIDTH, HEIGHT))

    for y in range(HEIGHT):
        ratio = y / HEIGHT

        r = int(BG_TOP[0] * (1-ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1-ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1-ratio) + BG_BOTTOM[2] * ratio)

        pygame.draw.line(
            background, (r, g, b),
            (0, y), (WIDTH, y)
        )

    return background


background = create_background()


def draw_background():
    screen.blit(background, (0, 0))

    # Decorative circles
    pygame.draw.circle(screen, (65, 45, 120), (60, 80), 100, 2)
    pygame.draw.circle(screen, (45, 90, 150), (940, 600), 120, 2)

    pygame.draw.circle(screen, (75, 50, 140), (850, 80), 65, 2)


# ==========================================
# 4. GLASSMORPHISM UI
# ==========================================

def draw_glass(rect, radius=20):
    glass = pygame.Surface(
        (rect.width, rect.height), pygame.SRCALPHA
    )

    pygame.draw.rect(
        glass, (255, 255, 255, 24),
        glass.get_rect(), border_radius=radius
    )

    pygame.draw.rect(
        glass, (255, 255, 255, 65),
        glass.get_rect(), width=2,
        border_radius=radius
    )

    screen.blit(glass, rect.topleft)


def draw_text(text, font_style, color, x, y, center=False):
    surface = font_style.render(str(text), True, color)

    if center:
        screen.blit(
            surface,
            (x - surface.get_width() // 2,
             y - surface.get_height() // 2)
        )
    else:
        screen.blit(surface, (x, y))


def draw_button(text, rect, active=False, color=PURPLE):
    mouse = pygame.mouse.get_pos()

    hover = rect.collidepoint(mouse)

    button_color = CYAN if hover else color

    draw_glass(rect, 14)

    pygame.draw.rect(
        screen, button_color,
        rect, border_radius=14
    )

    pygame.draw.rect(
        screen, (255, 255, 255),
        rect, width=2, border_radius=14
    )

    draw_text(
        text, font, WHITE,
        rect.centerx, rect.centery, True
    )


# ==========================================
# 5. PICTURE LOADING
# ==========================================

def load_picture(path):
    global image, picture_name

    try:
        loaded = pygame.image.load(path).convert()

        image = pygame.transform.smoothscale(
            loaded,
            (board_rect.width, board_rect.height)
        )

        picture_name = os.path.basename(path)
        return True

    except (pygame.error, OSError) as error:
        print("Picture loading error:", error)
        return False


def choose_picture():
    root = tk.Tk()
    root.withdraw()

    try:
        root.attributes("-topmost", True)
    except tk.TclError:
        pass

    path = filedialog.askopenfilename(
        title="Choose Your Puzzle Picture",
        filetypes=[
            ("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp")
        ]
    )

    root.destroy()

    if path:
        return load_picture(path)

    return False


def choose_category_picture(category):
    folder = os.path.join(ASSET_DIR, category.lower())

    if not os.path.isdir(folder):
        print("Create category folder:", folder)
        return False

    extensions = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

    pictures = [
        os.path.join(folder, file)
        for file in os.listdir(folder)
        if file.lower().endswith(extensions)
    ]

    if not pictures:
        print("Add pictures to:", folder)
        return False

    return load_picture(random.choice(pictures))


# ==========================================
# 6. PUZZLE SYSTEM
# ==========================================

def shuffle_puzzle():
    global tiles, moves, start_time
    global paused_time, dragging, drag_index

    total = grid_size * grid_size

    tiles = list(range(total))

    random.shuffle(tiles)

    # Prevent a puzzle that is already completed
    while tiles == list(range(total)):
        random.shuffle(tiles)

    moves = 0
    paused_time = 0
    start_time = time.time()

    dragging = False
    drag_index = None


def is_solved():
    return tiles == list(range(grid_size * grid_size))


def get_tile_rect(index):
    size = board_rect.width // grid_size

    row, col = divmod(index, grid_size)

    return pygame.Rect(
        board_rect.x + col * size,
        board_rect.y + row * size,
        size, size
    )


def swap_tiles(first, second):
    global moves

    if first == second:
        return

    tiles[first], tiles[second] = (
        tiles[second], tiles[first]
    )

    moves += 1


# ==========================================
# 7. DRAW PUZZLE BOARD
# ==========================================

def draw_puzzle():
    if image is None:
        return

    draw_glass(board_rect, 18)

    tile_size = board_rect.width // grid_size

    for index, tile_number in enumerate(tiles):

        rect = get_tile_rect(index)

        # Skip the tile being dragged
        if dragging and index == drag_index:
            continue

        row, col = divmod(tile_number, grid_size)

        source = pygame.Rect(
            col * tile_size,
            row * tile_size,
            tile_size,
            tile_size
        )

        tile_image = image.subsurface(source)

        tile_image = pygame.transform.smoothscale(
            tile_image,
            (tile_size - 4, tile_size - 4)
        )

        screen.blit(
            tile_image,
            (rect.x + 2, rect.y + 2)
        )

        pygame.draw.rect(
            screen, WHITE,
            rect, width=2, border_radius=5
        )

    # Draw dragged tile at mouse position
    if dragging and drag_index is not None:

        tile_number = tiles[drag_index]

        row, col = divmod(tile_number, grid_size)

        source = pygame.Rect(
            col * tile_size,
            row * tile_size,
            tile_size,
            tile_size
        )

        tile_image = image.subsurface(source)

        tile_image = pygame.transform.smoothscale(
            tile_image,
            (tile_size - 4, tile_size - 4)
        )

        mx, my = drag_position

        screen.blit(
            tile_image,
            (mx - tile_size // 2, my - tile_size // 2)
        )


# ==========================================
# 8. HOME SCREEN
# ==========================================

def draw_home():

    draw_background()

    draw_text(
        "PUZZLE GALAXY",
        title_font, CYAN,
        500, 55, True
    )

    draw_text(
        "Arrange • Explore • Complete",
        font, WHITE,
        500, 105, True
    )

    # Main panel
    draw_glass(pygame.Rect(35, 150, 930, 510), 25)

    draw_text(
        "CREATE YOUR PUZZLE",
        heading_font, WHITE, 75, 175
    )

    # Picture categories
    draw_text(
        "Choose Picture Category",
        font, CYAN, 75, 240
    )

    category_buttons = {}

    for i, category in enumerate(CATEGORIES):

        rect = pygame.Rect(
            75 + i * 210, 280, 180, 50
        )

        category_buttons[category] = rect

        draw_button(
            category,
            rect,
            color=GREEN if category == selected_category
            else PURPLE
        )

    # Custom picture
    draw_button(
        "CHOOSE YOUR OWN PICTURE",
        pygame.Rect(75, 355, 390, 55),
        color=PINK
    )

    draw_text(
        picture_name,
        small_font, MUTED, 85, 420
    )

    # Difficulty
    draw_text(
        "Select Difficulty",
        font, CYAN, 75, 465
    )

    level_buttons = {}

    for i, level in enumerate(LEVELS):

        rect = pygame.Rect(
            75 + i * 210, 505, 180, 50
        )

        level_buttons[level] = rect

        draw_button(
            level,
            rect,
            color=GREEN if level == selected_level
            else PURPLE
        )

    # Play and exit
    draw_button(
        "PLAY GAME",
        pygame.Rect(650, 330, 240, 70),
        color=GREEN
    )

    draw_button(
        "EXIT GAME",
        pygame.Rect(650, 430, 240, 65),
        color=PINK
    )

    draw_text(
        "Choose your picture and start playing!",
        small_font, WHITE,
        500, 620, True
    )

    return category_buttons, level_buttons


# ==========================================
# 9. GAME SCREEN
# ==========================================

def draw_game():

    draw_background()

    draw_text(
        "PICTURE PUZZLE",
        heading_font, CYAN, 45, 35
    )

    draw_text(
        f"Category: {selected_category}",
        small_font, WHITE, 50, 105
    )

    draw_text(
        f"Level: {selected_level}",
        small_font, WHITE, 50, 135
    )

    elapsed = int(
        time.time() - start_time - paused_time
    )

    draw_glass(
        pygame.Rect(35, 180, 285, 250), 20
    )

    draw_text("GAME STATISTICS", font, CYAN, 65, 205)

    draw_text(
        f"Moves: {moves}",
        font, WHITE, 65, 260
    )

    draw_text(
        f"Time: {elapsed} sec",
        font, WHITE, 65, 310
    )

    draw_text(
        f"Grid: {grid_size} x {grid_size}",
        font, WHITE, 65, 360
    )

    # Game buttons
    draw_button(
        "SHUFFLE",
        pygame.Rect(55, 460, 115, 48)
    )

    draw_button(
        "RESTART",
        pygame.Rect(185, 460, 115, 48),
        color=PINK
    )

    draw_button(
        "PAUSE",
        pygame.Rect(55, 525, 115, 48),
        color=GREEN
    )

    draw_button(
        "HOME",
        pygame.Rect(185, 525, 115, 48),
        color=PINK
    )

    draw_puzzle()

    draw_text(
        "Drag any tile onto another tile to swap them",
        small_font, WHITE,
        650, 685, True
    )


# ==========================================
# 10. PAUSE SCREEN
# ==========================================

def draw_pause():

    draw_game()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT), pygame.SRCALPHA
    )

    overlay.fill((10, 10, 30, 190))

    screen.blit(overlay, (0, 0))

    draw_glass(
        pygame.Rect(300, 220, 400, 280), 25
    )

    draw_text(
        "GAME PAUSED",
        title_font, CYAN,
        500, 285, True
    )

    draw_button(
        "RESUME",
        pygame.Rect(370, 350, 260, 55),
        color=GREEN
    )

    draw_button(
        "HOME",
        pygame.Rect(370, 420, 260, 55),
        color=PINK
    )


# ==========================================
# 11. WIN SCREEN
# ==========================================

def draw_win():

    draw_background()

    draw_text(
        "YOU DID IT!",
        title_font, GREEN,
        500, 90, True
    )

    draw_text(
        "Congratulations! Picture completed!",
        heading_font, WHITE,
        500, 155, True
    )

    # Show completed picture
    preview = pygame.transform.smoothscale(
        image, (350, 350)
    )

    screen.blit(preview, (325, 205))

    pygame.draw.rect(
        screen, CYAN,
        (325, 205, 350, 350),
        3, border_radius=12
    )

    elapsed = int(
        time.time() - start_time - paused_time
    )

    draw_text(
        f"Moves: {moves}     Time: {elapsed} seconds",
        font, WHITE, 500, 590, True
    )

    draw_button(
        "PLAY AGAIN",
        pygame.Rect(260, 635, 210, 55),
        color=GREEN
    )

    draw_button(
        "HOME",
        pygame.Rect(530, 635, 210, 55),
        color=PINK
    )


# ==========================================
# 12. MAIN GAME LOOP
# ==========================================

running = True

while running:

    if game_state == "menu":

        category_buttons, level_buttons = draw_home()

    elif game_state == "playing":

        draw_game()

    elif game_state == "paused":

        draw_pause()

    elif game_state == "won":

        draw_win()

    # --------------------------------------
    # EVENTS
    # --------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Keyboard controls
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                if game_state == "playing":
                    pause_started = time.time()
                    game_state = "paused"

                elif game_state == "paused":
                    paused_time += time.time() - pause_started
                    game_state = "playing"

        # ----------------------------------
        # HOME SCREEN EVENTS
        # ----------------------------------

        if game_state == "menu":

            if event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = event.pos

                for category, rect in category_buttons.items():

                    if rect.collidepoint(mx, my):

                        selected_category = category

                        choose_category_picture(category)

                if pygame.Rect(
                    75, 355, 390, 55
                ).collidepoint(mx, my):

                    choose_picture()

                for level, rect in level_buttons.items():

                    if rect.collidepoint(mx, my):
                        selected_level = level

                if pygame.Rect(
                    650, 330, 240, 70
                ).collidepoint(mx, my):

                    if image is None:
                        choose_category_picture(selected_category)

                    if image is not None:

                        grid_size = LEVELS[selected_level]

                        shuffle_puzzle()

                        game_state = "playing"

                if pygame.Rect(
                    650, 430, 240, 65
                ).collidepoint(mx, my):

                    running = False

        # ----------------------------------
        # GAME SCREEN EVENTS
        # ----------------------------------

        elif game_state == "playing":

            if event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = event.pos

                if pygame.Rect(
                    55, 460, 115, 48
                ).collidepoint(mx, my):

                    shuffle_puzzle()

                elif pygame.Rect(
                    185, 460, 115, 48
                ).collidepoint(mx, my):

                    shuffle_puzzle()

                elif pygame.Rect(
                    55, 525, 115, 48
                ).collidepoint(mx, my):

                    pause_started = time.time()
                    game_state = "paused"

                elif pygame.Rect(
                    185, 525, 115, 48
                ).collidepoint(mx, my):

                    game_state = "menu"

                elif board_rect.collidepoint(mx, my):

                    for index in range(len(tiles)):

                        if get_tile_rect(index).collidepoint(mx, my):

                            dragging = True
                            drag_index = index
                            drag_position = (mx, my)
                            break

            if event.type == pygame.MOUSEMOTION:

                if dragging:
                    drag_position = event.pos

            if event.type == pygame.MOUSEBUTTONUP:

                if dragging and drag_index is not None:

                    mx, my = event.pos

                    if board_rect.collidepoint(mx, my):

                        for index in range(len(tiles)):

                            if get_tile_rect(index).collidepoint(mx, my):

                                swap_tiles(drag_index, index)
                                break

                    dragging = False
                    drag_index = None

                    if is_solved():
                        game_state = "won"

        # ----------------------------------
        # PAUSE SCREEN EVENTS
        # ----------------------------------

        elif game_state == "paused":

            if event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = event.pos

                if pygame.Rect(
                    370, 350, 260, 55
                ).collidepoint(mx, my):

                    paused_time += time.time() - pause_started
                    game_state = "playing"

                elif pygame.Rect(
                    370, 420, 260, 55
                ).collidepoint(mx, my):

                    game_state = "menu"

        # ----------------------------------
        # WIN SCREEN EVENTS
        # ----------------------------------

        elif game_state == "won":

            if event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = event.pos

                if pygame.Rect(
                    260, 635, 210, 55
                ).collidepoint(mx, my):

                    shuffle_puzzle()
                    game_state = "playing"

                elif pygame.Rect(
                    530, 635, 210, 55
                ).collidepoint(mx, my):

                    game_state = "menu"

    pygame.display.flip()
    clock.tick(60)


pygame.quit()
sys.exit()
