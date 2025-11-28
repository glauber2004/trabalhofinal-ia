import pygame
import random

pygame.init()

# =============================
# CONFIGURAÇÕES DO AMBIENTE
# =============================
GRID_SIZE = 7
CELL_SIZE = 70
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE + 100
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
BLUE = (40, 90, 255)
ORANGE = (255, 150, 40)
GRAY = (140, 140, 140)
GOLD = (255, 215, 0)
RED = (220, 20, 20)

# =============================
# ÍCONES DO JOGO
# =============================

def draw_agent(surface, x, y):
    cx = x + CELL_SIZE // 2
    cy = y + CELL_SIZE // 2
    pygame.draw.circle(surface, BLACK, (cx, cy), 20)
    pygame.draw.rect(surface, (80, 80, 80), (cx - 12, cy + 5, 24, 14))

def draw_zombie(surface, x, y):
    cx = x + CELL_SIZE // 2
    cy = y + CELL_SIZE // 2
    pygame.draw.circle(surface, GREEN, (cx, cy), 20)
    pygame.draw.circle(surface, BLACK, (cx - 7, cy - 5), 5)
    pygame.draw.circle(surface, BLACK, (cx + 7, cy - 5), 5)

def draw_supply(surface, x, y):
    rect = pygame.Rect(x + 12, y + 12, 45, 45)
    pygame.draw.rect(surface, BLUE, rect)
    pygame.draw.rect(surface, ORANGE, (rect.x, rect.y, 45, 10))

def draw_rock(surface, x, y):
    points = [
        (x + 10, y + 50),
        (x + 25, y + 15),
        (x + 50, y + 25),
        (x + 60, y + 50),
    ]
    pygame.draw.polygon(surface, GRAY, points)

def draw_safe_zone(surface, x, y):
    pygame.draw.rect(surface, GOLD, (x + 10, y + 10, CELL_SIZE - 20, CELL_SIZE - 20))


# =============================
# TELA INICIAL
# =============================
def tela_inicial(screen):
    font = pygame.font.SysFont("arialblack", 48)
    font2 = pygame.font.SysFont("arial", 28)

    while True:
        screen.fill((40, 40, 40))

        title = font.render("THE LAST SURVIVOR - RL", True, GOLD)
        start = font2.render("Pressione ENTER para iniciar", True, WHITE)

        screen.blit(title, (40, 200))
        screen.blit(start, (120, 350))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return


# =============================
# GERA O MAPA
# =============================
def gerar_mapa():
    grid = [["vazio" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Agente
    ax, ay = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
    grid[ay][ax] = "agente"

    # Porta final (um quadrado dourado simples)
    px, py = GRID_SIZE - 1, GRID_SIZE - 1
    grid[py][px] = "safe"

    # Zumbis
    for _ in range(4):
        x, y = random.randint(0, GRID_SIZE - 2), random.randint(0, GRID_SIZE - 2)
        if grid[y][x] == "vazio":
            grid[y][x] = "zumbi"

    # Suprimentos
    for _ in range(5):
        x, y = random.randint(0, GRID_SIZE - 2), random.randint(0, GRID_SIZE - 2)
        if grid[y][x] == "vazio":
            grid[y][x] = "suprimento"

    # Pedras
    for _ in range(5):
        x, y = random.randint(0, GRID_SIZE - 2), random.randint(0, GRID_SIZE - 2)
        if grid[y][x] == "vazio":
            grid[y][x] = "pedra"

    return grid, (ax, ay)


# =============================
# MOVIMENTAÇÃO DO AGENTE
# =============================
def mover_agente(grid, pos, direction, score):
    x, y = pos
    nx, ny = x, y

    if direction == "up": ny -= 1
    if direction == "down": ny += 1
    if direction == "left": nx -= 1
    if direction == "right": nx += 1

    # limites
    if nx < 0 or nx >= GRID_SIZE or ny < 0 or ny >= GRID_SIZE:
        return pos, score, False, False

    cel = grid[ny][nx]

    # pedras bloqueiam
    if cel == "pedra":
        return pos, score, False, False

    # zumbi → perde 10 pontos e o jogo acaba
    if cel == "zumbi":
        score -= 10
        return (nx, ny), score, True, True

    # suprimento → ganha +10 pontos
    if cel == "suprimento":
        score += 10

    # porta final → vence
    if cel == "safe":
        return (nx, ny), score, True, False

    # movimento normal
    grid[y][x] = "vazio"
    grid[ny][nx] = "agente"

    return (nx, ny), score, False, False


# =============================
# DESENHA O GRID COMPLETO
# =============================
def desenhar_grid(screen, grid):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):

            x = col * CELL_SIZE
            y = row * CELL_SIZE + 100

            pygame.draw.rect(screen, (120, 200, 120), (x, y, CELL_SIZE, CELL_SIZE), 1)

            item = grid[row][col]

            if item == "agente":
                draw_agent(screen, x, y)
            elif item == "zumbi":
                draw_zombie(screen, x, y)
            elif item == "suprimento":
                draw_supply(screen, x, y)
            elif item == "pedra":
                draw_rock(screen, x, y)
            elif item == "safe":
                draw_safe_zone(screen, x, y)


# =============================
# LOOP PRINCIPAL
# =============================
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ambiente RL - The Last Survivor")
    clock = pygame.time.Clock()

    tela_inicial(screen)

    grid, agent_pos = gerar_mapa()
    score = 0
    terminou = False
    morreu = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.KEYDOWN and not terminou:
                if event.key == pygame.K_UP:
                    agent_pos, score, terminou, morreu = mover_agente(grid, agent_pos, "up", score)
                if event.key == pygame.K_DOWN:
                    agent_pos, score, terminou, morreu = mover_agente(grid, agent_pos, "down", score)
                if event.key == pygame.K_LEFT:
                    agent_pos, score, terminou, morreu = mover_agente(grid, agent_pos, "left", score)
                if event.key == pygame.K_RIGHT:
                    agent_pos, score, terminou, morreu = mover_agente(grid, agent_pos, "right", score)

        screen.fill((70, 130, 70))

        # HUD
        font = pygame.font.SysFont("arialblack", 32)
        text = font.render(f"Pontos: {score}", True, WHITE)
        screen.blit(text, (10, 30))

        desenhar_grid(screen, grid)

        # Mensagens finais
        font2 = pygame.font.SysFont("arialblack", 48)

        if terminou and morreu:
            msg = font2.render("Você Morreu!", True, RED)
            screen.blit(msg, (120, HEIGHT // 2))

        elif terminou:
            msg = font2.render("Você Venceu!", True, GOLD)
            screen.blit(msg, (140, HEIGHT // 2))

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
