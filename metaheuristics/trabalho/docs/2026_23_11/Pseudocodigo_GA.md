# Pseudocódigo do Algoritmo Genético (GA)

Cada cromossomo contém uma ordem dos clientes e, para cada cliente, uma ordem de preferência das facilidades. O decodificador usa essas ordens para montar a matriz de alocação. O indivíduo de menor custo é preservado a cada geração por elitismo.

N é o tamanho da população, p_mutação é a taxa de mutação e B é o orçamento de avaliações viáveis.

## Algoritmo principal

```text
ALGORITMO GA(instância, N, p_mutação, B)
    população ← lista vazia
    melhor ← NENHUMA
    melhor_custo ← +∞
    avaliações ← 0
    histórico ← lista vazia
    tentativas ← 0
    limite_tentativas ← 10 × B

    ENQUANTO população tiver menos de N indivíduos
             E avaliações < B E tentativas < limite_tentativas FAÇA
        indivíduo ← AVALIAR_CROMOSSOMO(GERAR_CROMOSSOMO())
        SE indivíduo ≠ FALHA ENTÃO
            INSERIR indivíduo na população
        FIM-SE
    FIM-ENQUANTO

    SE população estiver vazia ENTÃO
        RETORNAR FALHA
    FIM-SE

    ENQUANTO avaliações < B E tentativas < limite_tentativas FAÇA
        nova_população ← lista contendo o indivíduo de menor custo da população

        ENQUANTO nova_população tiver menos de N indivíduos
                 E avaliações < B E tentativas < limite_tentativas FAÇA
            SE UNIFORME(0,1) < 0,10 ENTÃO
                filho ← GERAR_CROMOSSOMO()
            SENÃO
                pai₁ ← TORNEIO(população)
                pai₂ ← TORNEIO(população)
                filho ← CRUZAR(pai₁, pai₂)
                MUTAR(filho, p_mutação)
            FIM-SE

            indivíduo ← AVALIAR_CROMOSSOMO(filho)
            SE indivíduo ≠ FALHA ENTÃO
                INSERIR indivíduo na nova_população
            FIM-SE
        FIM-ENQUANTO
        população ← nova_população
    FIM-ENQUANTO

    RETORNAR melhor e histórico
FIM-ALGORITMO
```

## Geração, seleção, cruzamento e mutação

```text
FUNÇÃO GERAR_CROMOSSOMO()
    ordem ← EMBARALHAR todos os clientes
    PARA cada cliente i FAÇA
        COM PROBABILIDADE 0,75
            preferências[i] ← ordenar facilidades pelo custo unitário para i
                               após adicionar um ruído uniforme entre 0 e 30
        SENÃO
            preferências[i] ← EMBARALHAR todas as facilidades
        FIM-ESCOLHA
    FIM-PARA
    RETORNAR (ordem, preferências)
FIM-FUNÇÃO

FUNÇÃO TORNEIO(população)
    SORTEAR dois indivíduos, com reposição
    RETORNAR o cromossomo do indivíduo de menor custo
FIM-FUNÇÃO

FUNÇÃO CRUZAR(pai₁, pai₂)
    corte ← SORTEAR uma posição interna na ordem, se houver
    filho.ordem ← prefixo de pai₁ até o corte
    COMPLETAR a ordem com os clientes ainda ausentes na ordem de pai₂
    PARA cada cliente i FAÇA
        filho.preferências[i] ← SORTEAR toda a lista de i de um dos dois pais
    FIM-PARA
    RETORNAR filho
FIM-FUNÇÃO

PROCEDIMENTO MUTAR(filho, p_mutação)
    COM PROBABILIDADE p_mutação, se houver pelo menos dois clientes,
        TROCAR duas posições na ordem dos clientes
    COM PROBABILIDADE p_mutação, se houver pelo menos duas facilidades,
        SORTEAR um cliente e TROCAR duas posições na lista de preferências dele
FIM-PROCEDIMENTO
```

## Decodificação e avaliação

```text
FUNÇÃO AVALIAR_CROMOSSOMO(cromossomo)
    tentativas ← tentativas + 1
    X ← matriz de alocação com zeros
    residual ← capacidades de todas as facilidades

    PARA cada cliente i na ordem do cromossomo FAÇA
        falta ← demanda[i]
        ENQUANTO falta > 0 FAÇA
            j ← primeira facilidade na preferência de i que tem capacidade
                 residual positiva e não atende um cliente conflitante com i
            SE não existir tal facilidade ENTÃO
                RETORNAR FALHA
            FIM-SE
            q ← MÍNIMO(falta, residual[j])
            X[i,j] ← X[i,j] + q
            residual[j] ← residual[j] − q
            falta ← falta − q
        FIM-ENQUANTO
    FIM-PARA

    y ← indicador das facilidades com fluxo positivo em X
    SE (X, y) for inviável ENTÃO
        RETORNAR FALHA
    FIM-SE

    Z ← custo de abertura + custo de transporte
    avaliações ← avaliações + 1
    SE Z < melhor_custo ENTÃO
        (melhor, melhor_custo) ← ((X, y), Z)
    FIM-SE
    REGISTRAR melhor_custo no histórico
    RETORNAR (Z, cromossomo)
FIM-FUNÇÃO
```
