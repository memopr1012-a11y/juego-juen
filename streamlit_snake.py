import streamlit as st
import random
import time
from PIL import Image

# --- Parámetros del juego ---
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 30

GAME_SPEED = 0.15

# Cargar imágenes (puedes reemplazar por sprites más bonitos)
HEAD_IMG = Image.open("snake_head.png").resize((CELL_SIZE, CELL_SIZE))
BODY_IMG = Image.open("snake_body.png").resize((CELL_SIZE, CELL_SIZE))
FOOD_IMG = Image.open("apple.png").resize((CELL_SIZE, CELL_SIZE))

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
    board = Image.new("RGBA", (width, height), (30, 30, 30, 255))

    # Comida
    fx, fy = st.session_state.food
    board.paste(FOOD_IMG, (fx * CELL_SIZE, fy * CELL_SIZE), FOOD_IMG)

    # Serpiente
    for i, (x, y) in enumerate(st.session_state.snake):
        if i == 0:
            board.paste(HEAD_IMG, (x * CELL_SIZE, y * CELL_SIZE), HEAD_IMG)
        else:
            board.paste(BODY_IMG, (x * CELL_SIZE, y * CELL_SIZE), BODY_IMG)

    return board

# --- Página principal ---
st.set_page_config(page_title="Snake Animado", page_icon="🐍", layout="wide")

st.title("🐍 Snake con teclas y diseño animado")
st.markdown("Usa las teclas **WASD** o **Flechas** para mover la serpiente.")

# Script JS para escuchar teclas y guardarlas en session_state
st.markdown(
    """
    <script>
    const streamlitDoc = window.parent.document;
    streamlitDoc.addEventListener("keydown", function(e) {
        let key = e.key;
        fetch("/_stcore/streamlit/js-event", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({"key": key})
        });
    });
    </script>
    """,
    unsafe_allow_html=True,
)

if "snake" not in st.session_state:
    initialize_game()

# Mostrar tablero
board_placeholder = st.empty()
score_placeholder = st.empty()

# Recibir teclas
if "last_key" not in st.session_state:
    st.session_state.last_key = "RIGHT"

def process_key():
    key = st.session_state.get("last_key", "")
    if key in ["ArrowUp", "w", "W"]:
        st.session_state.direction = "UP"
    elif key in ["ArrowDown", "s", "S"]:
        st.session_state.direction = "DOWN"
    elif key in ["ArrowLeft", "a", "A"]:
        st.session_state.direction = "LEFT"
    elif key in ["ArrowRight", "d", "D"]:
        st.session_state.direction = "RIGHT"

# --- Bucle del juego ---
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

    score_placeholder.metric("Puntuación", st.session_state.score)
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
