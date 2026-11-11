"""Jogo dos Oito (8-Puzzle): lógica do jogo e métodos de busca (BFS e A*).

Representação: tupla de 9 inteiros (linha a linha); 0 é o espaço vazio.
Este módulo não depende de tkinter, para poder ser testado sem interface.
"""
import heapq
import random
import time
from collections import deque
from dataclasses import dataclass, field

OBJETIVO = (1, 2, 3, 8, 0, 4, 7, 6, 5)

# Movimentos do ESPAÇO VAZIO: nome -> (delta_linha, delta_coluna)
MOVIMENTOS = {
    "Cima": (-1, 0),
    "Baixo": (1, 0),
    "Esquerda": (0, -1),
    "Direita": (0, 1),
}


# ----------------------------------------------------------------------------
# Regras do jogo
# ----------------------------------------------------------------------------
def vizinhos(estado):
    """Lista de (nome_do_movimento, novo_estado) com os movimentos válidos."""
    i = estado.index(0)
    linha, coluna = divmod(i, 3)
    resultado = []
    for nome, (dl, dc) in MOVIMENTOS.items():
        nl, nc = linha + dl, coluna + dc
        if 0 <= nl < 3 and 0 <= nc < 3:
            j = nl * 3 + nc
            novo = list(estado)
            novo[i], novo[j] = novo[j], novo[i]
            resultado.append((nome, tuple(novo)))
    return resultado


def sao_adjacentes(i, j):
    """True se as posições i e j do tabuleiro (0..8) são vizinhas (sem diagonal)."""
    (li, ci), (lj, cj) = divmod(i, 3), divmod(j, 3)
    return abs(li - lj) + abs(ci - cj) == 1


def _inversoes(estado):
    pecas = [p for p in estado if p != 0]
    return sum(1 for a in range(len(pecas)) for b in range(a + 1, len(pecas))
               if pecas[a] > pecas[b])


def eh_resolvivel(estado, objetivo=OBJETIVO):
    """Num tabuleiro 3x3, um estado é alcançável se tem a mesma paridade de
    inversões que o objetivo."""
    return _inversoes(estado) % 2 == _inversoes(objetivo) % 2


def embaralhar(estado, passos=30, rng=random):
    """Passeio aleatório de movimentos válidos (sempre gera estado resolvível)."""
    anterior = None
    for _ in range(passos):
        opcoes = [e for _, e in vizinhos(estado) if e != anterior]
        anterior, estado = estado, rng.choice(opcoes)
    return estado


def estado_aleatorio(rng=random, objetivo=OBJETIVO):
    """Estado resolvível sorteado uniformemente entre os alcançáveis."""
    while True:
        pecas = list(range(9))
        rng.shuffle(pecas)
        pecas = tuple(pecas)
        if pecas != objetivo and eh_resolvivel(pecas, objetivo):
            return pecas


# ----------------------------------------------------------------------------
# Heurística
# ----------------------------------------------------------------------------
def distancia_manhattan(estado, objetivo=OBJETIVO):
    """Soma das distâncias de Manhattan de cada peça (exceto o vazio) até a
    posição que ela ocupa no objetivo."""
    pos_objetivo = {peca: divmod(i, 3) for i, peca in enumerate(objetivo)}
    total = 0
    for i, peca in enumerate(estado):
        if peca == 0:
            continue
        l, c = divmod(i, 3)
        lo, co = pos_objetivo[peca]
        total += abs(l - lo) + abs(c - co)
    return total


# ----------------------------------------------------------------------------
# Buscas
# ----------------------------------------------------------------------------
@dataclass
class Resultado:
    metodo: str
    encontrado: bool
    caminho: list = field(default_factory=list)      # estados, do inicial ao objetivo
    movimentos: list = field(default_factory=list)   # nomes dos movimentos
    nos_expandidos: int = 0
    tempo: float = 0.0
    mensagem: str = ""

    @property
    def passos(self):
        return len(self.movimentos)


def _reconstruir(pai, estado):
    caminho, movimentos = [estado], []
    while pai[estado] is not None:
        estado, nome = pai[estado]
        caminho.append(estado)
        movimentos.append(nome)
    caminho.reverse()
    movimentos.reverse()
    return caminho, movimentos


def _sem_solucao(metodo):
    return Resultado(metodo, False, mensagem="Estado sem solução (paridade).")


def busca_amplitude(inicio, objetivo=OBJETIVO):
    """BFS: fila FIFO + conjunto de visitados. Nó expandido = estado retirado
    da fronteira (o teste de objetivo é feito na retirada, como no A*)."""
    if not eh_resolvivel(inicio, objetivo):
        return _sem_solucao("BFS")
    t0 = time.perf_counter()
    fila = deque([inicio])
    pai = {inicio: None}          # também serve de conjunto de visitados
    expandidos = 0
    while fila:
        estado = fila.popleft()
        expandidos += 1
        if estado == objetivo:
            caminho, movs = _reconstruir(pai, estado)
            return Resultado("BFS", True, caminho, movs, expandidos,
                             time.perf_counter() - t0)
        for nome, filho in vizinhos(estado):
            if filho not in pai:
                pai[filho] = (estado, nome)
                fila.append(filho)
    return _sem_solucao("BFS")


def busca_a_estrela(inicio, objetivo=OBJETIVO):
    """A*: fila de prioridade (heapq) ordenada por f(n) = g(n) + h(n), com h =
    Distância de Manhattan. Desempate por menor h e depois por ordem de inserção."""
    if not eh_resolvivel(inicio, objetivo):
        return _sem_solucao("A*")
    t0 = time.perf_counter()
    h0 = distancia_manhattan(inicio, objetivo)
    contador = 0
    fronteira = [(h0, h0, contador, 0, inicio)]       # (f, h, ordem, g, estado)
    pai = {inicio: None}
    melhor_g = {inicio: 0}
    fechados = set()
    expandidos = 0
    while fronteira:
        _, _, _, g, estado = heapq.heappop(fronteira)
        if estado in fechados:                         # entrada obsoleta
            continue
        fechados.add(estado)
        expandidos += 1
        if estado == objetivo:
            caminho, movs = _reconstruir(pai, estado)
            return Resultado("A*", True, caminho, movs, expandidos,
                             time.perf_counter() - t0)
        for nome, filho in vizinhos(estado):
            novo_g = g + 1
            if filho in fechados or novo_g >= melhor_g.get(filho, float("inf")):
                continue
            melhor_g[filho] = novo_g
            pai[filho] = (estado, nome)
            h = distancia_manhattan(filho, objetivo)
            contador += 1
            heapq.heappush(fronteira, (novo_g + h, h, contador, novo_g, filho))
    return _sem_solucao("A*")


METODOS = {"BFS": busca_amplitude, "A*": busca_a_estrela}


# ----------------------------------------------------------------------------
# Controlador do jogo (usado pela interface; sem tkinter)
# ----------------------------------------------------------------------------
class Jogo:
    def __init__(self, rng=None, objetivo=OBJETIVO):
        self.rng = rng or random.Random()
        self.objetivo = objetivo
        self.estado = objetivo
        self.jogadas = 0
        self.solucao = None     # Resultado da última busca
        self.indice = 0         # posição atual na solução
        self.novo_jogo()

    # -- estado do tabuleiro ------------------------------------------------
    @property
    def resolvido(self):
        return self.estado == self.objetivo

    def _descartar_solucao(self):
        self.solucao, self.indice = None, 0

    def novo_jogo(self):
        self.estado = estado_aleatorio(self.rng, self.objetivo)
        self.jogadas = 0
        self._descartar_solucao()

    def embaralhar(self, passos=30):
        self.estado = embaralhar(self.estado, passos, self.rng)
        self.jogadas = 0
        self._descartar_solucao()

    def clicar(self, posicao):
        """Jogada manual: só move se a peça clicada é adjacente ao vazio."""
        vazio = self.estado.index(0)
        if not sao_adjacentes(posicao, vazio):
            return False
        novo = list(self.estado)
        novo[posicao], novo[vazio] = novo[vazio], novo[posicao]
        self.estado = tuple(novo)
        self.jogadas += 1
        self._descartar_solucao()
        return True

    # -- solução automática ---------------------------------------------------
    def resolver(self, metodo):
        resultado = METODOS[metodo](self.estado, self.objetivo)
        if resultado.encontrado:
            self.solucao, self.indice = resultado, 0
        return resultado

    @property
    def total_passos(self):
        return self.solucao.passos if self.solucao else 0

    def proximo(self):
        if self.solucao and self.indice < self.total_passos:
            self.indice += 1
            self.estado = self.solucao.caminho[self.indice]
            return True
        return False

    def anterior(self):
        if self.solucao and self.indice > 0:
            self.indice -= 1
            self.estado = self.solucao.caminho[self.indice]
            return True
        return False
