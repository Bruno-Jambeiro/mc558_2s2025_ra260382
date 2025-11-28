import sys
import time
from io import StringIO
from contextlib import redirect_stdout

from gurobipy import Model, GRB, Env, quicksum

def parse_benchmark_flag():
    return any(arg in ("--benchmark", "-b") for arg in sys.argv[1:])

def minPathPL(grafo, s, d, N):
    """
    Resolve caminho mínimo s -> d usando Programação Linear.
    grafo[v] = lista de (vizinho, custo).
    Retorna o custo do menor caminho.
    """

    n = len(grafo)
    V = list(range(n))

    # Criar lista de arestas e dicionários de entrada/saída
    E = []
    out_edges = a = [[] for _ in range(n)]
    in_edges  = a = [[] for _ in range(n)]


    for i in V:
        for j, c in grafo[i]:
            E.append((i, j, c))
            out_edges[i].append((j, c))
            in_edges[j].append((i, c))

    m = Model("min_path_pl")

    # Variáveis x_ij para cada aresta
    x = {}
    print(in_edges, flush=True)
    for i, j, c in E:
        x[(i, j)] = m.addVar(lb=0, name=f"x_{i}_{j}")

    # Função objetivo: minimizar custo total
    m.setObjective(quicksum(c * x[(i, j)] for (i, j, c) in E), GRB.MINIMIZE)
    m.setParam('OutputFlag', 0)
    m.setParam('LogToConsole', 0)

    # Restrições de conservação de fluxo (linear e limpa)
    for v in V:
        flow_in  = quicksum(x[(u, v)] for u, _ in in_edges[v])
        flow_out = quicksum(x[(v, w)] for w, _ in out_edges[v])
        rhs = 1 if v == s else -1 if v == d else 0
        m.addConstr(flow_in - flow_out == rhs, name=f"flow_{v}")

    # Otimiza
    m.optimize()

    if m.status != GRB.OPTIMAL:
        return None

    return m.objVal

def main():
    # Parse benchmark flag
    BENCHMARK = parse_benchmark_flag()

    # Read inputs
    N, M, S, D = map(int, input().split())

    # Create bidirectional graph
    grafo = [[] for _ in range(N + 1)]
    for _ in range(M):
        u, v, c = input().split()
        u = int(u); v = int(v); c = float(c)
        grafo[u].append((v, c))
        grafo[v].append((u, c))  # bidirectional

    start_time = time.perf_counter() if BENCHMARK else None
    # Redirect stdout to swallow Gurobi license banner
    swallow = StringIO()
    with redirect_stdout(swallow):
        with Env(empty=True) as env:
            env.setParam('OutputFlag', 0)
            env.setParam('LogToConsole', 0)
            env.start()
            best = minPathPL(grafo, S, D, N)

    if BENCHMARK:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        # Print benchmark only to stderr so stdout remains comparável
        print(f"benchmark_ms: {elapsed_ms:.6f}", file=sys.stderr)

    # Print result with high precision (stdout only result)
    print(f"{best:.20f}")

# Run main
if __name__ == "__main__":
    main()
