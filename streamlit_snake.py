import streamlit as st
import random
import time
from PIL import Image, ImageDraw

# --- Constantes ---
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 25  # En píxeles

# Colores
BG_COLOR = "#1e1e2f"      # Fondo oscuro elegante
SNAKE_COLOR = "#4CAF50"   # Verde suave
FOOD_COLOR = "#FF5252"    # Rojo vibrante
HEAD_COLOR = "#76FF03"    # Verde brillante para la cabeza

# Velocidad base
DEFAULT_SPEED = 0.15


def initialize_game():
    """Configura el estado inicial del juego en st.session_state."""
    st.session_state.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    st.session_state.direction = "RIGHT"
    st.session_state.food = _get_random_food_pos(st.session_state.snake)
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.game_started = False
    st.session_state.speed = DEFAULT_SPEED


def _get_random_food_pos(snake):
    """Genera una posición aleatoria para la comida, asegurándose de que no esté en la serpiente."""
    while True:
        food_pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food_pos not in snake:
            return food_pos


def draw_board():
    """Dibuja el tablero de juego, la serpiente y la comida usando PIL."""
    width = GRID_WIDTH * CELL_SIZE
    height = GRID_HEIGHT * CELL_SIZE
    image = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(image)

    # Dibuja la comida
    food_pos = st.session_state.food
    draw.ellipse(
        [(food_pos[0] * CELL_SIZE + 3, food_pos[1] * CELL_SIZE + 3),
         ((food_pos[0] + 1) * CELL_SIZE - 3, (food_pos[1] + 1) * CELL_SIZE - 3)],
        fill=FOOD_COLOR
    )

    # Dibuja la serpiente
    for i, segment in enumerate(st.session_state.snake):
        color = HEAD_COLOR if i == 0 else SNAKE_COLOR
        draw.rounded_rectangle(
            [(segment[0] * CELL_SIZE + 2, segment[1] * CELL_SIZE + 2),
             ((segment[0] + 1) * CELL_SIZE - 2, (segment[1] + 1) * CELL_SIZE - 2)],
            radius=6,
            fill=color
        )
    return image


# --- App Principal ---
st.set_page_config(page_title="🐍 Snake Mejorado", page_icon="🎮", layout="wide")

st.title("🎮 Snake Game Mejorado en Streamlit")
st.markdown("¡Disfruta de una versión más **visual y divertida** del clásico juego de la culebrita!")

# Inicializa el estado del juego si no existe
if 'snake' not in st.session_state:
    initialize_game()

# --- Encabezado con puntuación y velocidad ---
score_col, speed_col = st.columns([2, 1])
score_col.metric("🏆 Puntuación", st.session_state.score)
st.session_state.speed = speed_col.slider("⚡ Velocidad", 0.05, 0.5, st.session_state.speed, 0.05)

# --- Layout de la UI del juego ---
col1, col2 = st.columns([3, 1])

with col1:
    board_placeholder = st.empty()
    board_placeholder.image(draw_board(), use_column_width=True)

with col2:
    st.markdown("### 🎛️ Controles")

    def set_direction(direction):
        current_dir = st.session_state.direction
        if (direction == "UP" and current_dir != "DOWN") or \
           (direction == "DOWN" and current_dir != "UP") or \
           (direction == "LEFT" and current_dir != "RIGHT") or \
           (direction == "RIGHT" and current_dir != "LEFT"):
            st.session_state.direction = direction

    # Joystick visual
    up = st.button("⬆️", on_click=set_direction, args=("UP",), use_container_width=True)
    left_col, right_col = st.columns(2)
    left_col.button("⬅️", on_click=set_direction, args=("LEFT",), use_container_width=True)
    right_col.button("➡️", on_click=set_direction, args=("RIGHT",), use_container_width=True)
    st.button("⬇️", on_click=set_direction, args=("DOWN",), use_container_width=True)

    st.markdown("---")

    # Botones de control
    if st.session_state.game_over:
        st.error(f"💀 ¡JUEGO TERMINADO! Puntuación final: {st.session_state.score}")
        if st.button("🔄 Reiniciar Juego", use_container_width=True):
            initialize_game()
            st.rerun()
    else:
        if not st.session_state.game_started:
            if st.button("▶️ Iniciar Juego", use_container_width=True):
                st.session_state.game_started = True
                st.rerun()
        else:
            if st.button("⏸️ Pausar Juego", use_container_width=True):
                st.session_state.game_started = False
                st.rerun()

# --- Lógica del juego ---
if st.session_state.game_started and not st.session_state.game_over:
    snake = st.session_state.snake.copy()
    head = snake[0]
    direction = st.session_state.direction

    # Nueva posición
    if direction == "UP":
        new_head = (head[0], head[1] - 1)
    elif direction == "DOWN":
        new_head = (head[0], head[1] + 1)
    elif direction == "LEFT":
        new_head = (head[0] - 1, head[1])
    else:  # RIGHT
        new_head = (head[0] + 1, head[1])

    # Colisión
    if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT) or new_head in snake:
        st.session_state.game_over = True
        st.rerun()

    # Actualiza la serpiente
    snake.insert(0, new_head)

    # Comer comida
    if new_head == st.session_state.food:
        st.session_state.score += 1
        st.session_state.food = _get_random_food_pos(snake)
    else:
        snake.pop()

    # Guardar estado
    st.session_state.snake = snake

    # Actualiza la UI
    score_col.metric("🏆 Puntuación", st.session_state.score)
    board_placeholder.image(draw_board(), use_column_width=True)

    # Espera según la velocidad
    time.sleep(st.session_state.speed)
    st.rerun()

