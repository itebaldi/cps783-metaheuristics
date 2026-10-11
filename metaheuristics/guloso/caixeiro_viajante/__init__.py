from collections.abc import Sequence

from metaheuristics.guloso import Aresta
from metaheuristics.guloso import raiz


def arestas_da_matriz(custos: Sequence[Sequence[float | None]]) -> list[Aresta]:
    """List the edges of an undirected graph given by its cost matrix.

    Only the upper triangle is read; ``None`` marks a missing edge.

    Parameters
    ----------
    custos : sequence of sequence of float or None
        Square cost matrix between vertices.

    Returns
    -------
    list of Aresta
        Edges as ``(i, j, custo)`` with 1-based ``i < j``, in row-major order.
    """
    arestas: list[Aresta] = []
    for i, linha in enumerate(custos):
        for j in range(i + 1, len(linha)):
            custo = linha[j]
            if custo is not None:
                arestas.append((i + 1, j + 1, custo))
    return arestas


def caixeiro_viajante_guloso(
    custos: Sequence[Sequence[float | None]],
) -> list[Aresta]:
    """Build a traveling salesman tour by greedily adding the cheapest edges.

    An edge is skipped when it gives a vertex degree 3 or closes a subcycle that
    leaves vertices out. Fewer than ``n`` edges means no tour was found.

    Parameters
    ----------
    custos : sequence of sequence of float or None
        Square symmetric cost matrix; ``None`` marks a missing edge.

    Returns
    -------
    list of Aresta
        Tour edges as ``(i, j, custo)`` in the order they were added.
    """
    n = len(custos)
    grau = [0] * (n + 1)
    pai = list(range(n + 1))
    ciclo: list[Aresta] = []
    for i, j, custo in sorted(arestas_da_matriz(custos), key=lambda a: a[2]):
        if len(ciclo) == n:
            break
        if grau[i] == 2 or grau[j] == 2:
            continue
        raiz_i = raiz(pai, i)
        raiz_j = raiz(pai, j)
        # i e j já conectados: só pode fechar o ciclo se ele passar por todos
        if raiz_i == raiz_j and len(ciclo) < n - 1:
            continue
        pai[raiz_i] = raiz_j
        grau[i] += 1
        grau[j] += 1
        ciclo.append((i, j, custo))
    return ciclo
