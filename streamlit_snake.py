import pygame
import random
import sys

# --- Inicialización ---
pygame.init()

# --- Colores ---
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
LIGHT_GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# --- Configuración de la pantalla ---
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 12  # velocidad inicial

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 Snake Game")

# --- Fuente ---
font = pygame.font.SysFont("Arial", 28, bold=True)


# --- Funciones auxiliares ---
def draw_snake(snake):
    for i, segment in enumerate(snake):
        color = LIGHT_GREEN if i == 0 else GREEN
        rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, color, rect)


def draw_food(food):
    rect = pygame.Rect(food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, RED, rect)


def draw_score(score):
    text = font.render(f"Puntuación: {score}", True, WHITE)
    screen.blit(text, (10, 10))


# --- Juego principal ---
def main():
    clock = pygame.time.Clock()

    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    direction = "RIGHT"
    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    score = 0
    game_over = False

    while True:
        # --- Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != "DOWN":
                    direction = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP":
                    direction = "DOWN"
                elif event.key == pygame.K_LEFT and direction != "RIGHT":
                    direction = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    direction = "RIGHT"

                # Reinicio tras perder
                elif game_over and event.key == pygame.K_SPACE:
                    return main()

        if not game_over:
            # --- Movimiento ---
            head = snake[0]
            if direction == "UP":
                new_head = (head[0], head[1] - 1)
            elif direction == "DOWN":
                new_head = (head[0], head[1] + 1)
            elif direction == "LEFT":
                new_head = (head[0] - 1, head[1])
            elif direction == "RIGHT":
                new_head = (head[0] + 1, head[1])

            # --- Colisiones ---
            if (
                new_head[0] < 0 or new_head[0] >= GRID_WIDTH
                or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT
                or new_head in snake
            ):
                game_over = True
            else:
                snake.insert(0, new_head)

                # Comer comida
                if new_head == food:
                    score += 1
                    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                else:
                    snake.pop()

        # --- Dibujar ---
        screen.fill(BLACK)

        if not game_over:
            draw_snake(snake)
            draw_food(food)
            draw_score(score)
        else:
            text1 = font.render("💀 GAME OVER 💀", True, RED)
            text2 = font.render(f"Puntuación: {score}", True, WHITE)
            text3 = font.render("Presiona ESPACIO para reiniciar", True, WHITE)
            screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 60))
            screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 - 20))
            screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.flip()
        clock.tick(FPS)


# --- Ejecutar ---
if __name__ == "__main__":
    main()
