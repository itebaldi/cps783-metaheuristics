# Iterated Local Search (ILS)

> Material de estudo — **Metaheurísticas em Otimização Combinatória**. Implementação do **problema da mochila 0-1** no mesmo formato do projeto de Simulated Annealing.

O **Iterated Local Search (ILS)**, ou **Busca Local Iterada**, é uma metaheurística que explora uma sequência de ótimos locais. A cada ciclo, aplica-se uma **perturbação** à solução corrente e executa-se novamente uma **busca local**. Um **critério de aceitação** decide se o novo ótimo local será a próxima solução corrente.

Esta organização modular está alinhada ao capítulo *Iterated Local Search*, de Lourenço, Martin e Stützle, e às aulas *Tema 5 — ILS*, da Profª Laura Bahiense. As decisões específicas para a mochila (vizinhança, reparo e números de iterações) são **escolhas desta implementação**, não requisitos impostos pelas fontes.

## 1. Intuição

A busca local pode parar em um ótimo local: nenhuma pequena alteração melhora a solução, embora existam soluções melhores em outra região. O ILS tenta escapar desse ponto sem descartar completamente o que já foi aprendido.

Uma perturbação **fraca demais** tende a levar de volta ao mesmo ótimo local; uma **forte demais** se aproxima de um reinício aleatório. Portanto, a intensidade deve ser calibrada.

## 2. Problema da mochila 0-1

Dados itens com pesos `peso_i`, valores `valor_i` e capacidade `W`, deseja-se:

\[
\max \sum_{i=1}^{n} valor_i x_i
\quad\text{sujeito a}\quad
\sum_{i=1}^{n} peso_i x_i \le W,\quad x_i\in\{0,1\}.
\]

Cada solução é um vetor binário: `1` indica item incluído e `0`, excluído. A função `calcular_valor_peso` devolve valor zero para uma solução inviável, por compatibilidade com o exercício de SA; o ILS **mantém as soluções viáveis** por construção e reparo.

## 3. Quatro componentes do ILS

| Componente | Implementação para mochila |
|---|---|
| Solução inicial | Embaralha os itens e insere os que cabem |
| Busca local | **Melhor melhora (steepest ascent)**, testando 1-flip e troca 1-por-1, sempre com capacidade respeitada |
| Perturbação | Inverte `intensidade_perturbacao` bits distintos e remove itens sorteados se precisar reparar o peso |
| Critério de aceitação | Aceita **somente melhora estrita** em relação à solução corrente |

A busca local combina *adicionar/remover um item* e *trocar um item selecionado por outro não selecionado*. A troca é importante: mesmo com a mochila cheia, pode haver uma substituição vantajosa.

A perturbação pode reduzir temporariamente o valor da solução, permitindo alcançar outra bacia de atração na próxima busca local. A aceitação conservadora faz com que a qualidade da solução corrente nunca diminua; isso simplifica o experimento, mas também pode limitar a diversificação.

## 4. Pseudocódigo

```text
s0       <- gerar_solucao_inicial(itens, W)
s        <- busca_local(s0)
s_melhor <- s

para k de 1 até max_iteracoes:
    s_perturbada <- perturbar_solucao(s, intensidade)
    s_candidata  <- busca_local(s_perturbada)

    se valor(s_candidata) > valor(s):
        s <- s_candidata

    se valor(s) > valor(s_melhor):
        s_melhor <- s

    registrar histórico

retornar s_melhor, histórico
```

O fluxo é **solução inicial → busca local → [perturbação → busca local → aceitação] repetidamente**.

## 5. Parâmetros

| Parâmetro | Papel | Valor no teste |
|---|---|---:|
| `max_iteracoes` | Número de ciclos de ILS | 250 |
| `intensidade_perturbacao` | Bits alterados *antes* do reparo | 4 |
| `random.seed(0)` | Reprodutibilidade da instância e da execução | 0 |
| `capacidade_mochila` | Limite de peso | Metade da soma dos pesos (divisão inteira) |

O ILS desta implementação **não tem temperatura nem fator de resfriamento**. Sua exploração é determinada principalmente pela perturbação e pela busca local.

## 6. Teste e comparação com Programação Dinâmica

O teste usa 20 itens aleatórios (pesos de 1 a 20, valores de 1 a 100) e calcula o ótimo por **Programação Dinâmica** (`programacao_dinamica`).

A qualidade do ILS é medida pelo *gap* percentual:

\[
Gap(\%) = 100\frac{Valor_{otimo}-Valor_{ILS}}{Valor_{otimo}}.
\]

O teste exige `gap <= 5` para **essa instância com essa semente**. Esse é um critério experimental do teste, **não uma garantia matemática do ILS**. Outros testes verificam viabilidade, tamanho do histórico, monotonicidade da melhor solução, reparo e validação de parâmetros.

**Comparação justa com SA:** SA realiza tentativas de vizinhos; cada ciclo do ILS pode avaliar muitos vizinhos dentro da busca local. Para comparar custo computacional, meça também tempo ou quantidade de avaliações da função objetivo, não só o número de iterações externas.

## 7. Executar

Na pasta que contém `iterated_local_search/` e `test_iterated_local_search_mochila.py`:

```bash
pip install pytest matplotlib
python -m pytest -v test_iterated_local_search_mochila.py
```

Exemplo Python:

```python
import random
from iterated_local_search import (
    gerar_instancia_aleatoria,
    programacao_dinamica,
    iterated_local_search_mochila,
)
from iterated_local_search.plot import plotar_iterated_local_search

random.seed(0)
itens = gerar_instancia_aleatoria(20, 20, 100)
capacidade = sum(item.peso for item in itens) // 2
otimo, _ = programacao_dinamica(itens, capacidade)
melhor, historico = iterated_local_search_mochila(itens, capacidade, 250, 4)
melhor_valor = historico["melhor_valor"][250]
print(
    f"Ótimo: {otimo} | ILS: {melhor_valor} | gap: {(otimo - melhor_valor) / otimo * 100:.2f}%"
)
plotar_iterated_local_search(historico, otimo, save=True)
```

Para produzir o gráfico durante o teste, mude `PLOT = False` para `True`.

## 8. Histórico retornado

`iterated_local_search_mochila` retorna `(melhor_solucao, output)`. Os dicionários em `output` são indexados de `0` a `max_iteracoes`:

- `valor_candidato`: valor depois da perturbação **e** da busca local.
- `valor_atual`: valor do incumbente após aplicar o critério de aceitação.
- `melhor_valor`: melhor valor encontrado até a iteração.
- `aceito`: `1` para melhora aceita; `0` para candidato rejeitado (iteração 0 é inicial).

## 9. Vantagens e limitações

**Vantagens:** simples, modular, admite busca local mais forte e não precisa de controle térmico. **Limitações:** não garante ótimo global; desempenho depende muito da vizinhança, intensidade da perturbação e aceitação. O critério de aceitação estrito pode estagnar em certas instâncias; aceitar empates ou pioras controladas são variantes possíveis, mas não fazem parte deste código.
