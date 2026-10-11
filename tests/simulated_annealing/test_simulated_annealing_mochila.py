import random

import pytest

from metaheuristics.simulated_annealing import gerar_instancia_aleatoria
from metaheuristics.simulated_annealing import programacao_dinamica
from metaheuristics.simulated_annealing import simulated_annealing_mochila
from metaheuristics.simulated_annealing.plot import plotar_simulated_annealing

PLOT = False


def test_simulated_annealing_mochila__notebook_example():
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)

    # a capacidade é definida pelo problema, nesse caso ela é cerca de metade do
    # peso total dos itens
    capacidade = sum(item.peso for item in itens) // 2

    # itens genéricos para simular um problema
    valor_otimo, _ = programacao_dinamica(itens, capacidade)

    melhor_solucao, output = simulated_annealing_mochila(
        itens=itens,
        capacidade_mochila=capacidade,
        temperatura_inicial=1000,
        temperatura_minima=1,
        fator_resfriamento=0.9,
        iteracoes_por_temperatura=100,
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
