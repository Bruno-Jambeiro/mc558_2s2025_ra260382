import sys
import time

from gurobipy import Model, GRB


def minPathPL(grafo, s, d):
    """
    Resolve caminho mínimo s -> d usando Programação Linear.
    grafo[v] = lista de (vizinho, custo).
    Retorna o custo do menor caminho.
    """

    n = len(grafo)
    V = list(range(n))

    # Criar lista de arestas e dicionários de entrada/saída
    E = []
    out_edges = {v: [] for v in V}
    in_edges  = {v: [] for v in V}

    for i in V:
        for j, c in grafo[i]:
            E.append((i, j, c))
            out_edges[i].append((j, c))
            in_edges[j].append((i, c))

    m = Model("min_path_pl")


    # Variáveis x_ij para cada aresta
    x = {}
    for i, j, c in E:
        x[(i, j)] = m.addVar(lb=0, name=f"x_{i}_{j}")

    # Função objetivo: minimizar custo total
    m.setObjective(
        sum(c * x[(i, j)] for (i, j, c) in E),
        GRB.MINIMIZE
    )

    # Restrições de conservação de fluxo (linear e limpa)
    for v in V:
        flow_in  = sum(x[(u, v)] for u, _ in in_edges[v])
        flow_out = sum(x[(v, w)] for w, _ in out_edges[v])
        rhs = 1 if v == s else -1 if v == d else 0
        m.addConstr(flow_in - flow_out == rhs, name=f"flow_{v}")

    # Otimiza
    m.optimize()

    if m.status != GRB.OPTIMAL:
        return None

    return m.objVal

def main():
    # Toggle benchmark mode here
    BENCHMARK = False

    # Read inputs
    N, M, S, D = map(int, input().split())

    # Create bidirectional graph
    grafo = [[] for _ in range(N + 1)]
    for _ in range(M):
        u, v, c = input().split()
        u = int(u)
        v = int(v)
        c = float(c)
        grafo[u].append((v, c))
        grafo[v].append((u, c))  # bidirectional

    # Dijkstra function

    # Benchmark start
    if BENCHMARK:
        print("Benchmark mode enabled", file=sys.stderr)
        start_time = time.perf_counter()

    best = minPathPL(grafo, S, D)

    # Benchmark end
    if BENCHMARK:
        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000
        print(f"Time = {elapsed_ms:.6f} ms", file=sys.stderr)

    # Print result with high precision
    print(f"{best:.20f}")

# Run main
if __name__ == "__main__":
    main()
