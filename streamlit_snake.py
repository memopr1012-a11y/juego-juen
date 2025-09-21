import streamlit as st
import random
import time
from PIL import Image, ImageDraw

# --- Configuración del juego ---
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 30
GAME_SPEED = 0.15

def initialize_game():
    st.session_state.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    st.session_state.direction = "RIGHT"
    st.session_state.food = _get_random_food_pos(st.session_state.snake)
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.game_started = False

def _get_random_food_pos(snake):
    while True:
        food_pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food_pos not in snake:
            return food_pos

def draw_board():
    width = GRID_WIDTH * CELL_SIZE
    height = GRID_HEIGHT * CELL_SIZE
    board = Image.new("RGBA", (width, height), (40, 40, 40, 255))
    draw = ImageDraw.Draw(board)

    # 🍎 Comida (círculo rojo con brillo)
    fx, fy = st.session_state.food
    x0, y0 = fx * CELL_SIZE + 5, fy * CELL_SIZE + 5
    x1, y1 = (fx + 1) * CELL_SIZE - 5, (fy + 1) * CELL_SIZE - 5
    draw.ellipse([x0, y0, x1, y1], fill=(255, 80, 80), outline=(200, 0, 0), width=3)

    # 🐍 Serpiente (cabeza distinta al cuerpo)
    for i, (x, y) in enumerate(st.session_state.snake):
        x0, y0 = x * CELL_SIZE + 2, y * CELL_SIZE + 2
        x1, y1 = (x + 1) * CELL_SIZE - 2, (y + 1) * CELL_SIZE - 2
        if i == 0:  # Cabeza
            draw.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=(0, 255, 100), outline=(0, 200, 80), width=3)
            # ojitos
            draw.ellipse([x0+5, y0+5, x0+10, y0+10], fill="black")
            draw.ellipse([x1-10, y0+5, x1-5, y0+10], fill="black")
        else:       # Cuerpo
            draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=(0, 200, 0), outline=(0, 150, 0), width=2)
    return board

# --- Interfaz ---
st.set_page_config(page_title="Snake Animado", page_icon="🐍", layout="wide")

st.title("🐍 Snake con teclas")
st.markdown("Usa las teclas **WASD** o **Flechas** para mover la serpiente.")

if "snake" not in st.session_state:
    initialize_game()

board_placeholder = st.empty()
score_placeholder = st.empty()

# Guardar última tecla (⚠️ Streamlit no captura teclado en tiempo real sin un componente JS externo)
if "last_key" not in st.session_state:
    st.session_state.last_key = "RIGHT"

# Controles manuales (puedes cambiarlos luego por captura con JS)
col1, col2, col3 = st.columns(3)
if col2.button("⬆️"): st.session_state.last_key = "UP"
if col1.button("⬅️"): st.session_state.last_key = "LEFT"
if col3.button("➡️"): st.session_state.last_key = "RIGHT"
if col2.button("⬇️"): st.session_state.last_key = "DOWN"

def process_key():
    key = st.session_state.last_key
    if key in ["UP", "DOWN", "LEFT", "RIGHT"]:
        st.session_state.direction = key

# --- Lógica del juego ---
if st.session_state.game_started and not st.session_state.game_over:
    process_key()

    snake = st.session_state.snake.copy()
    head = snake[0]
    direction = st.session_state.direction

    if direction == "UP":
        new_head = (head[0], head[1] - 1)
    elif direction == "DOWN":
        new_head = (head[0], head[1] + 1)
    elif direction == "LEFT":
        new_head = (head[0] - 1, head[1])
    else:
        new_head = (head[0] + 1, head[1])

    if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT) or new_head in snake:
        st.session_state.game_over = True
    else:
        snake.insert(0, new_head)
        if new_head == st.session_state.food:
            st.session_state.score += 1
            st.session_state.food = _get_random_food_pos(snake)
        else:
            snake.pop()
        st.session_state.snake = snake

    score_placeholder.metric("🏆 Puntuación", st.session_state.score)
    board_placeholder.image(draw_board())

    time.sleep(GAME_SPEED)
    st.rerun()

# Botones inicio/reinicio
if st.session_state.game_over:
    st.error(f"💀 GAME OVER - Puntuación: {st.session_state.score}")
    if st.button("🔄 Reiniciar"):
        initialize_game()
        st.rerun()
elif not st.session_state.game_started:
    if st.button("▶️ Iniciar"):
        st.session_state.game_started = True
        st.rerun()
