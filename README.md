# Metaheurísticas em Otimização Combinatória

Repositório de estudo sobre **heurísticas e metaheurísticas** para problemas de otimização combinatória. Cada algoritmo tem sua própria pasta, com a implementação em Python, um README explicando a teoria, um gráfico para visualizar o que está acontecendo e um teste com um exemplo.

## Conteúdo

| Pasta | Algoritmo | Problema |
|---|---|---|
| [`metaheuristics/guloso/`](metaheuristics/guloso/README.md) | Algoritmo guloso | — |
| [`metaheuristics/guloso/kruskal/`](metaheuristics/guloso/kruskal/README.md) | Kruskal | Árvore Geradora Mínima |
| [`metaheuristics/guloso/mochila/`](metaheuristics/guloso/mochila/README.md) | Heurísticas gulosas | Mochila 0-1 |
| [`metaheuristics/guloso/caixeiro_viajante/`](metaheuristics/guloso/caixeiro_viajante/README.md) | Heurística gulosa | Caixeiro Viajante |
| [`metaheuristics/simulated_annealing/`](metaheuristics/simulated_annealing/README.md) | Simulated Annealing | Mochila 0-1 |

## Instalação

Requer Python 3.11 e [Poetry](https://python-poetry.org/).

```bash
conda create -p ./venv python=3.11
conda activate ./venv
poetry install
```

## Como usar

Rodar os testes:

```bash
pytest
```

Os testes reproduzem os exemplos de cada README. Com `PLOT = True` no arquivo de teste, os gráficos são salvos em `plots/`, que não vai para o git.

Rodar o Simulated Annealing em uma instância aleatória e ver o gráfico:

```bash
python -m metaheuristics.simulated_annealing.plot
```

## Estrutura

```text
metaheuristics/
└── <algoritmo>/
    ├── __init__.py    implementação
    ├── plot.py        gráficos
    └── README.md      teoria e exemplos
tests/
└── <algoritmo>/       um teste por função, espelhando a estrutura acima
```
