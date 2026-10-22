"""Plot the Basic VNS convergence history."""


def plotar_variable_neighborhood_search(
    output: dict[str, dict[int, int]], valor_otimo: int | None = None,
    save: bool = False, caminho: str = "vns_mochila.png",
) -> None:
    """Plot candidate and incumbent values over VNS trials.

    Parameters
    ----------
    output : dict of {str: dict of {int: int}}
        Histories returned by ``variable_neighborhood_search_mochila``.
    valor_otimo : int or None, default=None
        Exact optimal objective (optional benchmark line).
    save : bool, default=False
        Whether to save the plot as a PNG.
    caminho : str, default='vns_mochila.png'
        Output image path when ``save`` is true.

    Returns
    -------
    None
        Displays and optionally saves a plot.
    """
    import matplotlib.pyplot as plt

    x = list(output["melhor_valor"])
    plt.figure(figsize=(10, 5))
    plt.plot(x, list(output["valor_candidato"].values()), label="Candidato após busca local", alpha=0.6)
    plt.plot(x, list(output["melhor_valor"].values()), label="Melhor solução")
    if valor_otimo is not None:
        plt.axhline(valor_otimo, linestyle="--", label="Ótimo (PD)")
    plt.xlabel("Tentativa de agitação / busca local")
    plt.ylabel("Valor da mochila")
    plt.title("Variable Neighborhood Search — Mochila 0-1")
    plt.legend()
    plt.tight_layout()
    if save:
        plt.savefig(caminho, dpi=150)
    plt.show()
