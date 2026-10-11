from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from metaheuristics.guloso import Aresta
from metaheuristics.guloso.kruskal import kruskal
from metaheuristics.guloso.plot import ESTILO
from metaheuristics.guloso.plot import Posicoes
from metaheuristics.guloso.plot import desenhar_grafo
from metaheuristics.guloso.plot import finalizar


def plotar_kruskal(
    posicoes: Posicoes,
    arestas: Sequence[Aresta],
    nome: str = "kruskal",
    show: bool = False,
    save: bool = False,
) -> Figure:
    """Plot a graph with its minimum spanning tree highlighted.

    When saving, writes a timestamped PNG to ``plots/guloso/kruskal`` at the
    repository root.

    Parameters
    ----------
    posicoes : mapping of {int: tuple of (float, float)}
        Plot coordinates of each vertex, labeled from 1 to n.
    arestas : sequence of Aresta
        Edges as ``(u, v, peso)``.
    nome : str, default 'kruskal'
        File name prefix when saving.
    show : bool, default False
        Whether to open the figure in a window, blocking until it is closed.
    save : bool, default False
        Whether to save the figure as PNG.

    Returns
    -------
    matplotlib.figure.Figure
        Figure with the graph and its minimum spanning tree.
    """
    arvore = kruskal(len(posicoes), arestas)
    custo = sum(peso for _, _, peso in arvore)

    with plt.rc_context(ESTILO):
        fig, ax = plt.subplots(figsize=(8, 5.5), layout="constrained")
        desenhar_grafo(ax, posicoes, arestas, arvore)
        ax.set_title(
            f"Kruskal: árvore geradora mínima de custo {custo:g}", loc="left"
        )

    finalizar(fig, "kruskal", nome, show, save)
    return fig
