import math
from collections.abc import Mapping
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from metaheuristics.guloso import Aresta

Posicoes = Mapping[int, tuple[float, float]]

PASTA_PLOTS = Path(__file__).resolve().parents[2] / "plots" / "guloso"

COR_SUPERFICIE = "#fcfcfb"
COR_TEXTO = "#0b0b0b"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_EIXO = "#c3c2b7"
COR_GRADE = "#e1e0d9"
COR_ARESTA = "lightgray"
COR_ESCOLHIDA = "red"
COR_HEURISTICA = "royalblue"
COR_OTIMO = "green"

ESTILO = {
    "figure.facecolor": COR_SUPERFICIE,
    "axes.facecolor": COR_SUPERFICIE,
    "axes.edgecolor": COR_EIXO,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": COR_GRADE,
    "grid.linewidth": 0.75,
    "axes.labelcolor": COR_TEXTO_SECUNDARIO,
    "axes.titlecolor": COR_TEXTO,
    "xtick.color": COR_EIXO,
    "ytick.color": COR_EIXO,
    "xtick.labelcolor": COR_TEXTO_SECUNDARIO,
    "ytick.labelcolor": COR_TEXTO_SECUNDARIO,
    "legend.frameon": False,
    "legend.labelcolor": COR_TEXTO_SECUNDARIO,
}


def finalizar(fig: Figure, subpasta: str, nome: str, show: bool, save: bool) -> None:
    """Save the figure as a timestamped PNG and/or open it in a window.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to output.
    subpasta : str
        Folder under ``plots/guloso`` at the repository root.
    nome : str
        File name prefix.
    show : bool
        Whether to open the figure, blocking until it is closed.
    save : bool
        Whether to save the figure as PNG.
    """
    if save:
        pasta = PASTA_PLOTS / subpasta
        pasta.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(pasta / f"{nome}_{datetime.now():%Y%m%d_%H%M%S}.png"))
    if show:
        plt.show()


def _posicao_rotulo(
    inicio: tuple[float, float],
    fim: tuple[float, float],
    ocupadas: Sequence[tuple[float, float]],
    distancia_minima: float,
) -> tuple[float, float]:
    """Pick a point along an edge that stays clear of already occupied points.

    Falls back to the midpoint when every candidate is too close.

    Parameters
    ----------
    inicio : tuple of (float, float)
        Coordinates of one end of the edge.
    fim : tuple of (float, float)
        Coordinates of the other end of the edge.
    ocupadas : sequence of tuple of (float, float)
        Points the label must keep away from.
    distancia_minima : float
        Minimum distance to every occupied point.

    Returns
    -------
    tuple of (float, float)
        Label coordinates.
    """
    for t in (0.5, 0.35, 0.65, 0.25, 0.75):
        ponto = (
            inicio[0] + t * (fim[0] - inicio[0]),
            inicio[1] + t * (fim[1] - inicio[1]),
        )
        if all(math.dist(ponto, outro) >= distancia_minima for outro in ocupadas):
            return ponto
    return (inicio[0] + fim[0]) / 2, (inicio[1] + fim[1]) / 2


def desenhar_grafo(
    ax: Axes,
    posicoes: Posicoes,
    arestas: Sequence[Aresta],
    escolhidas: Sequence[Aresta],
) -> None:
    """Draw a weighted graph, highlighting a subset of its edges.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to draw on.
    posicoes : mapping of {int: tuple of (float, float)}
        Plot coordinates of each vertex.
    arestas : sequence of Aresta
        All edges of the graph.
    escolhidas : sequence of Aresta
        Edges drawn highlighted; their weight labels are placed first.
    """
    pares_escolhidos = {frozenset((u, v)) for u, v, _ in escolhidas}
    xs = [x for x, _ in posicoes.values()]
    ys = [y for _, y in posicoes.values()]
    distancia_minima = 0.07 * math.dist((min(xs), min(ys)), (max(xs), max(ys)))
    ocupadas = list(posicoes.values())

    for u, v, peso in sorted(
        arestas, key=lambda aresta: frozenset(aresta[:2]) not in pares_escolhidos
    ):
        (x1, y1), (x2, y2) = posicoes[u], posicoes[v]
        escolhida = frozenset((u, v)) in pares_escolhidos
        ax.plot(
            [x1, x2],
            [y1, y2],
            color=COR_ESCOLHIDA if escolhida else COR_ARESTA,
            linewidth=3 if escolhida else 1.2,
            zorder=2 if escolhida else 1,
        )
        rotulo = _posicao_rotulo(
            posicoes[u], posicoes[v], ocupadas, distancia_minima
        )
        ocupadas.append(rotulo)
        ax.text(
            *rotulo,
            f"{peso:g}",
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold" if escolhida else "normal",
            color=COR_TEXTO if escolhida else COR_TEXTO_SECUNDARIO,
            bbox={"boxstyle": "round,pad=0.15", "fc": COR_SUPERFICIE, "ec": "none"},
            zorder=3,
        )

    ax.scatter(
        xs,
        ys,
        s=700,
        facecolor="white",
        edgecolor=COR_TEXTO,
        linewidth=1.5,
        zorder=4,
    )
    for vertice, (x, y) in posicoes.items():
        ax.text(x, y, str(vertice), ha="center", va="center", fontsize=12, zorder=5)

    ax.legend(
        handles=[
            Line2D(
                [], [], color=COR_ESCOLHIDA, linewidth=3, label="aresta escolhida"
            ),
            Line2D([], [], color=COR_ARESTA, linewidth=1.2, label="aresta do grafo"),
        ],
        loc="upper left",
        bbox_to_anchor=(1, 1),
    )
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.margins(0.12)
