# Projeto de Algoritmos de Caminho Mínimo

Este repositório contém implementações e análises de diferentes algoritmos para resolver o problema do caminho mínimo em grafos.

## Estrutura do Projeto

## Pré-requisitos

1.  **Compilador C++:** Um compilador com suporte a C++17 (ex: g++). No Windows, pode-se usar o MinGW ou o WSL.
2.  **Python 3:** Necessário para executar o `tester.py` e a implementação em PL.
3.  **Gurobi:** A implementação `plShortestPath.py` requer que a biblioteca `gurobipy` esteja instalada e uma licença do Gurobi ativa.


### Compilação Manual (C++)

Você pode compilar cada arquivo `.cpp` individualmente. Os comandos a seguir geram um executável chamado `a.exe` no Windows.

#### Compilação Padrão

Use o comando a seguir para uma compilação otimizada:

```bash
g++ -std=c++17 -O2 dijkstra.cpp -o dijkstra.exe
```

#### Compilação com Benchmark

Para medir o tempo de execução, os arquivos C++ contêm blocos de código que são ativados pela flag `-DBENCHMARK`.

```bash
g++ -std=c++17 -O2 -DBENCHMARK dijkstra.cpp -o dijkstra_bench.exe
```

Quando compilado com esta flag, o programa imprime o tempo de execução em milissegundos na saída de erro (`stderr`), sem afetar a saída principal (`stdout`).

### Usando o Testador (`tester.py`)

O script `tester.py` automatiza todo o processo de teste. Para executá-lo, basta rodar o seguinte comando no terminal:

```bash
python tester.py
```

O script irá:

1.  **Detectar Implementações:** Encontrar todos os arquivos `.cpp` e `.py` (exceto ele mesmo) no diretório.
2.  **Perguntar sobre Benchmark:**
    ```
    Benchmark mode? (y/n):
    ```
    -   Se você responder `y`, ele compilará os arquivos C++ com a flag `-DBENCHMARK` e passará um argumento de benchmark para os scripts Python.
    -   Se responder `n`, a compilação será a padrão.
3.  **Compilar e Executar:** Para cada implementação, o testador irá:
    -   Compilar o código C++.
    -   Executar o programa para cada arquivo de teste encontrado em `input/`.
    -   Comparar a saída do programa com o arquivo correspondente em `output/`.
4.  **Gerar Relatórios:** Salvar um resumo dos resultados (OK, WA - Wrong Answer, Erro) e os tempos de execução (se em modo benchmark) em arquivos `tests<NomeDaImplementacao>.txt`.

Por exemplo, ao final da execução, você terá os arquivos:
-   `testsdijkstra.txt`
-   `testsbiDijkstra.txt`
-   `testsplShortestPath.txt`
-   ... e assim por diante.

O testador compara saídas numéricas com uma tolerância de 1% para lidar com imprecisões de ponto flutuante.

