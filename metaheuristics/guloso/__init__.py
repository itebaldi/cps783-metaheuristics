Aresta = tuple[int, int, float]


def raiz(pai: list[int], v: int) -> int:
    """Return the representative of a vertex in a union-find forest.

    Compresses the path from ``v`` to its root in place.

    Parameters
    ----------
    pai : list of int
        Parent of each vertex; a root is its own parent.
    v : int
        Vertex to look up.

    Returns
    -------
    int
        Root of the component containing ``v``.
    """
    while pai[v] != v:
        pai[v] = pai[pai[v]]
        v = pai[v]
    return v
