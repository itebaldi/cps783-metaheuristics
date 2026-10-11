import math
import random


class Item:
    """Item of the 0-1 knapsack problem.

    Parameters
    ----------
    peso : int
        Item weight.
    valor : int
        Item value.
    """

    def __init__(self, peso: int, valor: int) -> None:
        self.peso = peso
        self.valor = valor

    def __repr__(self) -> str:
        return f"Item(peso={self.peso}, valor={self.valor})"


def gerar_instancia_aleatoria(
    num_itens: int, max_peso: int, max_valor: int
) -> list[Item]:
    """Generate a random list of knapsack items.

    Parameters
    ----------
    num_itens : int
        Number of items to generate.
    max_peso : int
        Upper bound for item weights, drawn uniformly from ``[1, max_peso]``.
    max_valor : int
        Upper bound for item values, drawn uniformly from ``[1, max_valor]``.

    Returns
    -------
    list of Item
        Generated items.
    """
    itens_gerados = []
    for _ in range(num_itens):
        peso = random.randint(1, max_peso)
        valor = random.randint(1, max_valor)
        itens_gerados.append(Item(peso, valor))
    return itens_gerados


def calcular_valor_peso(
    solucao: list[int], itens: list[Item], capacidade_mochila: int
) -> tuple[int, int]:
    """Compute the total value and weight of a knapsack solution.

    The value is 0 when the total weight exceeds the capacity.

    Parameters
    ----------
    solucao : list of int
        Binary vector where 1 means the item at that index is in the knapsack.
    itens : list of Item
        Items of the instance.
    capacidade_mochila : int
        Knapsack capacity.

    Returns
    -------
    tuple of (int, int)
        Total value and total weight of the selected items.
    """
    valor_total = 0
    peso_total = 0
    for i in range(len(solucao)):
        if solucao[i] == 1:
            valor_total += itens[i].valor
            peso_total += itens[i].peso
    if peso_total > capacidade_mochila:
        # ATENÇÃO: retorna 0 de valor se a capacidade for excedida
        return 0, peso_total
    return valor_total, peso_total


def programacao_dinamica(
    itens: list[Item], capacidade: int
) -> tuple[int, list[int]]:
    """Solve the 0-1 knapsack problem to optimality with dynamic programming.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    tuple of (int, list of int)
        Optimal value and binary vector of the selected items.
    """
    n = len(itens)
    dp = [[0 for _ in range(capacidade + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        item = itens[i - 1]
        for w in range(1, capacidade + 1):
            if item.peso <= w:
                dp[i][w] = max(item.valor + dp[i - 1][w - item.peso], dp[i - 1][w])
            else:
                dp[i][w] = dp[i - 1][w]

    # --- Início da Reconstrução da Solução---
    valor_maximo = dp[n][capacidade]

    # 1. Cria um array de zeros com o tamanho da lista de itens
    selecao = [0] * n

    w = capacidade
    for i in range(n, 0, -1):
        # Se o valor mudou da linha de cima para a atual, o item foi incluído
        if dp[i][w] != dp[i - 1][w]:
            # 2. Marca a posição do item como 1
            selecao[i - 1] = 1
            # E atualiza a capacidade restante
            w -= itens[i - 1].peso

    return valor_maximo, selecao


def gerar_solucao_inicial(itens: list[Item], capacidade_mochila: int) -> list[int]:
    """Generate a random feasible solution by greedily packing shuffled items.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade_mochila : int
        Knapsack capacity.

    Returns
    -------
    list of int
        Binary vector of the selected items.
    """
    solucao = [0] * len(itens)
    peso_atual = 0
    indices = list(range(len(itens)))

    # O shuffle faz cada execução começar de um ponto diferente e evita que a ordem
    # em que os itens estão na lista influencie a solução inicial.
    random.shuffle(indices)

    for i in indices:
        if peso_atual + itens[i].peso <= capacidade_mochila:
            solucao[i] = 1
            peso_atual += itens[i].peso
    return solucao


def gerar_vizinho(
    solucao: list[int], itens: list[Item], capacidade_mochila: int
) -> list[int]:
    """Generate a feasible neighbor by flipping one random bit of the solution.

    Redraws the index until the flip keeps the solution within capacity.

    Parameters
    ----------
    solucao : list of int
        Current binary solution, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade_mochila : int
        Knapsack capacity.

    Returns
    -------
    list of int
        New binary solution differing from the input in exactly one position.
    """
    vizinho = list(solucao)
    while True:
        idx = random.randint(0, len(itens) - 1)

        if vizinho[idx] == 0:
            if (
                calcular_valor_peso(vizinho, itens, capacidade_mochila)[1]
                + itens[idx].peso
                <= capacidade_mochila
            ):
                # adiciona vizinho
                vizinho[idx] = 1
                return vizinho
        else:
            # remove vizinho
            vizinho[idx] = 0
            return vizinho


def simulated_annealing_mochila(
    itens: list[Item],
    capacidade_mochila: int,
    temperatura_inicial: float,
    temperatura_minima: float,
    fator_resfriamento: float,
    iteracoes_por_temperatura: int,
) -> tuple[list[int], dict[str, dict[int, float]]]:
    """Solve the 0-1 knapsack problem with simulated annealing.

    Prints the initial solution and every improvement to stdout.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade_mochila : int
        Knapsack capacity.
    temperatura_inicial : float
        Starting temperature.
    temperatura_minima : float
        Temperature at or below which the search stops.
    fator_resfriamento : float
        Multiplicative cooling factor applied after each temperature level.
    iteracoes_por_temperatura : int
        Number of Metropolis iterations per temperature level.

    Returns
    -------
    melhor_solucao : list of int
        Best binary solution found.
    dict_output : dict of {str: dict of {int: float}}
        Per-iteration history keyed by ``'valor_vizinho'`` (neighbor value),
        ``'melhor_valor'`` (best value at each improvement, iteration 0 being the
        initial solution) and ``'temperature'``.
    """
    # Geração da Solução Inicial para a instância fornecida/gerada aleatoriamente
    solucao_atual = gerar_solucao_inicial(itens, capacidade_mochila)
    valor_inicial, _ = calcular_valor_peso(solucao_atual, itens, capacidade_mochila)
    # Demais inicializações
    melhor_solucao = list(solucao_atual)
    melhor_valor = valor_inicial
    temperatura = temperatura_inicial
    # utilizado para controlar em quais iterações temos melhorias
    iteracao_global = 0
    print("\n--- Solução Inicial ---")
    print(f"Solução Inicial: {melhor_solucao}")
    print(f"Valor Inicial: {melhor_valor}")

    # Loop externo: Resfriamento da temperatura
    print("\n--- Iterações SA ---")
    list_melhor_valor: dict[int, float] = {0: valor_inicial}
    list_valor_vizinho: dict[int, float] = {}
    list_temperature: dict[int, float] = {}
    while temperatura > temperatura_minima:
        # Loop interno: Iterações por nível de temperatura (Iterações de Metropolis)
        for _ in range(iteracoes_por_temperatura):
            iteracao_global += 1

            solucao_vizinha = gerar_vizinho(solucao_atual, itens, capacidade_mochila)
            valor_atual, _ = calcular_valor_peso(
                solucao_atual, itens, capacidade_mochila
            )
            valor_vizinho, _ = calcular_valor_peso(
                solucao_vizinha, itens, capacidade_mochila
            )

            list_valor_vizinho[iteracao_global] = valor_vizinho
            list_temperature[iteracao_global] = temperatura

            delta_valor = valor_vizinho - valor_atual

            if delta_valor > 0:
                solucao_atual = solucao_vizinha
                if valor_vizinho > melhor_valor:
                    melhor_solucao = list(solucao_vizinha)
                    melhor_valor = valor_vizinho
                    list_melhor_valor[iteracao_global] = melhor_valor
                    # IMPRIME UMA NOVA MELHOR SOLUÇÃO QUANDO ELA É ENCONTRADA
                    print(
                        f"Iteração {iteracao_global}, Temperatura {temperatura:.2f}: "
                        f"valor = {melhor_valor}, solução = {melhor_solucao}"
                    )
            else:
                probabilidade = math.exp(delta_valor / temperatura)
                if random.uniform(0, 1) < probabilidade:
                    solucao_atual = solucao_vizinha

        # Resfriamento da temperatura acontece apenas aqui, no loop externo
        temperatura *= fator_resfriamento

    dict_output = {
        "valor_vizinho": list_valor_vizinho,
        "melhor_valor": list_melhor_valor,
        "temperature": list_temperature,
    }
    return melhor_solucao, dict_output
