import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Protocol

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MaxNLocator

from metaheuristics.utils.plot import COR_ATUAL
from metaheuristics.utils.plot import COR_CANDIDATO
from metaheuristics.utils.plot import COR_EIXO
from metaheuristics.utils.plot import COR_FORA
from metaheuristics.utils.plot import COR_MELHOR
from metaheuristics.utils.plot import COR_MELHORA
from metaheuristics.utils.plot import COR_NOVO_MELHOR
from metaheuristics.utils.plot import COR_PIORA
from metaheuristics.utils.plot import COR_SUPERFICIE
from metaheuristics.utils.plot import COR_TEXTO
from metaheuristics.utils.plot import COR_TEXTO_SECUNDARIO
from metaheuristics.utils.plot import ESTILO
from metaheuristics.utils.plot import PASTA_PLOTS
from metaheuristics.utils.plot import finalizar
from metaheuristics.utils.plot import milhar
from metaheuristics.utils.plot import novas_melhores

# alocacao[cliente, facilidade]: uma linha por cliente, uma coluna por facilidade
Matriz = npt.NDArray[np.int_]
# abertas[facilidade], capacidades
Vetor = npt.NDArray[np.int_]
# (alocacao, abertas, custo) de uma solução
Solucao = tuple[Matriz, Vetor, int]


class Instancia(Protocol):
    """O que o depurador usa da instância.

    A ``Instance`` do notebook atende a essa interface.
    """

    capacidades: Vetor
    custos_fixos: Vetor
    demandas: Vetor
    custos_transporte: Matriz


COR_ETAPA = "#0b0b0b"
COR_FACILIDADE = COR_PIORA
COR_ENVIO = COR_MELHORA
PALETA_CLIENTES = [plt.get_cmap("tab20")(indice) for indice in range(20)]
# Segmentos mais estreitos que essa fração da maior capacidade ficam sem rótulo
LARGURA_MINIMA_ROTULO = 0.08
# Espessura da aresta do maior envio no grafo; as outras são proporcionais
LARGURA_MAXIMA_ENVIO = 6.0
# Posições tentadas para o rótulo de cada envio ao longo da aresta, de 0 (facilidade)
# a 1 (cliente). Começa perto do cliente, que recebe poucas arestas, e recua se o
# lugar já tiver outro rótulo.
POSICOES_ROTULO_ENVIO = (0.84, 0.7, 0.56, 0.42)
# Distâncias mínimas entre os centros de dois rótulos, em unidades do eixo do grafo
DISTANCIA_ROTULO_X = 0.2
DISTANCIA_ROTULO_Y = 0.035


def _cor(cliente: int) -> tuple[float, float, float, float]:
    return PALETA_CLIENTES[cliente % len(PALETA_CLIENTES)]


def _prefixo(metodo: str) -> str:
    """Nome de arquivo a partir do método: "GRASP + SA" vira "grasp_sa"."""
    sem_acento = (
        unicodedata.normalize("NFKD", metodo).encode("ascii", "ignore").decode()
    )
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_")


def _maiuscula(texto: str) -> str:
    return texto[:1].upper() + texto[1:]


def _lugar_do_rotulo(
    altura_facilidade: float,
    altura_cliente: float,
    colocados: list[tuple[float, float]],
) -> tuple[float, float]:
    """Primeiro ponto da aresta, a partir do cliente, longe dos rótulos já colocados."""
    for x in POSICOES_ROTULO_ENVIO:
        y = altura_facilidade + x * (altura_cliente - altura_facilidade)
        if all(
            abs(x - outro_x) >= DISTANCIA_ROTULO_X
            or abs(y - outro_y) >= DISTANCIA_ROTULO_Y
            for outro_x, outro_y in colocados
        ):
            return x, y
    x = POSICOES_ROTULO_ENVIO[0]
    return x, altura_facilidade + x * (altura_cliente - altura_facilidade)


class Debug:
    """Desenha uma figura por iteração de um método do CFLP.

    Passe uma instância como ``debug`` para um dos métodos do notebook. O método
    chama ``iniciar`` com o próprio nome, a unidade de iteração (reinício, tentativa
    ou geração) e o que são as duas soluções de cada iteração. À esquerda, a figura
    mostra a segunda solução (a melhorada) de dois jeitos. Em cima, uma barra por
    facilidade aberta, dividida nos clientes que ela atende, com a capacidade livre no
    fim. Embaixo, o grafo entre facilidades e clientes: cada envio é uma aresta verde,
    mais grossa quanto maior a quantidade. Cada cliente tem sempre a mesma cor. À
    direita fica o mini-histórico do custo total, com as duas soluções. Desenha a primeira
    iteração, as múltiplas de ``a_cada`` e a última bem-sucedida, até ``limite``
    figuras. O depurador nunca sorteia números, então os resultados são os mesmos com
    e sem ele.

    Parameters
    ----------
    show : bool, default False
        Se mostra cada figura (no notebook).
    save : bool, default False
        Se salva cada figura como PNG.
    a_cada : int or None, default None
        Desenha a cada ``a_cada`` iterações. Com ``None``, desenha só a última
        iteração bem-sucedida.
    limite : int, default 100
        Número máximo de figuras.
    pasta : str or pathlib.Path, optional
        Pasta das figuras; por padrão, ``plots/debug/<data-hora>/``.
    """

    def __init__(
        self,
        show: bool = False,
        save: bool = False,
        a_cada: int | None = None,
        limite: int = 100,
        pasta: str | Path | None = None,
    ) -> None:
        if a_cada is not None and a_cada < 1:
            raise ValueError("a_cada deve ser pelo menos 1, ou None.")
        if not (show or save):
            raise ValueError(
                "Ligue show e/ou save: sem eles o depurador não gera nada."
            )
        self.show = show
        self.save = save
        self.a_cada = a_cada
        self.limite = limite
        self.pasta = (
            Path(pasta)
            if pasta is not None
            else PASTA_PLOTS / "debug" / f"{datetime.now():%Y%m%d_%H%M%S}"
        )
        self.capacidades: Vetor = np.zeros(0, dtype=int)
        self.custos_fixos: Vetor = np.zeros(0, dtype=int)
        self.demandas: Vetor = np.zeros(0, dtype=int)
        self.custos_transporte: Matriz = np.zeros((0, 0), dtype=int)
        self.metodo = ""
        self.unidade = ""
        self.rotulos = ("", "")
        self.total: int | None = None
        self._texto_avaliacoes = ""
        self.figuras = 0
        self._avisou = False
        self.ativo = False
        self.iteracao = 0
        self._primeira_iteracao: int | None = None
        self.iteracoes: list[int] = []
        self.custos_primeira: list[int] = []
        self.custos_segunda: list[int] = []
        self.custos_melhores: list[int] = []
        self._ultima: tuple[Solucao, Solucao, Solucao] | None = None
        self._ultima_desenhada: int | None = None

    def iniciar(
        self,
        instance: Instancia,
        metodo: str,
        unidade: str,
        rotulos: tuple[str, str],
        total: int | None,
    ) -> None:
        """Configura o desenho para um método.

        ``unidade`` é o nome de cada iteração ("reinício", "tentativa", "geração"),
        ``rotulos`` diz o que são as duas alocações desenhadas, e ``total`` é o número
        de iterações, ou ``None`` quando não se sabe de antemão. A ``instance`` dá as
        capacidades, os custos e as demandas desenhados nos painéis.
        """
        self.capacidades = instance.capacidades
        self.custos_fixos = instance.custos_fixos
        self.demandas = instance.demandas
        self.custos_transporte = instance.custos_transporte
        self.metodo = metodo
        self.unidade = unidade
        self.rotulos = rotulos
        self.total = total
        self._texto_avaliacoes = ""

    def registrar_avaliacoes(self, realizadas: int, limite: int | None) -> None:
        """Atualiza a contagem acumulada exibida no cabeçalho da figura."""
        contagem = milhar(realizadas)
        if limite is not None:
            contagem += f"/{milhar(limite)}"
        self._texto_avaliacoes = f" · soluções avaliadas ({contagem})"

    def inicio_iteracao(self, iteracao: int) -> None:
        """Marca o início de uma iteração e decide se ela será desenhada."""
        if self._primeira_iteracao is None:
            self._primeira_iteracao = iteracao
        self.iteracao = iteracao
        self.ativo = self.a_cada is not None and (
            iteracao in (self._primeira_iteracao, self.total)
            or iteracao % self.a_cada == 0
        )

    def fim_iteracao(
        self, primeira: Solucao, segunda: Solucao, melhor: Solucao
    ) -> None:
        """Registra o resultado da iteração e desenha a figura, se ela estiver ativa."""
        self.iteracoes.append(self.iteracao)
        self.custos_primeira.append(primeira[2])
        self.custos_segunda.append(segunda[2])
        self.custos_melhores.append(melhor[2])
        self._ultima = (primeira, segunda, melhor)
        if self._pode_desenhar():
            self._desenhar(primeira, segunda, melhor)

    def fim(self) -> None:
        """Desenha a última iteração bem-sucedida, se ela ainda não foi desenhada."""
        if self._ultima is None or self.iteracoes[-1] == self._ultima_desenhada:
            return
        if self.figuras >= self.limite:
            return
        self.iteracao = self.iteracoes[-1]
        self._desenhar(*self._ultima)

    def _pode_desenhar(self) -> bool:
        if not self.ativo:
            return False
        if self.figuras >= self.limite:
            if not self._avisou:
                print(
                    f"Depurador: limite de {self.limite} figuras atingido; "
                    "as próximas iterações não serão desenhadas."
                )
                self._avisou = True
            return False
        return True

    def _desenhar(
        self, primeira: Solucao, segunda: Solucao, melhor: Solucao
    ) -> None:
        rotulo_primeira, rotulo_segunda = self.rotulos
        de_total = f" de {self.total}" if self.total is not None else ""
        texto = (
            f"{rotulo_primeira} {milhar(primeira[2])} → {rotulo_segunda} "
            f"{milhar(segunda[2])} · melhor {milhar(melhor[2])}"
        )
        with plt.style.context(ESTILO):
            fig = plt.figure(figsize=(15, 9.5), layout="constrained")
            grade = fig.add_gridspec(
                2, 2, width_ratios=(1.15, 1), height_ratios=(1, 2.4)
            )
            ax_barras = fig.add_subplot(grade[0, 0])
            ax_grafo = fig.add_subplot(grade[1, 0])
            ax_historico = fig.add_subplot(grade[:, 1])
            fig.suptitle(
                f"{self.metodo} · {self.unidade} {self.iteracao}{de_total}"
                f"{self._texto_avaliacoes}\n{texto}",
                x=0.01,
                ha="left",
                fontsize=11.5,
                fontweight="bold",
            )
            self._alocacao(ax_barras, segunda, f"1. {_maiuscula(rotulo_segunda)}")
            ax_barras.set_xlabel("unidades enviadas a cada cliente →")
            self._grafo(ax_grafo, segunda, f"2. Grafo: {rotulo_segunda}")
            self._historico(ax_historico)
            self._legenda(fig)
            finalizar(
                fig,
                f"{_prefixo(self.metodo)}_{self.iteracao:05d}",
                self.show,
                self.save,
                self.pasta,
            )
            plt.close(fig)
        self.figuras += 1
        self._ultima_desenhada = self.iteracao

    def _alocacao(self, ax: Axes, solucao: Solucao, titulo: str) -> None:
        alocacao, abertas, custo = solucao
        maior_capacidade = int(self.capacidades.max())
        facilidades_abertas = np.flatnonzero(abertas)
        for posicao, facilidade in enumerate(facilidades_abertas):
            usado = 0
            for cliente in np.flatnonzero(alocacao[:, facilidade]):
                quantidade = int(alocacao[cliente, facilidade])
                ax.barh(
                    posicao,
                    quantidade,
                    left=usado,
                    height=0.7,
                    color=_cor(int(cliente)),
                    edgecolor=COR_SUPERFICIE,
                    linewidth=1,
                )
                if quantidade >= LARGURA_MINIMA_ROTULO * maior_capacidade:
                    ax.text(
                        usado + quantidade / 2,
                        posicao,
                        f"C{cliente + 1} {quantidade}",
                        ha="center",
                        va="center",
                        fontsize=7.5,
                        color=COR_TEXTO,
                    )
                usado += quantidade
            capacidade = int(self.capacidades[facilidade])
            ax.barh(
                posicao, capacidade - usado, left=usado, height=0.7, color=COR_FORA
            )
            ax.text(
                capacidade + 0.01 * maior_capacidade,
                posicao,
                f"{usado}/{capacidade}",
                va="center",
                fontsize=8,
                color=COR_TEXTO_SECUNDARIO,
            )
        ax.set_yticks(
            range(len(facilidades_abertas)),
            [f"F{facilidade + 1}" for facilidade in facilidades_abertas],
        )
        ax.invert_yaxis()
        ax.set_xlim(0, maior_capacidade * 1.12)
        ax.grid(axis="y", visible=False)
        ax.set_title(f"{titulo} ({milhar(custo)})", loc="left", fontsize=11)

    def _grafo(self, ax: Axes, solucao: Solucao, titulo: str) -> None:
        """Facilidades à esquerda, clientes à direita e uma aresta por envio."""
        alocacao, abertas, custo = solucao
        n_clientes, n_facilidades = alocacao.shape
        altura_cliente = np.linspace(1, 0, n_clientes)
        altura_facilidade = (
            np.linspace(0.92, 0.08, n_facilidades)
            if n_facilidades > 1
            else np.array([0.5])
        )
        maior_envio = int(alocacao.max())
        rotulos_colocados: list[tuple[float, float]] = []

        for facilidade in np.flatnonzero(abertas):
            for cliente in range(n_clientes):
                pontas = (
                    [0, 1],
                    [altura_facilidade[facilidade], altura_cliente[cliente]],
                )
                quantidade = int(alocacao[cliente, facilidade])
                if quantidade == 0:
                    ax.plot(
                        *pontas,
                        color=COR_EIXO,
                        linestyle="--",
                        linewidth=0.5,
                        alpha=0.6,
                    )
                    continue
                ax.plot(
                    *pontas,
                    color=COR_ENVIO,
                    linewidth=1 + LARGURA_MAXIMA_ENVIO * quantidade / maior_envio,
                    solid_capstyle="butt",
                    zorder=3,
                )
                custo_envio = int(self.custos_transporte[cliente, facilidade])
                x_rotulo, y_rotulo = _lugar_do_rotulo(
                    altura_facilidade[facilidade],
                    altura_cliente[cliente],
                    rotulos_colocados,
                )
                rotulos_colocados.append((x_rotulo, y_rotulo))
                ax.text(
                    x_rotulo,
                    y_rotulo,
                    f"{quantidade}u · ${milhar(custo_envio * quantidade)}",
                    ha="center",
                    va="center",
                    fontsize=6.5,
                    color=COR_TEXTO,
                    zorder=4,
                    bbox={
                        "boxstyle": "round,pad=0.15",
                        "facecolor": COR_SUPERFICIE,
                        "edgecolor": "none",
                        "alpha": 0.85,
                    },
                )

        for facilidade in range(n_facilidades):
            altura = altura_facilidade[facilidade]
            capacidade = int(self.capacidades[facilidade])
            if abertas[facilidade]:
                usado = int(alocacao[:, facilidade].sum())
                ax.scatter(
                    0, altura, marker="s", s=260, color=COR_FACILIDADE, zorder=5
                )
                texto = (
                    f"F{facilidade + 1}\n{usado}/{capacidade}\n"
                    f"fixo ${milhar(int(self.custos_fixos[facilidade]))}"
                )
            else:
                ax.scatter(
                    0,
                    altura,
                    marker="s",
                    s=260,
                    facecolor=COR_SUPERFICIE,
                    edgecolor=COR_TEXTO_SECUNDARIO,
                    linewidth=1.5,
                    zorder=5,
                )
                texto = f"F{facilidade + 1}\nfechada"
            ax.text(-0.07, altura, texto, ha="right", va="center", fontsize=8.5)

        for cliente in range(n_clientes):
            ax.scatter(
                1,
                altura_cliente[cliente],
                s=170,
                color=_cor(cliente),
                edgecolor=COR_TEXTO,
                linewidth=0.6,
                zorder=5,
            )
            ax.text(
                1.06,
                altura_cliente[cliente],
                f"C{cliente + 1} · {int(self.demandas[cliente])} un.",
                ha="left",
                va="center",
                fontsize=8.5,
            )

        ax.set_xlim(-0.42, 1.38)
        ax.set_ylim(-0.06, 1.06)
        ax.axis("off")
        ax.set_title(f"{titulo} ({milhar(custo)})", loc="left", fontsize=11)

    def _historico(self, ax: Axes) -> None:
        ax.plot(
            self.iteracoes,
            self.custos_primeira,
            color=COR_CANDIDATO,
            linewidth=0.8,
        )
        ax.plot(self.iteracoes, self.custos_segunda, color=COR_ATUAL, linewidth=1.2)
        ax.step(
            self.iteracoes,
            self.custos_melhores,
            where="post",
            color=COR_MELHOR,
            linewidth=1.8,
        )
        ax.scatter(
            *novas_melhores(self.iteracoes, self.custos_melhores),
            s=28,
            color=COR_NOVO_MELHOR,
            zorder=5,
        )
        ax.scatter(
            [self.iteracoes[-1]],
            [self.custos_segunda[-1]],
            s=60,
            color=COR_ETAPA,
            zorder=6,
        )
        if self.total is not None:
            ax.set_xlim(0, self.total + 1)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.xaxis.set_major_formatter(FuncFormatter(milhar))
        ax.yaxis.set_major_formatter(FuncFormatter(milhar))
        ax.set_xlabel(self.unidade)
        ax.set_ylabel("custo total")
        ax.set_title("3. Mini-histórico do custo total", loc="left", fontsize=11)

    def _legenda(self, fig: Figure) -> None:
        def ponto(cor: str, rotulo: str, tamanho: float = 7) -> Line2D:
            return Line2D(
                [],
                [],
                marker="o",
                linestyle="none",
                color=cor,
                markersize=tamanho,
                label=rotulo,
            )

        rotulo_primeira, rotulo_segunda = self.rotulos
        itens = [
            Patch(color=_cor(0), label="cliente (a mesma cor nos dois painéis)"),
            Patch(color=COR_FORA, label="capacidade livre"),
            Line2D(
                [],
                [],
                marker="s",
                linestyle="none",
                color=COR_FACILIDADE,
                markersize=8,
                label="facilidade aberta",
            ),
            Line2D(
                [],
                [],
                marker="s",
                linestyle="none",
                markerfacecolor=COR_SUPERFICIE,
                markeredgecolor=COR_TEXTO_SECUNDARIO,
                markersize=8,
                label="facilidade fechada",
            ),
            Line2D(
                [],
                [],
                color=COR_ENVIO,
                linewidth=3,
                label="envio (espessura = quantidade)",
            ),
            Line2D(
                [],
                [],
                color=COR_EIXO,
                linestyle="--",
                linewidth=0.7,
                label="ligação sem envio",
            ),
            Line2D(
                [], [], color=COR_CANDIDATO, linewidth=0.8, label=rotulo_primeira
            ),
            Line2D([], [], color=COR_ATUAL, linewidth=1.2, label=rotulo_segunda),
            Line2D(
                [], [], color=COR_MELHOR, linewidth=1.8, label="melhor até agora"
            ),
            ponto(COR_NOVO_MELHOR, "nova melhor solução"),
            ponto(COR_ETAPA, f"{self.unidade} desta figura", tamanho=8),
        ]
        fig.legend(handles=itens, loc="outside lower center", ncol=6, fontsize=8.5)
