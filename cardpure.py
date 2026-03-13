import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 1400, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Letter Matching Game with Matrix")
clock = pygame.time.Clock()

BLACK_BG = (10,10,10)
WHITE_TEXT = (245,245,245)
PURPLE = (180,100,200)
BLACK_LETTER = (0,0,0)
YELLOW = (255,215,0)
GREEN = (0,255,0)
RED = (255,0,0)
MATRIX_COLORS = [(50,255,50),(0,200,255),(255,180,50)]

font_big = pygame.font.SysFont('comicsansms', 120)
font_medium = pygame.font.SysFont('comicsansms', 52)
font_small = pygame.font.SysFont('comicsansms', 36)

CARD = 110
SPACE = 12
ROWS = 15
COLS = 5
score = 0
xp = 0
level = 1
selected = []
plus_text = None
plus_time = 0
flip_animation = []
matrix_boost_end = 0

def random_letter_sensor():
    idx = random.randint(0, 25999)
    return chr(ord('A') + idx % 26)

class Card:
    def __init__(self, content, color, x, y, is_white=False):
        self.content = content
        self.color = color
        self.rect = pygame.Rect(x, y, CARD, CARD)
        self.visible = True
        self.selected = False
        self.is_white = is_white
        self.flipping = False
        self.flip_progress = 0
        self.new_content = None

def build_letters():
    cards = []
    start_x = WIDTH//2 - (COLS*CARD + (COLS-1)*SPACE)//2
    start_y = 50
    for r in range(ROWS):
        for c in range(COLS):
            x = start_x + c*(CARD+SPACE)
            y = start_y + r*(CARD+SPACE)
            cards.append(Card(random_letter_sensor(), PURPLE, x, y))
    return cards

def draw_cards(cards):
    for c in cards:
        if not c.visible:
            continue
        rect = c.rect.copy()
        if c.flipping:
            progress = c.flip_progress / 2
            shrink = abs(0.5 - progress) * 2
            rect.width = max(5, int(CARD * shrink))
            rect.centerx = c.rect.centerx
        pygame.draw.rect(screen, c.color, rect, border_radius=20)
        if not c.flipping:
            text_color = BLACK_LETTER if c.is_white else WHITE_TEXT
            text = font_big.render(c.content, True, text_color)
            tx = rect.centerx - text.get_width()//2
            ty = rect.centery - text.get_height()//2
            screen.blit(text, (tx, ty))
        if c.selected:
            pygame.draw.rect(screen,(255,255,0),rect,5)

def handle_click(card):
    global score, xp, level, plus_text, plus_time, flip_animation, matrix_boost_end
    if card.selected or card.flipping:
        card.selected = False
        selected.remove(card)
        return
    card.selected = True
    selected.append(card)
    if len(selected)!=2:
        return
    c1, c2 = selected
    gain = 0
    if not c1.is_white and not c2.is_white:
        if c1.content == c2.content:
            gain = 5
            matrix_boost_end = time.time() + 3
            for c in (c1,c2):
                c.flipping = True
                c.flip_progress = 0
                c.new_content = random_letter_sensor()
                c.is_white = True
                c.color = WHITE_TEXT
                flip_animation.append(c)
    elif c1.is_white and c2.is_white:
        if c1.content == c2.content:
            gain = 5
            c1.visible = False
            c2.visible = False
            matrix_boost_end = time.time() + 3
    score += gain
    xp += gain
    plus_text = f"+{gain}" if gain>0 else None
    plus_time = time.time()
    for c in selected:
        c.selected=False
    selected.clear()
    if score >= level*100:
        level += 1
        score += 25

cards = build_letters()
hud_x = 20
score_rect = pygame.Rect(hud_x, 20, 250, 50)
level_rect = pygame.Rect(hud_x, 80, 250, 50)
xp_rect = pygame.Rect(hud_x, 140, 250, 50)
cards_end_y = 50 + ROWS*(CARD + SPACE)
MATRIX_X = 50
MATRIX_Y = 170
MATRIX_W = 250
MATRIX_H = cards_end_y - MATRIX_Y - 30
restart_rect = pygame.Rect(MATRIX_X, cards_end_y + 20, 250, 60)

matrix_symbols = []
for i in range(80):
    matrix_symbols.append({
        'x': random.randint(MATRIX_X, MATRIX_X+MATRIX_W),
        'y': random.randint(MATRIX_Y, MATRIX_Y+MATRIX_H),
        'speed': random.uniform(2,6),
        'char': random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        'color': random.choice(MATRIX_COLORS)
    })

def draw_matrix():
    now = time.time()
    boost = 2 if now < matrix_boost_end else 1
    color_gold = YELLOW if now < matrix_boost_end else None
    for sym in matrix_symbols:
        sym['y'] += sym['speed'] * boost
        if sym['y'] > MATRIX_Y + MATRIX_H:
            sym['y'] = MATRIX_Y
            sym['char'] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        text_color = color_gold if color_gold else sym['color']
        text = font_small.render(sym['char'], True, text_color)
        screen.blit(text, (sym['x'], sym['y']))

running = True
while running:
    screen.fill(BLACK_BG)
    score_color = GREEN if score>=0 else RED
    screen.blit(font_small.render(f"Score: {score}", True, score_color), (score_rect.x, score_rect.y))
    screen.blit(font_small.render(f"Level: {level}", True, WHITE_TEXT), (level_rect.x, level_rect.y))
    screen.blit(font_small.render(f"XP: {xp}", True, WHITE_TEXT), (xp_rect.x, xp_rect.y))
    for c in flip_animation:
        if c.flipping:
            c.flip_progress += 1
            if c.flip_progress >= 2:
                c.flipping = False
                c.content = c.new_content
                c.new_content = None
    draw_cards(cards)
    draw_matrix()
    pygame.draw.rect(screen, (100,150,255), restart_rect, border_radius=15)
    screen.blit(font_small.render("Restart", True, BLACK_BG), (restart_rect.x+70, restart_rect.y+15))
    now = time.time()
    if plus_text and now-plus_time < 2:
        screen.blit(font_medium.render(plus_text, True, RED), (hud_x, 220))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if restart_rect.collidepoint(event.pos):
                score = max(0, score-10)
                xp = 0
                level = 1
                cards = build_letters()
                for i in range(80):
                    matrix_symbols[i]['x'] = random.randint(MATRIX_X, MATRIX_X+MATRIX_W)
                    matrix_symbols[i]['y'] = random.randint(MATRIX_Y, MATRIX_Y+MATRIX_H)
                    matrix_symbols[i]['speed'] = random.uniform(2,6)
                    matrix_symbols[i]['char'] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                    matrix_symbols[i]['color'] = random.choice(MATRIX_COLORS)
            for c in cards:
                if c.rect.collidepoint(event.pos) and c.visible:
                    handle_click(c)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()