//
// Created by Bruno on 26/11/2025.
//
#include <iostream>
#include <vector>
#include <algorithm>
#include <limits>
#include <functional>
#include <queue>
#include <iomanip>
#ifdef BENCHMARK
#include <chrono>
#endif
using namespace std;
#define MAXVERTEX ((int)5e5 + 10)
vector<pair<int,double>> grafo[MAXVERTEX]; //lista de adjacência, com pares (nó, custo) para as arestas
double Sdistances[MAXVERTEX];
double Ddistances[MAXVERTEX];

double INF = std::numeric_limits<double>::infinity();

double bidijkstra(int s, int d){
    fill(Sdistances, Sdistances + MAXVERTEX, INF);
    fill(Ddistances, Ddistances + MAXVERTEX, INF);
    Sdistances[s] = 0;
    Ddistances[d] = 0;
    priority_queue<pair<double, int>, vector<pair<double, int>>, greater<>> Spq;
    priority_queue<pair<double, int>, vector<pair<double, int>>, greater<>> Dpq;
    Spq.emplace(0, s);
    Dpq.emplace(0, d);
    double best = INF;
    while (!Spq.empty() && !Dpq.empty() && (Spq.top().first + Dpq.top().first < best)){

        {
            // avança a fronteira da Busca partindo de S
            auto [dist, v] = Spq.top();
            Spq.pop();
            if (Sdistances[v] < dist) continue;
            for (auto [u, custo]: grafo[v]) {
                if (Sdistances[u] > Sdistances[v] + custo) {
                    Sdistances[u] = Sdistances[v] + custo;
                    best = min(best, Sdistances[u] + Ddistances[u]);
                    Spq.emplace(Sdistances[u], u);
                }
            }
        }

        {
            auto [dist, v] = Dpq.top();
            Dpq.pop();
            if (Ddistances[v] < dist) continue;
            for (auto [u, custo]: grafo[v]) {
                if (Ddistances[u] > Ddistances[v] + custo) {
                    Ddistances[u] = Ddistances[v] + custo;
                    best = min(best, Sdistances[u] + Ddistances[u]);
                    Dpq.emplace(Ddistances[u], u);
                }
            }
        }
    }
    return best;
}


int main(){
    int N, M, S, D;
    cin >> N >> M >> S >> D;
    for(int i = 0; i < M; i++){
        int u, v;
        double c;
        cin >> u >> v >> c;
        grafo[v].emplace_back(u, c);
        grafo[u].emplace_back(v, c); //Grafo bi direcional
    }
#ifdef BENCHMARK
    cerr << "Benchmark mode enabled\n";
    auto start = chrono::high_resolution_clock::now();
#endif
    double best = bidijkstra(S, D);
#ifdef BENCHMARK
    auto end = chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> ms = end - start;

    std::cout.setf(std::ios::fixed);
    std::cout.precision(6); // number of decimal places
    cerr << "Time = "
         << ms.count()
         << " ms\n";
#endif
    cout << setprecision(20) << best;
}