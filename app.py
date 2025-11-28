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

OBJETIVO_COLETAR_TUDO = True  # << PARÂMETRO OBRIGATÓRIO PARA IA COLETAR TUDO

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
ALPHA = 0.1
GAMMA = 0.95
EPSILON = 1.0
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.995
MAX_STEPS = 300  # aumentado para garantir coleta total

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

    def get_state(self, grid, pos, suprimentos_coletados):
        """Estado reduzido — mais simples e mais fácil de aprender"""
        
        suprimentos_restantes = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] == "suprimento":
                    suprimentos_restantes.append((c, r))

        return (
            pos,
            tuple(sorted(suprimentos_restantes)),
            suprimentos_coletados,
        )

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state, training=True):
        if training and random.random() < self.epsilon:
            return random.choice(self.actions)

        q_vals = [self.get_q_value(state, a) for a in self.actions]
        max_q = max(q_vals)
        melhores = [self.actions[i] for i in range(4) if q_vals[i] == max_q]
        return random.choice(melhores)

    def update_q_value(self, state, action, reward, next_state):
        old_q = self.get_q_value(state, action)
        next_max = max([self.get_q_value(next_state, a) for a in self.actions])
        new_q = old_q + ALPHA * (reward + GAMMA * next_max - old_q)
        self.q_table[(state, action)] = new_q

    def decay_epsilon(self):
        self.epsilon = max(EPSILON_MIN, self.epsilon * EPSILON_DECAY)

    def save_q_table(self):
        with open("q_table.pkl", "wb") as f:
            pickle.dump(self.q_table, f)

    def load_q_table(self):
        if os.path.exists("q_table.pkl"):
            with open("q_table.pkl", "rb") as f:
                self.q_table = pickle.load(f)
            self.epsilon = EPSILON_MIN


# =============================
# TELA INICIAL
# =============================
def tela_inicial(screen):
    font = pygame.font.SysFont("arialblack", 40)
    font2 = pygame.font.SysFont("arial", 24)

    while True:
        screen.fill((40, 40, 40))

        screen.blit(font.render("THE LAST SURVIVOR - RL", True, GOLD), (20, 180))
        screen.blit(font2.render("A - IA Jogar", True, GREEN), (150, 300))
        screen.blit(font2.render("T - Treinar IA", True, BLUE), (150, 350))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a: 
                    return "ai"
                if event.key == pygame.K_t: 
                    return "train"


# =============================
# GERADOR DE MAPA ALEATÓRIO (EXECUTADO UMA VEZ)
# =============================
def gerar_mapa_aleatorio_fixo():
    """Gera um mapa aleatório que será usado durante toda a execução"""
    grid = [["vazio" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    posicoes_ocupadas = set()
    
    # Agente sempre no canto superior esquerdo
    ax, ay = 0, 0
    grid[ay][ax] = "agente"
    posicoes_ocupadas.add((ax, ay))
    
    # Porta final sempre no canto inferior direito
    px, py = GRID_SIZE - 1, GRID_SIZE - 1
    grid[py][px] = "safe"
    posicoes_ocupadas.add((px, py))
    
    # Função auxiliar para pegar posição livre
    def posicao_livre():
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            if (x, y) not in posicoes_ocupadas:
                return x, y
    
    # Adiciona 4 zumbis em posições aleatórias
    for _ in range(4):
        x, y = posicao_livre()
        grid[y][x] = "zumbi"
        posicoes_ocupadas.add((x, y))
    
    # Adiciona 5 suprimentos em posições aleatórias
    for _ in range(5):
        x, y = posicao_livre()
        grid[y][x] = "suprimento"
        posicoes_ocupadas.add((x, y))
    
    # Adiciona 5 pedras em posições aleatórias
    for _ in range(5):
        x, y = posicao_livre()
        grid[y][x] = "pedra"
        posicoes_ocupadas.add((x, y))
    
    return grid, (ax, ay)

# Variável global que armazena o mapa gerado
MAPA_GLOBAL = None
POSICAO_INICIAL = None

def obter_mapa():
    """Retorna o mapa global ou gera um novo se não existir"""
    global MAPA_GLOBAL, POSICAO_INICIAL
    if MAPA_GLOBAL is None:
        MAPA_GLOBAL, POSICAO_INICIAL = gerar_mapa_aleatorio_fixo()
    
    # Retorna uma CÓPIA do mapa para não modificar o original
    grid_copia = [row[:] for row in MAPA_GLOBAL]
    return grid_copia, POSICAO_INICIAL


# =============================
# MOVIMENTAÇÃO
# =============================
def mover_agente(grid, pos, direction, suprimentos_coletados):
    x, y = pos
    nx, ny = x, y

    if direction == "up": ny -= 1
    if direction == "down": ny += 1
    if direction == "left": nx -= 1
    if direction == "right": nx += 1

    if nx < 0 or nx >= GRID_SIZE or ny < 0 or ny >= GRID_SIZE:
        return pos, -1, False, False, suprimentos_coletados

    cel = grid[ny][nx]

    if cel == "pedra":
        return pos, -1, False, False, suprimentos_coletados

    if cel == "zumbi":
        return (nx, ny), -80, True, True, suprimentos_coletados

    reward = -0.2

    if cel == "suprimento":
        reward = 40
        suprimentos_coletados += 1

    if cel == "safe":
        if OBJETIVO_COLETAR_TUDO:
            if suprimentos_coletados >= 5:
                return (nx, ny), 200, True, False, suprimentos_coletados
            else:
                return (nx, ny), -20, True, False, suprimentos_coletados
        else:
            return (nx, ny), 50, True, False, suprimentos_coletados

    grid[y][x] = "vazio"
    grid[ny][nx] = "agente"

    return (nx, ny), reward, False, False, suprimentos_coletados


# =============================
# DESENHO
# =============================
def desenhar_grid(screen, grid):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            x = c * CELL_SIZE
            y = r * CELL_SIZE + 100

            pygame.draw.rect(screen, (120, 200, 120), (x, y, CELL_SIZE, CELL_SIZE), 1)

            item = grid[r][c]

            if item == "agente": draw_agent(screen, x, y)
            elif item == "zumbi": draw_zombie(screen, x, y)
            elif item == "suprimento": draw_supply(screen, x, y)
            elif item == "pedra": draw_rock(screen, x, y)
            elif item == "safe": draw_safe_zone(screen, x, y)


# =============================
# TREINAMENTO
# =============================
def treinar_agente(screen, agent, episodios=700):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20)
    font2 = pygame.font.SysFont("arialblack", 32)

    for ep in range(episodios):

        grid, pos = obter_mapa()
        suprimentos = 0
        steps = 0

        while steps < MAX_STEPS:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    agent.save_q_table()
                    return

            state = agent.get_state(grid, pos, suprimentos)
            action = agent.choose_action(state, True)

            new_pos, reward, done, morreu, suprimentos = mover_agente(grid, pos, action, suprimentos)

            next_state = agent.get_state(grid, new_pos, suprimentos)

            agent.update_q_value(state, action, reward, next_state)

            pos = new_pos
            steps += 1

            if done:
                break

        agent.decay_epsilon()

        if ep % 10 == 0:
            screen.fill((30, 30, 30))
            screen.blit(font2.render(f"Treinando IA...", True, GOLD), (100, 200))
            screen.blit(font.render(f"Episódio {ep}/{episodios}", True, WHITE), (150, 270))
            screen.blit(font.render(f"Epsilon: {agent.epsilon:.3f}", True, WHITE), (150, 310))
            pygame.display.update()
            clock.tick(60)

    agent.save_q_table()
    
    # Tela final de treinamento
    screen.fill((30, 30, 30))
    screen.blit(font2.render("TREINAMENTO CONCLUÍDO!", True, GREEN), (60, 250))
    screen.blit(font.render("Q-Table salva! Pressione ENTER", True, WHITE), (100, 320))
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return


# =============================
# MODO IA JOGANDO
# =============================
def ia_jogar(screen, agente):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22)
    font2 = pygame.font.SysFont("arialblack", 36)
    
    grid, pos = obter_mapa()
    suprimentos = 0
    steps = 0
    rodando = True

    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        if steps < MAX_STEPS:
            state = agente.get_state(grid, pos, suprimentos)
            action = agente.choose_action(state, False)

            pos, reward, done, morreu, suprimentos = mover_agente(grid, pos, action, suprimentos)
            steps += 1

            screen.fill((70, 130, 70))
            
            # HUD
            screen.blit(font.render(f"Passos: {steps}", True, WHITE), (10, 20))
            screen.blit(font.render(f"Suprimentos: {suprimentos}/5", True, BLUE), (10, 50))
            screen.blit(font.render("ESC - Voltar ao menu", True, WHITE), (240, 20))
            
            desenhar_grid(screen, grid)
            
            if done:
                if morreu:
                    screen.blit(font2.render("MORREU! 💀", True, RED), (130, HEIGHT // 2))
                elif suprimentos >= 5:
                    screen.blit(font2.render("PERFEITO! 🏆", True, GOLD), (110, HEIGHT // 2))
                    screen.blit(font.render(f"Completado em {steps} passos!", True, WHITE), (130, HEIGHT // 2 + 60))
                else:
                    screen.blit(font2.render("FALHOU!", True, RED), (150, HEIGHT // 2))
                    screen.blit(font.render(f"Faltaram {5-suprimentos} suprimentos", True, WHITE), (120, HEIGHT // 2 + 60))
                
                pygame.display.update()
                pygame.time.wait(3000)
                
                # Reinicia
                grid, pos = obter_mapa()
                suprimentos = 0
                steps = 0
        else:
            # Tempo esgotado
            screen.fill((70, 130, 70))
            desenhar_grid(screen, grid)
            screen.blit(font2.render("TEMPO ESGOTADO!", True, ORANGE), (70, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(3000)
            
            grid, pos = obter_mapa()
            suprimentos = 0
            steps = 0

        pygame.display.update()
        clock.tick(6)  # Velocidade da IA


# =============================
# LOOP PRINCIPAL DO JOGO
# =============================
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Last Survivor - Q-Learning")

    # Gera o mapa aleatório uma única vez no início
    global MAPA_GLOBAL, POSICAO_INICIAL
    print("🗺️  Gerando mapa aleatório...")
    MAPA_GLOBAL, POSICAO_INICIAL = gerar_mapa_aleatorio_fixo()
    print("✅ Mapa gerado! Elementos distribuídos:")
    print("   - Agente: (0, 0)")
    print("   - Porta Segura: (6, 6)")
    print("   - Zumbis: 4")
    print("   - Suprimentos: 5")
    print("   - Pedras: 5")

    agente = QLearningAgent()

    while True:
        modo = tela_inicial(screen)

        if modo == "train":
            treinar_agente(screen, agente, 700)

        elif modo == "ai":
            if not os.path.exists("q_table.pkl"):
                # Mensagem de erro
                screen.fill((40, 40, 40))
                font = pygame.font.SysFont("arial", 24)
                screen.blit(font.render("ERRO: Treine a IA primeiro!", True, RED), (80, 250))
                screen.blit(font.render("Pressione ENTER para voltar", True, WHITE), (90, 300))
                pygame.display.update()
                
                esperando = True
                while esperando:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            esperando = False
                continue
            
            agente.load_q_table()
            ia_jogar(screen, agente)

if __name__ == "__main__":
    main()