from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from metaheuristics.guloso.mochila import mochila_gulosa
from metaheuristics.guloso.plot import COR_HEURISTICA
from metaheuristics.guloso.plot import COR_OTIMO
from metaheuristics.guloso.plot import COR_SUPERFICIE
from metaheuristics.guloso.plot import COR_TEXTO
from metaheuristics.guloso.plot import COR_TEXTO_SECUNDARIO
from metaheuristics.guloso.plot import ESTILO
from metaheuristics.guloso.plot import finalizar


def plotar_mochila_gulosa(
    pesos: Sequence[int],
    valores: Sequence[int],
    capacidade: int,
    otimo: Sequence[int] | None = None,
    nome: str = "mochila_gulosa",
    show: bool = False,
    save: bool = False,
) -> Figure:
    """Plot how the three greedy knapsack criteria fill the knapsack.

    When saving, writes a timestamped PNG to ``plots/guloso/mochila`` at the
    repository root.

    Parameters
    ----------
    pesos : sequence of int
        Item weights.
    valores : sequence of int
        Item values.
    capacidade : int
        Knapsack capacity.
    otimo : sequence of int, optional
        Optimal binary solution drawn as a reference row.
    nome : str, default 'mochila_gulosa'
        File name prefix when saving.
    show : bool, default False
        Whether to open the figure in a window, blocking until it is closed.
    save : bool, default False
        Whether to save the figure as PNG.

    Returns
    -------
    matplotlib.figure.Figure
        Figure with one stacked bar of selected items per criterion.
    """
    linhas: list[tuple[str, Sequence[int], str]] = [
        (
            "#1 peso",
            mochila_gulosa(pesos, valores, capacidade, "peso"),
            COR_HEURISTICA,
        ),
        (
            "#2 valor",
            mochila_gulosa(pesos, valores, capacidade, "valor"),
            COR_HEURISTICA,
        ),
        (
            "#3 densidade",
            mochila_gulosa(pesos, valores, capacidade, "densidade"),
            COR_HEURISTICA,
        ),
    ]
    if otimo is not None:
        linhas.append(("ótimo", otimo, COR_OTIMO))

    with plt.rc_context(ESTILO):
        fig, ax = plt.subplots(
            figsize=(9, 1.5 + 0.7 * len(linhas)), layout="constrained"
        )
        for y, (_, selecao, cor) in enumerate(linhas):
            inicio = 0
            for j, bit in enumerate(selecao):
                if not bit:
                    continue
                ax.barh(
                    y,
                    pesos[j],
                    left=inicio,
                    height=0.6,
                    color=cor,
                    edgecolor=COR_SUPERFICIE,
                    linewidth=2,
                )
                ax.text(
                    inicio + pesos[j] / 2,
                    y,
                    str(j + 1),
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold",
                )
                inicio += pesos[j]
            valor = sum(v for v, bit in zip(valores, selecao) if bit)
            ax.text(
                capacidade * 1.04,
                y,
                f"valor {valor}  ·  peso {inicio}",
                va="center",
                color=COR_TEXTO_SECUNDARIO,
            )

        ax.axvline(capacidade, color=COR_TEXTO, linewidth=1.2, linestyle="--")
        ax.text(
            capacidade,
            -0.55,
            f"C = {capacidade}",
            ha="center",
            va="bottom",
            bbox={"boxstyle": "round,pad=0.2", "fc": COR_SUPERFICIE, "ec": "none"},
        )
        ax.set_yticks(range(len(linhas)), [rotulo for rotulo, _, _ in linhas])
        ax.set_ylim(len(linhas) - 0.5, -0.8)
        ax.set_xlim(0, capacidade * 1.6)
        ax.set_xlabel("Peso na mochila (números dentro das barras = itens)")
        ax.grid(axis="y", visible=False)
        ax.set_title("Mochila 0-1: heurísticas gulosas", loc="left")

    finalizar(fig, "mochila", nome, show, save)
    return fig
