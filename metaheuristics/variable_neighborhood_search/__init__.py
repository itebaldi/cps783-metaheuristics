"""Basic Variable Neighborhood Search (VNS) for the 0-1 knapsack problem."""

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


def agitacao(
    solucao: list[int], itens: list[Item], capacidade_mochila: int, k: int
) -> list[int]:
    """Generate a feasible random solution from a neighborhood of strength ``k``.

    Select ``k`` distinct bits to flip (Hamming distance ``k`` before repair).
    If the modified solution exceeds capacity, randomly remove selected items
    until feasible. Repair can change its final Hamming distance. This is a
    problem-specific choice, not a requirement of the general VNS framework.

    Parameters
    ----------
    solucao : list of int
        Feasible binary incumbent; not mutated.
    itens : list of Item
        Knapsack items.
    capacidade_mochila : int
        Non-negative capacity.
    k : int
        Number of distinct binary decisions to invert; 1 <= k <= len(itens).

    Returns
    -------
    list of int
        Feasible shaken solution.
    """
    if not (1 <= k <= len(itens)):
        raise ValueError("k deve estar entre 1 e o número de itens.")
    _, peso = calcular_valor_peso(solucao, itens, capacidade_mochila)
    if peso > capacidade_mochila:
        raise ValueError("A agitação exige solução viável.")
    nova = solucao.copy()
    for i in random.sample(range(len(itens)), k):
        nova[i] ^= 1
    _, peso = calcular_valor_peso(nova, itens, capacidade_mochila)
    escolhidos = [i for i, bit in enumerate(nova) if bit]
    random.shuffle(escolhidos)
    for i in escolhidos:
        if peso <= capacidade_mochila:
            break
        nova[i] = 0
        peso -= itens[i].peso
    return nova


def variable_neighborhood_search_mochila(
    itens: list[Item],
    capacidade_mochila: int,
    max_iteracoes: int = 250,
    k_max: int = 4,
) -> tuple[list[int], dict[str, dict[int, int]]]:
    """Solve the 0-1 knapsack problem using Basic VNS (BVNS).

    Start at a feasible solution and repeatedly perform random shaking in
    increasingly distant neighborhoods N_k, followed by best-improvement
    local search (1-flip and 1-for-1 swap). A strictly improving candidate is
    accepted and resets k to 1; otherwise k increases. When k exceeds k_max,
    a new cycle starts. ``max_iteracoes`` counts shaking/local-search trials,
    *not* full cycles. Histories have an entry for iteration 0 and each trial.

    Parameters
    ----------
    itens : list of Item
        Knapsack items (positive integer weights, non-negative values).
    capacidade_mochila : int
        Maximum allowed total weight (non-negative integer).
    max_iteracoes : int, default=250
        Maximum number of shaking/local-search trials; zero is allowed.
    k_max : int, default=4
        Maximum shaking neighborhood strength. Must be at least 1, and at
        most the number of items for non-empty instances.

    Returns
    -------
    melhor_solucao : list of int
        Best feasible binary selection found.
    output : dict of {str: dict of {int: int}}
        Histories keyed by ``'valor_candidato'``, ``'melhor_valor'``,
        ``'k'`` and ``'aceito'``. Iteration 0 has ``k=0`` and ``aceito=0``.
    """
    if not isinstance(capacidade_mochila, int) or capacidade_mochila < 0:
        raise ValueError("A capacidade deve ser um inteiro não negativo.")
    if not isinstance(max_iteracoes, int) or max_iteracoes < 0:
        raise ValueError("max_iteracoes deve ser inteiro não negativo.")
    if not isinstance(k_max, int) or k_max < 1 or (itens and k_max > len(itens)):
        raise ValueError("k_max deve estar entre 1 e o número de itens.")
    if any(not isinstance(item.peso, int) or item.peso <= 0 or
           not isinstance(item.valor, int) or item.valor < 0 for item in itens):
        raise ValueError("Pesos devem ser positivos e valores não negativos, ambos inteiros.")

    atual = gerar_solucao_inicial(itens, capacidade_mochila)
    valor_atual, _ = calcular_valor_peso(atual, itens, capacidade_mochila)
    melhor_solucao = atual.copy()
    output = {
        "valor_candidato": {0: valor_atual},
        "melhor_valor": {0: valor_atual},
        "k": {0: 0},
        "aceito": {0: 0},
    }
    k = 1
    for t in range(1, max_iteracoes + 1):
        if not itens:
            candidato, valor_candidato = [], 0
            k_usado = 0
        else:
            k_usado = k
            perturbada = agitacao(atual, itens, capacidade_mochila, k)
            candidato = busca_local(perturbada, itens, capacidade_mochila)
            valor_candidato, _ = calcular_valor_peso(candidato, itens, capacidade_mochila)
        aceito = int(valor_candidato > valor_atual)
        if aceito:
            atual, valor_atual = candidato, valor_candidato
            melhor_solucao = atual.copy()
            k = 1
        elif itens:
            k = k + 1 if k < k_max else 1
        output["valor_candidato"][t] = valor_candidato
        output["melhor_valor"][t] = valor_atual
        output["k"][t] = k_usado
        output["aceito"][t] = aceito
    return melhor_solucao, output
