"""Pytest tests for ILS on the 0-1 knapsack problem."""

import random

import pytest

from iterated_local_search import (
    Item,
    busca_local,
    calcular_valor_peso,
    gerar_instancia_aleatoria,
    iterated_local_search_mochila,
    perturbar_solucao,
    programacao_dinamica,
)
from iterated_local_search.plot import plotar_iterated_local_search

PLOT = False


def test_iterated_local_search_mochila__notebook_example():
    """Compare ILS with the exact optimum on one reproducible instance."""
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    valor_otimo, _ = programacao_dinamica(itens, capacidade)

    melhor_solucao, output = iterated_local_search_mochila(
        itens=itens,
        capacidade_mochila=capacidade,
        max_iteracoes=250,
        intensidade_perturbacao=4,
    )
    melhor_valor, peso = calcular_valor_peso(melhor_solucao, itens, capacidade)
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100 if valor_otimo else 0

    assert len(output["valor_candidato"]) == 251  # inclui a iteração 0
    assert len(output["melhor_valor"]) == 251
    assert peso <= capacidade
    assert melhor_valor == max(output["melhor_valor"].values())
    assert all(b >= a for a, b in zip(
        output["melhor_valor"].values(), list(output["melhor_valor"].values())[1:]
    ))
    assert gap <= 5

    if PLOT:
        plotar_iterated_local_search(output, valor_otimo, save=True)


def test_busca_local_nao_piora_e_respeita_capacidade():
    itens = [Item(2, 3), Item(3, 4), Item(4, 8)]
    inicial = [1, 0, 0]
    final = busca_local(inicial, itens, 5)
    assert inicial == [1, 0, 0]  # input não é modificado
    assert calcular_valor_peso(final, itens, 5) == (8, 4)


def test_perturbacao_mantem_viabilidade():
    random.seed(3)
    itens = [Item(4, 6), Item(5, 8), Item(3, 5), Item(2, 2)]
    inicial = [1, 0, 1, 0]
    perturbada = perturbar_solucao(inicial, itens, 7, 3)
    assert calcular_valor_peso(perturbada, itens, 7)[1] <= 7
    assert inicial == [1, 0, 1, 0]


def test_caso_sem_itens_e_sem_iteracoes():
    solucao, output = iterated_local_search_mochila([], 0, 0)
    assert solucao == []
    assert output["melhor_valor"] == {0: 0}


def test_parametros_invalidos():
    with pytest.raises(ValueError):
        iterated_local_search_mochila([Item(1, 2)], 4, 10, intensidade_perturbacao=2)
    with pytest.raises(ValueError):
        iterated_local_search_mochila([Item(1, 2)], 4, -1)
