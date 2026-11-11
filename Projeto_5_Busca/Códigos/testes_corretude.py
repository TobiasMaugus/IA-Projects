"""Testes de corretude da lógica do jogo e das buscas (executar: python testes_corretude.py)."""
import random

import puzzle as p


def aplicar(estado, movimentos):
    """Reexecuta uma lista de movimentos do vazio, validando cada um."""
    for nome in movimentos:
        opcoes = dict(p.vizinhos(estado))
        assert nome in opcoes, f"movimento inválido: {nome} em {estado}"
        estado = opcoes[nome]
    return estado


def test_numero_de_vizinhos():
    assert len(p.vizinhos((0, 1, 2, 3, 4, 5, 6, 7, 8))) == 2   # canto
    assert len(p.vizinhos((1, 0, 2, 3, 4, 5, 6, 7, 8))) == 3   # borda
    assert len(p.vizinhos(p.OBJETIVO)) == 4                    # centro


def test_movimentos_validos():
    estado = (1, 2, 3, 8, 0, 4, 7, 6, 5)
    for nome, filho in p.vizinhos(estado):
        assert sorted(filho) == list(range(9))
        assert sum(a != b for a, b in zip(estado, filho)) == 2  # só 2 posições mudam


def test_paridade_e_sem_solucao():
    impossivel = (2, 1, 3, 8, 0, 4, 7, 6, 5)                    # troca de duas peças
    assert not p.eh_resolvivel(impossivel)
    assert not p.busca_amplitude(impossivel).encontrado
    assert not p.busca_a_estrela(impossivel).encontrado


def test_casos_triviais():
    for busca in (p.busca_amplitude, p.busca_a_estrela):
        r = busca(p.OBJETIVO)
        assert r.encontrado and r.passos == 0
        um_passo = p.vizinhos(p.OBJETIVO)[0][1]
        r = busca(um_passo)
        assert r.encontrado and r.passos == 1


def test_solucoes_validas_e_otimas():
    rng = random.Random(7)
    for _ in range(25):
        inicio = p.estado_aleatorio(rng)
        bfs, astar = p.busca_amplitude(inicio), p.busca_a_estrela(inicio)
        for r in (bfs, astar):
            assert r.encontrado
            assert r.caminho[0] == inicio and r.caminho[-1] == p.OBJETIVO
            assert aplicar(inicio, r.movimentos) == p.OBJETIVO
            assert len(r.caminho) == r.passos + 1
        assert bfs.passos == astar.passos                      # ambos ótimos
        assert astar.nos_expandidos <= bfs.nos_expandidos      # A* nunca pior aqui
        assert p.distancia_manhattan(inicio) <= bfs.passos     # heurística admissível


def test_manhattan():
    assert p.distancia_manhattan(p.OBJETIVO) == 0
    assert p.distancia_manhattan(p.vizinhos(p.OBJETIVO)[0][1]) == 1


def test_embaralhar_gera_estado_resolvivel():
    rng = random.Random(3)
    for _ in range(50):
        assert p.eh_resolvivel(p.embaralhar(p.OBJETIVO, 40, rng))
        assert p.eh_resolvivel(p.estado_aleatorio(rng))


def test_controlador_jogada_manual():
    jogo = p.Jogo(random.Random(1))
    vazio = jogo.estado.index(0)
    longe = next(i for i in range(9) if i != vazio and not p.sao_adjacentes(i, vazio))
    antes = jogo.estado
    assert not jogo.clicar(longe) and jogo.estado == antes and jogo.jogadas == 0
    perto = next(i for i in range(9) if p.sao_adjacentes(i, vazio))
    assert jogo.clicar(perto) and jogo.jogadas == 1 and jogo.estado.index(0) == perto


def test_controlador_navegacao_da_solucao():
    jogo = p.Jogo(random.Random(5))
    inicial = jogo.estado
    r = jogo.resolver("A*")
    assert r.encontrado and jogo.estado == inicial
    while jogo.proximo():
        pass
    assert jogo.resolvido and jogo.indice == jogo.total_passos
    while jogo.anterior():
        pass
    assert jogo.estado == inicial and jogo.indice == 0
    jogo.proximo()
    vazio = jogo.estado.index(0)
    jogo.clicar(next(i for i in range(9) if p.sao_adjacentes(i, vazio)))
    assert jogo.solucao is None                               # jogada manual descarta a solução


if __name__ == "__main__":
    testes = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in testes:
        t()
        print(f"OK  {t.__name__}")
    print(f"\n{len(testes)} testes passaram.")
