"""Iterated Local Search (ILS) for the 0-1 knapsack problem."""

import random


class Item:
    """Item of the 0-1 knapsack problem.

    Parameters
    ----------
    peso : int
        Positive integer weight.
    valor : int
        Non-negative integer value.
    """

    def __init__(self, peso: int, valor: int) -> None:
        self.peso = peso
        self.valor = valor

    def __repr__(self) -> str:
        return f"Item(peso={self.peso}, valor={self.valor})"


def gerar_instancia_aleatoria(num_itens: int, max_peso: int, max_valor: int) -> list[Item]:
    """Generate a random instance using the global ``random`` state.

    Parameters
    ----------
    num_itens : int
        Number of items.
    max_peso : int
        Largest possible weight (minimum is 1).
    max_valor : int
        Largest possible value (minimum is 1).

    Returns
    -------
    list of Item
        Randomly sampled items.
    """
    if num_itens < 0 or max_peso < 1 or max_valor < 1:
        raise ValueError("Quantidade de itens e limites devem ser válidos.")
    return [Item(random.randint(1, max_peso), random.randint(1, max_valor))
            for _ in range(num_itens)]


def calcular_valor_peso(
    solucao: list[int], itens: list[Item], capacidade_mochila: int
) -> tuple[int, int]:
    """Compute objective value and weight; return value 0 if infeasible.

    Parameters
    ----------
    solucao : list of int
        Selection vector (0 or 1 for each item).
    itens : list of Item
        Knapsack items.
    capacidade_mochila : int
        Maximum allowed total weight.

    Returns
    -------
    tuple of (int, int)
        Value (zero if overweight), and actual selected weight.
    """
    if len(solucao) != len(itens):
        raise ValueError("Solução e itens devem ter o mesmo tamanho.")
    if any(bit not in (0, 1) for bit in solucao):
        raise ValueError("A solução deve ser binária.")
    valor = sum(item.valor for item, bit in zip(itens, solucao) if bit)
    peso = sum(item.peso for item, bit in zip(itens, solucao) if bit)
    return (valor if peso <= capacidade_mochila else 0), peso


def programacao_dinamica(itens: list[Item], capacidade: int) -> tuple[int, list[int]]:
    """Solve integer-weight 0-1 knapsack exactly by dynamic programming.

    Parameters
    ----------
    itens : list of Item
        Knapsack items with positive integer weights.
    capacidade : int
        Non-negative integer capacity.

    Returns
    -------
    tuple of (int, list of int)
        Optimal value and one optimal binary selection vector.
    """
    if capacidade < 0:
        raise ValueError("Capacidade não pode ser negativa.")
    n = len(itens)
    dp = [[0] * (capacidade + 1) for _ in range(n + 1)]
    for i, item in enumerate(itens, start=1):
        for w in range(capacidade + 1):
            dp[i][w] = dp[i - 1][w]
            if item.peso <= w:
                dp[i][w] = max(dp[i][w], item.valor + dp[i - 1][w - item.peso])
    selecao = [0] * n
    w = capacidade
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selecao[i - 1] = 1
            w -= itens[i - 1].peso
    return dp[n][capacidade], selecao


def gerar_solucao_inicial(itens: list[Item], capacidade_mochila: int) -> list[int]:
    """Generate a feasible initial solution by packing randomly ordered items.

    Parameters
    ----------
    itens : list of Item
        Knapsack items.
    capacidade_mochila : int
        Maximum total weight.

    Returns
    -------
    list of int
        Feasible binary solution.
    """
    solucao = [0] * len(itens)
    indices = list(range(len(itens)))
    random.shuffle(indices)
    peso_atual = 0
    for i in indices:
        if peso_atual + itens[i].peso <= capacidade_mochila:
            solucao[i] = 1
            peso_atual += itens[i].peso
    return solucao


def busca_local(
    solucao: list[int], itens: list[Item], capacidade_mochila: int
) -> list[int]:
    """Apply steepest ascent with feasible one-bit and swap neighbors.

    One-bit moves add or remove one item; swap moves remove one selected
    item and insert one unselected item. The procedure stops when no feasible
    *strictly better* neighbor exists. Neither the input nor items are changed.

    Parameters
    ----------
    solucao : list of int
        Feasible starting solution.
    itens : list of Item
        Knapsack items.
    capacidade_mochila : int
        Maximum total weight.

    Returns
    -------
    list of int
        Locally optimal feasible binary solution for this neighborhood.
    """
    atual = list(solucao)
    valor, peso = calcular_valor_peso(atual, itens, capacidade_mochila)
    if peso > capacidade_mochila:
        raise ValueError("A busca local exige uma solução inicial viável.")
    while True:
        melhor_movimento = None
        melhor_valor = valor
        # 1-flip: add/remove one item
        for i, item in enumerate(itens):
            novo_peso = peso + (item.peso if not atual[i] else -item.peso)
            novo_valor = valor + (item.valor if not atual[i] else -item.valor)
            if novo_peso <= capacidade_mochila and novo_valor > melhor_valor:
                melhor_valor, melhor_movimento = novo_valor, (i,)
        # 1-1 swap: allows improvement even when the knapsack is full
        selecionados = [i for i, bit in enumerate(atual) if bit]
        nao_selecionados = [j for j, bit in enumerate(atual) if not bit]
        for i in selecionados:
            for j in nao_selecionados:
                novo_peso = peso - itens[i].peso + itens[j].peso
                novo_valor = valor - itens[i].valor + itens[j].valor
                if novo_peso <= capacidade_mochila and novo_valor > melhor_valor:
                    melhor_valor, melhor_movimento = novo_valor, (i, j)
        if melhor_movimento is None:
            return atual
        for indice in melhor_movimento:
            atual[indice] ^= 1
        valor, peso = calcular_valor_peso(atual, itens, capacidade_mochila)


def perturbar_solucao(
    solucao: list[int], itens: list[Item], capacidade_mochila: int,
    intensidade_perturbacao: int = 3,
) -> list[int]:
    """Perturb the current solution by flipping sampled distinct bits.

    Unlike local search, the perturbation can temporarily decrease objective
    value. If its resulting weight exceeds capacity, random selected items are
    removed until feasible. This repair is a design choice for knapsack.

    Parameters
    ----------
    solucao : list of int
        Feasible current solution.
    itens : list of Item
        Knapsack items.
    capacidade_mochila : int
        Maximum allowed weight.
    intensidade_perturbacao : int, default 3
        Number of distinct bits to flip before feasibility repair.

    Returns
    -------
    list of int
        A new feasible binary solution.
    """
    if not 1 <= intensidade_perturbacao <= len(itens):
        raise ValueError("Intensidade deve estar entre 1 e a quantidade de itens.")
    nova = list(solucao)
    for i in random.sample(range(len(itens)), intensidade_perturbacao):
        nova[i] ^= 1
    _, peso = calcular_valor_peso(nova, itens, capacidade_mochila)
    selecionados = [i for i, bit in enumerate(nova) if bit]
    random.shuffle(selecionados)
    for i in selecionados:
        if peso <= capacidade_mochila:
            break
        nova[i] = 0
        peso -= itens[i].peso
    return nova


def iterated_local_search_mochila(
    itens: list[Item],
    capacidade_mochila: int,
    max_iteracoes: int,
    intensidade_perturbacao: int = 3,
) -> tuple[list[int], dict[str, dict[int, int]]]:
    """Optimize 0-1 knapsack by basic Iterated Local Search (ILS).

    Starting from a random feasible solution, perform local search; then
    repeatedly perturb the incumbent local optimum, optimize again by local
    search, and accept the candidate only if its value strictly improves the
    current solution. Track the best solution separately for benchmarking.

    Parameters
    ----------
    itens : list of Item
        Knapsack items.
    capacidade_mochila : int
        Maximum allowed total weight.
    max_iteracoes : int
        Number of ILS cycles (non-negative).
    intensidade_perturbacao : int, default 3
        Number of bits flipped during each perturbation, before repair.

    Returns
    -------
    melhor_solucao : list of int
        Best feasible selection vector found.
    dict_output : dict of {str: dict of {int: int}}
        Per-iteration history indexed from 0: ``'valor_candidato'`` is the
        optimized perturbed solution value, ``'valor_atual'`` is the accepted
        incumbent value, ``'melhor_valor'`` is best-so-far value, and
        ``'aceito'`` indicates accepted improvement (1 or 0).
    """
    if capacidade_mochila < 0 or max_iteracoes < 0:
        raise ValueError("Capacidade e iterações não podem ser negativas.")
    if any(item.peso <= 0 or item.valor < 0 for item in itens):
        raise ValueError("Itens devem ter peso positivo e valor não negativo.")
    if not itens and max_iteracoes > 0:
        raise ValueError("É necessário ao menos um item para perturbar.")
    if itens and not 1 <= intensidade_perturbacao <= len(itens):
        raise ValueError("Intensidade inválida para a quantidade de itens.")

    inicial = gerar_solucao_inicial(itens, capacidade_mochila)
    atual = busca_local(inicial, itens, capacidade_mochila)
    valor_atual, _ = calcular_valor_peso(atual, itens, capacidade_mochila)
    melhor = list(atual)
    melhor_valor = valor_atual
    output: dict[str, dict[int, int]] = {
        "valor_candidato": {0: valor_atual},
        "valor_atual": {0: valor_atual},
        "melhor_valor": {0: melhor_valor},
        "aceito": {0: 1},
    }
    for k in range(1, max_iteracoes + 1):
        perturbada = perturbar_solucao(atual, itens, capacidade_mochila, intensidade_perturbacao)
        candidata = busca_local(perturbada, itens, capacidade_mochila)
        valor_candidato, _ = calcular_valor_peso(candidata, itens, capacidade_mochila)
        aceito = int(valor_candidato > valor_atual)
        if aceito:
            atual = candidata
            valor_atual = valor_candidato
        if valor_atual > melhor_valor:
            melhor = list(atual)
            melhor_valor = valor_atual
        output["valor_candidato"][k] = valor_candidato
        output["valor_atual"][k] = valor_atual
        output["melhor_valor"][k] = melhor_valor
        output["aceito"][k] = aceito
    return melhor, output
