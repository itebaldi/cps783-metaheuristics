# Heurística Gulosa para o Caixeiro Viajante

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**, Tema 2. Parte de [Algoritmo Guloso](../README.md).

Uma heurística construtiva bem simples, **"estilo Kruskal"**: ordenar as arestas por custo e ir aceitando as mais baratas, desde que o resultado ainda possa virar um tour. Ao contrário do Kruskal, aqui o guloso **não é ótimo**, pode gerar **soluções péssimas** e pode até **não encontrar solução**.

## 1. O problema

O **Problema do Caixeiro Viajante** (*Traveling Salesman Problem*, TSP) é o problema combinatório mais conhecido e estudado. São dadas `n` cidades e os tempos de viagem entre cada par. O caixeiro precisa sair da sua cidade, passar **uma única vez** por todas as demais e voltar à origem. Qual sequência minimiza o tempo total?

Modelagem: um grafo completo onde os vértices são as cidades e as arestas têm como peso os tempos de viagem. Uma solução viável é um **tour** e, no grafo, corresponde a um **ciclo hamiltoniano**.

Premissas mais comuns: tempos positivos (`t_ij ≥ 0`), simetria (`t_ij = t_ji`) e desigualdade triangular (`t_ij + t_jk ≥ t_ik`).

## 2. O algoritmo

```text
Passo 1: ordene as arestas em ordem crescente de custo
         c(e_1) ≤ c(e_2) ≤ ... ≤ c(e_m),  com m = n(n − 1)/2
Passo 2: C ← ∅;  g[i] ← 0 para todo vértice i      // g = grau
Passo 3: para cada aresta e_k = (i, j), nessa ordem, enquanto |C| < n:
             se g[i] < 2 e g[j] < 2 e C ∪ {e_k} não contém subciclo:
                 C ← C ∪ {e_k};  g[i]++;  g[j]++
```

Duas regras garantem que o resultado seja um ciclo:

- **Grau:** num tour, cada cidade tem exatamente duas arestas, então nenhum vértice pode chegar a grau 3.
- **Subciclo:** não se pode fechar um ciclo que deixe cidades de fora. Só a **última** aresta, a `n`-ésima, pode fechar o ciclo, que então passa por todas as cidades.

O teste de subciclo usa o mesmo union-find do Kruskal (`raiz()`).

## 3. Exemplo: K6

Grafo completo com 6 vértices:

```text
      1    2    3    4    5    6
1     -    9    2    8   12   11
2          -    7   19   10   32
3               -   29   18    6
4                    -   24    3
5                         -   19
```

| Aresta | Custo | Decisão |
|---|---|---|
| (1, 3) | 2 | ✅ |
| (4, 6) | 3 | ✅ |
| (3, 6) | 6 | ✅ |
| (2, 3) | 7 | ❌ vértice 3 ficaria com **grau 3** |
| (1, 4) | 8 | ❌ fecharia o **subciclo** 1–3–6–4 |
| (1, 2) | 9 | ✅ |
| (2, 5) | 10 | ✅ |
| (1, 6), (1, 5), (3, 5), (2, 4), (5, 6) | 11–19 | ❌ grau 3 |
| (4, 5) | 24 | ✅ fecha o tour passando por todos |

Tour guloso: **1 – 3 – 6 – 4 – 5 – 2 – 1, custo 54**.

> Enumerando os 60 tours possíveis, o ótimo é 1 – 4 – 6 – 3 – 2 – 5 – 1, de **custo 46**. O guloso ficou 17% acima.

## 4. Onde o guloso falha

### Pode gerar péssimas soluções

Cinco vértices em pentágono: as arestas 1–5, 5–4, 4–3 e 3–2 custam 1, a aresta 1–2 custa `M` (muito grande) e as demais custam 2. O guloso pega as quatro arestas de custo 1, que formam o caminho 1–5–4–3–2, e então a **única** forma de fechar o tour é a aresta 1–2: **custo 4 + M**. Existe um tour de custo **7** (ex.: 1–3–2–4–5–1), mas o guloso não volta atrás. Quanto maior `M`, pior a solução.

### Pode não encontrar solução

Quatro vértices, **sem** a aresta 1–4. O guloso pega (2, 3) de custo 1, depois (1, 2), rejeita (2, 4) por grau, rejeita (1, 3) por subciclo e pega (3, 4). Sobram só 3 arestas e nenhuma para fechar: **não há tour**. O único tour viável, 1–2–4–3–1 (custo 10), não usa a aresta (2, 3), que foi a primeira escolha gulosa.

## 5. Próximo passo: heurísticas de melhoria

O tour guloso costuma servir de **ponto de partida** para uma busca local, que explora a vizinhança do tour para tentar melhorá-lo, como **2-OPT** (trocar pares de arestas não adjacentes) e **3-OPT** (remover três arestas e reconectar as partes da maneira mais barata).

## 6. Código

```python
from metaheuristics.guloso.caixeiro_viajante import caixeiro_viajante_guloso
from metaheuristics.guloso.caixeiro_viajante.plot import plotar_caixeiro_viajante

custos = [
    [None, 9, 2, 8, 12, 11],
    [9, None, 7, 19, 10, 32],
    [2, 7, None, 29, 18, 6],
    [8, 19, 29, None, 24, 3],
    [12, 10, 18, 24, None, 19],
    [11, 32, 6, 3, 19, None],
]

caixeiro_viajante_guloso(custos)
# [(1, 3, 2), (4, 6, 3), (3, 6, 6), (1, 2, 9), (2, 5, 10), (4, 5, 24)]

posicoes = {
    1: (2, 3),
    2: (0, 1.4),
    3: (6, 3.2),
    4: (6.5, 0),
    5: (3, 0.2),
    6: (8, 1.5),
}
plotar_caixeiro_viajante(custos, posicoes, show=True)
```

- `caixeiro_viajante_guloso(custos)`: matriz de custos simétrica, com `None` onde não há aresta. Retorna as arestas do tour **na ordem em que entraram**. Se vierem **menos de `n` arestas**, o guloso não encontrou tour.
- `plotar_caixeiro_viajante(custos, posicoes, show, save)`: desenha o grafo com o tour, completo ou parcial, em vermelho.
- Teste: [`tests/guloso/caixeiro_viajante/test_caixeiro_viajante_guloso.py`](../../../tests/guloso/caixeiro_viajante/test_caixeiro_viajante_guloso.py) reproduz os três exemplos acima: o K6, a aresta de custo `M` e o grafo sem tour.

## 7. Questões para revisão

1. Quais são as duas regras que diferenciam esta heurística do Kruskal? Por que cada uma é necessária?
2. Por que a última aresta pode fechar um ciclo e as anteriores não?
3. No exemplo da aresta de custo `M`, o que acontece com a qualidade da solução gulosa quando `M` cresce?
4. Por que o guloso falha no grafo sem a aresta 1–4, mesmo existindo um tour viável?
5. Como o 2-OPT poderia melhorar o tour de custo 54 do K6?

## 8. Referências

- **Kurz, M. E.** *Heuristics for the Traveling Salesman Problem.*

---

**Resumo em uma frase:** aceitar as arestas mais baratas respeitando grau 2 e sem subciclos constrói um tour rapidamente, mas a miopia pode levar a soluções arbitrariamente ruins ou a nenhuma solução.
