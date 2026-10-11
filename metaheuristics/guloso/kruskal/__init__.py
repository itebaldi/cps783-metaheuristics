from collections.abc import Sequence

from metaheuristics.guloso import Aresta
from metaheuristics.guloso import raiz


def kruskal(num_vertices: int, arestas: Sequence[Aresta]) -> list[Aresta]:
    """Build a minimum spanning tree with Kruskal's greedy algorithm.

    Edges of equal weight keep their input order. A disconnected graph yields a
    spanning forest with fewer than ``num_vertices - 1`` edges.

    Parameters
    ----------
    num_vertices : int
        Number of vertices, labeled from 1 to ``num_vertices``.
    arestas : sequence of Aresta
        Edges as ``(u, v, peso)``.

    Returns
    -------
    list of Aresta
        Tree edges in the order they were added.
    """
    pai = list(range(num_vertices + 1))
    arvore: list[Aresta] = []
    # H: arestas em ordem não decrescente de peso
    for u, v, peso in sorted(arestas, key=lambda aresta: aresta[2]):
        if len(arvore) == num_vertices - 1:
            break
        raiz_u = raiz(pai, u)
        raiz_v = raiz(pai, v)
        # T ∪ {h_i} é acíclico se u e v estão em componentes diferentes
        if raiz_u != raiz_v:
            pai[raiz_u] = raiz_v
            arvore.append((u, v, peso))
    return arvore
