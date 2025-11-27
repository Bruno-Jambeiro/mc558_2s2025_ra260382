//
// Created by Bruno on 26/11/2025.
//
#include <iostream>
#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
#include <functional>
#include <queue>
#include <iomanip>
#include <cmath>
#include <cassert>
using namespace std;
#define MAXVERTEX ((int)5e5 + 10)
vector<pair<int,int>> grafo[MAXVERTEX]; //lista de adjacência, com pares (nó, custo) para as arestas
int Sdistances[MAXVERTEX];
int Ddistances[MAXVERTEX];

int INF = INT_MAX/2;

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
int bidial_dijkstra(int s, int d, int max_edge, int N){
    fill(Sdistances, Sdistances + MAXVERTEX, INF);
    fill(Ddistances, Ddistances + MAXVERTEX, INF);
    Sdistances[s] = 0;
    Ddistances[d] = 0;
    dial_pq Spq(max_edge, N);
    dial_pq Dpq(max_edge, N);
    Spq.emplace(0, s);
    Dpq.emplace(0, d);
    int best = INF;
    while (!Spq.empty() && !Dpq.empty() && (Spq.top().first + Dpq.top().first < best)){

        {
            // avança a fronteira da Busca partindo de S
            auto [dist, v] = Spq.top();
            Spq.pop();
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
    int best =  bidial_dijkstra(S, D, max_cost, N);

    cout << setprecision(20) << best;
}