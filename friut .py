
import pygame
import random
import math
import json
import os
import sys

pygame.init()

# -------------------- CONFIGURATION --------------------

WIDTH, HEIGHT = 1100, 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("FRUIT CATCH | Ultimate Arcade")

clock = pygame.time.Clock()

# Fonts
FONT = pygame.font.SysFont("segoeui", 20)
SMALL = pygame.font.SysFont("segoeui", 15)
MEDIUM = pygame.font.SysFont("segoeui", 28, bold=True)
BIG = pygame.font.SysFont("segoeui", 54, bold=True)
LOGO = pygame.font.SysFont("segoeui", 65, bold=True)

# Colors
WHITE = (245, 248, 255)
MUTED = (165, 180, 205)
CYAN = (75, 225, 255)
PINK = (255, 105, 175)
PURPLE = (150, 115, 255)
GREEN = (100, 245, 180)
DARK = (12, 17, 38)

DATA_FILE = "fruit_catch_data.json"

# -------------------- GAME DATA --------------------

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "high_score": 0,
        "games_played": 0,
        "total_fruits": 0,
        "leaderboard": []
    }


data = load_data()

def save_data():
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except OSError:
        print("Could not save game data.")


# -------------------- BACKGROUND --------------------

particles = []

for _ in range(65):
    particles.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.uniform(0.3, 1.2),
        random.randint(2, 4)
    ])


def draw_background():
    screen.fill(DARK)

    # Gradient-like background
    for i in range(HEIGHT):
        blend = i / HEIGHT
        color = (
            int(12 + blend * 10),
            int(17 + blend * 8),
            int(38 + blend * 25)
        )
        pygame.draw.line(screen, color, (0, i), (WIDTH, i))

    # Glowing circles
    t = pygame.time.get_ticks() / 1000

    for x, y, color, radius in [
        (150, 180, PURPLE, 120),
        (950, 170, CYAN, 110),
        (550, 650, PINK, 130)
    ]:
        glow_x = x + math.sin(t + x) * 20
        glow_y = y + math.cos(t + y) * 15

        glow = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)

        for r in range(radius * 2, 0, -8):
            alpha = max(1, int(3 * (1 - r / (radius * 2))))
            pygame.draw.circle(
                glow,
                (*color, alpha),
                (radius * 2, radius * 2),
                r
            )

        screen.blit(
            glow,
            (glow_x - radius * 2, glow_y - radius * 2)
        )

    # Floating particles
    for particle in particles:
        particle[1] -= particle[2]

        if particle[1] < -10:
            particle[1] = HEIGHT + 10
            particle[0] = random.randint(0, WIDTH)

        pygame.draw.circle(
            screen,
            (100, 160, 220),
            (int(particle[0]), int(particle[1])),
            particle[3]
        )


# -------------------- UI HELPERS --------------------

def draw_text(text, font, color, x, y, center=True):
    image = font.render(str(text), True, color)
    rect = image.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(image, rect)
    return rect


def glass_panel(rect, radius=22):
    x, y, w, h = rect

    shadow = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
    pygame.draw.rect(
        shadow,
        (0, 0, 0, 65),
        (10, 10, w, h),
        border_radius=radius
    )
    screen.blit(shadow, (x - 10, y - 5))

    panel = pygame.Surface((w, h), pygame.SRCALPHA)

    pygame.draw.rect(
        panel,
        (255, 255, 255, 17),
        (0, 0, w, h),
        border_radius=radius
    )

    pygame.draw.rect(
        panel,
        (130, 190, 255, 75),
        (0, 0, w, h),
        width=1,
        border_radius=radius
    )

    screen.blit(panel, (x, y))


def draw_button(text, rect, mouse, color=CYAN):
    hovered = rect.collidepoint(mouse)

    x, y, w, h = rect

    # Glow
    if hovered:
        glow = pygame.Surface((w + 24, h + 24), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (*color, 45),
            (12, 12, w, h),
            border_radius=18
        )
        screen.blit(glow, (x - 12, y - 12))

    button = pygame.Surface((w, h), pygame.SRCALPHA)

    fill = (color[0], color[1], color[2], 55 if hovered else 27)

    pygame.draw.rect(
        button,
        fill,
        (0, 0, w, h),
        border_radius=15
    )

    pygame.draw.rect(
        button,
        (*color, 190 if hovered else 100),
        (0, 0, w, h),
        width=2,
        border_radius=15
    )

    screen.blit(button, (x, y))

    draw_text(
        text,
        FONT,
        WHITE if hovered else MUTED,
        x + w // 2,
        y + h // 2
    )

    return hovered


# -------------------- FRUIT DRAWING --------------------

FRUITS = [
    ("apple", (255, 75, 100), 10),
    ("orange", (255, 165, 60), 10),
    ("watermelon", (90, 230, 140), 15),
    ("grape", (175, 105, 255), 12),
    ("strawberry", (255, 85, 140), 15),
    ("lemon", (255, 225, 80), 10)
]


def draw_fruit(fruit):
    x = int(fruit["x"])
    y = int(fruit["y"])
    kind = fruit["kind"]
    color = fruit["color"]

    # Glow
    glow = pygame.Surface((85, 85), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*color, 25), (42, 42), 35)
    screen.blit(glow, (x - 42, y - 42))

    if kind == "watermelon":
        pygame.draw.ellipse(screen, (55, 180, 105), (x - 24, y - 18, 48, 38))
        pygame.draw.ellipse(screen, (120, 245, 145), (x - 20, y - 14, 40, 30))
        pygame.draw.ellipse(screen, (255, 95, 125), (x - 16, y - 10, 32, 22))

    elif kind == "lemon":
        pygame.draw.ellipse(screen, color, (x - 25, y - 15, 50, 30))

    elif kind == "grape":
        for dx, dy in [(-10, -7), (10, -7), (0, 8), (-10, 12), (10, 12)]:
            pygame.draw.circle(screen, color, (x + dx, y + dy), 11)

    elif kind == "strawberry":
        pygame.draw.polygon(
            screen,
            color,
            [(x - 19, y - 12), (x + 19, y - 12), (x, y + 24)]
        )
        pygame.draw.circle(screen, color, (x, y - 8), 18)

    else:
        pygame.draw.circle(screen, color, (x, y), 22)

    # Leaf
    if kind in ("apple", "orange", "strawberry"):
        pygame.draw.ellipse(
            screen,
            GREEN,
            (x + 2, y - 27, 15, 9)
        )

    # Shine
    pygame.draw.circle(
        screen,
        (255, 255, 255),
        (x - 8, y - 9),
        4
    )


# -------------------- BASKET --------------------

def draw_basket(x, y):
    # Basket glow
    glow = pygame.Surface((150, 80), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (70, 220, 255, 35), (10, 10, 130, 60))
    screen.blit(glow, (x - 75, y - 35))

    # Basket
    pygame.draw.arc(
        screen,
        CYAN,
        (x - 42, y - 32, 84, 65),
        math.pi,
        2 * math.pi,
        5
    )

    pygame.draw.polygon(
        screen,
        (50, 170, 205),
        [
            (x - 43, y - 5),
            (x + 43, y - 5),
            (x + 31, y + 30),
            (x - 31, y + 30)
        ]
    )

    pygame.draw.lines(
        screen,
        (125, 235, 255),
        False,
        [
            (x - 43, y - 5),
            (x + 43, y - 5),
            (x + 31, y + 30),
            (x - 31, y + 30),
            (x - 43, y - 5)
        ],
        3
    )

    pygame.draw.line(
        screen,
        (160, 245, 255),
        (x - 22, y),
        (x - 16, y + 25),
        2
    )

    pygame.draw.line(
        screen,
        (160, 245, 255),
        (x + 22, y),
        (x + 16, y + 25),
        2
    )


# -------------------- BUTTON LAYOUT --------------------

def main_buttons():
    return {
        "play": pygame.Rect(400, 300, 300, 58),
        "mode": pygame.Rect(400, 375, 300, 52),
        "stats": pygame.Rect(400, 445, 145, 48),
        "how": pygame.Rect(555, 445, 145, 48),
        "settings": pygame.Rect(400, 510, 145, 48),
        "leaderboard": pygame.Rect(555, 510, 145, 48),
        "exit": pygame.Rect(400, 575, 300, 45)
    }


# -------------------- GAME SETTINGS --------------------

screen_state = "menu"

difficulty = "Normal"
game_mode = "Classic"

DIFFICULTIES = ["Easy", "Normal", "Hard"]

DIFFICULTY_SETTINGS = {
    "Easy": {"speed": 3.5, "spawn": 1.1, "time": 75},
    "Normal": {"speed": 5, "spawn": 0.8, "time": 60},
    "Hard": {"speed": 7, "spawn": 0.55, "time": 45}
}

score = 0
lives = 5
remaining_time = 60
fruits_caught = 0
fruits_missed = 0

basket_x = WIDTH // 2
basket_y = HEIGHT - 85
basket_speed = 8

fruits = []
spawn_timer = 0

# -------------------- GAME FUNCTIONS --------------------

def start_game():
    global screen_state, score, lives
    global remaining_time, fruits_caught, fruits_missed
    global fruits, basket_x, spawn_timer

    score = 0
    lives = 5
    fruits_caught = 0
    fruits_missed = 0

    settings = DIFFICULTY_SETTINGS[difficulty]
    remaining_time = settings["time"]

    fruits = []
    basket_x = WIDTH // 2
    spawn_timer = 0

    screen_state = "game"


def spawn_fruit():
    kind, color, points = random.choice(FRUITS)

    fruits.append({
        "x": random.randint(45, WIDTH - 45),
        "y": -35,
        "kind": kind,
        "color": color,
        "points": points,
        "speed": DIFFICULTY_SETTINGS[difficulty]["speed"]
    })


def finish_game():
    global screen_state

    data["games_played"] += 1
    data["total_fruits"] += fruits_caught

    if score > data["high_score"]:
        data["high_score"] = score

    data["leaderboard"].append(score)
    data["leaderboard"] = sorted(
        data["leaderboard"],
        reverse=True
    )[:10]

    save_data()
    screen_state = "gameover"


def update_game(dt):
    global score, lives, remaining_time
    global fruits_caught, fruits_missed
    global spawn_timer, basket_x

    settings = DIFFICULTY_SETTINGS[difficulty]

    remaining_time -= dt

    if remaining_time <= 0 or lives <= 0:
        remaining_time = max(0, remaining_time)
        finish_game()
        return

    # Basket movement
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        basket_x -= basket_speed

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        basket_x += basket_speed

    basket_x = max(45, min(WIDTH - 45, basket_x))

    # Spawn fruits
    spawn_timer += dt

    if spawn_timer >= settings["spawn"]:
        spawn_fruit()
        spawn_timer = 0

    # Move fruits
    for fruit in fruits[:]:
        fruit["y"] += fruit["speed"] * 60 * dt

        # Catch fruit
        caught = (
            abs(fruit["x"] - basket_x) < 52
            and basket_y - 25 < fruit["y"] < basket_y + 25
        )

        if caught:
            score += fruit["points"]
            fruits_caught += 1
            fruits.remove(fruit)
            continue

        # Missed fruit
        if fruit["y"] > HEIGHT + 30:
            fruits.remove(fruit)
            fruits_missed += 1
            lives -= 1


# -------------------- MENU --------------------

def draw_menu(mouse):
    draw_background()

    t = pygame.time.get_ticks() / 1000
    logo_y = 130 + math.sin(t * 2) * 8

    draw_text(
        "FRUIT",
        LOGO,
        CYAN,
        WIDTH // 2,
        int(logo_y)
    )

    draw_text(
        "CATCH",
        LOGO,
        PINK,
        WIDTH // 2,
        int(logo_y + 65)
    )

    draw_text(
        "THE ULTIMATE FRUIT CATCHING ARCADE",
        SMALL,
        MUTED,
        WIDTH // 2,
        235
    )

    buttons = main_buttons()

    draw_button("▶  PLAY GAME", buttons["play"], mouse, CYAN)
    draw_button("🎮  SELECT MODE", buttons["mode"], mouse, PURPLE)

    draw_button("STATISTICS", buttons["stats"], mouse, GREEN)
    draw_button("HOW TO PLAY", buttons["how"], mouse, CYAN)

    draw_button("SETTINGS", buttons["settings"], mouse, PURPLE)
    draw_button("LEADERBOARD", buttons["leaderboard"], mouse, PINK)

    draw_button("EXIT GAME", buttons["exit"], mouse, PINK)

    draw_text(
        f"PERSONAL BEST: {data['high_score']}",
        SMALL,
        MUTED,
        WIDTH // 2,
        660
    )


# -------------------- MODE SELECTION --------------------

def draw_mode(mouse):
    draw_background()
    glass_panel((300, 120, 500, 490))

    draw_text("SELECT GAME MODE", BIG, WHITE, WIDTH // 2, 180)

    modes = [
        ("CLASSIC", "Catch fruits and beat the timer"),
        ("SURVIVAL", "Catch fruits while protecting your lives")
    ]

    mode_rects = [
        pygame.Rect(365, 270, 370, 90),
        pygame.Rect(365, 385, 370, 90)
    ]

    for i, (name, description) in enumerate(modes):
        rect = mode_rects[i]
        color = CYAN if game_mode == name.title() else PURPLE

        draw_button(name, rect, mouse, color)
        draw_text(description, SMALL, MUTED, WIDTH // 2, rect.y + 65)

    back = pygame.Rect(425, 535, 250, 48)
    draw_button("BACK TO MENU", back, mouse, PINK)

    return mode_rects, back


# -------------------- DIFFICULTY SCREEN --------------------

def draw_difficulty(mouse):
    draw_background()
    glass_panel((300, 150, 500, 420))

    draw_text("CHOOSE DIFFICULTY", BIG, WHITE, WIDTH // 2, 220)

    rects = []

    for i, level in enumerate(DIFFICULTIES):
        rect = pygame.Rect(390, 290 + i * 70, 320, 52)
        rects.append(rect)

        color = GREEN if difficulty == level else CYAN
        draw_button(level.upper(), rect, mouse, color)

    back = pygame.Rect(425, 510, 250, 45)
    draw_button("BACK", back, mouse, PINK)

    return rects, back


# -------------------- GAME SCREEN --------------------

def draw_game():
    draw_background()

    # Game panel
    glass_panel((25, 20, WIDTH - 50, 75), 18)

    draw_text(
        f"SCORE  {score}",
        MEDIUM,
        CYAN,
        140,
        57
    )

    draw_text(
        f"TIME  {max(0, int(remaining_time))}s",
        MEDIUM,
        PINK,
        WIDTH // 2,
        57
    )

    draw_text(
        f"LIVES  {'♥ ' * lives}",
        MEDIUM,
        GREEN,
        WIDTH - 160,
        57
    )

    # Timer bar
    total_time = DIFFICULTY_SETTINGS[difficulty]["time"]
    bar_width = int((max(0, remaining_time) / total_time) * 350)

    pygame.draw.rect(
        screen,
        (45, 55, 85),
        (WIDTH // 2 - 175, 105, 350, 9),
        border_radius=5
    )

    pygame.draw.rect(
        screen,
        PINK,
        (WIDTH // 2 - 175, 105, bar_width, 9),
        border_radius=5
    )

    # Fruits
    for fruit in fruits:
        draw_fruit(fruit)

    # Basket
    draw_basket(basket_x, basket_y)

    draw_text(
        "MOVE: ← → or A / D       PAUSE: SPACE",
        SMALL,
        MUTED,
        WIDTH // 2,
        HEIGHT - 22
    )


# -------------------- PAUSE SCREEN --------------------

def draw_pause(mouse):
    draw_game()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 10, 30, 175))
    screen.blit(overlay, (0, 0))

    glass_panel((350, 245, 400, 230))

    draw_text("GAME PAUSED", BIG, WHITE, WIDTH // 2, 300)

    resume = pygame.Rect(420, 360, 260, 45)
    menu = pygame.Rect(420, 420, 260, 40)

    draw_button("RESUME", resume, mouse, GREEN)
    draw_button("MAIN MENU", menu, mouse, PINK)

    return resume, menu


# -------------------- GAME OVER --------------------

def draw_gameover(mouse):
    draw_background()

    glass_panel((320, 125, 460, 470))

    draw_text("GAME OVER", BIG, PINK, WIDTH // 2, 195)

    draw_text("YOUR FINAL SCORE", FONT, MUTED, WIDTH // 2, 275)
    draw_text(str(score), BIG, CYAN, WIDTH // 2, 330)

    draw_text(
        f"Fruits caught: {fruits_caught}",
        FONT,
        WHITE,
        WIDTH // 2,
        390
    )

    draw_text(
        f"Fruits missed: {fruits_missed}",
        FONT,
        MUTED,
        WIDTH // 2,
        425
    )

    draw_text(
        f"Personal best: {data['high_score']}",
        SMALL,
        GREEN,
        WIDTH // 2,
        460
    )

    again = pygame.Rect(405, 500, 290, 48)
    menu = pygame.Rect(405, 560, 290, 40)

    draw_button("PLAY AGAIN", again, mouse, CYAN)
    draw_button("MAIN MENU", menu, mouse, PINK)

    return again, menu


# -------------------- INFORMATION SCREENS --------------------

def draw_info(title, lines, mouse):
    draw_background()
    glass_panel((260, 115, 580, 500))

    draw_text(title, BIG, WHITE, WIDTH // 2, 180)

    for i, line in enumerate(lines):
        draw_text(
            line,
            FONT,
            MUTED,
            WIDTH // 2,
            275 + i * 48
        )

    back = pygame.Rect(420, 535, 260, 48)
    draw_button("BACK TO MENU", back, mouse, PINK)

    return back


def draw_settings(mouse):
    draw_background()
    glass_panel((300, 135, 500, 460))

    draw_text("SETTINGS", BIG, WHITE, WIDTH // 2, 205)

    draw_text(
        f"DIFFICULTY: {difficulty.upper()}",
        MEDIUM,
        CYAN,
        WIDTH // 2,
        300
    )

    rects = []

    for i, level in enumerate(DIFFICULTIES):
        rect = pygame.Rect(390, 345 + i * 55, 320, 42)
        rects.append(rect)

        draw_button(
            level.upper(),
            rect,
            mouse,
            GREEN if difficulty == level else PURPLE
        )

    back = pygame.Rect(425, 525, 250, 42)
    draw_button("BACK", back, mouse, PINK)

    return rects, back


# -------------------- MAIN LOOP --------------------

running = True
paused = False

while running:
    dt = clock.tick(FPS) / 1000
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            save_data()
            running = False

        # Keep the game usable when the window is resized
        elif event.type == pygame.VIDEORESIZE:
            WIDTH = max(800, event.w)
            HEIGHT = max(600, event.h)
            screen = pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.RESIZABLE
            )
            basket_y = HEIGHT - 85
            basket_x = max(45, min(WIDTH - 45, basket_x))

        elif event.type == pygame.KEYDOWN:

            if screen_state == "game":
                if event.key == pygame.K_SPACE:
                    screen_state = "pause"

            elif screen_state == "pause":
                if event.key == pygame.K_SPACE:
                    screen_state = "game"
                elif event.key == pygame.K_ESCAPE:
                    screen_state = "menu"

            elif event.key == pygame.K_ESCAPE:
                screen_state = "menu"

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if screen_state == "menu":
                buttons = main_buttons()

                if buttons["play"].collidepoint(mouse):
                    screen_state = "difficulty"

                elif buttons["mode"].collidepoint(mouse):
                    screen_state = "mode"

                elif buttons["stats"].collidepoint(mouse):
                    screen_state = "stats"

                elif buttons["how"].collidepoint(mouse):
                    screen_state = "how"

                elif buttons["settings"].collidepoint(mouse):
                    screen_state = "settings"

                elif buttons["leaderboard"].collidepoint(mouse):
                    screen_state = "leaderboard"

                elif buttons["exit"].collidepoint(mouse):
                    save_data()
                    running = False

            elif screen_state == "mode":
                rects, back = draw_mode(mouse)

                if rects[0].collidepoint(mouse):
                    game_mode = "Classic"

                elif rects[1].collidepoint(mouse):
                    game_mode = "Survival"

                elif back.collidepoint(mouse):
                    screen_state = "menu"

            elif screen_state == "difficulty":
                rects, back = draw_difficulty(mouse)

                for i, rect in enumerate(rects):
                    if rect.collidepoint(mouse):
                        difficulty = DIFFICULTIES[i]
                        start_game()

                if back.collidepoint(mouse):
                    screen_state = "menu"

            elif screen_state == "pause":
                resume, menu = draw_pause(mouse)

                if resume.collidepoint(mouse):
                    screen_state = "game"

                elif menu.collidepoint(mouse):
                    screen_state = "menu"

            elif screen_state == "gameover":
                again, menu = draw_gameover(mouse)

                if again.collidepoint(mouse):
                    start_game()

                elif menu.collidepoint(mouse):
                    screen_state = "menu"

            elif screen_state == "stats":
                back = pygame.Rect(420, 535, 260, 48)
                if back.collidepoint(mouse):
                    screen_state = "menu"

            elif screen_state == "how":
                back = pygame.Rect(420, 535, 260, 48)
                if back.collidepoint(mouse):
                    screen_state = "menu"

            elif screen_state == "leaderboard":
                back = pygame.Rect(420, 535, 260, 48)
                if back.collidepoint(mouse):
                    screen_state = "menu"

            elif screen_state == "settings":
                rects, back = draw_settings(mouse)

                for i, rect in enumerate(rects):
                    if rect.collidepoint(mouse):
                        difficulty = DIFFICULTIES[i]

                if back.collidepoint(mouse):
                    screen_state = "menu"

    # -------------------- DRAW STATES --------------------

    if screen_state == "menu":
        draw_menu(mouse)

    elif screen_state == "mode":
        draw_mode(mouse)

    elif screen_state == "difficulty":
        draw_difficulty(mouse)

    elif screen_state == "game":
        update_game(dt)
        draw_game()

    elif screen_state == "pause":
        draw_pause(mouse)

    elif screen_state == "gameover":
        draw_gameover(mouse)

    elif screen_state == "stats":
        draw_info(
            "PLAYER STATISTICS",
            [
                f"Games played: {data['games_played']}",
                f"Personal best: {data['high_score']}",
                f"Total fruits caught: {data['total_fruits']}",
                f"Current difficulty: {difficulty}"
            ],
            mouse
        )

    elif screen_state == "how":
        draw_info(
            "HOW TO PLAY",
            [
                "Move basket using LEFT and RIGHT arrows",
                "You can also use A and D keys",
                "Catch falling fruits to earn points",
                "Each fruit gives you 10-15 points",
                "Avoid missing fruits: you have 5 lives",
                "Beat the countdown and set a high score!"
            ],
            mouse
        )

    elif screen_state == "leaderboard":
        lines = ["TOP 10 SCORES"]

        for i, value in enumerate(data["leaderboard"][:10]):
            lines.append(f"{i + 1}.  {value} points")

        draw_info("LEADERBOARD", lines, mouse)

    elif screen_state == "settings":
        draw_settings(mouse)

    pygame.display.flip()


save_data()
pygame.quit()
sys.exit()
