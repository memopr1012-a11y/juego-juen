import streamlit as st
import random
import time
from PIL import Image
import base64
from io import BytesIO

# --- Sprites embebidos en base64 ---
def load_sprite(base64_str):
    return Image.open(BytesIO(base64.b64decode(base64_str))).convert("RGBA")

# 🐍 Cabeza de la serpiente
snake_head_b64 = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABo0lEQVRYR+2Wv0sDQRTHf0sXWlYp
yLwClWBpkVqCFtZeBG9DaEwRUeAuRNgzJAexQELQpI5EUopKoV1VgFDi2QlFBQgh+vva9vdObXOy
tWk6M3/3nnvvOd/zMwsJIMIYkwm+AKnGAh9imMYA5U4fDfgDa7cBdRoVqBJ1AOmE1xijFcOAk80z
llmDwXGe3gZ2RBjHnl6CqZ2yHjG0pUL4ZjjLO/yQux5J7R9jJNoPqHqvNiRhxhcmPcbWizCwHgi0
cXkGtzLs84rJyoZVJq0PAdfYwcKkN85K3L1q0xZT6UScdMu5uEbqOfcSuwklpW0B9T6zDdOdIkdl
3dTaa/h6IuzX0h8JfJbBGn0b9OtMp1DqcluZ30uGgXak+Y7Otms/IpwN77rV6A9XgGoZGH3bCv+B
qfAqks+2gk5AewMkE/djSy+gSQAAAABJRU5ErkJggg==
"""

# 🐍 Cuerpo de la serpiente
snake_body_b64 = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABY0lEQVRYR+2WPUvDQBTHfxdaGqtK
tEsVvIDiCh7AaP9AFsYJ9YEMNYMQP4AlpP+AcoEbuQBdW1g8SnvQmCZjIyC+RCV3gLLnYw62mTff
mztnK3gAyMiIFyB+jB3MALuBd9wCda4HkQT+Y3OMrE3CvJJ4s8FY3gTx1rvGMKcM4+U6uLCEmK2x
Dx9gyb1GjG1VcYOdTsnqN3YQccrnP5xgM+A0jbGuXcBuZcJz7idb6ydJtgLOMJ+WjY8my3SCE0Jp
ce3qciqHINJzTBlgxNNr09C0lsqD80OdoVkPNqM4Q0wQGeqtBpSR16j5txqvC3yn6L9EzAeCsnNO
q3AvADHfXgFVSmewAAAAASUVORK5CYII=
"""

# 🍎 Comida (manzana)
apple_b64 = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABWElEQVRYR+2WwUoDQRSGv2+ZbNNK
RGq1Gp0ajUZJjZJ+gLthhZI7kT2+gXrXxPkCc6OYt6lF2qghIWBK6yGBow9Nnuye95XoBEXiP03G
SwCxFvAc7wbFMaT44YxB/Af63/g/AJfYBLjDqTqBWzAuZbpXwF5mD1nmICm/RBHzMi7+7kU8B3hJ
bZr4rRrcswe3HY1L1AfTfznV2t4gE4FxjD3PpE+LAC/D6rNgs8xV6iyc4NMa6g1+Y0muUttYZAZT
qgbXKn8XGApbqn8VK0dUzfQ6MdyJgM8D1LYpUl8Ejkm59kCt+McDNC5b1pqutbVgItqLwFo6QXvX
fhUAAAAASUVORK5CYII=
"""

HEAD_IMG = load_sprite(snake_head_b64)
BODY_IMG = load_sprite(snake_body_b64)
FOOD_IMG = load_sprite(apple_b64)

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

# --- Interfaz ---
st.set_page_config(page_title="Snake Animado", page_icon="🐍", layout="wide")

st.title("🐍 Snake con teclas y diseño animado")
st.markdown("Usa las teclas **WASD** o **Flechas** para mover la serpiente.")

if "snake" not in st.session_state:
    initialize_game()

board_placeholder = st.empty()
score_placeholder = st.empty()

# Captura de teclas con JS
st.markdown(
    """
    <script>
    const streamlitDoc = window.parent.document;
    streamlitDoc.addEventListener("keydown", function(e) {
        let key = e.key;
        window.parent.postMessage({isStreamlitKeyEvent: true, key: key}, "*");
    });
    </script>
    """,
    unsafe_allow_html=True,
)

if "last_key" not in st.session_state:
    st.session_state.last_key = "RIGHT"

# Placeholder para mensajes de teclado
key_event = st.experimental_get_query_params().get("key", [""])[0]

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
