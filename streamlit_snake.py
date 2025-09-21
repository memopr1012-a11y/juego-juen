import streamlit as st
import random
import time
from PIL import Image, ImageDraw

# --- Constantes ---
# Tablero de juego
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 25  # En píxeles

# Colores
BG_COLOR = "#000000"      # Negro
SNAKE_COLOR = "#00FF00"   # Verde
FOOD_COLOR = "#FF0000"    # Rojo
HEAD_COLOR = "#33FF33"    # Verde más claro para la cabeza

# Velocidad del juego
GAME_SPEED = 0.15  # Segundos por fotograma


def initialize_game():
    """Configura el estado inicial del juego en st.session_state."""
    st.session_state.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    st.session_state.direction = "RIGHT"
    st.session_state.food = _get_random_food_pos(st.session_state.snake)
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.game_started = False


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
    draw.rectangle(
        [(food_pos[0] * CELL_SIZE, food_pos[1] * CELL_SIZE),
         ((food_pos[0] + 1) * CELL_SIZE, (food_pos[1] + 1) * CELL_SIZE)],
        fill=FOOD_COLOR
    )

    # Dibuja la serpiente
    for i, segment in enumerate(st.session_state.snake):
        color = HEAD_COLOR if i == 0 else SNAKE_COLOR
        draw.rectangle(
            [(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE),
             ((segment[0] + 1) * CELL_SIZE, (segment[1] + 1) * CELL_SIZE)],
            fill=color
        )
    return image


# --- App Principal ---
st.set_page_config(page_title="Streamlit Snake", page_icon="🐍")

st.title("🐍 Streamlit Snake Game")
st.markdown("Un juego clásico de la culebrita hecho con Streamlit. Usa los botones para controlar la serpiente.")

# Inicializa el estado del juego si no existe
if 'snake' not in st.session_state:
    initialize_game()

# --- Layout de la UI del juego ---
col1, col2 = st.columns([3, 1])  # El tablero es 3 veces más ancho que los controles

with col1:
    st.markdown("### Tablero de Juego")
    board_placeholder = st.empty()
    board_placeholder.image(draw_board(), use_column_width=True)

with col2:
    st.markdown("### Controles")
    score_placeholder = st.metric("Puntuación", st.session_state.score)

    # --- Callbacks de control ---
    def set_direction(direction):
        current_dir = st.session_state.direction
        # Evita que la serpiente se invierta
        if (direction == "UP" and current_dir != "DOWN") or \
           (direction == "DOWN" and current_dir != "UP") or \
           (direction == "LEFT" and current_dir != "RIGHT") or \
           (direction == "RIGHT" and current_dir != "LEFT"):
            st.session_state.direction = direction

    # --- Botones de control ---
    st.button("⬆️", on_click=set_direction, args=("UP",), use_container_width=True)
    left_col, right_col = st.columns(2)
    left_col.button("⬅️", on_click=set_direction, args=("LEFT",), use_container_width=True)
    right_col.button("➡️", on_click=set_direction, args=("RIGHT",), use_container_width=True)
    st.button("⬇️", on_click=set_direction, args=("DOWN",), use_container_width=True)

    st.markdown("---")

    # --- Lógica de Inicio/Pausa/Reinicio ---
    if st.session_state.game_over:
        st.error(f"¡JUEGO TERMINADO! Puntuación final: {st.session_state.score}")
        if st.button("Jugar de Nuevo", use_container_width=True):
            initialize_game()
            st.rerun()
    else:
        if not st.session_state.game_started:
            if st.button("Iniciar Juego", use_container_width=True):
                st.session_state.game_started = True
                st.rerun()
        else:
            if st.button("Pausar Juego", use_container_width=True):
                st.session_state.game_started = False
                st.rerun()

# --- Lógica del Bucle de Juego ---
if st.session_state.game_started and not st.session_state.game_over:
    # Obtener estado actual
    snake = st.session_state.snake.copy()
    head = snake[0]
    direction = st.session_state.direction

    # Calcular nueva posición de la cabeza
    if direction == "UP":
        new_head = (head[0], head[1] - 1)
    elif direction == "DOWN":
        new_head = (head[0], head[1] + 1)
    elif direction == "LEFT":
        new_head = (head[0] - 1, head[1])
    else:  # RIGHT
        new_head = (head[0] + 1, head[1])

    # --- Detección de Colisiones ---
    if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT) or new_head in snake:
        st.session_state.game_over = True
        st.rerun()  # Refresca para mostrar la pantalla de "Juego Terminado"

    # --- Actualizar Serpiente ---
    snake.insert(0, new_head)

    # --- Consumo de Comida ---
    if new_head == st.session_state.food:
        st.session_state.score += 1
        st.session_state.food = _get_random_food_pos(snake)
    else:
        snake.pop()  # Elimina la cola si no se comió comida

    # Actualizar estado
    st.session_state.snake = snake

    # --- Actualizar UI ---
    score_placeholder.metric("Puntuación", st.session_state.score)
    board_placeholder.image(draw_board(), use_column_width=True)

    # --- Esperar y refrescar para el siguiente fotograma ---
    time.sleep(GAME_SPEED)
    st.rerun()
