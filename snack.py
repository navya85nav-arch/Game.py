
import pygame
import random
import math
import sys
import os

pygame.init()

# =====================================================
# CONFIGURATION
# =====================================================

WIDTH, HEIGHT = 1100, 760
FPS = 60

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT), pygame.RESIZABLE
)

pygame.display.set_caption("NEON SNAKE | Arcade Edition")
clock = pygame.time.Clock()

# Grid configuration
COLS = 24
ROWS = 18

# Neon color palette
WHITE = (245, 248, 255)
MUTED = (145, 160, 190)
PURPLE = (165, 90, 255)
CYAN = (40, 225, 255)
BLUE = (65, 115, 255)
GREEN = (80, 255, 170)
PINK = (255, 85, 175)

BG_TOP = (10, 13, 32)
BG_BOTTOM = (30, 17, 58)

# Typography
def get_font(size, bold=False):
    return pygame.font.SysFont(
        "segoeui", size, bold=bold
    )


# =====================================================
# GAME VARIABLES
# =====================================================

snake = [(12, 9), (11, 9), (10, 9)]

direction = (1, 0)
next_direction = (1, 0)

food = (17, 9)

score = 0
high_score = 0

game_state = "playing"

move_timer = 0
move_delay = 125

food_animation = 0
particles = []

# High score storage
HIGH_SCORE_FILE = "highscore.txt"


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read().strip())
    except (OSError, ValueError):
        return 0


def save_high_score():
    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(high_score))
    except OSError:
        pass


high_score = load_high_score()


# =====================================================
# BACKGROUND
# =====================================================

background_cache = None
background_size = None


def create_background():
    global background_cache, background_size

    size = screen.get_size()

    if background_cache is not None and background_size == size:
        return

    width, height = size

    background_cache = pygame.Surface(
        (width, height)
    )

    for y in range(height):
        ratio = y / max(height, 1)

        color = tuple(
            int(BG_TOP[i] * (1-ratio) +
                BG_BOTTOM[i] * ratio)
            for i in range(3)
        )

        pygame.draw.line(
            background_cache,
            color,
            (0, y),
            (width, y)
        )

    background_size = size


def draw_background():
    create_background()
    screen.blit(background_cache, (0, 0))

    # Decorative glowing orbs
    t = pygame.time.get_ticks() / 1000

    for x, y, radius, color in [
        (90, 130, 130, PURPLE),
        (950, 580, 170, CYAN),
        (WIDTH // 2, HEIGHT - 20, 110, BLUE)
    ]:
        glow = pygame.Surface(
            (radius * 2, radius * 2),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            glow,
            (*color, 12),
            (radius, radius),
            radius
        )

        screen.blit(
            glow,
            (
                int(x + math.sin(t + x) * 8) - radius,
                int(y + math.cos(t + y) * 8) - radius
            )
        )


# =====================================================
# TEXT RENDERING
# =====================================================

def draw_text(text, size, color, center, bold=False):
    surface = get_font(size, bold).render(
        str(text), True, color
    )

    rect = surface.get_rect(center=center)
    screen.blit(surface, rect)


# =====================================================
# GLASSMORPHISM CARD
# =====================================================

def draw_glass_card(rect, border_color=PURPLE):
    x, y, w, h = rect

    # Soft shadow
    shadow = pygame.Surface(
        (w + 20, h + 20), pygame.SRCALPHA
    )

    pygame.draw.rect(
        shadow,
        (0, 0, 0, 65),
        (10, 10, w, h),
        border_radius=22
    )

    screen.blit(shadow, (x - 10, y - 10))

    # Glass panel
    panel = pygame.Surface(
        (w, h), pygame.SRCALPHA
    )

    pygame.draw.rect(
        panel,
        (255, 255, 255, 19),
        (0, 0, w, h),
        border_radius=22
    )

    pygame.draw.rect(
        panel,
        (*border_color, 115),
        (0, 0, w, h),
        1,
        border_radius=22
    )

    screen.blit(panel, (x, y))


# =====================================================
# INTERACTIVE BUTTON
# =====================================================

def draw_button(text, rect, color=PURPLE):
    mouse = pygame.mouse.get_pos()

    hovering = pygame.Rect(rect).collidepoint(mouse)

    active_color = (
        CYAN if hovering else color
    )

    draw_glass_card(rect, active_color)

    center = pygame.Rect(rect).center

    draw_text(
        text,
        17,
        WHITE,
        center,
        True
    )

    return pygame.Rect(rect)


# =====================================================
# GAME HELPERS
# =====================================================

def random_food():
    available = [
        (x, y)
        for x in range(COLS)
        for y in range(ROWS)
        if (x, y) not in snake
    ]

    if not available:
        return None

    return random.choice(available)


def reset_game():
    global snake, direction, next_direction
    global food, score, game_state, move_timer
    global move_delay, particles

    snake = [
        (12, 9),
        (11, 9),
        (10, 9)
    ]

    direction = (1, 0)
    next_direction = (1, 0)

    food = random_food()

    score = 0
    move_timer = 0
    move_delay = 125

    particles.clear()
    game_state = "playing"


def create_particles(position):
    for _ in range(16):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1, 4)

        particles.append({
            "x": position[0],
            "y": position[1],
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": 30,
            "color": random.choice(
                [GREEN, CYAN, PURPLE, PINK]
            )
        })


def update_particles():
    for particle in particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["life"] -= 1

        if particle["life"] <= 0:
            particles.remove(particle)


def draw_particles():
    for particle in particles:
        alpha = max(
            0, min(255, particle["life"] * 8)
        )

        particle_surface = pygame.Surface(
            (10, 10), pygame.SRCALPHA
        )

        pygame.draw.circle(
            particle_surface,
            (*particle["color"], alpha),
            (5, 5),
            4
        )

        screen.blit(
            particle_surface,
            (
                int(particle["x"] - 5),
                int(particle["y"] - 5)
            )
        )


# =====================================================
# GAME MOVEMENT
# =====================================================

def update_game():
    global snake, direction, food
    global score, high_score
    global game_state, move_delay

    direction = next_direction

    head_x, head_y = snake[0]

    new_head = (
        head_x + direction[0],
        head_y + direction[1]
    )

    growing = new_head == food

    # Wall collision
    if (
        new_head[0] < 0
        or new_head[0] >= COLS
        or new_head[1] < 0
        or new_head[1] >= ROWS
    ):
        game_state = "over"
        return

    # Allow moving into the old tail position
    body_to_check = snake if growing else snake[:-1]

    if new_head in body_to_check:
        game_state = "over"
        return

    snake.insert(0, new_head)

    if growing:
        score += 10

        create_particles(food)

        if score > high_score:
            high_score = score
            save_high_score()

        food = random_food()

        if food is None:
            game_state = "won"
            return

        # Gradually increase speed
        move_delay = max(65, 125 - score // 30)

    else:
        snake.pop()


def change_direction(new_direction):
    global next_direction

    # Prevent reverse movement
    if (
        new_direction[0] + direction[0] == 0
        and new_direction[1] + direction[1] == 0
    ):
        return

    next_direction = new_direction


# =====================================================
# RESPONSIVE BOARD LAYOUT
# =====================================================

def get_board_rect():
    available_width = WIDTH - 100
    available_height = HEIGHT - 245

    cell = min(
        available_width // COLS,
        available_height // ROWS
    )

    cell = max(10, cell)

    board_width = COLS * cell
    board_height = ROWS * cell

    x = (WIDTH - board_width) // 2
    y = 190 + max(
        0, (available_height - board_height) // 2
    )

    return pygame.Rect(
        x, y, board_width, board_height
    ), cell


# =====================================================
# DRAW SNAKE
# =====================================================

def draw_snake(board_rect, cell):
    for index, segment in enumerate(snake):
        x, y = segment

        px = board_rect.x + x * cell
        py = board_rect.y + y * cell

        margin = max(2, cell // 12)

        rect = pygame.Rect(
            px + margin,
            py + margin,
            cell - margin * 2,
            cell - margin * 2
        )

        color = (
            GREEN if index == 0
            else (
                CYAN if index % 2
                else (75, 175, 220)
            )
        )

        # Soft snake glow
        if index == 0:
            glow = pygame.Surface(
                (cell * 2, cell * 2),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                glow,
                (*GREEN, 35),
                (cell, cell),
                cell // 1.5
            )

            screen.blit(
                glow,
                (px - cell // 2, py - cell // 2)
            )

        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=max(4, cell // 3)
        )

        # Head eyes
        if index == 0:
            eye_radius = max(2, cell // 11)

            if direction == (1, 0):
                eyes = [
                    (rect.centerx + 5, rect.centery - 5),
                    (rect.centerx + 5, rect.centery + 5)
                ]
            elif direction == (-1, 0):
                eyes = [
                    (rect.centerx - 5, rect.centery - 5),
                    (rect.centerx - 5, rect.centery + 5)
                ]
            elif direction == (0, -1):
                eyes = [
                    (rect.centerx - 5, rect.centery - 5),
                    (rect.centerx + 5, rect.centery - 5)
                ]
            else:
                eyes = [
                    (rect.centerx - 5, rect.centery + 5),
                    (rect.centerx + 5, rect.centery + 5)
                ]

            for eye in eyes:
                pygame.draw.circle(
                    screen, WHITE, eye, eye_radius
                )


# =====================================================
# DRAW FOOD
# =====================================================

def draw_food(board_rect, cell):
    if food is None:
        return

    t = pygame.time.get_ticks() / 180

    pulse = 1 + math.sin(t) * 0.12

    x = board_rect.x + food[0] * cell + cell // 2
    y = board_rect.y + food[1] * cell + cell // 2

    radius = max(4, int(cell * 0.29 * pulse))

    # Outer glow
    glow = pygame.Surface(
        (cell * 3, cell * 3),
        pygame.SRCALPHA
    )

    pygame.draw.circle(
        glow,
        (*PINK, 35),
        (cell * 1.5, cell * 1.5),
        int(cell * 0.8 * pulse)
    )

    screen.blit(
        glow,
        (x - cell * 1.5, y - cell * 1.5)
    )

    # Food core
    pygame.draw.circle(
        screen, PINK, (x, y), radius
    )

    pygame.draw.circle(
        screen, WHITE,
        (x - radius // 3, y - radius // 3),
        max(2, radius // 4)
    )


# =====================================================
# HEADER & SCOREBOARD
# =====================================================

def draw_header():
    draw_text(
        "NEON SNAKE",
        38,
        WHITE,
        (WIDTH // 2, 48),
        True
    )

    draw_text(
        "ARCADE EDITION  •  LEVEL UP YOUR GAME",
        13,
        CYAN,
        (WIDTH // 2, 83)
    )

    # Score card
    card_width = min(230, (WIDTH - 70) // 3)

    score_rect = (
        WIDTH // 2 - card_width - 15,
        105,
        card_width,
        62
    )

    high_rect = (
        WIDTH // 2 + 15,
        105,
        card_width,
        62
    )

    draw_glass_card(score_rect, GREEN)
    draw_glass_card(high_rect, PURPLE)

    draw_text(
        f"SCORE  {score}",
        19,
        GREEN,
        (score_rect[0] + card_width // 2, 136),
        True
    )

    draw_text(
        f"BEST  {high_score}",
        19,
        PURPLE,
        (high_rect[0] + card_width // 2, 136),
        True
    )


# =====================================================
# GAME SCREEN
# =====================================================

def draw_game():
    draw_background()
    draw_header()

    board_rect, cell = get_board_rect()

    # Board glass panel
    panel = board_rect.inflate(24, 24)

    draw_glass_card(panel, CYAN)

    # Subtle board grid
    for x in range(COLS + 1):
        px = board_rect.x + x * cell

        pygame.draw.line(
            screen,
            (255, 255, 255, 20),
            (px, board_rect.y),
            (px, board_rect.bottom),
            1
        )

    for y in range(ROWS + 1):
        py = board_rect.y + y * cell

        pygame.draw.line(
            screen,
            (255, 255, 255, 20),
            (board_rect.x, py),
            (board_rect.right, py),
            1
        )

    draw_food(board_rect, cell)
    draw_snake(board_rect, cell)

    draw_particles()

    # Bottom controls
    button_width = 145
    gap = 20
    total_width = button_width * 2 + gap

    start_x = (WIDTH - total_width) // 2
    button_y = HEIGHT - 65

    pause_label = (
        "RESUME" if game_state == "paused"
        else "PAUSE"
    )

    pause_rect = draw_button(
        pause_label,
        (start_x, button_y, button_width, 45),
        PURPLE
    )

    restart_rect = draw_button(
        "RESTART",
        (
            start_x + button_width + gap,
            button_y,
            button_width,
            45
        ),
        CYAN
    )

    return pause_rect, restart_rect


# =====================================================
# GAME OVER OVERLAY
# =====================================================

def draw_overlay(title, subtitle, color):
    overlay = pygame.Surface(
        (WIDTH, HEIGHT), pygame.SRCALPHA
    )

    overlay.fill((5, 8, 25, 175))
    screen.blit(overlay, (0, 0))

    card = (
        WIDTH // 2 - 220,
        HEIGHT // 2 - 125,
        440,
        250
    )

    draw_glass_card(card, color)

    draw_text(
        title,
        36,
        color,
        (WIDTH // 2, HEIGHT // 2 - 65),
        True
    )

    draw_text(
        subtitle,
        19,
        WHITE,
        (WIDTH // 2, HEIGHT // 2 - 15)
    )

    draw_button(
        "PLAY AGAIN",
        (
            WIDTH // 2 - 100,
            HEIGHT // 2 + 35,
            200,
            48
        ),
        color
    )


# =====================================================
# EVENT HANDLING
# =====================================================

def handle_click(position, pause_rect, restart_rect):
    global game_state

    if restart_rect.collidepoint(position):
        reset_game()
        return

    if pause_rect.collidepoint(position):
        if game_state == "playing":
            game_state = "paused"

        elif game_state == "paused":
            game_state = "playing"

        return

    if game_state in ("over", "won"):
        card_button = pygame.Rect(
            WIDTH // 2 - 100,
            HEIGHT // 2 + 35,
            200,
            48
        )

        if card_button.collidepoint(position):
            reset_game()


# =====================================================
# MAIN GAME LOOP
# =====================================================

running = True

while running:

    dt = clock.tick(FPS)
    move_timer += dt
    food_animation += dt

    pause_rect = pygame.Rect(0, 0, 0, 0)
    restart_rect = pygame.Rect(0, 0, 0, 0)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Window resizing
        if event.type == pygame.VIDEORESIZE:
            WIDTH = max(650, event.w)
            HEIGHT = max(540, event.h)

            screen = pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.RESIZABLE
            )

            background_cache = None

        # Keyboard controls
        if event.type == pygame.KEYDOWN:

            if event.key in (
                pygame.K_UP, pygame.K_w
            ):
                change_direction((0, -1))

            elif event.key in (
                pygame.K_DOWN, pygame.K_s
            ):
                change_direction((0, 1))

            elif event.key in (
                pygame.K_LEFT, pygame.K_a
            ):
                change_direction((-1, 0))

            elif event.key in (
                pygame.K_RIGHT, pygame.K_d
            ):
                change_direction((1, 0))

            elif event.key == pygame.K_SPACE:
                if game_state == "playing":
                    game_state = "paused"

                elif game_state == "paused":
                    game_state = "playing"

            elif event.key == pygame.K_r:
                reset_game()

            elif event.key == pygame.K_ESCAPE:
                if game_state == "playing":
                    game_state = "paused"

                elif game_state == "paused":
                    game_state = "playing"

        # Mouse controls
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                handle_click(
                    event.pos,
                    pause_rect,
                    restart_rect
                )

    # Update game
    if game_state == "playing":

        if move_timer >= move_delay:
            update_game()
            move_timer = 0

    update_particles()

    # Render
    pause_rect, restart_rect = draw_game()

    if game_state == "paused":
        draw_overlay(
            "PAUSED",
            "Take a break. Your game is waiting!",
            CYAN
        )

    elif game_state == "over":
        draw_overlay(
            "GAME OVER",
            f"Your final score: {score}",
            PINK
        )

    elif game_state == "won":
        draw_overlay(
            "YOU WIN!",
            f"Perfect! Final score: {score}",
            GREEN
        )

    pygame.display.flip()


# =====================================================
# CLEAN EXIT
# =====================================================

save_high_score()
pygame.quit()
sys.exit()
