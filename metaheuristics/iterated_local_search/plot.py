"""Visualization of an Iterated Local Search run."""

import matplotlib.pyplot as plt


def plotar_iterated_local_search(output: dict, valor_otimo: int | None = None,
                                save: bool = False):
    """Plot candidate and best-so-far values across ILS cycles.

    Parameters
    ----------
    output : dict
        History returned by ``iterated_local_search_mochila``.
    valor_otimo : int or None, default None
        Dynamic-programming optimum used as a horizontal reference line.
    save : bool, default False
        Save to ``ils_mochila.png`` if True.

    Returns
    -------
    matplotlib.figure.Figure
        Matplotlib figure, left open for the caller to display or close.
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(list(output["valor_candidato"]), list(output["valor_candidato"].values()),
            label="Valor do candidato", alpha=0.65)
    ax.plot(list(output["melhor_valor"]), list(output["melhor_valor"].values()),
            label="Melhor valor", linewidth=2)
    if valor_otimo is not None:
        ax.axhline(valor_otimo, linestyle="--", label="Ótimo (PD)")
    ax.set(xlabel="Iteração ILS", ylabel="Valor total", title="ILS — Mochila 0-1")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    if save:
        fig.savefig("ils_mochila.png", dpi=160)
    return fig
