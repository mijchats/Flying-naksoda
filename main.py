import pygame
import sys
import random
import os
import math

pygame.init()

# --- Sound Setup ---
# Sound files load karna
try:
    wing_sound = pygame.mixer.Sound('wing.wav')
    hit_sound = pygame.mixer.Sound('hit.wav')
    point_sound = pygame.mixer.Sound('point.wav')
except:
    print("Sound files nahi mili, files ka naam check karein.")

# ---------------- MOBILE SCREEN SIZE ----------------
# Mobile portrait size (9:16 ratio jesa mobile screen per fit ho)
WIDTH, HEIGHT = 405, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flying Naksoda")

# --- Background image load karna ---
try:
    background_image = pygame.image.load("background.png").convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except:
    background_image = None
# -----------------------------------


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Bird image load
try:
    bird_image = pygame.image.load("Naksodha.png").convert_alpha()
    bird_image = pygame.transform.scale(bird_image, (40, 40))
except:
    bird_image = pygame.Surface((40, 40))
    bird_image.fill((255, 255, 0))

# Pipe image load
try:
    pipe_image = pygame.image.load("pipe.png").convert_alpha()
except:
    pipe_image = None

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE = (0, 191, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 204, 0)
YELLOW_DARK = (204, 153, 0)
GOLD = (255, 215, 0)

bird_y = HEIGHT // 2
bird_velocity = 0
gravity = 0.25

# ---------------- PIPE SETTINGS (yahan se multiple pipes control hote hain) ----------------
PIPE_WIDTH = 50
pipe_gap = 170
PIPE_SPEED = 3
PIPE_SPAWN_DISTANCE = 220   # 2 pipes ke beech horizontal fasla. Kam karo = zyada hard, zyada karo = easy

# pipe height ka range screen ki nayi height ke hisab se
PIPE_HEIGHT_MIN = 100
PIPE_HEIGHT_MAX = HEIGHT - pipe_gap - 150

# pipes ab ek single variable nahi balke ek LIST hai
# har pipe ek dictionary hai: {'x': ..., 'height': ..., 'scored': ...}
pipes = []

score = 0
score_scale = 1.0          # ---- FANCY SCORE: score pop-animation ke liye ----
game_active = False
font = pygame.font.SysFont('Arial', 30, bold=True)
small_font = pygame.font.SysFont('Arial', 24, bold=True)
title_font = pygame.font.SysFont('arialblack', 48, bold=True)
button_font = pygame.font.SysFont('Arial', 30, bold=True)

# ---- FANCY SCORE: dedicated fonts (bade, bold, professional look) ----
SCORE_BASE_SIZE = 55
score_font_base = pygame.font.SysFont('arialblack', SCORE_BASE_SIZE, bold=True)
hs_font = pygame.font.SysFont('arialblack', 22, bold=True)

clock = pygame.time.Clock()

# ---------------- HIGH SCORE SETUP ----------------
HIGHSCORE_FILE = "highscore.txt"


def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0


def save_highscore(value):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(value))
    except:
        pass


high_score = load_highscore()


# ============================================================
# ---------------- FANCY / PROFESSIONAL TEXT ------------------
# ============================================================

def draw_text_outline(surface, text, font_obj, x, y, text_color=WHITE,
                       outline_color=BLACK, outline_width=3, align="center"):
    """
    Flappy Bird jesa outlined text: andar white/gold fill, bahar black border.
    align: "center" (x,y = center point), "topleft", ya "topright"
           (topright ka matlab x,y = right edge ka point, taake text kabhi
           screen se bahar na nikle).
    """
    outline_surfaces = []
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                outline_surfaces.append((font_obj.render(text, True, outline_color), dx, dy))

    main_surf = font_obj.render(text, True, text_color)

    if align == "center":
        rect = main_surf.get_rect(center=(round(x), round(y)))
    elif align == "topright":
        rect = main_surf.get_rect(topright=(round(x), round(y)))
    else:
        rect = main_surf.get_rect(topleft=(round(x), round(y)))

    for surf, dx, dy in outline_surfaces:
        surface.blit(surf, (rect.x + dx, rect.y + dy))

    surface.blit(main_surf, rect)


def draw_fancy_score(surface, current_score, best_score, scale):
    """
    Current score = screen ke bilkul top-center mein, bara, white text +
    black outline, pop-animation ke sath (jaise asli Flappy Bird mein hota hai).
    High score = top-right corner mein, screen ke andar hi (10px margin), chota,
    golden text + black outline.
    """
    dynamic_size = max(20, int(SCORE_BASE_SIZE * scale))
    dynamic_font = pygame.font.SysFont('arialblack', dynamic_size, bold=True)

    draw_text_outline(
        surface, str(current_score), dynamic_font,
        WIDTH / 2, 55,
        text_color=WHITE, outline_color=BLACK, outline_width=3, align="center"
    )

    draw_text_outline(
        surface, f"Best: {best_score}", hs_font,
        WIDTH - 12, 15,
        text_color=GOLD, outline_color=BLACK, outline_width=2, align="topright"
    )

# ============================================================
# --------------- END FANCY / PROFESSIONAL TEXT ---------------
# ============================================================


def create_pipe(x):
    return {
        'x': x,
        'height': random.randint(PIPE_HEIGHT_MIN, PIPE_HEIGHT_MAX),
        'scored': False
    }


def reset_game():
    global bird_y, bird_velocity, pipes, score, score_scale
    bird_y = HEIGHT // 2
    bird_velocity = 0
    score = 0
    score_scale = 1.0
    # Game start hote hi 2 pipes ek saath daal do taake shuru se hi 2 pipes dikhein
    pipes = [create_pipe(WIDTH), create_pipe(WIDTH + PIPE_SPAWN_DISTANCE)]


def flap_or_start():
    """Tap/click/space dabane per ye function chalta hai - jump ya game start"""
    global game_active
    if game_active:
        global bird_velocity
        bird_velocity = -6
        try:
            wing_sound.play()  # <--- SOUND: Udne ki awaaz
        except:
            pass
    else:
        game_active = True
        reset_game()


# ============================================================
# ------------------ PROFESSIONAL MENU CODE ------------------
# ============================================================

def draw_gradient_background(surface, top_color, bottom_color):
    """Agar background.png na mile to sundar gradient background banata hai"""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = top_color[0] + (bottom_color[0] - top_color[0]) * ratio
        g = top_color[1] + (bottom_color[1] - top_color[1]) * ratio
        b = top_color[2] + (bottom_color[2] - top_color[2]) * ratio
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


def draw_text_with_shadow(surface, text, font, color, shadow_color, x, y, center=True):
    shadow = font.render(text, True, shadow_color)
    main = font.render(text, True, color)
    if center:
        rect = main.get_rect(center=(x, y))
        shadow_rect = shadow.get_rect(center=(x + 3, y + 3))
    else:
        rect = main.get_rect(topleft=(x, y))
        shadow_rect = shadow.get_rect(topleft=(x + 3, y + 3))
    surface.blit(shadow, shadow_rect)
    surface.blit(main, rect)


class Button:
    """Hover per smoothly bara hone wala professional button"""
    def __init__(self, text, center_x, center_y, width=200, height=65):
        self.text = text
        self.center_x = center_x
        self.center_y = center_y
        self.base_width = width
        self.base_height = height
        self.hover_scale = 1.0

    def get_rect(self):
        w = self.base_width * self.hover_scale
        h = self.base_height * self.hover_scale
        return pygame.Rect(self.center_x - w / 2, self.center_y - h / 2, w, h)

    def is_hovered(self, mouse_pos):
        return self.get_rect().collidepoint(mouse_pos)

    def update(self, mouse_pos):
        target = 1.08 if self.is_hovered(mouse_pos) else 1.0
        self.hover_scale += (target - self.hover_scale) * 0.2

    def draw(self, surface):
        rect = self.get_rect()
        shadow_rect = rect.copy()
        shadow_rect.y += 6
        pygame.draw.rect(surface, YELLOW_DARK, shadow_rect, border_radius=18)
        pygame.draw.rect(surface, YELLOW, rect, border_radius=18)
        pygame.draw.rect(surface, WHITE, rect, width=3, border_radius=18)

        label = button_font.render(self.text, True, BLACK)
        label_rect = label.get_rect(center=rect.center)
        surface.blit(label, label_rect)


play_button = Button("PLAY", WIDTH // 2, HEIGHT // 2 + 60)
menu_timer = 0


def draw_menu(mouse_pos):
    """Professional looking start menu"""
    global menu_timer
    menu_timer += 1

    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        draw_gradient_background(screen, (78, 192, 202), (200, 230, 201))

    # halka dark overlay taake text zyada clear dikhe
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 60))
    screen.blit(overlay, (0, 0))

    # Bird floating animation
    bounce = math.sin(menu_timer * 0.08) * 12
    bird_rect_menu = bird_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140 + int(bounce)))
    screen.blit(bird_image, bird_rect_menu)

    # Title
    draw_text_with_shadow(screen, "FLYING NAKSODA", title_font, WHITE, BLACK,
                           WIDTH // 2, HEIGHT // 2 - 40)

    # Play button
    play_button.update(mouse_pos)
    play_button.draw(screen)

    # Instructions
    draw_text_with_shadow(screen, "Tap / Click / SPACE to Flap", small_font, WHITE, BLACK,
                           WIDTH // 2, HEIGHT // 2 + 150)
    draw_text_with_shadow(screen, "Press ESC to Exit", small_font, WHITE, BLACK,
                           WIDTH // 2, HEIGHT // 2 + 180)

    # High score - fancy outline wala (top-right, screen ke andar hi)
    draw_text_outline(screen, f"High Score: {high_score}", hs_font,
                       WIDTH - 12, 15, text_color=GOLD, outline_color=BLACK,
                       outline_width=2, align="topright")

# ============================================================
# --------------------- END MENU CODE -------------------------
# ============================================================


while True:
    mouse_pos = pygame.mouse.get_pos()

    if game_active and background_image:
        screen.blit(background_image, (0, 0))
    elif game_active:
        screen.fill(BLUE)
    # menu ka background draw_menu() khud sambhalta hai

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ---------------- TOUCH CONTROL (tap se chalega) ----------------
        # Mouse click (PC per test karne ke liye, aur mobile per bhi kaam karta hai)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_active:
                flap_or_start()
            else:
                # Menu me sirf Play button dabane per hi game start ho
                if play_button.is_hovered(mouse_pos):
                    flap_or_start()

        # Real finger touch event (mobile touchscreen ke liye)
        if event.type == pygame.FINGERDOWN:
            if game_active:
                flap_or_start()
            else:
                finger_pos = (event.x * WIDTH, event.y * HEIGHT)
                if play_button.is_hovered(finger_pos):
                    flap_or_start()

        # Keyboard (SPACE) - PC per bhi chal sake isliye rakha hai
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                flap_or_start()
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    if game_active:
        bird_velocity += gravity
        bird_y += bird_velocity

        # ---- SAB PIPES KO MOVE KARO ----
        for pipe in pipes:
            pipe['x'] -= PIPE_SPEED

        # ---- NAYA PIPE ADD KARO jab last pipe kaafi door nikal jaye ----
        if pipes[-1]['x'] < WIDTH - PIPE_SPAWN_DISTANCE:
            pipes.append(create_pipe(WIDTH))

        # ---- PURANE PIPES HATAO jo screen se bahar nikal gaye ----
        pipes = [p for p in pipes if p['x'] > -PIPE_WIDTH]

        bird_rect = pygame.Rect(50, int(bird_y), 40, 40)

        # ---- HAR PIPE KO DRAW, SCORE AUR COLLISION CHECK KARO ----
        collided = False
        for pipe in pipes:
            top_pipe_rect = pygame.Rect(pipe['x'], 0, PIPE_WIDTH, pipe['height'])
            bottom_pipe_rect = pygame.Rect(
                pipe['x'], pipe['height'] + pipe_gap, PIPE_WIDTH, HEIGHT - (pipe['height'] + pipe_gap)
            )

            if pipe_image:
                top_pipe_img = pygame.transform.scale(pipe_image, (PIPE_WIDTH, pipe['height']))
                screen.blit(top_pipe_img, (pipe['x'], 0))
                bottom_pipe_img = pygame.transform.scale(
                    pipe_image, (PIPE_WIDTH, HEIGHT - (pipe['height'] + pipe_gap))
                )
                screen.blit(bottom_pipe_img, (pipe['x'], pipe['height'] + pipe_gap))
            else:
                pygame.draw.rect(screen, GREEN, top_pipe_rect)
                pygame.draw.rect(screen, GREEN, bottom_pipe_rect)

            # score sirf ek dafa badhe jab bird pipe cross kare
            if not pipe['scored'] and pipe['x'] + PIPE_WIDTH < 50:
                pipe['scored'] = True
                score += 1
                score_scale = 1.35   # ---- FANCY SCORE: score badhte hi thora "pop" ----
                try:
                    point_sound.play()  # <--- SOUND: Score badhne ki awaaz
                except:
                    pass
                # ---- HIGH SCORE LIVE UPDATE (agar current score ne record tod diya) ----
                if score > high_score:
                    high_score = score

            if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
                collided = True

        screen.blit(bird_image, (50, int(bird_y)))

        # ---- FANCY SCORE: pop-animation ko normal size ki taraf wapas le aana ----
        if score_scale > 1.0:
            score_scale -= 0.03
            if score_scale < 1.0:
                score_scale = 1.0

        draw_fancy_score(screen, score, high_score, score_scale)

        if collided or bird_y > HEIGHT or bird_y < 0:
            try:
                hit_sound.play()  # <--- SOUND: Marne ki awaaz
            except:
                pass
            # ---- GAME KHATAM HONE PER HIGH SCORE FILE MEIN SAVE KARO ----
            if score > high_score:
                high_score = score
            save_highscore(high_score)
            game_active = False
    else:
        # ---------------- YAHAN PURANE "Tap Screen to Play" KI JAGAH NAYA MENU ----------------
        draw_menu(mouse_pos)

    pygame.display.update()
    clock.tick(60)
