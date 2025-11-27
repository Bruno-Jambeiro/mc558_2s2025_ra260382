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
double distances[MAXVERTEX];

double INF = std::numeric_limits<double>::infinity();

void dijkstra(int s, int d){
    fill(distances, distances + MAXVERTEX, INF);
    distances[s] = 0;
    priority_queue<pair<double, int>, vector<pair<double, int>>, greater<>> pq;
    pq.emplace(0, s);
    while (!pq.empty()){
        auto [dist, v] = pq.top(); pq.pop();
        if (distances[v] < dist) continue;
        if (v == d) return;
        for (auto [u, custo] : grafo[v]){
            if (distances[u] > distances[v] + custo){
                distances[u] = distances[v] + custo;
                pq.emplace(distances[u], u);
            }
        }
    }
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
    dijkstra(S, D);

#ifdef BENCHMARK
    auto end = chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> ms = end - start;

    std::cout.setf(std::ios::fixed);
    std::cout.precision(6); // number of decimal places
    cerr << "Time = "
         << ms.count()
         << " ms\n";
#endif
    cout << setprecision(20) << distances[D];
}