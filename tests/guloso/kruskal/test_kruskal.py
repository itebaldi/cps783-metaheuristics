from metaheuristics.guloso.kruskal import kruskal
from metaheuristics.guloso.kruskal.plot import plotar_kruskal

PLOT = True


def test_kruskal__seven_vertex_graph():
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

    assert arvore == [
        (3, 6, 1),
        (4, 7, 1),
        (5, 6, 2),
        (2, 3, 3),
        (6, 7, 5),
        (1, 3, 6),
    ]
    assert sum(peso for _, _, peso in arvore) == 18

    if PLOT:
        posicoes = {
            1: (1, 2),
            2: (0, 1),
            3: (1, 1),
            4: (2, 1),
            5: (0, 0),
            6: (1, 0),
            7: (2, 0),
        }
        plotar_kruskal(posicoes, arestas, save=True)
