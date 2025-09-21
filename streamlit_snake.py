# app.py
import streamlit as st
import random
import time
import math
from PIL import Image, ImageDraw
import base64

# Sonidos base64 (pequeños "beeps")
EAT_SOUND = """
data:audio/wav;base64,UklGRhQAAABXQVZFZm10IBAAAAABAAEA... (truncado por brevedad)
"""
GAMEOVER_SOUND = """
data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEA... (truncado por brevedad)
"""

# Intentamos usar streamlit_javascript para captura de teclado
USE_JS = True
try:
    from streamlit_javascript import st_javascript
except Exception:
    USE_JS = False

# ---------- CONFIG ----------
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 28
BASE_SPEED = 0.18
MIN_SPEED = 0.05
SPEED_STEP = 0.006

# ---------- INIT ----------
st.set_page_config(page_title="🐍 Snake Mejorado", layout="wide", page_icon="🎮")
st.title("🎮 Snake Mejorado con teclas, sonidos y animación")

if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    st.session_state.direction = "RIGHT"
    st.session_state.food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    st.session_state.score = 0
    st.session_state.best = 0
    st.session_state.game_started = False
    st.session_state.game_over = False
    st.session_state.paused = False
    st.session_state.speed = BASE_SPEED
    st.session_state.last_key = None
    st.session_state.frame = 0
    st.session_state.sound_to_play = None

# ---------- HELPERS ----------
def reset_game():
    st.session_state.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    st.session_state.direction = "RIGHT"
    st.session_state.food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.paused = False
    st.session_state.speed = BASE_SPEED
    st.session_state.frame = 0

def place_food(snake):
    while True:
        p = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if p not in snake:
            return p

def rotate_point(cx, cy, x, y, angle):
    s, c = math.sin(angle), math.cos(angle)
    x -= cx; y -= cy
    xr = x * c - y * s
    yr = x * s + y * c
    return cx + xr, cy + yr

def draw_head(draw, x0, y0, x1, y1, direction):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = min((x1 - x0), (y1 - y0)) / 2 - 2
    p1 = (cx + r, cy)
    p2 = (cx - r * 0.6, cy - r * 0.6)
    p3 = (cx - r * 0.6, cy + r * 0.6)
    angle = {"UP": -math.pi/2, "DOWN": math.pi/2, "LEFT": math.pi, "RIGHT": 0}[direction]
    pts = [rotate_point(cx, cy, *p, angle) for p in (p1, p2, p3)]
    draw.polygon(pts, fill=(30, 220, 120), outline=(5, 120, 60))
    # ojos
    ex1, ey1 = rotate_point(cx, cy, cx + r*0.3, cy - r*0.25, angle)
    ex2, ey2 = rotate_point(cx, cy, cx + r*0.3, cy + r*0.25, angle)
    for ex, ey in [(ex1, ey1), (ex2, ey2)]:
        draw.ellipse([ex-2, ey-2, ex+2, ey+2], fill="black")

def draw_board():
    cell = CELL_SIZE
    w, h = GRID_WIDTH * cell, GRID_HEIGHT * cell
    img = Image.new("RGBA", (w, h), (25, 28, 32, 255))
    draw = ImageDraw.Draw(img)
    # comida
    fx, fy = st.session_state.food
    margin = cell * 0.2
    draw.ellipse([fx*cell+margin, fy*cell+margin, (fx+1)*cell-margin, (fy+1)*cell-margin],
                 fill=(255, 90, 90), outline=(200, 30, 30), width=2)
    # serpiente
    phase = (st.session_state.frame % 20) / 20 * math.pi*2
    for i, (sx, sy) in enumerate(st.session_state.snake):
        x0, y0, x1, y1 = sx*cell+2, sy*cell+2, (sx+1)*cell-2, (sy+1)*cell-2
        if i == 0:
            draw_head(draw, x0, y0, x1, y1, st.session_state.direction)
        else:
            offset_x = math.sin(phase + i*0.5) * 2
            offset_y = math.cos(phase + i*0.5) * 1
            rect = [x0+offset_x, y0+offset_y, x1+offset_x, y1+offset_y]
            draw.rounded_rectangle(rect, radius=6, fill=(10, 160, 80), outline=(5, 120, 60))
    return img

# ---------- LAYOUT ----------
col1, col2 = st.columns([3, 1])

with col2:
    st.subheader("Controles")
    st.write("Teclado: **WASD/Flechas**, P pausa")
    st.write("Móvil: botones táctiles")
    st.metric("Puntuación", st.session_state.score)
    st.metric("Mejor", st.session_state.best)
    if st.button("▶️ Iniciar/Reiniciar"):
        reset_game(); st.session_state.game_started = True
    if st.button("⏸️ Pausar/Reanudar"):
        st.session_state.paused = not st.session_state.paused
    st.markdown("---")
    c1,c2,c3 = st.columns(3)
    if c1.button("⬆️"): st.session_state.last_key = "ArrowUp"
    if c2.button("⬅️"): st.session_state.last_key = "ArrowLeft"
    if c3.button("➡️"): st.session_state.last_key = "ArrowRight"
    if st.button("⬇️"): st.session_state.last_key = "ArrowDown"

with col1:
    board_placeholder = st.empty()
    st.caption("🐍 Snake con animación, teclado y sonidos.")

# ---------- KEYS ----------
if USE_JS:
    try:
        last = st_javascript("""
        new Promise((resolve) => {
          document.onkeydown = (e) => resolve(e.key);
        });
        """, key="listener")
        if last: st.session_state.last_key = last
    except: pass

def process_key():
    k = st.session_state.get("last_key")
    if not k: return
    dirs = {"ArrowUp":"UP","w":"UP","ArrowDown":"DOWN","s":"DOWN",
            "ArrowLeft":"LEFT","a":"LEFT","ArrowRight":"RIGHT","d":"RIGHT"}
    if k.lower() == "p": st.session_state.paused = not st.session_state.paused; return
    if k in dirs:
        newdir = dirs[k]
        cur = st.session_state.direction
        if (newdir=="UP" and cur!="DOWN") or (newdir=="DOWN" and cur!="UP") or \
           (newdir=="LEFT" and cur!="RIGHT") or (newdir=="RIGHT" and cur!="LEFT"):
            st.session_state.direction = newdir
process_key()

# ---------- GAME LOOP ----------
if st.session_state.game_started and not st.session_state.paused and not st.session_state.game_over:
    st.session_state.frame += 1
    snake = st.session_state.snake.copy()
    head = snake[0]
    moves = {"UP":(0,-1),"DOWN":(0,1),"LEFT":(-1,0),"RIGHT":(1,0)}
    dx,dy = moves[st.session_state.direction]
    new_head = (head[0]+dx, head[1]+dy)
    if not(0<=new_head[0]<GRID_WIDTH and 0<=new_head[1]<GRID_HEIGHT) or new_head in snake:
        st.session_state.game_over = True
        st.session_state.best = max(st.session_state.best, st.session_state.score)
        st.session_state.sound_to_play = GAMEOVER_SOUND
    else:
        snake.insert(0,new_head)
        if new_head == st.session_state.food:
            st.session_state.score += 1
            st.session_state.speed = max(MIN_SPEED, st.session_state.speed - SPEED_STEP)
            st.session_state.food = place_food(snake)
            st.session_state.sound_to_play = EAT_SOUND
        else: snake.pop()
        st.session_state.snake = snake
    board_placeholder.image(draw_board(), use_column_width=True)
    time.sleep(st.session_state.speed)
    st.experimental_rerun()
else:
    board_placeholder.image(draw_board(), use_column_width=True)
    if st.session_state.game_over: st.error(f"💀 GAME OVER — Score: {st.session_state.score}")

# ---------- SOUNDS ----------
if st.session_state.sound_to_play:
    st.audio(st.session_state.sound_to_play, format="audio/wav", autoplay=True)
    st.session_state.sound_to_play = None
