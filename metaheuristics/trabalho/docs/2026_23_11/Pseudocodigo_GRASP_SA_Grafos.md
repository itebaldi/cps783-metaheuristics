# Pseudocódigo do GRASP + SA com grafos

O grafo de conflitos determina quais clientes podem compartilhar uma facilidade. A rede de transporte calcula as quantidades para as ligações escolhidas. O SA propõe mudanças nessas ligações e reavalia o fluxo.

R limita os reinícios, P limita os passos do SA por reinício, α controla a lista restrita de candidatos (RCL) e B é o orçamento de avaliações viáveis. T₀ é a temperatura inicial, β é o fator de resfriamento e T_mín é a temperatura de parada, igual a 10⁻¹² no código.

## Onde o GRASP atua

A cada reinício, o **GRASP constrói a configuração inicial de ligações** em duas etapas.

1. O GRASP embaralha a ordem dos clientes. **CONSTRUIR_COM_RCL** percorre essa ordem e sorteia facilidades entre os candidatos compatíveis de menor custo. Isso produz uma alocação inicial. Cada entrega positiva dessa alocação vira uma ligação permitida em L.
2. **AMPLIAR_LIGAÇÕES** monta outra lista restrita de candidatos, agora de ligações extras. Sorteia ligações de baixo custo de transporte e as inclui se forem compatíveis com os clientes já habilitados na facilidade.

Com L pronta, **AVALIAR_REDE** recalcula as quantidades a enviar pelas ligações permitidas. Em seguida, o **SA** parte dessa configuração, propõe mudanças em L e recalcula o fluxo para avaliar cada mudança.

Por exemplo, se uma facilidade já habilitou o cliente 2, o GRASP exclui o cliente 5 dos candidatos para essa facilidade porque os dois estão em conflito. O fluxo então calcula as entregas usando as ligações que foram habilitadas.

## Algoritmo principal

```text
ALGORITMO GRASP_SA_GRAFOS(instância, R, P, α, B, T₀, β, T_mín)
    G ← grafo não dirigido com os clientes e suas arestas de conflito
    clientes_ativos ← clientes com demanda positiva
    melhor ← NENHUMA
    melhor_custo ← +∞
    avaliações ← 0
    histórico ← lista vazia
    redes_testadas ← 0
    abertura_gulosa ← facilidades em ordem crescente de custo fixo/capacidade,
                      até que a capacidade somada cubra a demanda total

    PARA reinício de 1 até R, enquanto avaliações < B, FAÇA
        /* GRASP — escolhe as ligações iniciais e acrescenta ligações compatíveis */
        disponíveis ← alternar entre abertura_gulosa e todas as facilidades,
                      começando pela abertura_gulosa
        ordem ← EMBARALHAR clientes_ativos
        X ← CONSTRUIR_COM_RCL(disponíveis, ordem, α)
        SE X = FALHA ENTÃO
            PASSAR ao próximo reinício
        FIM-SE

        PARA cada facilidade j FAÇA
            L[j] ← clientes i com X[i,j] > 0
        FIM-PARA
        L ← AMPLIAR_LIGAÇÕES(L, G, clientes_ativos, α)

        /* FLUXO — calcula as quantidades para a configuração criada pelo GRASP */
        Z_atual ← AVALIAR_REDE(L)
        SE Z_atual = FALHA ENTÃO
            PASSAR ao próximo reinício
        FIM-SE

        /* SA — testa mudanças nas ligações, com novo cálculo de fluxo */
        T ← T₀
        REPETIR até P passos enquanto avaliações < B, T > T_mín
                   e houver clientes_ativos
            L' ← PROPOR_MUDANÇA(L, G, clientes_ativos)
            SE L' ≠ FALHA ENTÃO
                Z_vizinho ← AVALIAR_REDE(L')
                SE Z_vizinho ≠ FALHA ENTÃO
                    Δ ← Z_vizinho − Z_atual
                    SE Δ ≤ 0 OU UNIFORME(0,1) < exp(−Δ/T) ENTÃO
                        (L, Z_atual) ← (L', Z_vizinho)
                    FIM-SE
                FIM-SE
            FIM-SE
            T ← β × T
        FIM-REPETIR
    FIM-PARA

    SE melhor = NENHUMA ENTÃO
        RETORNAR FALHA
    FIM-SE
    RETORNAR melhor (X, y, L), histórico e redes_testadas
FIM-ALGORITMO
```

## GRASP — construção inicial com RCL

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

## GRASP — ampliação das ligações

```text
FUNÇÃO AMPLIAR_LIGAÇÕES(L, G, clientes_ativos, α)
    REPETIR
        candidatos ← pares (j,i) em que L[j] é não vazio,
                     i é ativo, i ∉ L[j] e i não conflita com nenhum membro de L[j]
        SE candidatos estiver vazio ENTÃO
            RETORNAR L
        FIM-SE
        pontuação de (j,i) ← custo de transporte por unidade de j para i
        limite ← menor_pontuação + α × (maior_pontuação − menor_pontuação)
        (j,i) ← SORTEAR entre os pares com pontuação ≤ limite
        L[j] ← L[j] ∪ {i}
    FIM-REPETIR
FIM-FUNÇÃO

```

## SA — proposta de mudança nas ligações

```text
FUNÇÃO PROPOR_MUDANÇA(L, G, clientes_ativos)
    j ← SORTEAR uma facilidade
    SE capacidade[j] = 0 ENTÃO
        RETORNAR FALHA
    FIM-SE
    L' ← CÓPIA(L)
    movimento ← SORTEAR fechamento, remoção ou inclusão,
                com probabilidades 1/5, 1/5 e 3/5, respectivamente

    SE movimento = fechamento ENTÃO
        L'[j] ← ∅
    SENÃO SE movimento = remoção ENTÃO
        SE L[j] = ∅ ENTÃO
            RETORNAR FALHA
        FIM-SE
        i ← SORTEAR um cliente de L[j]
        L'[j] ← L[j] − {i}
    SENÃO
        i ← SORTEAR entre os clientes_ativos
        L'[j] ← (L[j] − VIZINHOS(G, i)) ∪ {i}
    FIM-SE

    SE L' = L ENTÃO
        RETORNAR FALHA
    FIM-SE
    RETORNAR L'
FIM-FUNÇÃO
```

## Avaliação de uma configuração por fluxo de custo mínimo

```text
FUNÇÃO AVALIAR_REDE(L)
    redes_testadas ← redes_testadas + 1
    VERIFICAR que não há pares conflitantes no mesmo conjunto L[j]
    y ← indicador das facilidades com L[j] não vazio
    SE algum cliente com demanda positiva não tiver ligação
       OU a soma das capacidades abertas for insuficiente ENTÃO
        RETORNAR FALHA
    FIM-SE

    MONTAR uma rede dirigida com uma origem e nós para facilidades e clientes
    oferta da origem ← soma das demandas
    demanda de cada cliente ← demanda da instância
    PARA cada facilidade aberta j FAÇA
        ADICIONAR arco origem → j com capacidade da facilidade e custo zero
        PARA cada cliente i em L[j] FAÇA
            ADICIONAR arco j → i com capacidade demanda[i]
                      e custo unitário custo_transporte[i,j]
        FIM-PARA
    FIM-PARA

    (X, custo_transporte) ← RESOLVER_FLUXO_DE_CUSTO_MÍNIMO(rede)
    SE o fluxo não atender toda a demanda ENTÃO
        RETORNAR FALHA
    FIM-SE

    Z ← custo_transporte + soma dos custos fixos das facilidades indicadas por y
    avaliações ← avaliações + 1
    SE Z < melhor_custo ENTÃO
        (melhor, melhor_custo) ← ((X, y, L), Z)
    FIM-SE
    REGISTRAR melhor_custo no histórico
    RETORNAR Z
FIM-FUNÇÃO
```
