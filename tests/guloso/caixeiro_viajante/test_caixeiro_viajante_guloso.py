import pytest

from metaheuristics.guloso.caixeiro_viajante import caixeiro_viajante_guloso
from metaheuristics.guloso.caixeiro_viajante.plot import plotar_caixeiro_viajante

PLOT = True
M = 100


@pytest.mark.parametrize(
    ("exemplo", "custos", "posicoes", "esperado"),
    [
        pytest.param(
            "k6",
            [
                [None, 9, 2, 8, 12, 11],
                [9, None, 7, 19, 10, 32],
                [2, 7, None, 29, 18, 6],
                [8, 19, 29, None, 24, 3],
                [12, 10, 18, 24, None, 19],
                [11, 32, 6, 3, 19, None],
            ],
            {
                1: (2, 3),
                2: (0, 1.4),
                3: (6, 3.2),
                4: (6.5, 0),
                5: (3, 0.2),
                6: (8, 1.5),
            },
            [(1, 3, 2), (4, 6, 3), (3, 6, 6), (1, 2, 9), (2, 5, 10), (4, 5, 24)],
            id="k6",
        ),
        pytest.param(
            "expensive_closing_edge",
            [
                [None, M, 2, 2, 1],
                [M, None, 1, 2, 2],
                [2, 1, None, 1, 2],
                [2, 2, 1, None, 1],
                [1, 2, 2, 1, None],
            ],
            {
                1: (0, 2),
                2: (1.9, 0.62),
                3: (1.18, -1.62),
                4: (-1.18, -1.62),
                5: (-1.9, 0.62),
            },
            [(1, 5, 1), (2, 3, 1), (3, 4, 1), (4, 5, 1), (1, 2, M)],
            id="expensive_closing_edge",
        ),
        pytest.param(
            "no_feasible_tour",
            [
                [None, 2, 3, None],
                [2, None, 1, 2],
                [3, 1, None, 3],
                [None, 2, 3, None],
            ],
            {1: (0, 0), 2: (1.5, 1), 3: (1.5, -1), 4: (3, 0)},
            [(2, 3, 1), (1, 2, 2), (3, 4, 3)],
            id="no_feasible_tour",
        ),
    ],
)
def test_caixeiro_viajante_guloso__classic_cases(
    exemplo, custos, posicoes, esperado
):
    assert caixeiro_viajante_guloso(custos) == esperado

    if PLOT:
        plotar_caixeiro_viajante(custos, posicoes, nome=exemplo, save=True)
