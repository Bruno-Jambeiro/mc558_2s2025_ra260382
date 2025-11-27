//
// Created by Bruno on 26/11/2025.
//
#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
#include <iomanip>
#include <cmath>
#include <cassert>
#ifdef BENCHMARK
#include <chrono>
#endif
using namespace std;
#define MAXVERTEX ((int)5e5 + 10)
vector<pair<int,int>> grafo[MAXVERTEX]; //lista de adjacência, com pares (nó, custo) para as arestas
int distances[MAXVERTEX];

int INF = INT_MAX / 2;

struct dial_pq{
    int num_buckets;
    vector<int> buckets[501];
    pair<int,int>* onde;
    int head = 0;
    int true_value = 0;

    explicit dial_pq(int max_edge, int N) : num_buckets(max_edge + 1) {
        onde = (pair<int,int>*)malloc(sizeof(pair<int,int>) * (N + 10));
        fill(onde, onde + (N + 10), pair<int,int>(-1, -1));

    }


private :
    int size = 0;

public:
    pair<int, int> top(){
        while((buckets[head].empty() && size) || (buckets[head].back() == -1) ){
            if (!buckets[head].empty() && buckets[head].back() == -1) {
                buckets[head].pop_back();
                continue;
            }
            //cout << head << " ";
            head++;
            true_value++;
            if (head >= num_buckets) head-=num_buckets;
        }
        return {true_value, buckets[head].back()};
    }
    void pop(){
        buckets[head].pop_back();
        size--;
    }
    void emplace(int dist, int v){
        this->invalidate(onde[v]);
        int i = dist - true_value + head;
        if (i >= num_buckets) i-= num_buckets;
        buckets[i].push_back(v);
        size++;
        onde[v] = pair<int,int>(i, buckets[i].size() - 1);
    }

    bool empty(){
        return size == 0;
    }

    virtual ~dial_pq() {
        free(onde);
    }

private:
    void invalidate(pair<int,int> ind){
        if (ind == pair<int,int>(-1, -1)) return;
        size--;
        buckets[ind.first][ind.second] = -1;
    }

};

void dial_dijkstra(int s, int d, int max_edge, int N){
    fill(distances, distances + MAXVERTEX, INF);
    distances[s] = 0;
    //priority_queue<pair<int, int>, vector<pair<int, int>>, greater<>> pq;
    dial_pq pq(max_edge, N);
    pq.emplace((int)0, s);
    while (!pq.empty()){
        auto [dist, v] = pq.top(); pq.pop();
        //if (distances[v] != pq.true_value) {cout << "first v: " << v << " distances[v]:  " << distances[v] << " true_value: " << pq.true_value << '\n';};
        if (v == d) return;
        for (auto [u, custo] : grafo[v]){
            if (distances[u] > distances[v] + custo){
                distances[u] = distances[v] + custo;
//                if(distances[u] - pq.true_value > 500){
//                    cout << "u: " << u << " v: " << v << " true_value: " << pq.true_value  << " head: " << pq.head << " custo: " << custo
//                    << " distances[v]: " << distances[v] << '\n';
//                }
                pq.emplace(distances[u], u);
            }
        }
    }
}


int main(){
    int N, M, S, D;
    cin >> N >> M >> S >> D;
    int max_cost = -1;
    for(int i = 0; i < M; i++){
        int u, v;
        double c;
        cin >> u >> v >> c;
        int cost = round(c);
        max_cost = max(max_cost, cost);
        grafo[v].emplace_back(u, cost);
        grafo[u].emplace_back(v, cost); //Grafo bi direcional
    }
#ifdef BENCHMARK
    cerr << "Benchmark mode enabled\n";
    auto start = chrono::high_resolution_clock::now();
#endif
    dial_dijkstra(S, D, max_cost, N);
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