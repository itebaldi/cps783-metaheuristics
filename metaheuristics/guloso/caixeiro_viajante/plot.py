from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from metaheuristics.guloso.caixeiro_viajante import arestas_da_matriz
from metaheuristics.guloso.caixeiro_viajante import caixeiro_viajante_guloso
from metaheuristics.guloso.plot import ESTILO
from metaheuristics.guloso.plot import Posicoes
from metaheuristics.guloso.plot import desenhar_grafo
from metaheuristics.guloso.plot import finalizar


def plotar_caixeiro_viajante(
    custos: Sequence[Sequence[float | None]],
    posicoes: Posicoes,
    nome: str = "caixeiro_viajante",
    show: bool = False,
    save: bool = False,
) -> Figure:
    """Plot a graph with the greedy traveling salesman tour highlighted.

    When saving, writes a timestamped PNG to ``plots/guloso/caixeiro_viajante``
    at the repository root.

    Parameters
    ----------
    custos : sequence of sequence of float or None
        Square symmetric cost matrix; ``None`` marks a missing edge.
    posicoes : mapping of {int: tuple of (float, float)}
        Plot coordinates of each vertex, labeled from 1 to n.
    nome : str, default 'caixeiro_viajante'
        File name prefix when saving.
    show : bool, default False
        Whether to open the figure in a window, blocking until it is closed.
    save : bool, default False
        Whether to save the figure as PNG.

    Returns
    -------
    matplotlib.figure.Figure
        Figure with the graph and the greedy tour, complete or partial.
    """
    ciclo = caixeiro_viajante_guloso(custos)
    if len(ciclo) == len(custos):
        custo = sum(custo for _, _, custo in ciclo)
        titulo = f"Caixeiro viajante guloso: tour de custo {custo:g}"
    else:
        titulo = (
            "Caixeiro viajante guloso: sem tour viável "
            f"({len(ciclo)} de {len(custos)} arestas)"
        )

    with plt.rc_context(ESTILO):
        fig, ax = plt.subplots(figsize=(8, 5.5), layout="constrained")
        desenhar_grafo(ax, posicoes, arestas_da_matriz(custos), ciclo)
        ax.set_title(titulo, loc="left")

    finalizar(fig, "caixeiro_viajante", nome, show, save)
    return fig
