import random
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from metaheuristics.simulated_annealing import gerar_instancia_aleatoria
from metaheuristics.simulated_annealing import programacao_dinamica
from metaheuristics.simulated_annealing import simulated_annealing_mochila

NUM_ITENS = 20
MAX_PESO_ITEM = 20
MAX_VALOR_ITEM = 100
SEMENTE = None

TEMPERATURA_INICIAL = 1000
TEMPERATURA_MINIMA = 1
FATOR_RESFRIAMENTO = 0.9
ITERACOES_POR_TEMPERATURA = 100

PASTA_PLOTS = Path(__file__).resolve().parents[2] / "plots" / "simulated_annealing"

COR_SUPERFICIE = "#fcfcfb"
COR_TEXTO = "#0b0b0b"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_EIXO = "#c3c2b7"
COR_GRADE = "#e1e0d9"
COR_VIZINHO = "lightgray"
COR_MELHOR = "royalblue"
COR_NOVA_MELHOR = "red"
COR_OTIMO = "green"
COR_TEMPERATURA = "tab:blue"

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


def plotar_simulated_annealing(
    output: dict[str, dict[int, float]],
    valor_otimo: int | None = None,
    show: bool = False,
    save: bool = False,
) -> Figure:
    """Plot the per-iteration history of a simulated annealing run.

    When saving, writes a timestamped PNG to ``plots/simulated_annealing`` at the
    repository root.

    Parameters
    ----------
    output : dict of {str: dict of {int: float}}
        History keyed by ``'valor_vizinho'``, ``'melhor_valor'`` and
        ``'temperature'``, each mapping iteration to value.
    valor_otimo : int, optional
        Optimal value drawn as a reference line and used to compute the gap.
    show : bool, default False
        Whether to open the figure in a window, blocking until it is closed.
    save : bool, default False
        Whether to save the figure as PNG.

    Returns
    -------
    matplotlib.figure.Figure
        Figure with solution values on top and temperature below.
    """
    vizinhos = output["valor_vizinho"]
    melhores = output["melhor_valor"]
    temperaturas = output["temperature"]
    ultima_iteracao = max(vizinhos, default=0)
    melhor_valor = list(melhores.values())[-1]

    with plt.rc_context(ESTILO):
        fig, (ax_valor, ax_temperatura) = plt.subplots(
            2,
            1,
            figsize=(11, 7),
            sharex=True,
            height_ratios=(3, 1),
            layout="constrained",
        )

        ax_valor.plot(
            list(vizinhos),
            list(vizinhos.values()),
            color=COR_VIZINHO,
            linewidth=0.6,
            label="Valor do vizinho (exploração)",
        )
        ax_valor.step(
            [*melhores, ultima_iteracao],
            [*melhores.values(), melhor_valor],
            where="post",
            color=COR_MELHOR,
            linewidth=1.5,
            label=f"Melhor valor (SA): {melhor_valor}",
        )
        ax_valor.plot(
            list(melhores),
            list(melhores.values()),
            linestyle="none",
            marker="o",
            markersize=6,
            color=COR_NOVA_MELHOR,
            markeredgecolor=COR_SUPERFICIE,
            markeredgewidth=1.5,
            label="Nova melhor solução",
        )

        titulo = "Simulated Annealing na Mochila 0-1"
        if valor_otimo is not None:
            ax_valor.axhline(
                valor_otimo,
                color=COR_OTIMO,
                linewidth=1.5,
                linestyle="--",
                label=f"Ótimo (PD): {valor_otimo}",
            )
            if valor_otimo > 0:
                gap = (valor_otimo - melhor_valor) / valor_otimo * 100
                titulo += f"  ·  gap {gap:.2f}%"

        ax_valor.set_title(titulo, loc="left", fontsize=13)
        ax_valor.set_ylabel("Valor da solução")
        ax_valor.legend(loc="lower right")

        ax_temperatura.plot(
            list(temperaturas),
            list(temperaturas.values()),
            color=COR_TEMPERATURA,
            linewidth=1.5,
        )
        ax_temperatura.set_ylabel("Temperatura")
        ax_temperatura.set_xlabel("Iteração")
        ax_temperatura.margins(x=0.01)

    if save:
        PASTA_PLOTS.mkdir(parents=True, exist_ok=True)
        caminho = PASTA_PLOTS / f"sa_mochila_{datetime.now():%Y%m%d_%H%M%S}.png"
        fig.savefig(str(caminho))
    if show:
        plt.show()

    return fig


def main() -> None:
    """Run simulated annealing on a random instance and show its history."""
    random.seed(SEMENTE)
    itens = gerar_instancia_aleatoria(NUM_ITENS, MAX_PESO_ITEM, MAX_VALOR_ITEM)
    capacidade = sum(item.peso for item in itens) // 2
    valor_otimo, _ = programacao_dinamica(itens, capacidade)
    _, output = simulated_annealing_mochila(
        itens,
        capacidade,
        TEMPERATURA_INICIAL,
        TEMPERATURA_MINIMA,
        FATOR_RESFRIAMENTO,
        ITERACOES_POR_TEMPERATURA,
    )
    plotar_simulated_annealing(output, valor_otimo, show=True, save=True)


if __name__ == "__main__":
    main()
