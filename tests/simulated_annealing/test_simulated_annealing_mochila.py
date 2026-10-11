import random

import pytest

from metaheuristics.simulated_annealing import gerar_instancia_aleatoria
from metaheuristics.simulated_annealing import programacao_dinamica
from metaheuristics.simulated_annealing import simulated_annealing_mochila
from metaheuristics.simulated_annealing.plot import plotar_simulated_annealing

PLOT = True


def test_simulated_annealing_mochila__notebook_example():
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    valor_otimo, _ = programacao_dinamica(itens, capacidade)
    melhor_solucao, output = simulated_annealing_mochila(
        itens, capacidade, 1000, 1, 0.9, 100
    )
    melhor_valor = max(output["melhor_valor"].values())
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100

    assert len(output["valor_vizinho"]) == 6600
    assert output["temperature"][4035] == pytest.approx(14.78, abs=0.005)
    assert sum(item.peso for item, bit in zip(itens, melhor_solucao) if bit) <= (
        capacidade
    )
    assert gap <= 5

    if PLOT:
        plotar_simulated_annealing(output, valor_otimo, save=True)
