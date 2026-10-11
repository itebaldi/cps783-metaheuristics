# Algoritmo Guloso

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**, Tema 2.

Um **algoritmo guloso** constrói uma solução passo a passo: a cada iteração escolhe o objeto mais "apetitoso" que vê pela frente, e esse objeto passa a fazer parte da solução **para sempre**. É a forma mais comum de **heurística construtiva** e é muito usado para gerar **soluções iniciais** que depois serão melhoradas por busca local ou por metaheurísticas.

Esta pasta tem três exemplos clássicos, cada um em sua subpasta:

| Pasta | Problema | O guloso é ótimo? |
|---|---|---|
| [`kruskal/`](kruskal/README.md) | Árvore Geradora Mínima | **Sim**, sempre |
| [`mochila/`](mochila/README.md) | Mochila 0-1 | Não |
| [`caixeiro_viajante/`](caixeiro_viajante/README.md) | Caixeiro Viajante | Não, e pode até não achar solução |

## 1. Por que heurísticas?

Em problemas NP-difíceis, em geral os **algoritmos exatos sacrificam o tempo** e os **algoritmos aproximados sacrificam a otimalidade**. A enumeração explícita só funciona para `n` bem pequeno:

- **Mochila 0-1:** há da ordem de `2^n` subconjuntos de itens.
- **Caixeiro viajante:** há da ordem de `n!` tours.

| `n` | `n²` | `2^n` | `n!` |
|---|---|---|---|
| 10 | 10² | 1,02 × 10³ | 3,6 × 10⁶ |
| 100 | 10⁴ | 1,27 × 10³⁰ | 9,33 × 10¹⁵⁷ |
| 1000 | 10⁶ | 1,07 × 10³⁰¹ | 4,02 × 10²⁵⁶⁷ |

**Heurísticas** são simples, intuitivas e rápidas, fornecem em geral soluções de boa qualidade, mas **não garantem o ótimo** nem uma distância máxima até ele.

## 2. Intuição: miopia

O algoritmo guloso é **míope**: decide com base apenas na informação da iteração corrente, sem olhar as consequências futuras. Ele **jamais se arrepende**: as escolhas são definitivas (irrevogáveis).

## 3. Preceito e premissas

- **Preceito:** fazer uma escolha gulosa (míope), na esperança de que ela leve a uma boa solução global, possivelmente ótima.
- **Premissas:** a escolha feita em cada passo deve ser
  - **viável:** satisfaz as restrições do problema;
  - **localmente ótima:** é a melhor entre as escolhas viáveis;
  - **irrevogável:** não pode ser alterada nos passos seguintes.

Para um problema ser resolvido **de forma ótima** por um guloso, ele precisa ter **subestrutura ótima** (a solução ótima contém soluções ótimas de subproblemas, como na programação dinâmica) e a **propriedade de escolha gulosa** (uma solução global pode ser encontrada por uma sequência de melhorias locais a partir de uma configuração inicial).

Problemas que admitem solução gulosa ótima para **qualquer** instância são **raros**. Na prática, um guloso às vezes gera o ótimo, às vezes soluções muito boas, às vezes soluções ruins e, dependendo da instância, pode nem gerar solução. Por isso a **prova de corretude** é tão importante.

## 4. Pseudocódigo genérico

Os três algoritmos desta pasta seguem o mesmo esqueleto:

```text
entrada: candidatos E; critério guloso; teste de viabilidade

S ← ∅
ordene E pelo critério guloso
para cada e em E, nessa ordem:
    se S ∪ {e} é viável:
        S ← S ∪ {e}          // escolha irrevogável
retornar S
```

O que muda de um problema para outro:

| Problema | Candidatos | Critério guloso | Viável se... |
|---|---|---|---|
| Árvore Geradora Mínima | arestas | menor peso | não formar ciclo |
| Mochila 0-1 | itens | menor peso, maior valor ou maior valor/peso | couber na capacidade residual |
| Caixeiro Viajante | arestas | menor custo | nenhum vértice com grau 3 e nenhum subciclo |

## 5. Tipos básicos de heurísticas

| Tipo | O que faz | Exemplo |
|---|---|---|
| **Construtiva** | Constrói uma solução viável do nada, de forma iterativa | Os três gulosos desta pasta |
| **Melhoria (busca local)** | Parte de uma solução e a troca continuamente por uma vizinha melhor, enquanto possível | 2-OPT e 3-OPT para o caixeiro viajante |

Uma **metaheurística** é uma estratégia para percorrer o espaço de busca e escapar de ótimos locais de baixa qualidade. Uma vez especializada para um problema, ela também se torna uma heurística.

## 6. Estrutura do código

```text
metaheuristics/guloso/
├── __init__.py              tipo Aresta e union-find (raiz), usados por Kruskal e Caixeiro
├── plot.py                  estilo e desenho de grafos compartilhados
├── kruskal/                 Árvore Geradora Mínima
├── mochila/                 Mochila 0-1
└── caixeiro_viajante/       Caixeiro Viajante
```

Cada subpasta tem `__init__.py` (algoritmo), `plot.py` (gráfico) e `README.md`. Os testes em `tests/guloso/` reproduzem os exemplos de cada README:

```bash
pytest tests/guloso
```

Com `PLOT = True` no arquivo de teste, os gráficos são salvos em `plots/guloso/<algoritmo>/`.

## 7. Vantagens e limitações

**Vantagens**
- Fácil de conceber e de implementar.
- Muito rápido e eficiente.
- Bom gerador de soluções iniciais.

**Limitações**
- Raramente encontra o ótimo.
- Como é muito intuitivo, pode "pregar peças": gerar soluções arbitrariamente ruins ou até não gerar solução.
- Parecer obviamente correto não basta: a prova de corretude nem sempre é simples.

## 8. Questões para revisão

1. O que significa dizer que o algoritmo guloso é míope?
2. Quais são as três premissas de uma escolha gulosa?
3. Por que subestrutura ótima não basta para garantir que o guloso é ótimo?
4. Qual é a diferença entre uma heurística construtiva e uma de melhoria?
5. Por que a enumeração explícita é inviável para a Mochila 0-1 e para o Caixeiro Viajante?

## 9. Referências

- **Kruskal, J. B.** (1956). *On the Shortest Spanning Subtree of a Graph and the Traveling Salesman Problem*. Proceedings of the American Mathematical Society, 7(1), 48–50.
- **Hristakeva, M.; Shrestha, D.** *Different Approaches to Solve the 0/1 Knapsack Problem.*
- **Kurz, M. E.** *Heuristics for the Traveling Salesman Problem.*

---

**Resumo em uma frase:** o guloso faz, a cada passo, a melhor escolha viável que enxerga e nunca volta atrás; é rápido e simples, mas só é ótimo em problemas raros como a Árvore Geradora Mínima.
