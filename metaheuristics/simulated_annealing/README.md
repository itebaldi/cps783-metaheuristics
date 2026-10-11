# Simulated Annealing (SA)

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**.

O **Simulated Annealing (SA)**, ou **Recozimento Simulado**, é uma metaheurística de busca local probabilística inspirada no recozimento físico de materiais. Foi introduzida para otimização combinatória por **Kirkpatrick, Gelatt e Vecchi (1983)**. Sua característica central é **aceitar ocasionalmente movimentos que pioram a função objetivo**, permitindo escapar de mínimos locais.

## 1. Intuição

Em uma busca local de **minimização**, normalmente só aceitamos um vizinho se seu custo for menor. Isso pode levar a um **mínimo local**: nenhuma mudança permitida melhora a solução, embora existam soluções melhores em outras regiões do espaço de busca.

O SA começa com uma temperatura alta, favorecendo a **exploração**. À medida que a temperatura diminui, torna-se menos provável aceitar pioras, favorecendo a **intensificação** da busca.

| Analogia física | Otimização |
|---|---|
| Estado do material | Solução candidata |
| Energia | Valor da função objetivo |
| Rearranjo atômico | Movimento para solução vizinha |
| Temperatura | Controle da aceitação de pioras |
| Resfriamento | Redução progressiva da aleatoriedade |

## 2. Elementos do problema

Para minimizar uma função `f(s)`:

- **Solução corrente (`s`)**: estado a partir do qual o próximo vizinho é gerado.
- **Vizinhança (`N(s)`)**: conjunto de soluções acessíveis por um movimento definido para o problema.
- **Função objetivo (`f`)**: atribui o custo a uma solução.
- **Melhor solução (`s_best`)**: melhor estado encontrado ao longo da execução, guardado separadamente do estado corrente.
- **Temperatura (`T`)**: controla a probabilidade de aceitar pioras.

Dado um vizinho `s'`, calcule:

$$
\Delta = f(s') - f(s)
$$

A **regra de Metropolis** (para minimização) é:

$$
P(\text{aceitar }s') =
\begin{cases}
1, & \Delta \leq 0 \\
\exp(-\Delta/T), & \Delta > 0
\end{cases}
$$

Para `Δ > 0`, sorteia-se `u ~ Uniforme(0,1)`. O movimento é aceito quando `u < exp(-Δ/T)`.

**Exemplo:** se o custo passa de 100 para 105, então `Δ = 5`. Com `T = 10`, a probabilidade de aceitar a piora é `exp(-0,5) ≈ 0,6065` (**60,65%**). Com `T = 1`, cai para aproximadamente **0,67%**.

## 3. Pseudocódigo

```text
entrada: solução inicial s; f; gerador de vizinhos N;
         temperatura inicial T0; temperatura final Tf;
         fator de resfriamento α; iterações por temperatura SAmax

s_best ← s
T ← T0

enquanto T > Tf:
    repetir SAmax vezes:
        s' ← vizinho aleatório de s
        Δ ← f(s') - f(s)

        se Δ ≤ 0 ou aleatório(0, 1) < exp(-Δ / T):
            s ← s'

        se f(s) < f(s_best):
            s_best ← s

    T ← α × T

retornar s_best
```

A temperatura é mantida durante várias tentativas de movimento (*loop interno de Metropolis*) e atualizada no *loop externo*.

## 4. Principais parâmetros

| Parâmetro | Função | Efeito prático |
|---|---|---|
| `T0` | Temperatura inicial | Valores altos favorecem aceitar pioras no começo |
| `Tf` | Temperatura final | Define um limite de parada |
| `α` | Fator de resfriamento geométrico (`0 < α < 1`) | Quanto mais próximo de 1, mais lento o resfriamento |
| `SAmax` | Tentativas por temperatura | Controla o esforço de exploração em cada nível térmico |
| `N(s)` | Estrutura de vizinhança | Determina quais transformações são possíveis |
| `f(s)` | Função objetivo | Define a qualidade das soluções |

### Resfriamento geométrico

$$
T_{k+1}=\alpha T_k,\quad 0<\alpha<1
$$

Por exemplo, com `T0 = 100` e `α = 0,9`, as temperaturas seguintes são `90`, `81`, `72,9` etc. Na prática, `T0`, `Tf`, `α` e `SAmax` precisam ser calibrados para a escala dos custos e o tamanho do problema. Outra alternativa de parada é interromper quando a taxa de aceitação ou a melhoria se torna muito baixa.

## 5. O que Hajek (1988) demonstrou?

Em **_Cooling Schedules for Optimal Annealing_**, Bruce Hajek analisa condições matemáticas para que o estado corrente do SA convirja **em probabilidade** para o conjunto de mínimos globais.

### Profundidade de um mínimo local

A profundidade de um mínimo local não global é a **menor barreira de custo acima do mínimo** que precisa ser ultrapassada, por uma sequência de movimentos permitidos, para alcançar uma solução de custo menor.

Exemplo: partindo de um mínimo de custo `20`, se o melhor caminho para alcançar uma solução melhor precisa passar por custo máximo `35`, a profundidade é `35 - 20 = 15`. **Não** é a diferença entre o custo local e o custo global.

Seja `d*` a **maior profundidade entre os mínimos locais não globais**.

### Condição de convergência

Sob as hipóteses do artigo (entre elas: espaço finito, conectividade/irredutibilidade e *weak reversibility* da estrutura de vizinhança), a condição central é:

$$
\sum_{k=1}^{\infty}\exp(-d^*/T_k)=\infty
$$

Para a agenda logarítmica (indexada aqui por `k ≥ 1`):

$$
T_k=\frac{c}{\log(k+1)}
$$

a convergência em probabilidade ao conjunto de mínimos globais ocorre **se, e somente se**:

$$
\boxed{c\geq d^*}
$$

Isso decorre de `exp(-d*/T_k) = (k+1)^(-d*/c)` e do critério de divergência da série-p.

**Interpretação:** a temperatura deve diminuir suficientemente devagar para que o algoritmo continue tendo oportunidades de escapar inclusive das bacias locais mais profundas.

**Limite importante:** essa é uma garantia **assintótica**, não uma promessa de encontrar o ótimo em um número finito de iterações. Em aplicações reais, `d*` costuma ser desconhecido e o resfriamento logarítmico pode ser lento demais. Por isso, agendas geométricas são frequentes em implementações práticas, embora não ofereçam automaticamente a mesma garantia teórica.

## 6. Exemplo de aplicação: layout de vagas de garagem

Um possível uso em problemas arquitetônicos é otimizar um layout de estacionamento:

- **Solução:** posição e orientação de vagas, fileiras e corredores.
- **Vizinhos:** deslocar uma vaga, rotacionar uma fileira, ajustar um corredor ou reorganizar parte do layout.
- **Objetivo:** maximizar vagas válidas e minimizar interferências, circulação inadequada e violações de restrições.

Uma função de minimização ilustrativa seria:

$$
f(s)=-10\,N_{\text{vagas válidas}}+100\,C_{\text{circulação}}+500\,I_{\text{interferências}}
$$

Os coeficientes são **exemplos**, não pesos recomendados. Algumas restrições (segurança, normas, acessibilidade) podem precisar ser tratadas como **rígidas**, e não apenas penalizadas.

O SA pode aceitar temporariamente um layout com menos vagas para abrir espaço à reorganização e, depois, alcançar uma configuração melhor.

> **Observação:** reconhecer paredes, estacas e outros elementos a partir de DWG/DXF é principalmente um problema de interpretação/classificação geométrica. O SA pode auxiliar na escolha entre hipóteses conflitantes, mas não realiza esse reconhecimento sozinho.

## 7. Vantagens e limitações

**Vantagens**
- Implementação relativamente simples.
- Capacidade de escapar de mínimos locais.
- Flexibilidade para problemas combinatórios variados.
- Não requer derivadas da função objetivo.

**Limitações**
- Desempenho sensível à vizinhança e ao resfriamento.
- Pode exigir muitas avaliações de custo.
- Não garante o ótimo global em uma execução finita comum.
- Não é necessariamente a melhor escolha quando existem métodos exatos eficientes para o problema.

## 8. Questões para revisão

1. Por que aceitar soluções piores pode melhorar o resultado final?
2. Qual é a diferença entre `s` e `s_best`?
3. O que acontece com `exp(-Δ/T)` quando `T` diminui?
4. Por que a definição da vizinhança altera a dificuldade de escapar de mínimos locais?
5. Qual é a diferença entre o resfriamento geométrico e o logarítmico?
6. O que significa a profundidade `d*` no teorema de Hajek?
7. Por que convergência em probabilidade não significa garantia em tempo finito?

## 9. Referências

- **Bahiense, Laura.** *Metaheurísticas em Otimização Combinatória — Tema 4: Simulated Annealing (SA).* Material de aula, CPS783.
- **Metropolis, N. et al.** (1953). *Equation of State Calculations by Fast Computing Machines*. Journal of Chemical Physics, 21, 1087–1092. DOI: [10.1063/1.1699114](https://doi.org/10.1063/1.1699114).
- **Kirkpatrick, S.; Gelatt, C. D.; Vecchi, M. P.** (1983). *Optimization by Simulated Annealing*. Science, 220(4598), 671–680.
- **Hajek, B.** (1988). *Cooling Schedules for Optimal Annealing*. Mathematics of Operations Research, 13(2), 311–329.

---

**Resumo em uma frase:** o SA alterna exploração e intensificação controlando probabilisticamente a aceitação de pioras; a teoria de Hajek explica por que escapar das barreiras de custo mais profundas exige um resfriamento suficientemente lento.
