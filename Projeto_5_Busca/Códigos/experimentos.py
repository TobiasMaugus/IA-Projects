"""Experimentos: compara BFS e A* (Distância de Manhattan) no Jogo dos Oito.

Uso: python experimentos.py [--casos 50] [--seed 42] [--csv resultados_experimentos.csv]

Para cada estado inicial aleatório (resolvível) mede: passos da solução, nós
expandidos e tempo de execução de cada método, e calcula a redução percentual de
nós e o speedup (tempo BFS / tempo A*).
"""
import argparse
import csv
import random
import statistics as st

import puzzle as p

FAIXAS = [("até 16 passos", 0, 16), ("17 a 20", 17, 20),
          ("21 a 24", 21, 24), ("25 ou mais", 25, 99)]


def rodar(casos, seed):
    rng = random.Random(seed)
    linhas = []
    for k in range(1, casos + 1):
        inicio = p.estado_aleatorio(rng)
        bfs = p.busca_amplitude(inicio)
        astar = p.busca_a_estrela(inicio)
        assert bfs.passos == astar.passos, "BFS e A* devem achar solução de mesmo tamanho"
        linhas.append({
            "caso": k, "estado_inicial": "".join(map(str, inicio)), "passos": bfs.passos,
            "nos_bfs": bfs.nos_expandidos, "nos_astar": astar.nos_expandidos,
            "tempo_bfs": bfs.tempo, "tempo_astar": astar.tempo,
            "reducao_nos_pct": 100 * (1 - astar.nos_expandidos / bfs.nos_expandidos),
            "speedup": bfs.tempo / astar.tempo,
        })
    return linhas


def resumo(linhas):
    nb = st.mean(l["nos_bfs"] for l in linhas)
    na = st.mean(l["nos_astar"] for l in linhas)
    tb = st.mean(l["tempo_bfs"] for l in linhas)
    ta = st.mean(l["tempo_astar"] for l in linhas)
    return {
        "casos": len(linhas), "passos_medio": st.mean(l["passos"] for l in linhas),
        "nos_bfs": nb, "nos_astar": na, "reducao_pct": 100 * (1 - na / nb),
        "tempo_bfs": tb, "tempo_astar": ta, "speedup": tb / ta,
        "speedup_mediano": st.median(l["speedup"] for l in linhas),
    }


def imprimir(linhas):
    r = resumo(linhas)
    print(f"\n{'faixa de profundidade':<16}{'casos':>6}{'nós BFS':>11}{'nós A*':>9}"
          f"{'redução':>10}{'t BFS (s)':>11}{'t A* (s)':>10}{'speedup':>9}")
    for nome, lo, hi in FAIXAS:
        grupo = [l for l in linhas if lo <= l["passos"] <= hi]
        if grupo:
            g = resumo(grupo)
            print(f"{nome:<16}{g['casos']:>6}{g['nos_bfs']:>11.0f}{g['nos_astar']:>9.0f}"
                  f"{g['reducao_pct']:>9.1f}%{g['tempo_bfs']:>11.4f}{g['tempo_astar']:>10.4f}"
                  f"{g['speedup']:>8.1f}x")
    print(f"{'TOTAL':<16}{r['casos']:>6}{r['nos_bfs']:>11.0f}{r['nos_astar']:>9.0f}"
          f"{r['reducao_pct']:>9.1f}%{r['tempo_bfs']:>11.4f}{r['tempo_astar']:>10.4f}"
          f"{r['speedup']:>8.1f}x")
    print(f"\nPassos médios da solução: {r['passos_medio']:.1f}")
    print(f"Speedup mediano por caso: {r['speedup_mediano']:.1f}x")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--csv", default="resultados_experimentos.csv")
    a = ap.parse_args()
    print(f"Executando {a.casos} casos (seed={a.seed}) ...")
    linhas = rodar(a.casos, a.seed)
    imprimir(linhas)
    with open(a.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    print(f"\nResultados por caso salvos em {a.csv}")


if __name__ == "__main__":
    main()
