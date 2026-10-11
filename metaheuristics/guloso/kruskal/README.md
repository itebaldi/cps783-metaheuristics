# Kruskal para Árvore Geradora Mínima

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**, Tema 2. Parte de [Algoritmo Guloso](../README.md).

O **algoritmo de Kruskal**, proposto em 1956 por Joseph Bernard Kruskal Jr., é o **exemplo de sucesso** do método guloso: para a Árvore Geradora Mínima, a escolha gulosa leva **sempre** à solução ótima.

## 1. O problema

Uma **árvore geradora** de um grafo `G` com `n` vértices é um subgrafo **conexo e acíclico** que contém todos os vértices de `G` e exatamente `n − 1` de suas arestas. Em geral, um grafo tem **várias** árvores geradoras.

Quando as arestas têm peso, o **problema da Árvore Geradora Mínima (AGM)** é encontrar a árvore geradora de **peso total mínimo**.

## 2. O algoritmo

**Princípio:** a cada iteração, incluir na árvore a **aresta de menor custo que não forme ciclo**. A árvore fica pronta após `n − 1` inclusões.

```text
entrada: grafo G = (V, A) e pesos d_ij

ordene as arestas em ordem não decrescente de peso no vetor H
T ← ∅
para cada aresta h_i de H, nessa ordem:
    se T ∪ {h_i} é acíclico:
        T ← T ∪ {h_i}
    se |T| = n − 1:
        pare
retornar T
```

| Etapa | Custo |
|---|---|
| Ordenação das arestas | `O(m log m)` |
| Escolha das arestas | `O(m)` vezes |
| **Total** | **`O(m log m)`** |

### Como o código testa se forma ciclo

O código usa uma estrutura **union-find**, implementada em `raiz()`: cada vértice aponta para um representante do seu componente. Adicionar a aresta `(u, v)` **forma ciclo** se e somente se `u` e `v` já têm o mesmo representante, ou seja, já estão conectados. Quando a aresta entra, os dois componentes são unidos.

## 3. Exemplo

Grafo com 7 vértices e 9 arestas. O vetor `H` com as arestas ordenadas por peso:

| | Aresta | Peso | Decisão |
|---|---|---|---|
| `h1` | (3, 6) | 1 | ✅ entra |
| `h2` | (4, 7) | 1 | ✅ entra |
| `h3` | (5, 6) | 2 | ✅ entra |
| `h4` | (2, 3) | 3 | ✅ entra |
| `h5` | (2, 6) | 3 | ❌ fecharia o ciclo 2–3–6 |
| `h6` | (6, 7) | 5 | ✅ entra |
| `h7` | (1, 3) | 6 | ✅ entra: são `n − 1 = 6` arestas, **FIM** |
| `h8` | (2, 5) | 8 | não examinada |
| `h9` | (3, 4) | 9 | não examinada |

Árvore geradora mínima: **custo 1 + 1 + 2 + 3 + 5 + 6 = 18**.

## 4. Código

```python
from metaheuristics.guloso.kruskal import kruskal
from metaheuristics.guloso.kruskal.plot import plotar_kruskal

arestas = [
    (1, 3, 6),
    (2, 3, 3),
    (2, 5, 8),
    (2, 6, 3),
    (3, 4, 9),
    (3, 6, 1),
    (4, 7, 1),
    (5, 6, 2),
    (6, 7, 5),
]

arvore = kruskal(7, arestas)
# [(3, 6, 1), (4, 7, 1), (5, 6, 2), (2, 3, 3), (6, 7, 5), (1, 3, 6)]

posicoes = {
    1: (1, 2),
    2: (0, 1),
    3: (1, 1),
    4: (2, 1),
    5: (0, 0),
    6: (1, 0),
    7: (2, 0),
}
plotar_kruskal(posicoes, arestas, show=True)
```

- `kruskal(num_vertices, arestas)`: vértices numerados de `1` a `n`, arestas como `(u, v, peso)`. Retorna as arestas da árvore **na ordem em que entraram**. Arestas de mesmo peso mantêm a ordem da entrada.
- `plotar_kruskal(posicoes, arestas, show, save)`: desenha o grafo com a árvore em vermelho.
- Teste: [`tests/guloso/kruskal/test_kruskal.py`](../../../tests/guloso/kruskal/test_kruskal.py) reproduz o exemplo acima.

## 5. Questões para revisão

1. Por que uma árvore geradora de `n` vértices tem exatamente `n − 1` arestas?
2. No exemplo, por que a aresta `h5 = (2, 6)` foi rejeitada, se tem o mesmo peso de `h4`?
3. Por que o algoritmo pode parar antes de examinar `h8` e `h9`?
4. Qual etapa domina a complexidade `O(m log m)`?
5. O que muda no algoritmo se o grafo não for conexo?

## 6. Referências

- **Kruskal, J. B.** (1956). *On the Shortest Spanning Subtree of a Graph and the Traveling Salesman Problem*. Proceedings of the American Mathematical Society, 7(1), 48–50.

---

**Resumo em uma frase:** ordenar as arestas por peso e aceitar cada uma que não forme ciclo produz, sempre, a árvore geradora de peso mínimo.
