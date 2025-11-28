import pygame
import random
import numpy as np
import pickle
import os

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
# PARÂMETROS DE Q-LEARNING
# =============================
ALPHA = 0.1  # Taxa de aprendizado
GAMMA = 0.95  # Fator de desconto
EPSILON = 1.0  # Exploração inicial
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.995
MAX_STEPS = 100  # Máximo de passos por episódio

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
# CLASSE DO AGENTE Q-LEARNING
# =============================
class QLearningAgent:
    def __init__(self):
        self.q_table = {}
        self.epsilon = EPSILON
        self.actions = ["up", "down", "left", "right"]
        
    def get_state(self, grid, pos):
        """Converte o grid e posição em um estado serializável"""
        state_grid = tuple(tuple(row) for row in grid)
        return (state_grid, pos)
    
    def get_q_value(self, state, action):
        """Retorna o valor Q para um par estado-ação"""
        return self.q_table.get((state, action), 0.0)
    
    def choose_action(self, state, training=True):
        """Escolhe uma ação usando epsilon-greedy"""
        if training and random.random() < self.epsilon:
            return random.choice(self.actions)
        
        q_values = [self.get_q_value(state, action) for action in self.actions]
        max_q = max(q_values)
        best_actions = [self.actions[i] for i in range(len(self.actions)) if q_values[i] == max_q]
        return random.choice(best_actions)
    
    def update_q_value(self, state, action, reward, next_state):
        """Atualiza a Q-table usando a equação de Q-Learning"""
        old_q = self.get_q_value(state, action)
        next_max_q = max([self.get_q_value(next_state, a) for a in self.actions])
        new_q = old_q + ALPHA * (reward + GAMMA * next_max_q - old_q)
        self.q_table[(state, action)] = new_q
    
    def decay_epsilon(self):
        """Reduz o epsilon para diminuir a exploração"""
        self.epsilon = max(EPSILON_MIN, self.epsilon * EPSILON_DECAY)
    
    def save_q_table(self, filename="q_table.pkl"):
        """Salva a Q-table em arquivo"""
        with open(filename, "wb") as f:
            pickle.dump(self.q_table, f)
    
    def load_q_table(self, filename="q_table.pkl"):
        """Carrega a Q-table de arquivo"""
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                self.q_table = pickle.load(f)
            self.epsilon = EPSILON_MIN  # Usa epsilon mínimo quando carrega


# =============================
# TELA INICIAL
# =============================
def tela_inicial(screen):
    font = pygame.font.SysFont("arialblack", 40)
    font2 = pygame.font.SysFont("arial", 24)

    while True:
        screen.fill((40, 40, 40))

        title = font.render("THE LAST SURVIVOR - RL", True, GOLD)
        manual = font2.render("Pressione M para Modo MANUAL", True, WHITE)
        ai = font2.render("Pressione A para Modo IA (Q-Learning)", True, GREEN)
        train = font2.render("Pressione T para TREINAR IA", True, BLUE)

        screen.blit(title, (30, 150))
        screen.blit(manual, (100, 280))
        screen.blit(ai, (80, 330))
        screen.blit(train, (110, 380))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    return "manual"
                if event.key == pygame.K_a:
                    return "ai"
                if event.key == pygame.K_t:
                    return "train"


# =============================
# GERA O MAPA ESTÁTICO
# =============================
def gerar_mapa_estatico():
    """Cria um mapa fixo para treinamento consistente"""
    grid = [["vazio" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    # Posição inicial do agente (canto superior esquerdo)
    ax, ay = 0, 0
    grid[ay][ax] = "agente"
    
    # Porta final (canto inferior direito)
    grid[6][6] = "safe"
    
    # Zumbis em posições estratégicas
    grid[1][2] = "zumbi"
    grid[3][3] = "zumbi"
    grid[4][5] = "zumbi"
    grid[5][1] = "zumbi"
    
    # Suprimentos espalhados
    grid[0][3] = "suprimento"
    grid[1][5] = "suprimento"
    grid[2][1] = "suprimento"
    grid[4][2] = "suprimento"
    grid[5][5] = "suprimento"
    
    # Pedras como obstáculos
    grid[2][2] = "pedra"
    grid[2][4] = "pedra"
    grid[3][0] = "pedra"
    grid[4][4] = "pedra"
    grid[5][3] = "pedra"
    
    return grid, (ax, ay)

def gerar_mapa():
    """Gera mapa aleatório para modo manual"""
    grid = [["vazio" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Agente
    ax, ay = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
    grid[ay][ax] = "agente"

    # Porta final
    px, py = GRID_SIZE - 1, GRID_SIZE - 1
    if grid[py][px] == "agente":
        px, py = GRID_SIZE - 2, GRID_SIZE - 2
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
def mover_agente(grid, pos, direction):
    x, y = pos
    nx, ny = x, y

    if direction == "up": ny -= 1
    if direction == "down": ny += 1
    if direction == "left": nx -= 1
    if direction == "right": nx += 1

    # limites
    if nx < 0 or nx >= GRID_SIZE or ny < 0 or ny >= GRID_SIZE:
        return pos, -1, False, False  # Penalidade por tentar sair do mapa

    cel = grid[ny][nx]

    # pedras bloqueiam
    if cel == "pedra":
        return pos, -1, False, False

    # zumbi → perde 10 pontos e o jogo acaba
    if cel == "zumbi":
        grid[y][x] = "vazio"
        grid[ny][nx] = "agente"
        return (nx, ny), -10, True, True

    # suprimento → ganha +10 pontos
    reward = 0
    if cel == "suprimento":
        reward = 10

    # porta final → vence
    if cel == "safe":
        grid[y][x] = "vazio"
        grid[ny][nx] = "agente"
        return (nx, ny), 50, True, False  # Grande recompensa por vencer

    # movimento normal
    grid[y][x] = "vazio"
    grid[ny][nx] = "agente"

    return (nx, ny), reward - 0.1, False, False  # Pequena penalidade por cada passo


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
# MODO TREINAMENTO
# =============================
def treinar_agente(screen, agent, episodios=500):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20)
    
    stats = {
        "vitorias": 0,
        "derrotas": 0,
        "recompensa_total": []
    }
    
    for ep in range(episodios):
        # USA MAPA ESTÁTICO PARA TREINAMENTO
        grid, agent_pos = gerar_mapa_estatico()
        steps = 0
        episode_reward = 0
        
        while steps < MAX_STEPS:
            # Processa eventos para não travar
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    agent.save_q_table()
                    return
            
            state = agent.get_state(grid, agent_pos)
            action = agent.choose_action(state, training=True)
            
            new_pos, reward, done, morreu = mover_agente(grid, agent_pos, action)
            episode_reward += reward
            
            next_state = agent.get_state(grid, new_pos)
            agent.update_q_value(state, action, reward, next_state)
            
            agent_pos = new_pos
            steps += 1
            
            if done:
                if morreu:
                    stats["derrotas"] += 1
                else:
                    stats["vitorias"] += 1
                break
        
        stats["recompensa_total"].append(episode_reward)
        agent.decay_epsilon()
        
        # Atualiza visualização a cada 10 episódios
        if ep % 10 == 0:
            screen.fill((40, 40, 40))
            
            titulo = font.render(f"TREINANDO IA - Episódio {ep + 1}/{episodios}", True, GOLD)
            epsilon_text = font.render(f"Epsilon: {agent.epsilon:.3f}", True, WHITE)
            vitorias = font.render(f"Vitórias: {stats['vitorias']}", True, GREEN)
            derrotas = font.render(f"Derrotas: {stats['derrotas']}", True, RED)
            
            avg_reward = np.mean(stats["recompensa_total"][-100:]) if stats["recompensa_total"] else 0
            reward_text = font.render(f"Recompensa Média (últimos 100): {avg_reward:.2f}", True, WHITE)
            
            screen.blit(titulo, (50, 150))
            screen.blit(epsilon_text, (50, 200))
            screen.blit(vitorias, (50, 250))
            screen.blit(derrotas, (50, 300))
            screen.blit(reward_text, (50, 350))
            
            pygame.display.update()
            clock.tick(60)
    
    agent.save_q_table()
    
    # Tela final de treinamento
    while True:
        screen.fill((40, 40, 40))
        
        font2 = pygame.font.SysFont("arialblack", 36)
        titulo = font2.render("TREINAMENTO CONCLUÍDO!", True, GOLD)
        vitorias = font.render(f"Total de Vitórias: {stats['vitorias']}", True, GREEN)
        derrotas = font.render(f"Total de Derrotas: {stats['derrotas']}", True, RED)
        salvo = font.render("Q-Table salva em 'q_table.pkl'", True, WHITE)
        continuar = font.render("Pressione ENTER para voltar ao menu", True, WHITE)
        
        screen.blit(titulo, (50, 150))
        screen.blit(vitorias, (50, 220))
        screen.blit(derrotas, (50, 270))
        screen.blit(salvo, (50, 320))
        screen.blit(continuar, (50, 400))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return


# =============================
# MODO JOGO (MANUAL OU IA)
# =============================
def jogar(screen, modo, agent=None):
    clock = pygame.time.Clock()
    
    # Modo IA usa mapa estático, manual usa aleatório
    if modo == "ai":
        grid, agent_pos = gerar_mapa_estatico()
    else:
        grid, agent_pos = gerar_mapa()
    
    score = 0
    terminou = False
    morreu = False
    steps = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            
            if event.type == pygame.KEYDOWN and not terminou:
                if modo == "manual":
                    direction = None
                    if event.key == pygame.K_UP:
                        direction = "up"
                    elif event.key == pygame.K_DOWN:
                        direction = "down"
                    elif event.key == pygame.K_LEFT:
                        direction = "left"
                    elif event.key == pygame.K_RIGHT:
                        direction = "right"
                    
                    if direction:
                        agent_pos, reward, terminou, morreu = mover_agente(grid, agent_pos, direction)
                        score += reward
                        steps += 1
                
                if event.key == pygame.K_RETURN and terminou:
                    return
        
        # Modo IA
        if modo == "ai" and not terminou and steps < MAX_STEPS:
            state = agent.get_state(grid, agent_pos)
            action = agent.choose_action(state, training=False)
            agent_pos, reward, terminou, morreu = mover_agente(grid, agent_pos, action)
            score += reward
            steps += 1
            pygame.time.delay(200)  # Delay para visualizar
        
        screen.fill((70, 130, 70))
        
        # HUD
        font = pygame.font.SysFont("arialblack", 28)
        font2 = pygame.font.SysFont("arial", 20)
        
        score_text = font.render(f"Pontos: {score:.1f}", True, WHITE)
        steps_text = font2.render(f"Passos: {steps}/{MAX_STEPS}", True, WHITE)
        mode_text = font2.render(f"Modo: {'MANUAL' if modo == 'manual' else 'IA'}", True, GOLD)
        
        screen.blit(score_text, (10, 20))
        screen.blit(steps_text, (10, 55))
        screen.blit(mode_text, (280, 55))
        
        desenhar_grid(screen, grid)
        
        # Mensagens finais
        font3 = pygame.font.SysFont("arialblack", 42)
        
        if terminou and morreu:
            msg = font3.render("Você Morreu!", True, RED)
            screen.blit(msg, (110, HEIGHT // 2))
            msg2 = font2.render("Pressione ENTER para voltar", True, WHITE)
            screen.blit(msg2, (120, HEIGHT // 2 + 60))
        elif terminou:
            msg = font3.render("Você Venceu!", True, GOLD)
            screen.blit(msg, (120, HEIGHT // 2))
            msg2 = font2.render("Pressione ENTER para voltar", True, WHITE)
            screen.blit(msg2, (120, HEIGHT // 2 + 60))
        elif steps >= MAX_STEPS:
            terminou = True
            msg = font3.render("Tempo Esgotado!", True, ORANGE)
            screen.blit(msg, (90, HEIGHT // 2))
            msg2 = font2.render("Pressione ENTER para voltar", True, WHITE)
            screen.blit(msg2, (120, HEIGHT // 2 + 60))
        
        pygame.display.update()
        clock.tick(FPS)


# =============================
# LOOP PRINCIPAL
# =============================
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Last Survivor - RL Q-Learning")
    
    agent = QLearningAgent()
    
    # Tenta carregar Q-table existente
    if os.path.exists("q_table.pkl"):
        agent.load_q_table()
    
    while True:
        modo = tela_inicial(screen)
        
        if modo == "train":
            treinar_agente(screen, agent, episodios=500)
        elif modo == "manual":
            jogar(screen, "manual")
        elif modo == "ai":
            jogar(screen, "ai", agent)


if __name__ == "__main__":
    main()