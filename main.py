
import asyncio
import pygame
import sys
import os
import random
import math
import array

pygame.init()

# =========================================================
# CLEAR WEB + MOBILE RESPONSIVE SETUP
# =========================================================
# This version fixes the GitHub/Pygbag browser problem where the game appears as
# a small blurry desktop canvas with grey space around it. It reads the real
# browser viewport, uses a portrait mobile layout on phones, and forces the
# canvas to fill the Chrome/Safari screen.
IS_BROWSER = sys.platform == "emscripten"

DESKTOP_SIZE = (1000, 700)
MOBILE_SIZE = (430, 760)

DISPLAY_W, DISPLAY_H = DESKTOP_SIZE
WIDTH, HEIGHT = DESKTOP_SIZE
MOBILE_LAYOUT = False

try:
    DISPLAY_FLAGS = pygame.RESIZABLE
except Exception:
    DISPLAY_FLAGS = 0


def get_js_viewport_size():
    """Return the real browser viewport size in CSS pixels when running in Pygbag."""
    if not IS_BROWSER:
        return None
    try:
        import platform as browser_platform
        window = getattr(browser_platform, "window", None)
        if window is None:
            return None

        # innerWidth/innerHeight are the visible page area. This is more reliable
        # on GitHub Pages than pygame.display.Info(), which can return the old
        # desktop canvas size such as 1000x700.
        w = int(window.innerWidth)
        h = int(window.innerHeight)
        if w > 0 and h > 0:
            return w, h
    except Exception:
        pass
    return None


def apply_browser_page_fix():
    """Make the generated Pygbag canvas fill the whole mobile/desktop browser."""
    if not IS_BROWSER:
        return
    try:
        import platform as browser_platform
        window = getattr(browser_platform, "window", None)
        if window is None:
            return
        document = window.document

        # Remove the default grey page background/margins and stop the page from
        # scrolling while using touch controls.
        document.documentElement.style.margin = "0"
        document.documentElement.style.padding = "0"
        document.documentElement.style.width = "100%"
        document.documentElement.style.height = "100%"
        document.documentElement.style.overflow = "hidden"
        document.documentElement.style.background = "#0A1220"

        document.body.style.margin = "0"
        document.body.style.padding = "0"
        document.body.style.width = "100vw"
        document.body.style.height = "100dvh"
        document.body.style.minHeight = "100vh"
        document.body.style.overflow = "hidden"
        document.body.style.background = "#0A1220"
        document.body.style.touchAction = "none"

        canvas = document.querySelector("canvas")
        if canvas:
            canvas.style.position = "fixed"
            canvas.style.left = "0"
            canvas.style.top = "0"
            canvas.style.right = "0"
            canvas.style.bottom = "0"
            canvas.style.width = "100vw"
            canvas.style.height = "100dvh"
            canvas.style.maxWidth = "none"
            canvas.style.maxHeight = "none"
            canvas.style.margin = "0"
            canvas.style.padding = "0"
            canvas.style.display = "block"
            canvas.style.objectFit = "fill"
            canvas.style.background = "#0A1220"
            canvas.style.touchAction = "none"
    except Exception:
        pass


def get_real_display_size():
    """Safe display-size detection for desktop and Pygbag browser/mobile."""
    js_size = get_js_viewport_size()
    if js_size:
        return js_size

    try:
        info = pygame.display.Info()
        if info.current_w > 0 and info.current_h > 0:
            return int(info.current_w), int(info.current_h)
    except Exception:
        pass

    return DESKTOP_SIZE


def choose_mobile_layout(display_w, display_h):
    """Use the clear portrait mobile screens on phones and small browser windows."""
    return display_h >= display_w or display_w <= 700


# Initial layout selection.
apply_browser_page_fix()
DISPLAY_W, DISPLAY_H = get_real_display_size()
MOBILE_LAYOUT = choose_mobile_layout(DISPLAY_W, DISPLAY_H)
WIDTH, HEIGHT = MOBILE_SIZE if MOBILE_LAYOUT else DESKTOP_SIZE

display_screen = pygame.display.set_mode((DISPLAY_W, DISPLAY_H), DISPLAY_FLAGS)
screen = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("CyberShield Academy: Teen Digital Defenders")
clock = pygame.time.Clock()
apply_browser_page_fix()


def configure_layout_after_resize(w=None, h=None):
    """Update browser/window size and rebuild layout when orientation changes."""
    global DISPLAY_W, DISPLAY_H, WIDTH, HEIGHT, MOBILE_LAYOUT
    global display_screen, screen, player_speed, enemy_speed

    if w is None or h is None:
        w, h = get_real_display_size()

    DISPLAY_W = max(1, int(w))
    DISPLAY_H = max(1, int(h))

    new_mobile = choose_mobile_layout(DISPLAY_W, DISPLAY_H)
    layout_changed = new_mobile != MOBILE_LAYOUT
    MOBILE_LAYOUT = new_mobile
    WIDTH, HEIGHT = MOBILE_SIZE if MOBILE_LAYOUT else DESKTOP_SIZE

    display_screen = pygame.display.set_mode((DISPLAY_W, DISPLAY_H), DISPLAY_FLAGS)

    if layout_changed or screen.get_size() != (WIDTH, HEIGHT):
        screen = pygame.Surface((WIDTH, HEIGHT))

        # These are defined later, so only call them after the full file is loaded.
        if "make_fonts" in globals():
            make_fonts()
        if "make_rects_for_layout" in globals():
            make_rects_for_layout()
        if "player_speed" in globals():
            player_speed = 4 if MOBILE_LAYOUT else 5
        if "enemy_speed" in globals():
            enemy_speed = 2.4 if MOBILE_LAYOUT else 3.0

    apply_browser_page_fix()


def screen_to_game_pos(pos):
    """Convert desktop/browser click coordinates into virtual game coordinates."""
    x, y = pos
    return int(x * WIDTH / max(1, DISPLAY_W)), int(y * HEIGHT / max(1, DISPLAY_H))


def finger_to_game_pos(event):
    """Pygame finger events use 0..1 coordinates. Convert directly to game layout."""
    return int(event.x * WIDTH), int(event.y * HEIGHT)


def present_frame():
    """Scale the virtual game to the whole desktop/mobile/browser frame."""
    if IS_BROWSER:
        apply_browser_page_fix()

    display_screen.fill(DARK_BG if "DARK_BG" in globals() else (10, 18, 32))

    if display_screen.get_size() != (WIDTH, HEIGHT):
        # Use normal scale instead of smoothscale because smoothscale made small
        # web text look blurry on mobile screenshots.
        frame = pygame.transform.scale(screen, (DISPLAY_W, DISPLAY_H))
        display_screen.blit(frame, (0, 0))
    else:
        display_screen.blit(screen, (0, 0))

    pygame.display.flip()

# =========================================================
# THEME
# =========================================================
WHITE = (235, 242, 250)
BLACK = (8, 13, 20)

DARK_BG = (10, 18, 32)
DARK_PANEL = (15, 29, 50)
CARD_BG = (22, 38, 62)

NEON_BLUE = (66, 153, 225)
NEON_GREEN = (72, 187, 120)
NEON_PURPLE = (128, 90, 213)
NEON_PINK = (213, 63, 140)

RED = (229, 62, 62)
YELLOW = (236, 201, 75)
ORANGE = (237, 137, 54)
GRAY = (135, 150, 170)

OPTION_BG = (28, 54, 88)
OPTION_HOVER = (66, 153, 225)
OPTION_BORDER = (99, 179, 237)
PROGRESS_BG = (31, 41, 55)


# =========================================================
# ASSETS / FONTS
# =========================================================
def base_path():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()


BASE_DIR = base_path()
HIGH_SCORE_FILE = os.path.join(BASE_DIR, "cybershield_teen_defenders_highscore.txt")


def load_font(size, bold=False):
    """Reliable fonts for PyCharm and browser builds."""
    preferred = ["arial", "calibri", "verdana", "dejavusans"]
    for name in preferred:
        try:
            font_obj = pygame.font.SysFont(name, size, bold=bold)
            if font_obj:
                return font_obj
        except Exception:
            pass
    return pygame.font.Font(None, size)


def make_fonts():
    global FONT_SMALL, FONT, FONT_TITLE, FONT_BIG, FONT_TINY
    if MOBILE_LAYOUT:
        FONT_TINY = load_font(14)
        FONT_SMALL = load_font(17)
        FONT = load_font(21, bold=True)
        FONT_TITLE = load_font(28, bold=True)
        FONT_BIG = load_font(35, bold=True)
    else:
        FONT_TINY = load_font(17)
        FONT_SMALL = load_font(20)
        FONT = load_font(26, bold=True)
        FONT_TITLE = load_font(42, bold=True)
        FONT_BIG = load_font(56, bold=True)


make_fonts()


def get_font(size="normal"):
    if size == "tiny":
        return FONT_TINY
    if size == "small":
        return FONT_SMALL
    if size == "title":
        return FONT_TITLE
    if size == "big":
        return FONT_BIG
    return FONT


# =========================================================
# SOUND SYSTEM
# =========================================================
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    SOUND_ON = True
except Exception:
    SOUND_ON = False


def make_sound(freq=440, duration=0.2, volume=0.35):
    if not SOUND_ON:
        return None

    sample_rate = 44100
    samples = int(sample_rate * duration)
    buf = array.array("h")

    for i in range(samples):
        value = int(32767 * volume * math.sin(2 * math.pi * freq * i / sample_rate))
        buf.append(value)

    try:
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None


click_sound = make_sound(500, 0.07)
correct_sound = make_sound(850, 0.14)
wrong_sound = make_sound(180, 0.22)
coin_sound = make_sound(1100, 0.07)
win_sound = make_sound(700, 0.45)


def play(sound):
    if SOUND_ON and sound:
        try:
            sound.play()
        except Exception:
            pass


# =========================================================
# GAME DATA
# =========================================================
tools = [
    "Firewall Shield",
    "Password Scanner",
    "Privacy Cloak",
    "2-Step Login Boost"
]

levels = [
    {
        "title": "Level 1: Password Power-Up",
        "zone": "Collect password cores and dodge weak-password bots.",
        "story": "Your school game account is under attack by a weak password bot.",
        "question": "Which password is the strongest choice?",
        "options": ["12345678", "password", "K@vAli#2026!", "myname123"],
        "answer": 2,
        "lesson": "A strong password mixes uppercase letters, lowercase letters, numbers, and symbols.",
        "badge": "Password Pro",
        "enemy": "Weak Password Bot",
        "item": "Password Core",
        "theme": NEON_BLUE
    },
    {
        "title": "Level 2: Scam Message Zone",
        "zone": "Collect trusted messages and avoid scam traps.",
        "story": "A message says: 'You won a free phone! Click now to claim it.'",
        "question": "What is the safest move?",
        "options": ["Click the link", "Forward it", "Check the sender and report it", "Enter your password"],
        "answer": 2,
        "lesson": "Scam messages often use prizes, pressure, or fake links to trick people.",
        "badge": "Scam Spotter",
        "enemy": "Phishing Phantom",
        "item": "Trusted Message",
        "theme": NEON_GREEN
    },
    {
        "title": "Level 3: Privacy Street",
        "zone": "Collect privacy tokens and avoid oversharing drones.",
        "story": "A friend wants to post their home address on a public profile.",
        "question": "What advice should you give?",
        "options": ["Post it publicly", "Share it with strangers", "Keep personal details private", "Add their phone number too"],
        "answer": 2,
        "lesson": "Keep addresses, phone numbers, school details, and private information away from public posts.",
        "badge": "Privacy Guardian",
        "enemy": "Overshare Drone",
        "item": "Privacy Token",
        "theme": NEON_PURPLE
    },
    {
        "title": "Level 4: Malware Rush",
        "zone": "Collect clean files and avoid infected downloads.",
        "story": "A pop-up says it can make your laptop faster if you download a file.",
        "question": "What should you do?",
        "options": ["Download it", "Close it and avoid unknown downloads", "Send it to friends", "Turn off antivirus"],
        "answer": 1,
        "lesson": "Unknown downloads can hide viruses, spyware, or malware.",
        "badge": "Malware Blocker",
        "enemy": "Virus Bug",
        "item": "Clean File",
        "theme": ORANGE
    },
    {
        "title": "Level 5: Kindness Arena",
        "zone": "Collect support stars and avoid toxic comments.",
        "story": "Someone is being bullied in an online group chat.",
        "question": "What is the best response?",
        "options": ["Join in", "Laugh at it", "Block, report, support, and save evidence", "Share the post"],
        "answer": 2,
        "lesson": "Cyberbullying should be reported. Support the person affected and keep evidence.",
        "badge": "Online Respect Hero",
        "enemy": "Toxic Comment",
        "item": "Support Star",
        "theme": NEON_PINK
    },
    {
        "title": "Final Level: ShadowNet Showdown",
        "zone": "Collect security codes and avoid ShadowNet drones.",
        "story": "ShadowNet creates a fake login page to steal student accounts.",
        "question": "How can you protect your account better?",
        "options": ["Use two-factor authentication", "Give away your password", "Use the same password everywhere", "Turn off security"],
        "answer": 0,
        "lesson": "Two-factor authentication adds an extra step, making your account harder to steal.",
        "badge": "ShadowNet Stopper",
        "enemy": "ShadowNet Drone",
        "item": "Security Code",
        "theme": RED
    }
]


# =========================================================
# STATE
# =========================================================
score = 0
coins = 0
level = 0
lives = 3
game_state = "start"
selected_message = ""
badges = []
question_start_time = 0
mini_start_time = 0
selected_quiz_option = None
mission_passed = False
completed_levels = set()

pointer_pos = (0, 0)
pointer_pressed = False
pointer_just_pressed = False

player_speed = 4 if MOBILE_LAYOUT else 5
enemy_speed = 2.4 if MOBILE_LAYOUT else 3.0
enemy_direction = 1
collectibles = []
mini_target = 4
particles = []
hero_frame = 0


def load_high_score():
    if IS_BROWSER:
        return 0
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
    except Exception:
        pass
    return 0


def save_high_score(value):
    if IS_BROWSER:
        return
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
            f.write(str(value))
    except Exception:
        pass


high_score = load_high_score()


# =========================================================
# RESPONSIVE GAME OBJECTS
# =========================================================
def make_rects_for_layout():
    global PLAY_AREA, player, enemy
    global touch_left, touch_right, touch_up, touch_down

    if MOBILE_LAYOUT:
        PLAY_AREA = pygame.Rect(25, 215, WIDTH - 50, 315)

        pad_size = 58
        base_y = HEIGHT - 130
        base_x = 35
        touch_left = pygame.Rect(base_x, base_y + 58, pad_size, pad_size)
        touch_right = pygame.Rect(base_x + 132, base_y + 58, pad_size, pad_size)
        touch_up = pygame.Rect(base_x + 66, base_y, pad_size, pad_size)
        touch_down = pygame.Rect(base_x + 66, base_y + 58, pad_size, pad_size)
    else:
        PLAY_AREA = pygame.Rect(40, 220, WIDTH - 80, 340)

        touch_left = pygame.Rect(55, 610, 60, 60)
        touch_right = pygame.Rect(185, 610, 60, 60)
        touch_up = pygame.Rect(120, 545, 60, 60)
        touch_down = pygame.Rect(120, 610, 60, 60)

    player_w, player_h = (34, 45) if MOBILE_LAYOUT else (42, 55)
    enemy_w, enemy_h = (46, 46) if MOBILE_LAYOUT else (60, 60)

    player = pygame.Rect(PLAY_AREA.left + 45, PLAY_AREA.bottom - player_h - 15, player_w, player_h)
    enemy = pygame.Rect(PLAY_AREA.right - enemy_w - 100, PLAY_AREA.top + 45, enemy_w, enemy_h)


make_rects_for_layout()


# =========================================================
# UI HELPERS
# =========================================================
def is_dark_colour(color):
    brightness = (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000
    return brightness < 130


def text_width(text, font):
    return font.size(text)[0]


def wrap_text(text, max_width, font):
    words = text.split()
    lines = []
    line = ""

    for word in words:
        test = (line + " " + word).strip()
        if font.size(test)[0] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word

    if line:
        lines.append(line)

    return lines


def draw_text(text, x, y, color=WHITE, size="normal"):
    font = get_font(size)
    render = font.render(str(text), True, color)
    screen.blit(render, (x, y))
    return render.get_rect(topleft=(x, y))


def draw_centered_text(text, y, color=WHITE, size="normal", x=0, width=None):
    if width is None:
        width = WIDTH
    font = get_font(size)
    render = font.render(str(text), True, color)
    screen.blit(render, (x + (width - render.get_width()) // 2, y))
    return render.get_rect()


def draw_wrapped_text(text, x, y, max_width, color=WHITE, size="small", line_gap=6, align="left"):
    font = get_font(size)
    lines = wrap_text(str(text), max_width, font)

    for line in lines:
        render = font.render(line, True, color)
        if align == "center":
            line_x = x + (max_width - render.get_width()) // 2
        elif align == "right":
            line_x = x + max_width - render.get_width()
        else:
            line_x = x
        screen.blit(render, (line_x, y))
        y += font.get_height() + line_gap

    return y


def draw_panel(x, y, w, h, border_color=NEON_BLUE, fill=CARD_BG, radius=16):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=radius)
    return rect


def draw_progress_bar(x, y, w, h, value, fill_color):
    value = max(0, min(1, value))
    bg = pygame.Rect(x, y, w, h)
    fill = pygame.Rect(x, y, int(w * value), h)
    pygame.draw.rect(screen, PROGRESS_BG, bg, border_radius=10)
    pygame.draw.rect(screen, fill_color, fill, border_radius=10)
    pygame.draw.rect(screen, WHITE, bg, 1, border_radius=10)


def draw_cyber_background():
    screen.fill(DARK_BG)

    grid = 40 if MOBILE_LAYOUT else 50
    for x in range(0, WIDTH, grid):
        pygame.draw.line(screen, (18, 35, 75), (x, 0), (x, HEIGHT), 1)

    for y in range(0, HEIGHT, grid):
        pygame.draw.line(screen, (18, 35, 75), (0, y), (WIDTH, y), 1)

    pygame.draw.circle(screen, (0, 80, 120), (int(WIDTH * 0.83), int(HEIGHT * 0.16)), 48 if MOBILE_LAYOUT else 75, 2)
    pygame.draw.circle(screen, (80, 40, 130), (int(WIDTH * 0.16), int(HEIGHT * 0.80)), 62 if MOBILE_LAYOUT else 95, 2)

    # Keep particles very light for phone performance.
    for _ in range(6 if MOBILE_LAYOUT else 12):
        pygame.draw.circle(screen, (0, 80, 120), (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 1)


def consume_click(rect):
    global pointer_just_pressed
    touch_rect = rect.inflate(10 if MOBILE_LAYOUT else 4, 10 if MOBILE_LAYOUT else 4)
    if pointer_just_pressed and touch_rect.collidepoint(pointer_pos):
        pointer_just_pressed = False
        play(click_sound)
        return True
    return False


def draw_button(text, x, y, w, h, color=NEON_GREEN, size="small"):
    rect = pygame.Rect(x, y, w, h)
    hover = rect.inflate(8, 8).collidepoint(pointer_pos)

    if hover:
        fill = YELLOW
        border = WHITE
        text_color = BLACK
    else:
        fill = color
        border = OPTION_BORDER if is_dark_colour(color) else NEON_BLUE
        text_color = WHITE if is_dark_colour(color) else BLACK

    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, border, rect, 3, border_radius=14)

    font = get_font(size)
    lines = wrap_text(text, w - 22, font)
    total_h = len(lines) * font.get_height() + max(0, len(lines) - 1) * 4
    text_y = y + (h - total_h) // 2

    for line in lines:
        render = font.render(line, True, text_color)
        screen.blit(render, (x + (w - render.get_width()) // 2, text_y))
        text_y += font.get_height() + 4

    return consume_click(rect)


def draw_quiz_option(index, text, x, y, w, h, accent_color):
    rect = pygame.Rect(x, y, w, h)
    hover = rect.inflate(8, 8).collidepoint(pointer_pos)

    fill = OPTION_HOVER if hover else OPTION_BG
    border = YELLOW if hover else accent_color
    text_color = BLACK if hover else WHITE

    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, border, rect, 3, border_radius=14)

    num_w = 36 if MOBILE_LAYOUT else 44
    num_rect = pygame.Rect(x + 10, y + 9, num_w, h - 18)
    pygame.draw.rect(screen, border, num_rect, border_radius=10)

    draw_centered_text(str(index + 1), y + (h - get_font("small").get_height()) // 2, text_color, "small", num_rect.x, num_rect.w)
    draw_wrapped_text(text, x + num_w + 22, y + 10, w - num_w - 32, text_color, "small", 3)

    return consume_click(rect)


def draw_hud():
    if MOBILE_LAYOUT:
        pygame.draw.rect(screen, DARK_PANEL, (0, 0, WIDTH, 82))
        pygame.draw.line(screen, NEON_BLUE, (0, 82), (WIDTH, 82), 2)

        draw_text("Score " + str(score), 16, 14, NEON_BLUE, "tiny")
        draw_text("Credits " + str(coins), 146, 14, NEON_GREEN, "tiny")
        draw_text("Lives " + str(lives), 300, 14, RED, "tiny")

        draw_text("High " + str(high_score), 16, 48, NEON_PURPLE, "tiny")
        draw_text("Level " + str(level + 1) + "/" + str(len(levels)), 300, 48, YELLOW, "tiny")
    else:
        pygame.draw.rect(screen, DARK_PANEL, (0, 0, WIDTH, 82))
        pygame.draw.line(screen, NEON_BLUE, (0, 82), (WIDTH, 82), 3)

        draw_text("SCORE: " + str(score), 30, 25, NEON_BLUE, "small")
        draw_text("CREDITS: " + str(coins), 175, 25, NEON_GREEN, "small")
        draw_text("LIVES: " + str(lives), 320, 25, RED, "small")
        draw_text("HIGH SCORE: " + str(high_score), 520, 25, NEON_PURPLE, "small")
        draw_text("LEVEL: " + str(level + 1) + "/" + str(len(levels)), 800, 25, YELLOW, "small")


def create_particles(x, y, color):
    for _ in range(8 if MOBILE_LAYOUT else 12):
        particles.append([
            x,
            y,
            random.uniform(-3, 3),
            random.uniform(-3, 3),
            random.randint(15, 28),
            color
        ])


def update_particles():
    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 1

        if p[4] <= 0:
            particles.remove(p)
        else:
            pygame.draw.circle(screen, p[5], (int(p[0]), int(p[1])), 3)


# =========================================================
# TOUCH / MOVEMENT
# =========================================================
def draw_mobile_controls():
    show_controls = MOBILE_LAYOUT or IS_BROWSER
    if not show_controls:
        return

    label_y = HEIGHT - 166 if MOBILE_LAYOUT else 580
    draw_centered_text("TOUCH CONTROLS", label_y, GRAY, "tiny", 0, WIDTH if MOBILE_LAYOUT else 300)

    controls = [
        (touch_left, "←"),
        (touch_right, "→"),
        (touch_up, "↑"),
        (touch_down, "↓")
    ]

    for rect, label in controls:
        pressed = pointer_pressed and rect.inflate(8, 8).collidepoint(pointer_pos)
        fill = OPTION_HOVER if pressed else OPTION_BG
        border = YELLOW if pressed else OPTION_BORDER
        text_color = BLACK if pressed else WHITE

        pygame.draw.rect(screen, fill, rect, border_radius=14)
        pygame.draw.rect(screen, border, rect, 3, border_radius=14)
        draw_centered_text(label, rect.y + (rect.h - get_font("normal").get_height()) // 2, text_color, "normal", rect.x, rect.w)


def handle_touch_movement():
    if not pointer_pressed:
        return

    active = pygame.Rect(pointer_pos[0], pointer_pos[1], 1, 1)

    if touch_left.inflate(8, 8).colliderect(active):
        player.x -= player_speed
    if touch_right.inflate(8, 8).colliderect(active):
        player.x += player_speed
    if touch_up.inflate(8, 8).colliderect(active):
        player.y -= player_speed
    if touch_down.inflate(8, 8).colliderect(active):
        player.y += player_speed


# =========================================================
# GAME DRAWING
# =========================================================
def draw_animated_player():
    global hero_frame
    hero_frame += 1

    bounce = int(math.sin(hero_frame * 0.15) * (2 if MOBILE_LAYOUT else 4))
    glow_radius = 28 if MOBILE_LAYOUT else 38
    head_radius = 14 if MOBILE_LAYOUT else 19

    pygame.draw.circle(screen, (0, 80, 120), (player.centerx, player.centery + bounce), glow_radius)
    pygame.draw.circle(screen, NEON_BLUE, (player.centerx, player.y + 13 + bounce), head_radius)

    body = pygame.Rect(player.x + int(player.w * 0.18), player.y + int(player.h * 0.50) + bounce, int(player.w * 0.64), int(player.h * 0.45))
    pygame.draw.rect(screen, NEON_GREEN, body, border_radius=7)

    visor = pygame.Rect(player.x + int(player.w * 0.24), player.y + 7 + bounce, int(player.w * 0.52), 7)
    pygame.draw.rect(screen, BLACK, visor, border_radius=4)

    pygame.draw.circle(screen, WHITE, (player.x + int(player.w * 0.38), player.y + 10 + bounce), 2)
    pygame.draw.circle(screen, WHITE, (player.x + int(player.w * 0.62), player.y + 10 + bounce), 2)


def draw_enemy(name):
    glow = 34 if MOBILE_LAYOUT else 45
    pygame.draw.circle(screen, (120, 20, 40), enemy.center, glow)
    pygame.draw.rect(screen, RED, enemy, border_radius=10)
    pygame.draw.rect(screen, NEON_PINK, enemy, 3, border_radius=10)

    eye_y = enemy.y + int(enemy.h * 0.35)
    pygame.draw.circle(screen, BLACK, (enemy.x + int(enemy.w * 0.30), eye_y), 5)
    pygame.draw.circle(screen, BLACK, (enemy.x + int(enemy.w * 0.70), eye_y), 5)
    pygame.draw.line(screen, BLACK, (enemy.x + int(enemy.w * 0.25), enemy.y + int(enemy.h * 0.73)), (enemy.x + int(enemy.w * 0.75), enemy.y + int(enemy.h * 0.73)), 3)

    if not MOBILE_LAYOUT:
        draw_wrapped_text(name, enemy.x - 50, enemy.y - 38, 160, RED, "tiny", 2, "center")


def draw_collectible(item):
    pygame.draw.circle(screen, YELLOW, item.center, item.w // 2)
    pygame.draw.circle(screen, ORANGE, item.center, max(4, item.w // 4))
    pygame.draw.circle(screen, WHITE, item.center, 3)


def create_safe_collectible():
    size = 22 if MOBILE_LAYOUT else 26
    padding = 28 if MOBILE_LAYOUT else 34

    min_x = PLAY_AREA.left + padding
    max_x = PLAY_AREA.right - padding - size
    min_y = PLAY_AREA.top + padding
    max_y = PLAY_AREA.bottom - padding - size

    for _ in range(120):
        item = pygame.Rect(random.randint(min_x, max_x), random.randint(min_y, max_y), size, size)

        too_close_to_player = item.colliderect(player.inflate(90 if MOBILE_LAYOUT else 120, 90 if MOBILE_LAYOUT else 120))
        too_close_to_enemy = item.colliderect(enemy.inflate(80 if MOBILE_LAYOUT else 110, 80 if MOBILE_LAYOUT else 110))
        too_close_to_other = any(item.colliderect(other.inflate(45, 45)) for other in collectibles)

        if not too_close_to_player and not too_close_to_enemy and not too_close_to_other:
            return item

    return pygame.Rect(random.randint(min_x, max_x), random.randint(min_y, max_y), size, size)


# =========================================================
# RESET
# =========================================================
def reset_game():
    global score, coins, level, lives, game_state, selected_message
    global badges, question_start_time, selected_quiz_option, mission_passed

    score = 0
    coins = 0
    level = 0
    lives = 3
    game_state = "start"
    selected_message = ""
    badges = []
    question_start_time = 0
    selected_quiz_option = None
    mission_passed = False
    completed_levels.clear()
    particles.clear()
    make_rects_for_layout()


def reset_mini_game():
    global mini_start_time, enemy_direction, mission_passed

    mission_passed = False
    make_rects_for_layout()

    player.x = PLAY_AREA.left + 45
    player.y = PLAY_AREA.bottom - player.height - 15

    enemy.x = PLAY_AREA.right - enemy.width - (80 if MOBILE_LAYOUT else 150)
    enemy.y = random.randint(PLAY_AREA.top + 35, PLAY_AREA.bottom - enemy.height - 25)
    enemy_direction = 1

    collectibles.clear()
    for _ in range(mini_target):
        collectibles.append(create_safe_collectible())

    mini_start_time = pygame.time.get_ticks()


# =========================================================
# SCREENS
# =========================================================
def start_screen():
    draw_cyber_background()

    if MOBILE_LAYOUT:
        draw_centered_text("CYBERSHIELD", 38, NEON_BLUE, "big")
        draw_centered_text("TEEN DEFENDERS", 82, NEON_GREEN, "title")

        draw_panel(24, 140, WIDTH - 48, 310, NEON_PURPLE)
        draw_centered_text("WELCOME", 165, YELLOW, "normal", 24, WIDTH - 48)

        draw_wrapped_text(
            "Train like a digital defender. Complete missions, dodge online threats, answer cyber-safety questions, earn badges, and stop ShadowNet.",
            48, 210, WIDTH - 96, WHITE, "small", 8, "center"
        )

        draw_centered_text("Mobile: tap buttons and use the D-pad.", 482, GRAY, "tiny")
        if draw_button("START GAME", 70, 540, WIDTH - 140, 58, NEON_GREEN, "normal"):
            return "intro"
        if draw_button("QUIT", 145, 625, WIDTH - 290, 48, RED, "small"):
            pygame.quit()
            sys.exit()
    else:
        draw_centered_text("CYBERSHIELD ACADEMY", 60, NEON_BLUE, "big")
        draw_centered_text("TEEN DIGITAL DEFENDERS", 128, NEON_GREEN, "title")

        draw_panel(130, 195, 740, 285, NEON_PURPLE)
        draw_centered_text("WELCOME TO THE ACADEMY", 225, YELLOW, "normal", 130, 740)

        draw_wrapped_text(
            "Train like a digital defender in a cyber-safety game made for teenagers. Complete missions, dodge online threats, answer quick safety questions, earn badges, and stop ShadowNet before it takes over the school network.",
            185, 275, 630, WHITE, "small", 8, "center"
        )

        draw_centered_text("Desktop: use mouse and arrow keys. Mobile: tap and use touch controls.", 488, GRAY, "small")
        if draw_button("START GAME", 365, 525, 270, 60, NEON_GREEN, "normal"):
            return "intro"
        if draw_button("QUIT", 420, 610, 160, 45, RED, "small"):
            pygame.quit()
            sys.exit()

    return "start"


def intro_screen():
    draw_cyber_background()

    if MOBILE_LAYOUT:
        draw_centered_text("BRIEFING", 42, NEON_PURPLE, "big")
        draw_panel(22, 110, WIDTH - 44, 455, NEON_BLUE)

        lines = [
            "ShadowNet has launched a digital attack on the academy network.",
            "Move your cadet, collect items, avoid enemies, and answer each question.",
            "Correct answers earn badges and unlock your cyber defender rank."
        ]

        y = 150
        for line in lines:
            y = draw_wrapped_text(line, 48, y, WIDTH - 96, WHITE, "small", 8, "center") + 14

        draw_centered_text("CADET GEAR", 360, NEON_GREEN, "normal", 22, WIDTH - 44)
        y = 400
        for item in tools:
            y = draw_wrapped_text("• " + item, 58, y, WIDTH - 116, WHITE, "small", 5, "left") + 4

        if draw_button("CONTINUE", 90, 615, WIDTH - 180, 58, NEON_GREEN, "normal"):
            return "concept"
    else:
        draw_centered_text("PLAYER BRIEFING", 55, NEON_PURPLE, "title")
        draw_panel(80, 125, 840, 430, NEON_BLUE)

        lines = [
            "ShadowNet has launched a digital attack on the academy network.",
            "As a CyberShield cadet, you will complete six missions based on real online safety skills.",
            "Move your character, collect mission items, avoid enemies, and answer each question before time runs out.",
            "Your choices matter. Smart decisions earn badges and keep the network safe."
        ]

        y = 165
        for line in lines:
            y = draw_wrapped_text(line, 130, y, 760, WHITE, "small", 8, "center") + 12

        draw_centered_text("CADET GEAR", 345, NEON_GREEN, "normal", 80, 840)
        y = 390
        for item in tools:
            draw_wrapped_text("• " + item, 220, y, 560, WHITE, "small", 6, "center")
            y += 35

        if draw_button("CONTINUE", 390, 600, 220, 60, NEON_GREEN, "normal"):
            return "concept"

    return "intro"


def concept_screen():
    draw_cyber_background()

    if MOBILE_LAYOUT:
        draw_centered_text("HOW TO PLAY", 42, NEON_BLUE, "big")
        draw_panel(22, 115, WIDTH - 44, 440, NEON_GREEN)

        lines = [
            "Desktop: use arrow keys.",
            "Mobile: hold the touch D-pad.",
            "Collect all mission items.",
            "Avoid enemies or you lose a life.",
            "Answer the question correctly to pass."
        ]

        y = 150
        for line in lines:
            draw_panel(45, y - 8, WIDTH - 90, 48, NEON_BLUE)
            draw_wrapped_text(line, 62, y, WIDTH - 124, WHITE, "small", 4, "center")
            y += 72

        if draw_button("OPEN MISSION MAP", 60, 615, WIDTH - 120, 58, NEON_GREEN, "small"):
            return "map"
    else:
        draw_centered_text("HOW TO PLAY", 55, NEON_BLUE, "title")
        draw_panel(85, 130, 830, 430, NEON_GREEN)

        lines = [
            "Desktop: use arrow keys or WASD to move your cadet.",
            "Mobile: hold the touch D-pad buttons to move your cadet.",
            "Collect all mission items before the timer reaches zero.",
            "Avoid enemies. Touching one will cost you a life.",
            "After every mission, answer a quick cyber-safety question."
        ]

        y = 175
        for line in lines:
            draw_panel(145, y - 8, 710, 42, NEON_BLUE)
            draw_wrapped_text(line, 175, y, 650, WHITE, "small", 6, "center")
            y += 68

        if draw_button("OPEN MISSION MAP", 340, 600, 320, 60, NEON_GREEN, "normal"):
            return "map"

    return "concept"


def map_screen():
    global level

    draw_cyber_background()
    draw_hud()

    first_done = 0 in completed_levels

    draw_centered_text("MISSION MAP", 98 if MOBILE_LAYOUT else 110, YELLOW, "title")
    message = "Choose any mission." if first_done else "Play Level 1 first to unlock the full map."
    draw_wrapped_text(message, 30 if MOBILE_LAYOUT else 100, 136 if MOBILE_LAYOUT else 165, WIDTH - 60 if MOBILE_LAYOUT else 800, WHITE, "small", 4, "center")

    zone_names = [
        "Password",
        "Scam",
        "Privacy",
        "Malware",
        "Kindness",
        "ShadowNet"
    ]

    if MOBILE_LAYOUT:
        card_w, card_h = 178, 92
        x_positions = [28, 224, 28, 224, 28, 224]
        y_positions = [185, 185, 300, 300, 415, 415]
    else:
        card_w, card_h = 210, 95
        x_positions = [80, 330, 620, 140, 430, 720]
        y_positions = [230, 230, 230, 415, 415, 415]

    for i, name in enumerate(zone_names):
        rect = pygame.Rect(x_positions[i], y_positions[i], card_w, card_h)
        is_completed = i in completed_levels
        is_playable = first_done or i == 0

        if not is_playable:
            color = GRAY
            status = "LOCKED"
        elif is_completed:
            color = NEON_GREEN
            status = "CLEARED"
        elif i == level:
            color = YELLOW
            status = "SELECTED"
        else:
            color = NEON_BLUE if rect.collidepoint(pointer_pos) else NEON_PURPLE
            status = "ACTIVE"

        draw_panel(rect.x, rect.y, rect.w, rect.h, color)
        draw_wrapped_text(name, rect.x + 10, rect.y + 20, rect.w - 20, color, "small", 3, "center")
        draw_centered_text(status, rect.y + rect.h - 30, color, "tiny", rect.x, rect.w)

        if is_playable and consume_click(rect):
            level = i

    if MOBILE_LAYOUT:
        panel_y = 540
        draw_panel(26, panel_y, WIDTH - 52, 58, NEON_PURPLE)
        draw_wrapped_text("Selected: " + levels[level]["title"], 42, panel_y + 13, WIDTH - 84, WHITE, "tiny", 3, "center")

        if draw_button("START MISSION", 68, 625, WIDTH - 136, 58, NEON_GREEN if first_done else ORANGE, "small"):
            if first_done or level == 0:
                reset_mini_game()
                return "mini"
    else:
        draw_panel(170, 540, 660, 58, NEON_PURPLE)
        selected_text = "SELECTED MISSION: " + levels[level]["title"]
        draw_wrapped_text(selected_text, 205, 558, 590, WHITE, "small", 6, "center")

        if draw_button("START SELECTED MISSION" if first_done else "PLAY LEVEL 1", 330 if first_done else 380, 615, 340 if first_done else 240, 60, NEON_GREEN if first_done else ORANGE, "small"):
            if first_done or level == 0:
                reset_mini_game()
                return "mini"

    return "map"


def mini_game_screen():
    global lives, coins, score, enemy_direction, selected_message

    current = levels[level]
    theme_color = current["theme"]

    draw_cyber_background()
    draw_hud()

    elapsed = (pygame.time.get_ticks() - mini_start_time) // 1000
    mission_time = 25
    time_left = max(0, mission_time - elapsed)
    timer_ratio = time_left / mission_time

    if MOBILE_LAYOUT:
        draw_centered_text(current["title"].replace("Level ", "L"), 90, theme_color, "small")
        draw_wrapped_text(current["zone"], 30, 120, WIDTH - 60, WHITE, "tiny", 3, "center")
        draw_text("Collect: " + str(mini_target), 28, 166, NEON_GREEN, "tiny")
        draw_text("Time: " + str(time_left), WIDTH - 105, 166, RED, "tiny")
        draw_progress_bar(150, 170, 120, 12, timer_ratio, theme_color if timer_ratio > 0.35 else RED)
    else:
        draw_centered_text(current["title"], 100, theme_color, "normal")
        draw_wrapped_text(current["zone"], 100, 135, 800, WHITE, "small", 7, "center")
        draw_text("COLLECT: " + str(mini_target) + " " + current["item"], 55, 180, NEON_GREEN, "small")
        draw_text("TIME: " + str(time_left), 805, 100, RED, "small")
        draw_progress_bar(735, 135, 210, 18, timer_ratio, theme_color if timer_ratio > 0.35 else RED)
        draw_centered_text("Desktop: arrow keys/WASD  •  Mobile: touch D-pad  •  Avoid enemies", 200, GRAY, "small")

    pygame.draw.rect(screen, DARK_PANEL, PLAY_AREA, border_radius=18)
    pygame.draw.rect(screen, theme_color, PLAY_AREA, 2, border_radius=18)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.x += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player.y -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.y += player_speed

    handle_touch_movement()

    player.left = max(player.left, PLAY_AREA.left + 8)
    player.right = min(player.right, PLAY_AREA.right - 8)
    player.top = max(player.top, PLAY_AREA.top + 8)
    player.bottom = min(player.bottom, PLAY_AREA.bottom - 8)

    current_enemy_speed = enemy_speed + (level * (0.18 if MOBILE_LAYOUT else 0.25))
    enemy.x += current_enemy_speed * enemy_direction

    if enemy.left <= PLAY_AREA.left + 16 or enemy.right >= PLAY_AREA.right - 16:
        enemy_direction *= -1
        enemy.y = random.randint(PLAY_AREA.top + 28, PLAY_AREA.bottom - enemy.height - 20)

    for item in collectibles[:]:
        draw_collectible(item)
        if player.colliderect(item):
            collectibles.remove(item)
            coins += 2
            score += 2
            create_particles(item.centerx, item.centery, YELLOW)
            play(coin_sound)

    draw_animated_player()
    draw_enemy(current["enemy"])
    update_particles()

    collected_now = mini_target - len(collectibles)

    if MOBILE_LAYOUT:
        draw_centered_text("Collected: " + str(collected_now) + "/" + str(mini_target), PLAY_AREA.bottom + 14, NEON_GREEN, "tiny")
        draw_progress_bar(120, PLAY_AREA.bottom + 40, WIDTH - 240, 12, collected_now / mini_target, NEON_GREEN)
    else:
        draw_centered_text("COLLECTED: " + str(collected_now) + "/" + str(mini_target), 572, NEON_GREEN, "small")
        draw_progress_bar(390, 595, 220, 14, collected_now / mini_target, NEON_GREEN)

    draw_mobile_controls()

    if player.colliderect(enemy):
        lives -= 1
        play(wrong_sound)
        selected_message = "You touched an enemy and lost one life. Keep moving and try again!"
        create_particles(player.centerx, player.centery, RED)

        player.x = PLAY_AREA.left + 45
        player.y = PLAY_AREA.bottom - player.height - 15
        enemy.x = PLAY_AREA.right - enemy.width - (80 if MOBILE_LAYOUT else 150)

        if lives <= 0:
            return "end"

    if len(collectibles) == 0:
        play(correct_sound)
        score += 5
        return "quiz"

    if time_left <= 0:
        lives -= 1
        selected_message = "Mission timer ended. You lost one life, but you can try again."
        play(wrong_sound)

        if lives <= 0:
            return "end"

        return "map"

    return "mini"


def quiz_screen():
    global score, coins, selected_message, lives
    global question_start_time, selected_quiz_option, mission_passed

    current = levels[level]
    theme_color = current["theme"]

    draw_cyber_background()
    draw_hud()

    if question_start_time == 0:
        question_start_time = pygame.time.get_ticks()

    elapsed = (pygame.time.get_ticks() - question_start_time) // 1000
    question_time = 15
    time_left = max(0, question_time - elapsed)
    timer_ratio = time_left / question_time

    if MOBILE_LAYOUT:
        draw_centered_text("CYBER QUESTION", 94, theme_color, "title")
        draw_centered_text("Timer: " + str(time_left), 128, RED, "small")
        draw_progress_bar(110, 158, WIDTH - 220, 13, timer_ratio, theme_color if timer_ratio > 0.35 else RED)

        draw_panel(20, 185, WIDTH - 40, 460, theme_color)
        draw_wrapped_text(current["story"], 40, 212, WIDTH - 80, WHITE, "tiny", 5, "center")
        draw_wrapped_text(current["question"], 40, 292, WIDTH - 80, NEON_GREEN, "small", 5, "center")

        y = 378
        option_x, option_w, option_h = 30, WIDTH - 60, 56
    else:
        draw_centered_text(current["title"], 102, theme_color, "title")
        draw_centered_text("QUESTION TIMER: " + str(time_left), 153, RED, "small")
        draw_progress_bar(365, 176, 270, 16, timer_ratio, theme_color if timer_ratio > 0.35 else RED)

        draw_panel(55, 205, 890, 420, theme_color)
        draw_centered_text("MISSION STORY", 230, NEON_BLUE, "normal", 55, 890)
        draw_wrapped_text(current["story"], 105, 267, 790, WHITE, "small", 7, "center")
        draw_centered_text("QUESTION", 325, NEON_GREEN, "normal", 55, 890)
        draw_wrapped_text(current["question"], 105, 360, 790, WHITE, "small", 7, "center")
        draw_centered_text("Choose with mouse/touch or press keys 1 - 4", 400, GRAY, "small")

        y = 428
        option_x, option_w, option_h = 110, 780, 48

    for i, option in enumerate(current["options"]):
        clicked = draw_quiz_option(i, option, option_x, y, option_w, option_h, theme_color)
        key_selected = selected_quiz_option == i

        if clicked or key_selected:
            question_start_time = 0
            selected_quiz_option = None

            if i == current["answer"]:
                mission_passed = True
                score += 10
                coins += 5

                if current["badge"] not in badges:
                    badges.append(current["badge"])

                selected_message = "Correct! Badge earned: " + current["badge"] + ". " + current["lesson"]
                play(correct_sound)
            else:
                mission_passed = False
                lives -= 1
                selected_message = "Wrong choice. " + current["lesson"]
                play(wrong_sound)

                if lives <= 0:
                    return "end"

            return "result"

        y += 66 if MOBILE_LAYOUT else 56

    if time_left <= 0:
        question_start_time = 0
        selected_quiz_option = None
        mission_passed = False
        lives -= 1
        selected_message = "Time over! " + current["lesson"]
        play(wrong_sound)

        if lives <= 0:
            return "end"

        return "result"

    return "quiz"


def result_screen():
    global level, mission_passed

    draw_cyber_background()
    draw_hud()

    if mission_passed:
        completed_levels.add(level)
        all_done = len(completed_levels) >= len(levels)
        title_text = "MISSION PASSED"
        button_text = "FINAL REPORT" if all_done else "BACK TO MAP"
        title_color = NEON_GREEN
    else:
        all_done = False
        title_text = "MISSION NOT PASSED"
        button_text = "RETRY MISSION"
        title_color = ORANGE

    if MOBILE_LAYOUT:
        draw_centered_text(title_text, 105, title_color, "title")
        draw_panel(22, 158, WIDTH - 44, 390, title_color)

        draw_wrapped_text(selected_message, 46, 190, WIDTH - 92, WHITE, "small", 7, "center")

        if mission_passed:
            draw_centered_text("TOOLS USED", 345, NEON_BLUE, "small", 22, WIDTH - 44)
            y = 388
            for tool in tools:
                y = draw_wrapped_text("• " + tool, 58, y, WIDTH - 116, WHITE, "tiny", 4, "left") + 2
        else:
            draw_centered_text("TRY AGAIN TIP", 345, NEON_BLUE, "small", 22, WIDTH - 44)
            draw_wrapped_text(
                "Collect the items again and choose the correct answer to pass this mission.",
                52, 390, WIDTH - 104, WHITE, "small", 6, "center"
            )

        if draw_button(button_text, 80, 615, WIDTH - 160, 58, NEON_BLUE if mission_passed else ORANGE, "small"):
            if mission_passed:
                passed_level = level
                mission_passed = False

                if all_done:
                    play(win_sound)
                    return "end"

                if passed_level == 0 and len(completed_levels) == 1:
                    level = 1

                return "map"

            reset_mini_game()
            return "mini"
    else:
        draw_centered_text(title_text, 110, title_color, "title")
        draw_panel(85, 180, 830, 330, title_color)
        draw_wrapped_text(selected_message, 135, 225, 730, WHITE, "small", 8, "center")

        if mission_passed:
            draw_centered_text("TOOLS USED", 330, NEON_BLUE, "normal", 85, 830)
            y = 372
            for tool in tools:
                draw_wrapped_text("• " + tool, 180, y, 640, WHITE, "small", 6, "center")
                y += 35
        else:
            draw_centered_text("TRY AGAIN TIP", 330, NEON_BLUE, "normal", 85, 830)
            draw_wrapped_text(
                "Complete the mission item collection again, then answer the question correctly to pass this mission.",
                180, 375, 640, WHITE, "small", 6, "center"
            )

        if draw_button(button_text, 375, 590, 250, 60, NEON_BLUE if mission_passed else ORANGE, "normal"):
            if mission_passed:
                passed_level = level
                mission_passed = False

                if all_done:
                    play(win_sound)
                    return "end"

                if passed_level == 0 and len(completed_levels) == 1:
                    level = 1

                return "map"

            reset_mini_game()
            return "mini"

    return "result"


def end_screen():
    global high_score

    draw_cyber_background()

    if score > high_score:
        high_score = score
        save_high_score(high_score)

    if lives <= 0:
        ending = "ShadowNet broke through this time. Replay the missions and level up your cyber skills."
        rank = "Rookie Cadet"
        rank_color = RED
    elif score >= 85:
        ending = "Amazing work! You stopped ShadowNet and proved you are a top digital defender."
        rank = "Elite Teen Defender"
        rank_color = YELLOW
    elif score >= 65:
        ending = "Great job! You stopped most of ShadowNet's attack and made strong cyber-safety decisions."
        rank = "CyberShield Hero"
        rank_color = NEON_GREEN
    elif score >= 45:
        ending = "Good effort! You protected key parts of the network, but a few skills still need practice."
        rank = "Skilled Cadet"
        rank_color = NEON_BLUE
    else:
        ending = "You completed the basics. Try again to earn more badges and improve your score."
        rank = "New Defender"
        rank_color = WHITE

    if MOBILE_LAYOUT:
        draw_centered_text("GAME REPORT", 45, NEON_PURPLE, "big")
        draw_panel(22, 118, WIDTH - 44, 430, NEON_BLUE)

        draw_centered_text("Final Score: " + str(score), 150, NEON_BLUE, "small", 22, WIDTH - 44)
        draw_centered_text("Credits: " + str(coins), 184, NEON_GREEN, "small", 22, WIDTH - 44)
        draw_centered_text("High Score: " + str(high_score), 218, NEON_PURPLE, "small", 22, WIDTH - 44)
        draw_centered_text("Rank: " + rank, 260, rank_color, "small", 22, WIDTH - 44)
        draw_wrapped_text(ending, 48, 305, WIDTH - 96, WHITE, "small", 7, "center")

        draw_centered_text("Badges Earned", 420, NEON_GREEN, "small", 22, WIDTH - 44)
        y = 455
        if badges:
            for badge in badges[:4]:
                y = draw_wrapped_text("• " + badge, 70, y, WIDTH - 140, WHITE, "tiny", 3, "center")
        else:
            draw_centered_text("No badges earned yet.", y, WHITE, "tiny", 22, WIDTH - 44)

        if draw_button("PLAY AGAIN", 48, 600, 150, 55, NEON_GREEN, "small"):
            reset_game()
            return "start"
        if draw_button("QUIT", 232, 600, 150, 55, RED, "small"):
            pygame.quit()
            sys.exit()
    else:
        draw_centered_text("GAME COMPLETE", 55, NEON_PURPLE, "big")
        draw_panel(110, 135, 780, 430, NEON_BLUE)

        draw_centered_text("FINAL REPORT", 165, YELLOW, "normal", 110, 780)
        draw_centered_text("FINAL SCORE: " + str(score), 210, NEON_BLUE, "normal", 110, 780)
        draw_centered_text("DEFENDER CREDITS: " + str(coins), 250, NEON_GREEN, "normal", 110, 780)
        draw_centered_text("HIGH SCORE: " + str(high_score), 290, NEON_PURPLE, "normal", 110, 780)
        draw_centered_text("RANK: " + rank, 335, rank_color, "normal", 110, 780)
        draw_wrapped_text(ending, 170, 380, 660, WHITE, "small", 8, "center")

        draw_centered_text("BADGES EARNED", 442, NEON_GREEN, "small", 110, 780)
        y = 472
        if badges:
            for badge in badges[:4]:
                draw_wrapped_text("• " + badge, 220, y, 560, WHITE, "small", 4, "center")
                y += 25
        else:
            draw_centered_text("No badges earned yet.", y, WHITE, "small", 110, 780)

        if draw_button("PLAY AGAIN", 260, 610, 230, 55, NEON_GREEN, "normal"):
            reset_game()
            return "start"
        if draw_button("QUIT GAME", 520, 610, 220, 55, RED, "normal"):
            pygame.quit()
            sys.exit()

    return "end"


# =========================================================
# INPUT
# =========================================================
def update_input_from_event(event):
    global pointer_pos, pointer_pressed, pointer_just_pressed
    global selected_quiz_option

    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    if event.type == pygame.VIDEORESIZE:
        configure_layout_after_resize(event.w, event.h)

    if event.type == pygame.MOUSEMOTION:
        pointer_pos = screen_to_game_pos(event.pos)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        pointer_pressed = True
        pointer_just_pressed = True
        pointer_pos = screen_to_game_pos(event.pos)

    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        pointer_pressed = False
        pointer_pos = screen_to_game_pos(event.pos)

    if event.type == pygame.FINGERDOWN:
        pointer_pressed = True
        pointer_just_pressed = True
        pointer_pos = finger_to_game_pos(event)

    if event.type == pygame.FINGERMOTION:
        pointer_pressed = True
        pointer_pos = finger_to_game_pos(event)

    if event.type == pygame.FINGERUP:
        pointer_pressed = False
        pointer_pos = finger_to_game_pos(event)

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if event.key == pygame.K_r and game_state == "end":
            reset_game()

        if game_state == "quiz":
            if event.key == pygame.K_1:
                selected_quiz_option = 0
            elif event.key == pygame.K_2:
                selected_quiz_option = 1
            elif event.key == pygame.K_3:
                selected_quiz_option = 2
            elif event.key == pygame.K_4:
                selected_quiz_option = 3


# =========================================================
# MAIN LOOP
# =========================================================
async def main():
    global pointer_pos, pointer_just_pressed, game_state

    frame_counter = 0

    while True:
        pointer_just_pressed = False
        frame_counter += 1

        # On mobile browsers the address bar can change the viewport height.
        # Checking regularly keeps the canvas fitted after refresh/orientation changes.
        if IS_BROWSER and frame_counter % 20 == 0:
            current_w, current_h = get_real_display_size()
            if abs(current_w - DISPLAY_W) > 2 or abs(current_h - DISPLAY_H) > 2:
                configure_layout_after_resize(current_w, current_h)
            else:
                apply_browser_page_fix()

        if not pointer_pressed:
            try:
                pointer_pos = screen_to_game_pos(pygame.mouse.get_pos())
            except Exception:
                pass

        for event in pygame.event.get():
            update_input_from_event(event)

        if game_state == "start":
            game_state = start_screen()
        elif game_state == "intro":
            game_state = intro_screen()
        elif game_state == "concept":
            game_state = concept_screen()
        elif game_state == "map":
            game_state = map_screen()
        elif game_state == "mini":
            game_state = mini_game_screen()
        elif game_state == "quiz":
            game_state = quiz_screen()
        elif game_state == "result":
            game_state = result_screen()
        elif game_state == "end":
            game_state = end_screen()

        present_frame()
        clock.tick(60)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
