import altair as alt
import pandas as pd
import streamlit as st
from scipy import stats

from src import graficos
from src.config import ORDEM, VARIAVEIS, VARIAVEIS_PADRAO, rotulo
from src.data_loader import load_data

st.set_page_config(
    page_title="Delivery de comida: clientes e satisfação",
    page_icon=":material/delivery_dining:",
    layout="wide",
)

df = load_data()
TOTAL_CLIENTES = len(df)


def pct(valor):
    """Formata proporção no padrão brasileiro: 0.761 -> '76,1%'."""
    return f"{valor * 100:.1f}%".replace(".", ",")


def decimal(valor, casas=1):
    return f"{valor:.{casas}f}".replace(".", ",")


def delta_vs_base(diferenca, unidade):
    """Delta do st.metric com sinal e vírgula decimal; diferença ~0 fica cinza e sem seta."""
    texto = f"{diferenca:+.1f}".replace(".", ",") + f" {unidade}"
    neutro = round(diferenca, 1) == 0
    return {"delta": texto, "delta_color": "off" if neutro else "normal", "delta_arrow": "off" if neutro else "auto"}


def forca_correlacao(r):
    r = abs(r)
    if r < 0.1:
        return "desprezível"
    if r < 0.3:
        return "fraca"
    if r < 0.5:
        return "moderada"
    if r < 0.7:
        return "forte"
    return "muito forte"


def limpar_filtros_d1():
    for chave in [k for k in st.session_state if str(k).startswith("d1_")]:
        del st.session_state[chave]


def limpar_filtros_d2():
    for chave in [k for k in st.session_state if str(k).startswith("d2_")]:
        del st.session_state[chave]


st.title("Delivery de comida: quem são os clientes e o que os faz voltar")
st.caption(
    f"{TOTAL_CLIENTES} clientes de um app de delivery em Bangalore (Índia), após remover duplicatas · "
    "Fonte: [Online Food Ordering Dataset (Kaggle)](https://www.kaggle.com/datasets/srisyra02/online-food-ordering-dataset)"
)

# ============================================================ Sidebar: filtros do Dashboard 1
with st.sidebar:
    st.header(":material/tune: Filtros do Dashboard 1")
    st.caption("Controlam a aba **Correlação e distribuição**. O Dashboard 2 tem filtros próprios no topo da aba.")

    variaveis = st.multiselect(
        "Variáveis quantitativas",
        options=list(VARIAVEIS),
        default=VARIAVEIS_PADRAO,
        format_func=rotulo,
        key="d1_variaveis",
        help="Renda e escolaridade entram como códigos ordinais (0 = menor nível, 4 = maior).",
    )

    metodo = st.segmented_control(
        "Método de correlação",
        options=["spearman", "pearson", "kendall"],
        default="spearman",
        format_func=str.capitalize,
        required=True,
        key="d1_metodo",
        help="Spearman e Kendall medem relação monotônica e servem para variáveis ordinais. "
        "Pearson mede relação linear entre variáveis contínuas.",
    )

    separar_por_recompra = st.toggle(
        "Separar distribuição por recompra",
        value=False,
        key="d1_separar",
        help="Pinta os histogramas por 'pediria novamente' (Sim/Não).",
    )

    st.subheader("Intervalos", divider="orange")
    remover_outliers = st.toggle(
        "Remover outliers (regra do IQR)",
        value=False,
        key="d1_outliers",
        help="Exclui valores fora de [Q1 − 1,5·IQR, Q3 + 1,5·IQR] nas variáveis selecionadas, "
        "a mesma regra usada na EDA (em idade, isso remove quem tem mais de 30,5 anos).",
    )

    # Um slider de intervalo por variável selecionada, com os limites reais do dado
    intervalos = {}
    for var in variaveis:
        info = VARIAVEIS[var]
        if info["tipo"] == "continua" and df[var].dtype.kind == "f":
            minimo, maximo, passo, formato = float(df[var].min()), float(df[var].max()), 0.001, "%.3f"
        else:
            minimo, maximo, passo, formato = int(df[var].min()), int(df[var].max()), 1, "%d"
        intervalos[var] = st.slider(
            info["rotulo"],
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            step=passo,
            format=formato,
            key=f"d1_intervalo_{var}",
        )

    st.button(":material/restart_alt: Restaurar filtros", on_click=limpar_filtros_d1, width="stretch")

# Aplica os filtros do Dashboard 1
df_d1 = df
for var, (inicio, fim) in intervalos.items():
    df_d1 = df_d1[df_d1[var].between(inicio, fim)]
if remover_outliers:
    for var in variaveis:
        q1, q3 = df[var].quantile([0.25, 0.75])
        iqr = q3 - q1
        df_d1 = df_d1[df_d1[var].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)]

aba1, aba2 = st.tabs(
    [":material/scatter_plot: Dashboard 1 · Correlação e distribuição", ":material/monitoring: Dashboard 2 · KPIs de satisfação"]
)

# ============================================================ Dashboard 1
with aba1:
    st.caption(
        f"**{len(df_d1)}** de {TOTAL_CLIENTES} clientes dentro dos filtros "
        f"({pct(len(df_d1) / TOTAL_CLIENTES)} da base)."
    )

    col_correlacao, col_distribuicao = st.columns([1, 1.25], gap="large")

    with col_correlacao:
        with st.container(border=True):
            st.subheader(f"Correlação ({metodo.capitalize()})")

            if len(variaveis) < 2:
                st.info("Selecione pelo menos 2 variáveis na barra lateral para calcular a correlação.", icon=":material/info:")
            elif len(df_d1) < 10:
                st.warning("Poucos clientes dentro dos filtros (menos de 10) para uma correlação confiável. Amplie os intervalos.", icon=":material/warning:")
            else:
                # Variável sem variação dentro do filtro não tem correlação definida
                constantes = [v for v in variaveis if df_d1[v].nunique() < 2]
                usadas = [v for v in variaveis if v not in constantes]
                if constantes:
                    st.warning(
                        "Sem variação no recorte atual (correlação indefinida): " + ", ".join(rotulo(v) for v in constantes),
                        icon=":material/warning:",
                    )
                if len(usadas) >= 2:
                    corr = graficos.matriz_correlacao(df_d1, usadas, metodo)
                    st.altair_chart(
                        graficos.heatmap_correlacao(corr, usadas),
                        width="stretch",
                        alt=f"Mapa de calor da correlação de {metodo} entre as variáveis selecionadas",
                    )

                    # Destaque do par com a correlação mais forte (fora da diagonal), com teste de significância
                    pares = corr[corr["var_x"] < corr["var_y"]].dropna()
                    par = pares.loc[pares["correlacao"].abs().idxmax()]
                    var_a = next(v for v in usadas if rotulo(v) == par["var_x"])
                    var_b = next(v for v in usadas if rotulo(v) == par["var_y"])
                    teste = {"spearman": stats.spearmanr, "pearson": stats.pearsonr, "kendall": stats.kendalltau}[metodo]
                    p_valor = teste(df_d1[var_a], df_d1[var_b])[1]
                    significancia = "estatisticamente significativa" if p_valor < 0.05 else "não significativa"
                    st.markdown(
                        f"**Par mais forte:** {par['var_x']} × {par['var_y']}, "
                        f"r = {decimal(par['correlacao'], 2)} (correlação {forca_correlacao(par['correlacao'])}, "
                        f"{significancia}, p = {p_valor:.2g})."
                    )
                    if metodo == "pearson" and any(VARIAVEIS[v]["tipo"] == "ordinal" for v in usadas):
                        st.caption(
                            ":material/info: Pearson supõe distâncias iguais entre os valores. "
                            "Para renda e escolaridade (ordinais), prefira Spearman ou Kendall."
                        )

    with col_distribuicao:
        with st.container(border=True):
            st.subheader("Distribuição")

            if not variaveis:
                st.info("Selecione pelo menos 1 variável na barra lateral para ver a distribuição.", icon=":material/info:")
            elif df_d1.empty:
                st.warning("Nenhum cliente dentro dos intervalos escolhidos.", icon=":material/warning:")
            else:
                # Um gráfico por variável, em grade de 2 colunas (cada um com a própria escala)
                for inicio in range(0, len(variaveis), 2):
                    colunas = st.columns(2)
                    for coluna, var in zip(colunas, variaveis[inicio : inicio + 2]):
                        with coluna:
                            st.altair_chart(
                                graficos.histograma(df_d1, var, separar_por_recompra),
                                width="stretch",
                                alt=f"Distribuição da variável {rotulo(var)}",
                            )

    with st.expander(":material/table: Resumo estatístico e dados filtrados"):
        if variaveis and not df_d1.empty:
            resumo = df_d1[variaveis].describe().T.rename(index=rotulo)
            resumo["assimetria"] = df_d1[variaveis].skew().rename(index=rotulo)
            st.dataframe(resumo.round(2), alt="Estatísticas descritivas das variáveis selecionadas")
        st.dataframe(df_d1, hide_index=True, alt="Tabela com os clientes dentro dos filtros")

# ============================================================ Dashboard 2
with aba2:
    # Barra de filtros no topo da aba (padrão "filtro superior" do Power BI)
    with st.container(border=True):
        f1, f2, f3, f4 = st.columns([1, 1.6, 1.2, 1.3], vertical_alignment="bottom")
        with f1:
            generos = st.pills("Gênero", ORDEM["genero"], selection_mode="multi", default=ORDEM["genero"], key="d2_genero")
        with f2:
            ocupacoes = st.multiselect("Ocupação", ORDEM["ocupacao"], default=ORDEM["ocupacao"], key="d2_ocupacao")
        with f3:
            tipos = st.pills(
                "Tipo de cliente", ORDEM["tipo_cliente"], selection_mode="multi", default=ORDEM["tipo_cliente"], key="d2_tipo"
            )
        with f4:
            idade_min, idade_max = int(df["idade"].min()), int(df["idade"].max())
            faixa_idade = st.slider("Idade", idade_min, idade_max, (idade_min, idade_max), key="d2_idade")

    df_d2 = df[
        df["genero"].isin(generos)
        & df["ocupacao"].isin(ocupacoes)
        & df["tipo_cliente"].isin(tipos)
        & df["idade"].between(*faixa_idade)
    ]

    # Seleção cruzada: o clique numa barra do gráfico de faixa etária fica salvo no session_state
    # (key="d2_grafico_faixa"). Lemos aqui, antes dos KPIs, para que métricas e gráficos usem o mesmo recorte.
    estado_grafico = st.session_state.get("d2_grafico_faixa")
    itens = estado_grafico["selection"].get("faixa", []) if estado_grafico else []
    faixas_selecionadas = [item["faixa_etaria"] for item in itens]
    df_recorte = df_d2[df_d2["faixa_etaria"].isin(faixas_selecionadas)] if faixas_selecionadas else df_d2

    if faixas_selecionadas:
        st.caption(
            f":material/filter_alt: Recorte pela faixa etária **{', '.join(faixas_selecionadas)}** "
            "(clique em uma área vazia do gráfico de faixa etária para limpar)."
        )

    # Referência para os deltas: a base completa, sem nenhum filtro
    base_recompra = (df["pede_novamente"] == "Sim").mean()
    base_feedback = (df["feedback"] == "Positivo").mean()
    base_idade = df["idade"].mean()

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    if df_recorte.empty:
        for coluna, nome in zip([k1, k2, k3, k4], ["Clientes no recorte", "Taxa de recompra", "Feedback positivo", "Idade média"]):
            coluna.metric(nome, "—", border=True)
    else:
        taxa_recompra = (df_recorte["pede_novamente"] == "Sim").mean()
        taxa_feedback = (df_recorte["feedback"] == "Positivo").mean()
        idade_media = df_recorte["idade"].mean()

        k1.metric(
            "Clientes no recorte",
            len(df_recorte),
            delta=f"{pct(len(df_recorte) / TOTAL_CLIENTES)} da base",
            delta_color="off",
            delta_arrow="off",
            border=True,
            help="Quantos clientes atendem aos filtros e à faixa etária selecionada.",
        )
        k2.metric(
            "Taxa de recompra",
            pct(taxa_recompra),
            **delta_vs_base((taxa_recompra - base_recompra) * 100, "p.p."),
            delta_description="vs. base completa",
            border=True,
            help="Percentual de clientes que pediriam novamente pelo app (Output = Sim).",
        )
        k3.metric(
            "Feedback positivo",
            pct(taxa_feedback),
            **delta_vs_base((taxa_feedback - base_feedback) * 100, "p.p."),
            delta_description="vs. base completa",
            border=True,
            help="Percentual de clientes que deram avaliação positiva ao serviço.",
        )
        k4.metric(
            "Idade média",
            f"{decimal(idade_media)} anos",
            # Idade mais alta ou mais baixa não é "bom" nem "ruim": delta sempre cinza
            **{**delta_vs_base(idade_media - base_idade, "anos"), "delta_color": "off"},
            delta_description="vs. base completa",
            border=True,
            help="Idade média dos clientes no recorte. Na EDA, quem pediria novamente é ~1,6 ano mais novo.",
        )

    if df_d2.empty:
        st.warning("Nenhum cliente atende aos filtros escolhidos. Amplie a seleção.", icon=":material/warning:")
        st.button(":material/restart_alt: Restaurar filtros", on_click=limpar_filtros_d2, key="restaurar_d2")
    else:
        taxa_recorte = (df_recorte["pede_novamente"] == "Sim").mean() if not df_recorte.empty else 0.0
        taxa_filtros = (df_d2["pede_novamente"] == "Sim").mean()

        g1, g2 = st.columns(2, gap="medium")
        with g1:
            with st.container(border=True):
                st.markdown("**Taxa de recompra por faixa etária**")
                st.caption(
                    "Clique em uma barra (shift + clique para várias) para filtrar os KPIs e os outros gráficos. "
                    "A linha tracejada é a média dos filtros."
                )
                selecao = alt.selection_point(name="faixa", fields=["faixa_etaria"])
                st.altair_chart(
                    graficos.recompra_por_faixa(df_d2, selecao, taxa_filtros),
                    key="d2_grafico_faixa",
                    on_select="rerun",
                    width="stretch",
                    alt="Gráfico de barras da taxa de recompra por faixa etária, com seleção por clique",
                )
        with g2:
            with st.container(border=True):
                st.markdown("**Feedback por ocupação**")
                st.caption("Proporção de avaliações positivas e negativas em cada ocupação.")
                if df_recorte.empty:
                    st.info("Sem clientes no recorte selecionado.", icon=":material/info:")
                else:
                    st.altair_chart(
                        graficos.feedback_por_ocupacao(df_recorte),
                        width="stretch",
                        alt="Barras empilhadas com a proporção de feedback positivo e negativo por ocupação",
                    )

        g3, g4 = st.columns(2, gap="medium")
        with g3:
            with st.container(border=True):
                st.markdown("**Taxa de recompra por renda mensal**")
                st.caption("A linha tracejada é a média do recorte atual.")
                if df_recorte.empty:
                    st.info("Sem clientes no recorte selecionado.", icon=":material/info:")
                else:
                    st.altair_chart(
                        graficos.recompra_por_renda(df_recorte, taxa_recorte),
                        width="stretch",
                        alt="Gráfico de barras da taxa de recompra por faixa de renda mensal",
                    )
        with g4:
            with st.container(border=True):
                st.markdown("**Recompra por tipo de cliente**")
                st.caption("Quantos clientes de cada tipo pediriam novamente.")
                if df_recorte.empty:
                    st.info("Sem clientes no recorte selecionado.", icon=":material/info:")
                else:
                    st.altair_chart(
                        graficos.recompra_por_tipo_cliente(df_recorte),
                        width="stretch",
                        alt="Barras empilhadas com o número de clientes por tipo, divididos entre Sim e Não",
                    )

    with st.expander(":material/help: Como ler este dashboard"):
        st.markdown(
            """
- **Taxa de recompra** = percentual de clientes com `Output = Yes`. O dataset não documenta formalmente essa coluna;
  seguimos a leitura mais comum dele, de que indica se o cliente **pediria novamente** pelo app.
- Os **deltas** dos KPIs comparam o recorte atual com a base completa (285 clientes).
- Grupos pequenos (ex.: *Do lar*, *Novo*) têm poucas pessoas: passe o mouse nas barras para ver quantos clientes há em cada uma.
- Todos os clientes do tipo **Novo** têm família de 1 pessoa, padrão que a EDA apontou como possível artefato do dataset.
            """
        )
