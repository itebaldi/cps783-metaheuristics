# Pseudocódigo do GRASP + Simulated Annealing

A construção inicial usa uma lista restrita de candidatos (RCL). O SA pode aceitar pioras de custo e reduz a temperatura após cada vizinho viável avaliado.

Parâmetros comuns. R é o máximo de reinícios, P é o máximo de passos por reinício, α controla a RCL e B é o orçamento de avaliações viáveis. T₀ é a temperatura inicial, β é o fator de resfriamento e T_mín é a temperatura de parada, igual a 10⁻¹² no código.

## Algoritmo principal

```text
ALGORITMO GRASP_SA(instância, R, P, α, B, T₀, β, T_mín)
    melhor ← NENHUMA
    melhor_custo ← +∞
    avaliações ← 0
    histórico ← lista vazia
    abertura_gulosa ← facilidades em ordem crescente de custo fixo/capacidade,
                      até que a capacidade somada cubra a demanda total

    PARA reinício de 1 até R, enquanto avaliações < B, FAÇA
        disponíveis ← alternar entre abertura_gulosa e todas as facilidades,
                      começando pela abertura_gulosa
        ordem ← EMBARALHAR todos os clientes
        X ← CONSTRUIR_COM_RCL(disponíveis, ordem, α)
        SE X = FALHA ENTÃO
            PASSAR ao próximo reinício
        FIM-SE

        y ← indicador das facilidades com fluxo positivo em X
        SE (X, y) for inviável ENTÃO
            PASSAR ao próximo reinício
        FIM-SE

        atual ← (X, y)
        Z_atual ← AVALIAR(atual)
        T ← T₀

        REPETIR até P passos enquanto avaliações < B
            SE T ≤ T_mín ENTÃO
                ENCERRAR a busca local deste reinício
            FIM-SE
            vizinho ← GERAR_VIZINHO_VIÁVEL(X da solução atual)
            SE vizinho = FALHA ENTÃO
                ENCERRAR a busca local deste reinício
            FIM-SE

            Z_vizinho ← AVALIAR(vizinho)
            Δ ← Z_vizinho − Z_atual
            SE Δ ≤ 0 OU UNIFORME(0,1) < exp(−Δ/T) ENTÃO
                (atual, Z_atual) ← (vizinho, Z_vizinho)
            FIM-SE
            T ← β × T
        FIM-REPETIR
    FIM-PARA

    SE melhor = NENHUMA ENTÃO
        RETORNAR FALHA
    FIM-SE
    RETORNAR melhor e histórico
FIM-ALGORITMO
```

## Avaliação de uma solução viável

```text
FUNÇÃO AVALIAR(s)
    Z ← custo de abertura + custo de transporte de s
    avaliações ← avaliações + 1
    SE Z < melhor_custo ENTÃO
        (melhor, melhor_custo) ← (s, Z)
    FIM-SE
    REGISTRAR melhor_custo no histórico
    RETORNAR Z
FIM-FUNÇÃO
```

## Construção inicial com RCL

```text
FUNÇÃO CONSTRUIR_COM_RCL(disponíveis, ordem_clientes, α)
    X ← matriz de alocação com zeros
    residual ← capacidades das facilidades disponíveis

    PARA cada cliente i em ordem_clientes FAÇA
        falta ← demanda[i]
        ENQUANTO falta > 0 FAÇA
            candidatos ← facilidades disponíveis com capacidade residual positiva
                          e sem clientes já atendidos que conflitem com i
            SE candidatos estiver vazio ENTÃO
                RETORNAR FALHA
            FIM-SE

            PARA cada facilidade j em candidatos FAÇA
                q[j] ← MÍNIMO(falta, residual[j])
                pontuação[j] ← custo_transporte[i,j]
                SE j ainda não tiver fluxo ENTÃO
                    pontuação[j] ← pontuação[j] + custo_fixo[j] / q[j]
                FIM-SE
            FIM-PARA

            limite ← menor_pontuação + α × (maior_pontuação − menor_pontuação)
            RCL ← facilidades candidatas com pontuação ≤ limite
            j ← SORTEAR(RCL)
            X[i,j] ← X[i,j] + q[j]
            residual[j] ← residual[j] − q[j]
            falta ← falta − q[j]
        FIM-ENQUANTO
    FIM-PARA
    RETORNAR X
FIM-FUNÇÃO
```

## Geração de um vizinho

```text
FUNÇÃO GERAR_VIZINHO_VIÁVEL(X)
    SE houver menos de duas facilidades ou nenhuma entrega ENTÃO
        RETORNAR FALHA
    FIM-SE

    REPETIR até 30 vezes
        (i, origem) ← SORTEAR uma alocação com X[i,origem] > 0
        destino ← SORTEAR uma facilidade diferente da origem

        COM PROBABILIDADE 0,5
            Propor transferir parte da entrega de i da origem para o destino
            Sortear uma quantidade inteira de 1 até o menor valor entre
                a entrega atual de i na origem e a capacidade livre do destino
        SENÃO
            Sortear outro cliente k que receba do destino
            Propor trocar quantidades iguais de i e k entre origem e destino
            Sortear uma quantidade inteira de 1 até o menor dos dois fluxos atuais
        FIM-ESCOLHA

        SE a proposta pôde ser feita e respeita demandas, capacidades e conflitos ENTÃO
            X' ← resultado do movimento
            y' ← indicador das facilidades com fluxo positivo em X'
            RETORNAR (X', y')
        FIM-SE
    FIM-REPETIR
    RETORNAR FALHA
FIM-FUNÇÃO
```
