from collections.abc import Sequence
from typing import Literal

Criterio = Literal["peso", "valor", "densidade"]


def mochila_gulosa(
    pesos: Sequence[int],
    valores: Sequence[int],
    capacidade: int,
    criterio: Criterio,
) -> list[int]:
    """Fill a 0-1 knapsack greedily, scanning items in the order of a criterion.

    Parameters
    ----------
    pesos : sequence of int
        Item weights.
    valores : sequence of int
        Item values.
    capacidade : int
        Knapsack capacity.
    criterio : {'peso', 'valor', 'densidade'}
        Scan order: non-decreasing weight, non-increasing value or non-increasing
        value-to-weight ratio.

    Returns
    -------
    list of int
        Binary vector where 1 means the item is in the knapsack.
    """
    # Heurísticas #1, #2 e #3: só muda a ordem em que os itens são examinados
    ordens = {
        "peso": lambda j: pesos[j],
        "valor": lambda j: -valores[j],
        "densidade": lambda j: -valores[j] / pesos[j],
    }
    ordem = sorted(range(len(pesos)), key=ordens[criterio])

    selecao = [0] * len(pesos)
    capacidade_residual = capacidade
    for j in ordem:
        if capacidade_residual - pesos[j] >= 0:
            selecao[j] = 1
            capacidade_residual -= pesos[j]
    return selecao
