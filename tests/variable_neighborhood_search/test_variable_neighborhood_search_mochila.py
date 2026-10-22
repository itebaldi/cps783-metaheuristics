"""Pytest tests for Basic VNS on the 0-1 knapsack problem."""

import random
import pytest
from variable_neighborhood_search import (
    Item, gerar_instancia_aleatoria, programacao_dinamica,
    calcular_valor_peso, agitacao, busca_local,
    variable_neighborhood_search_mochila,
)
from variable_neighborhood_search.plot import plotar_variable_neighborhood_search

PLOT = False


def test_variable_neighborhood_search_mochila__notebook_example():
    """Benchmark the same 20-item seed-0 instance as SA and ILS."""
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    valor_otimo, _ = programacao_dinamica(itens, capacidade)
    melhor_solucao, output = variable_neighborhood_search_mochila(
        itens=itens, capacidade_mochila=capacidade,
        max_iteracoes=250, k_max=4,
    )
    melhor_valor, peso = calcular_valor_peso(melhor_solucao, itens, capacidade)
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100 if valor_otimo else 0
    assert len(output["valor_candidato"]) == 251
    assert len(output["melhor_valor"]) == 251
    assert len(output["k"]) == 251
    assert peso <= capacidade
    assert melhor_valor == output["melhor_valor"][250]
    valores = list(output["melhor_valor"].values())
    assert all(b >= a for a, b in zip(valores, valores[1:]))
    assert gap <= 5
    if PLOT:
        plotar_variable_neighborhood_search(output, valor_otimo, save=True)


def test_agitacao_e_viabilidade():
    random.seed(3)
    itens = [Item(4, 6), Item(5, 8), Item(3, 5), Item(2, 2)]
    inicial = [1, 0, 1, 0]
    resultado = agitacao(inicial, itens, 7, 3)
    assert calcular_valor_peso(resultado, itens, 7)[1] <= 7
    assert inicial == [1, 0, 1, 0]


def test_agitacao_diferenca_exata_quando_viavel():
    random.seed(4)
    itens = [Item(1, 2) for _ in range(8)]
    solucao = [0] * 8
    vizinha = agitacao(solucao, itens, 8, 3)
    assert sum(a != b for a, b in zip(solucao, vizinha)) == 3


def test_busca_local_nao_piora():
    itens = [Item(2, 3), Item(3, 4), Item(4, 8)]
    inicial = [1, 0, 0]
    melhor = busca_local(inicial, itens, 5)
    assert inicial == [1, 0, 0]
    assert calcular_valor_peso(melhor, itens, 5) == (8, 4)


def test_caso_vazio_e_zero_iteracoes():
    solucao, output = variable_neighborhood_search_mochila([], 0, 0)
    assert solucao == []
    assert output["melhor_valor"] == {0: 0}
    solucao, output = variable_neighborhood_search_mochila([], 0, 3)
    assert len(output["melhor_valor"]) == 4


def test_parametros_invalidos():
    with pytest.raises(ValueError):
        variable_neighborhood_search_mochila([Item(1, 2)], 4, 10, k_max=2)
    with pytest.raises(ValueError):
        variable_neighborhood_search_mochila([Item(1, 2)], 4, -1, k_max=1)
    with pytest.raises(ValueError):
        variable_neighborhood_search_mochila([Item(1, 2)], -1, 10, k_max=1)


def test_melhoria_reinicia_vizinhanca(monkeypatch):
    """Verify the defining reset-to-N1 rule on deterministic mocked candidates."""
    import variable_neighborhood_search as vns
    itens = [Item(1, 1), Item(1, 2), Item(1, 3)]
    monkeypatch.setattr(vns, "gerar_solucao_inicial", lambda *_: [1, 0, 0])
    usados = []

    def fake_agitacao(solucao, itens, capacidade, k):
        usados.append(k)
        return solucao

    candidates = iter([[1, 0, 0], [0, 1, 0], [0, 1, 0]])
    monkeypatch.setattr(vns, "agitacao", fake_agitacao)
    monkeypatch.setattr(vns, "busca_local", lambda *_: next(candidates))
    _, output = vns.variable_neighborhood_search_mochila(itens, 1, 3, 3)
    assert usados == [1, 2, 1]
    assert list(output["aceito"].values()) == [0, 0, 1, 0]
