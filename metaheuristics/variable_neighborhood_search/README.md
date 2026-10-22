# Variable Neighborhood Search (VNS) — Mochila 0-1

Implementação didática do **Basic Variable Neighborhood Search (BVNS)**, aplicando a troca sistemática de vizinhanças ao **problema da mochila 0-1**. A estrutura mantém os mesmos nomes de utilitários e estilo de docstrings (`Parameters` / `Returns`) do projeto de Simulated Annealing e da versão de ILS.

## Problema

Para cada item `i`, existem peso `peso_i`, valor `valor_i` e decisão binária `x_i`:

\[
\max \sum_i valor_i x_i \quad \text{sujeito a}\quad
\sum_i peso_i x_i \le C,\quad x_i \in \{0,1\}.
\]

## Como o VNS funciona

O BVNS de **Mladenović e Hansen (1997)** utiliza diferentes estruturas de vizinhança e três etapas principais: **agitação** (*shaking*), **busca local** e **mudança de vizinhança**.

1. Gerar uma solução inicial viável (inserção em ordem aleatória).
2. Partindo de `k = 1`, gerar uma solução agitada em `N_k(s)`.
3. Aplicar busca local à solução agitada.
4. Se a solução melhorada superar a solução corrente, **aceitá-la e voltar a `k = 1`**.
5. Caso contrário, tentar `k + 1`. Após `k_max`, reiniciar o ciclo em `k = 1` até alcançar o orçamento de tentativas.

Na implementação, `N_k` **inverte k bits distintos**, escolhidos aleatoriamente, antes da etapa de reparação de capacidade. A distância de Hamming do resultado final pode ser menor após reparação. Essa escolha é uma adaptação ao problema da mochila, e não uma definição universal do VNS.

A **busca local** implementa *best improvement* sobre movimentos viáveis de **1-flip** (adicionar/remover item) e **1-1 swap** (trocar item selecionado por não selecionado). Ela é sempre a mesma em todas as agitações, conforme o BVNS básico. Essa implementação **não é VND ou GVNS**.

### Pseudocódigo

```text
s <- GerarSolucaoInicial()
k <- 1
para t = 1, ..., max_iteracoes:
    s' <- Agitacao(s, k)
    s'' <- BuscaLocal(s')
    se valor(s'') > valor(s):
        s <- s''
        k <- 1
    senão:
        k <- k + 1
        se k > k_max: k <- 1
retornar s
```

**Nota sobre a parada:** aqui `max_iteracoes` é o número de *tentativas de agitação + busca local*, não o número de ciclos completos por todas as vizinhanças. O histórico inclui também a iteração 0.

## Estrutura

```text
variable_neighborhood_search/
├── __init__.py    # Item, instâncias, PD, solução inicial, busca local, agitação, BVNS
├── plot.py        # Plot da evolução dos candidatos e da melhor solução
└── README.md
test_variable_neighborhood_search_mochila.py
```

## Exemplo de uso

```python
import random
from variable_neighborhood_search import (
    gerar_instancia_aleatoria, programacao_dinamica,
    variable_neighborhood_search_mochila, calcular_valor_peso,
)
from variable_neighborhood_search.plot import plotar_variable_neighborhood_search

random.seed(0)
itens = gerar_instancia_aleatoria(20, 20, 100)
capacidade = sum(item.peso for item in itens) // 2
valor_otimo, _ = programacao_dinamica(itens, capacidade)

melhor_solucao, output = variable_neighborhood_search_mochila(
    itens=itens,
    capacidade_mochila=capacidade,
    max_iteracoes=250,
    k_max=4,
)
melhor_valor, peso = calcular_valor_peso(melhor_solucao, itens, capacidade)
gap = (valor_otimo - melhor_valor) / valor_otimo * 100 if valor_otimo else 0
print(f"Ótimo={valor_otimo}, VNS={melhor_valor}, peso={peso}, gap={gap:.2f}%")
plotar_variable_neighborhood_search(output, valor_otimo, save=True)
```

## Históricos (`output`)

- `valor_candidato[t]`: valor após agitação e busca local.
- `melhor_valor[t]`: melhor valor aceito até a tentativa `t`.
- `k[t]`: vizinhança utilizada na tentativa (0 na inicialização).
- `aceito[t]`: 1 quando há melhoria estrita; 0 caso contrário.

## Como executar

No diretório que contém a pasta `variable_neighborhood_search`:

```bash
python -m pip install pytest matplotlib
python -m pytest -q test_variable_neighborhood_search_mochila.py
```

Altere `PLOT = True` no teste para mostrar e salvar um gráfico.

## Como avaliar

O código compara o resultado heurístico com a **Programação Dinâmica (PD)**, exata para pesos/capacidade inteiros. Para ótimo positivo:

\[
\operatorname{gap}(\%) = 100\,\frac{valor_{otimo} - valor_{VNS}}{valor_{otimo}}.
\]

O teste principal utiliza a mesma instância reproduzível de **20 itens**, semente **0** e capacidade igual à metade do peso total do SA original. O teste exige `gap <= 5%`, viabilidade e histórico consistente; esse limite é um **critério de teste**, não uma garantia teórica do VNS.

Para experimentos científicos, compare **muitas instâncias e sementes**, tempos, média e distribuição do gap, e varie `k_max`. Para comparar SA, ILS e VNS, mantenha fixos os itens e a capacidade e controle o orçamento computacional (tempo ou número de avaliações) — o mesmo número de iterações pode representar esforços diferentes.

## Referências

- Mladenović, N.; Hansen, P. (1997). *Variable Neighborhood Search*. **Computers & Operations Research**, 24(11), 1097–1100. Referência para agitação, busca local, mudança de vizinhança e reinício em `k=1`.
- Bahiense, L. *Metaheurísticas em Otimização Combinatória — Tema 6: Variable Neighborhood Search (VNS)*. Material didático fornecido; especialmente páginas 3, 8–10, 11–17 e 19.

**Distinção importante:** o artigo original ilustra o método usando TSP; os movimentos binários e o reparo de mochila aqui são decisões específicas desta implementação didática.
