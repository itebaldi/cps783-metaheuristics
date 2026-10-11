import pytest

from metaheuristics.guloso.mochila import mochila_gulosa
from metaheuristics.guloso.mochila.plot import plotar_mochila_gulosa

PLOT = True


@pytest.mark.parametrize(
    ("criterio", "pesos", "valores", "capacidade", "esperado", "otimo"),
    [
        pytest.param(
            "peso", [3, 4, 6], [2, 6, 10], 7, [1, 1, 0], [0, 0, 1], id="by_weight"
        ),
        pytest.param(
            "valor", [7, 3, 2], [10, 8, 6], 7, [1, 0, 0], [0, 1, 1], id="by_value"
        ),
        pytest.param(
            "densidade",
            [4, 3, 7, 5, 3, 2, 3],
            [12, 8, 17, 11, 6, 2, 2],
            9,
            [1, 1, 0, 0, 0, 1, 0],
            [1, 0, 0, 1, 0, 0, 0],
            id="by_density",
        ),
    ],
)
def test_mochila_gulosa__each_criterion_misses_optimum(
    criterio, pesos, valores, capacidade, esperado, otimo
):
    selecao = mochila_gulosa(pesos, valores, capacidade, criterio)
    valor = sum(v for v, bit in zip(valores, selecao) if bit)
    valor_otimo = sum(v for v, bit in zip(valores, otimo) if bit)

    assert selecao == esperado
    assert valor < valor_otimo

    if PLOT:
        plotar_mochila_gulosa(
            pesos, valores, capacidade, otimo, nome=f"mochila_{criterio}", save=True
        )
