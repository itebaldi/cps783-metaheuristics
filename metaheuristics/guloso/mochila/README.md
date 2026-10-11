# Heurísticas Gulosas para a Mochila 0-1

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**, Tema 2. Parte de [Algoritmo Guloso](../README.md).

Para a Mochila 0-1 não existe guloso ótimo. Aqui estão **três heurísticas construtivas** que fazem exatamente a mesma coisa (examinar os itens em uma ordem e colocar cada um que ainda couber), mudando **apenas o critério de ordenação**.

## 1. O problema

Um viajante deseja levar `n` itens. O item `j` tem valor `p_j` e peso `w_j`, e a mochila tem capacidade `C`. Quais itens levar?

Variável de decisão: `x_j = 1` se o item `j` vai na mochila, `0` caso contrário.

$$
\max \sum_{j} p_j x_j
\quad \text{s.a.} \quad
\sum_{j} w_j x_j \leq C,
\qquad x_j \in \{0, 1\}
$$

Sem perda de generalidade: `p_j, w_j > 0`, `C > 0`, `Σ w_j > C` (nem tudo cabe) e `w_j ≤ C` (cada item cabe sozinho).

## 2. As três heurísticas

| # | Guloso em... | Ordem de exame | Exemplo | Guloso | Ótimo |
|---|---|---|---|---|---|
| 1 | utilização da capacidade | peso `w_j` não decrescente | `C = 7`, `w = [3, 4, 6]`, `p = [2, 6, 10]` | itens {1, 2}, valor **8** | item {3}, valor **10** |
| 2 | ganho de valor | valor `p_j` não crescente | `C = 7`, `w = [7, 3, 2]`, `p = [10, 8, 6]` | item {1}, valor **10** | itens {2, 3}, valor **14** |
| 3 | densidade de valor | `p_j / w_j` não crescente | `C = 9`, `w = [4, 3, 7, 5, 3, 2, 3]`, `p = [12, 8, 17, 11, 6, 2, 2]` | itens {1, 2, 6}, valor **22** | itens {1, 4}, valor **23** |

A **heurística #3** não fornece o ótimo, mas é a **melhor das três** e, para problemas maiores, costuma produzir boas soluções. Para a **mochila fracionária** (quando é possível levar uma fração de um item) ela é **ótima**. Conforme `n` cresce, ela **tende** a gerar soluções melhores.

O plot desta pasta roda as três heurísticas na mesma instância. Na instância da heurística #3, a #1 obtém valor 16 e a #2 obtém 19, contra 22 da #3 e 23 do ótimo.

## 3. O algoritmo

```text
Passo 1: ordene os n itens pelo critério (ex.: p_j / w_j não crescente)
Passo 2: S ← ∅            // conjunto solução
         C̄ ← C            // capacidade residual
Passo 3: para cada item j, nessa ordem:
             se C̄ − w_j ≥ 0:
                 S ← S ∪ {j}
                 C̄ ← C̄ − w_j
         retorne S
```

Note que o algoritmo **não para** no primeiro item que não cabe: ele continua examinando os seguintes, porque um item menor ainda pode caber. No exemplo da #3, o item 3 (peso 7) não cabe, mas o item 6 (peso 2) cabe depois.

Bem implementado, o custo é dominado pela ordenação: **`O(n log n)`**.

## 4. Código

```python
from metaheuristics.guloso.mochila import mochila_gulosa
from metaheuristics.guloso.mochila.plot import plotar_mochila_gulosa

pesos = [4, 3, 7, 5, 3, 2, 3]
valores = [12, 8, 17, 11, 6, 2, 2]

mochila_gulosa(pesos, valores, 9, "densidade")
# [1, 1, 0, 0, 0, 1, 0]  → itens 1, 2 e 6

plotar_mochila_gulosa(pesos, valores, 9, otimo=[1, 0, 0, 1, 0, 0, 0], show=True)
```

- `mochila_gulosa(pesos, valores, capacidade, criterio)`: `criterio` é `"peso"`, `"valor"` ou `"densidade"`. Retorna um vetor binário, a mesma representação usada no [Simulated Annealing](../../simulated_annealing/README.md).
- `plotar_mochila_gulosa(pesos, valores, capacidade, otimo, show, save)`: uma barra por heurística, com os itens escolhidos empilhados até a capacidade `C`, e o ótimo em verde quando informado.
- Teste: [`tests/guloso/mochila/test_mochila_gulosa.py`](../../../tests/guloso/mochila/test_mochila_gulosa.py) reproduz os três exemplos da tabela.

## 5. Questões para revisão

1. Construa uma instância em que a heurística #3 seja pior que a #1.
2. Por que a heurística #3 é ótima para a mochila fracionária, mas não para a 0-1?
3. Por que o algoritmo continua examinando itens depois que um deles não coube?
4. Qual é a complexidade de cada passo do algoritmo?
5. Como uma solução gulosa poderia servir de ponto de partida para o Simulated Annealing?

## 6. Referências

- **Hristakeva, M.; Shrestha, D.** *Different Approaches to Solve the 0/1 Knapsack Problem.*

---

**Resumo em uma frase:** as três heurísticas enchem a mochila com o que ainda cabe, diferindo só na ordem de exame; a ordenação por densidade `p_j / w_j` é a melhor delas, mas ainda não garante o ótimo.
