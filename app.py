import altair as alt
import streamlit as st
from scipy import stats

from src import graficos
from src.config import ordem, rotulo, variaveis
from src.data_loader import load_data

st.set_page_config(page_title="Delivery de comida: clientes e satisfação", page_icon=":material/delivery_dining:", layout="wide")

df = load_data()
total = len(df)


def num(valor, casas=1):
    return f"{valor:.{casas}f}".replace(".", ",")


def pct(valor):
    return num(valor * 100) + "%"


def taxa(d, coluna="pede_novamente", valor="Sim"):
    return (d[coluna] == valor).mean()


def delta(diferenca, unidade, colorido=True):
    # diferença ~0 fica cinza e sem seta
    neutro = round(diferenca, 1) == 0
    return {
        "delta": f"{diferenca:+.1f}".replace(".", ",") + f" {unidade}",
        "delta_color": "normal" if colorido and not neutro else "off",
        "delta_arrow": "off" if neutro else "auto",
        "delta_description": "vs. base completa",
    }


def forca(r):
    return next(nome for limite, nome in [(0.1, "desprezível"), (0.3, "fraca"), (0.5, "moderada"), (0.7, "forte"), (2, "muito forte")] if abs(r) < limite)


def limpar(prefixo):
    for chave in [k for k in st.session_state if str(k).startswith(prefixo)]:
        del st.session_state[chave]


st.title("Delivery de comida: quem são os clientes e o que os faz voltar")
st.caption(
    f"{total} clientes de um app de delivery em Bangalore (Índia), após remover duplicatas · "
    "Fonte: [Online Food Ordering Dataset (Kaggle)](https://www.kaggle.com/datasets/srisyra02/online-food-ordering-dataset)"
)

# sidebar: filtros do dashboard 1
with st.sidebar:
    st.header(":material/tune: Filtros do Dashboard 1")
    st.caption("Controlam a aba **Correlação e distribuição**. O Dashboard 2 tem filtros próprios no topo da aba.")
    selecionadas = st.multiselect(
        "Variáveis quantitativas", options=list(variaveis), default=list(variaveis), format_func=rotulo, key="d1_variaveis",
        help="Renda e escolaridade entram como códigos ordinais (0 = menor nível, 4 = maior).",
    )
    metodo = st.segmented_control(
        "Método de correlação", options=["spearman", "pearson", "kendall"], default="spearman",
        format_func=str.capitalize, required=True, key="d1_metodo",
        help="Spearman e Kendall medem relação monotônica e servem para variáveis ordinais. "
        "Pearson mede relação linear entre variáveis contínuas.",
    )
    separar = st.toggle("Separar distribuição por recompra", key="d1_separar", help="Pinta os histogramas por 'pediria novamente' (Sim/Não).")
    st.subheader("Intervalos", divider="orange")
    sem_outliers = st.toggle(
        "Remover outliers (regra do IQR)", key="d1_outliers",
        help="Exclui valores fora de [Q1 − 1,5·IQR, Q3 + 1,5·IQR] nas variáveis selecionadas, "
        "a mesma regra usada na EDA (em idade, isso remove quem tem mais de 30,5 anos).",
    )
    intervalos = {}
    for var in selecionadas:
        lo, hi = int(df[var].min()), int(df[var].max())
        intervalos[var] = st.slider(rotulo(var), lo, hi, (lo, hi), key=f"d1_intervalo_{var}")
    st.button(":material/restart_alt: Restaurar filtros", on_click=limpar, args=("d1_",), width="stretch")

df_d1 = df
for var, (inicio, fim) in intervalos.items():
    df_d1 = df_d1[df_d1[var].between(inicio, fim)]
if sem_outliers:
    for var in selecionadas:
        q1, q3 = df[var].quantile([0.25, 0.75])
        df_d1 = df_d1[df_d1[var].between(q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1))]

aba1, aba2 = st.tabs([":material/scatter_plot: Dashboard 1 · Correlação e distribuição", ":material/monitoring: Dashboard 2 · KPIs de satisfação"])

with aba1:
    st.caption(f"**{len(df_d1)}** de {total} clientes dentro dos filtros ({pct(len(df_d1) / total)} da base).")
    col_corr, col_dist = st.columns([1, 1.25], gap="large")

    with col_corr, st.container(border=True):
        st.subheader(f"Correlação ({metodo.capitalize()})")
        if len(selecionadas) < 2:
            st.info("Selecione pelo menos 2 variáveis na barra lateral para calcular a correlação.", icon=":material/info:")
        elif len(df_d1) < 10:
            st.warning("Poucos clientes dentro dos filtros (menos de 10) para uma correlação confiável. Amplie os intervalos.", icon=":material/warning:")
        else:
            # variável constante no recorte não tem correlação definida
            constantes = [v for v in selecionadas if df_d1[v].nunique() < 2]
            usadas = [v for v in selecionadas if v not in constantes]
            if constantes:
                st.warning("Sem variação no recorte atual (correlação indefinida): " + ", ".join(map(rotulo, constantes)), icon=":material/warning:")
            if len(usadas) >= 2:
                corr = graficos.matriz_correlacao(df_d1, usadas, metodo)
                st.altair_chart(graficos.heatmap_correlacao(corr, usadas), width="stretch", alt=f"Mapa de calor da correlação de {metodo} entre as variáveis selecionadas")
                pares = corr[corr["var_x"] < corr["var_y"]].dropna()
                par = pares.loc[pares["correlacao"].abs().idxmax()]
                a = next(v for v in usadas if rotulo(v) == par["var_x"])
                b = next(v for v in usadas if rotulo(v) == par["var_y"])
                teste = {"spearman": stats.spearmanr, "pearson": stats.pearsonr, "kendall": stats.kendalltau}[metodo]
                p = teste(df_d1[a], df_d1[b])[1]
                st.markdown(
                    f"**Par mais forte:** {par['var_x']} × {par['var_y']}, r = {num(par['correlacao'], 2)} "
                    f"(correlação {forca(par['correlacao'])}, {'estatisticamente significativa' if p < 0.05 else 'não significativa'}, p = {p:.2g})."
                )
                if metodo == "pearson" and any(variaveis[v]["tipo"] == "ordinal" for v in usadas):
                    st.caption(":material/info: Pearson supõe distâncias iguais entre os valores. Para renda e escolaridade (ordinais), prefira Spearman ou Kendall.")

    with col_dist, st.container(border=True):
        st.subheader("Distribuição")
        if not selecionadas:
            st.info("Selecione pelo menos 1 variável na barra lateral para ver a distribuição.", icon=":material/info:")
        elif df_d1.empty:
            st.warning("Nenhum cliente dentro dos intervalos escolhidos.", icon=":material/warning:")
        else:
            for i in range(0, len(selecionadas), 2):
                for coluna, var in zip(st.columns(2), selecionadas[i : i + 2]):
                    coluna.altair_chart(graficos.histograma(df_d1, var, separar), width="stretch", alt=f"Distribuição da variável {rotulo(var)}")

    with st.expander(":material/table: Resumo estatístico e dados filtrados"):
        if selecionadas and not df_d1.empty:
            resumo = df_d1[selecionadas].describe().T
            resumo["assimetria"] = df_d1[selecionadas].skew()
            st.dataframe(resumo.rename(index=rotulo).round(2), alt="Estatísticas descritivas das variáveis selecionadas")
        st.dataframe(df_d1, hide_index=True, alt="Tabela com os clientes dentro dos filtros")

with aba2:
    with st.container(border=True):
        f1, f2, f3, f4 = st.columns([1, 1.6, 1.2, 1.3], vertical_alignment="bottom")
        generos = f1.pills("Gênero", ordem["genero"], selection_mode="multi", default=ordem["genero"], key="d2_genero")
        ocupacoes = f2.multiselect("Ocupação", ordem["ocupacao"], default=ordem["ocupacao"], key="d2_ocupacao")
        tipos = f3.pills("Tipo de cliente", ordem["tipo_cliente"], selection_mode="multi", default=ordem["tipo_cliente"], key="d2_tipo")
        lo, hi = int(df["idade"].min()), int(df["idade"].max())
        idades = f4.slider("Idade", lo, hi, (lo, hi), key="d2_idade")

    df_d2 = df[df["genero"].isin(generos) & df["ocupacao"].isin(ocupacoes) & df["tipo_cliente"].isin(tipos) & df["idade"].between(*idades)]

    # seleção cruzada: o clique no gráfico de faixa etária fica no session_state e é lido antes dos kpis
    estado = st.session_state.get("d2_grafico_faixa")
    faixas = [item["faixa_etaria"] for item in (estado["selection"].get("faixa", []) if estado else [])]
    recorte = df_d2[df_d2["faixa_etaria"].isin(faixas)] if faixas else df_d2
    if faixas:
        st.caption(f":material/filter_alt: Recorte pela faixa etária **{', '.join(faixas)}** (clique em uma área vazia do gráfico de faixa etária para limpar).")

    k1, k2, k3, k4 = st.columns(4)
    if recorte.empty:
        for coluna, nome in zip([k1, k2, k3, k4], ["Clientes no recorte", "Taxa de recompra", "Feedback positivo", "Idade média"]):
            coluna.metric(nome, "—", border=True)
    else:
        recompra, feedback, idade = taxa(recorte), taxa(recorte, "feedback", "Positivo"), recorte["idade"].mean()
        k1.metric("Clientes no recorte", len(recorte), delta=f"{pct(len(recorte) / total)} da base", delta_color="off", delta_arrow="off",
                  border=True, help="Quantos clientes atendem aos filtros e à faixa etária selecionada.")
        k2.metric("Taxa de recompra", pct(recompra), **delta((recompra - taxa(df)) * 100, "p.p."), border=True,
                  help="Percentual de clientes que pediriam novamente pelo app (Output = Sim).")
        k3.metric("Feedback positivo", pct(feedback), **delta((feedback - taxa(df, "feedback", "Positivo")) * 100, "p.p."), border=True,
                  help="Percentual de clientes que deram avaliação positiva ao serviço.")
        # idade maior ou menor não é "boa" nem "ruim": delta sempre cinza
        k4.metric("Idade média", f"{num(idade)} anos", **delta(idade - df["idade"].mean(), "anos", colorido=False), border=True,
                  help="Idade média dos clientes no recorte. Na EDA, quem pediria novamente é ~1,6 ano mais novo.")

    if df_d2.empty:
        st.warning("Nenhum cliente atende aos filtros escolhidos. Amplie a seleção.", icon=":material/warning:")
        st.button(":material/restart_alt: Restaurar filtros", on_click=limpar, args=("d2_",), key="restaurar_d2")
    else:
        def quadro(coluna, titulo, legenda, grafico, descricao):
            with coluna, st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.caption(legenda)
                if recorte.empty:
                    st.info("Sem clientes no recorte selecionado.", icon=":material/info:")
                else:
                    st.altair_chart(grafico(), width="stretch", alt=descricao)

        g1, g2 = st.columns(2, gap="medium")
        with g1, st.container(border=True):
            st.markdown("**Taxa de recompra por faixa etária**")
            st.caption("Clique em uma barra (shift + clique para várias) para filtrar os KPIs e os outros gráficos. A linha tracejada é a média dos filtros.")
            st.altair_chart(
                graficos.taxa_recompra(df_d2, "faixa_etaria", "Faixa etária", taxa(df_d2), alt.Axis(labelAngle=0), 48, alt.selection_point(name="faixa", fields=["faixa_etaria"])),
                key="d2_grafico_faixa", on_select="rerun", width="stretch",
                alt="Gráfico de barras da taxa de recompra por faixa etária, com seleção por clique",
            )
        quadro(g2, "Feedback por ocupação", "Proporção de avaliações positivas e negativas em cada ocupação.",
               lambda: graficos.feedback_por_ocupacao(recorte), "Barras empilhadas com a proporção de feedback positivo e negativo por ocupação")
        g3, g4 = st.columns(2, gap="medium")
        quadro(g3, "Taxa de recompra por renda mensal", "A linha tracejada é a média do recorte atual.",
               lambda: graficos.taxa_recompra(recorte, "renda_mensal", "Renda mensal", taxa(recorte), alt.Axis(labelAngle=-25, labelLimit=130, labelOverlap=False), 40),
               "Gráfico de barras da taxa de recompra por faixa de renda mensal")
        quadro(g4, "Recompra por tipo de cliente", "Quantos clientes de cada tipo pediriam novamente.",
               lambda: graficos.recompra_por_tipo_cliente(recorte), "Barras empilhadas com o número de clientes por tipo, divididos entre Sim e Não")

    with st.expander(":material/help: Como ler este dashboard"):
        st.markdown(
            f"""
- **Taxa de recompra** = percentual de clientes com `Output = Yes`. O dataset não documenta formalmente essa coluna;
  seguimos a leitura mais comum dele, de que indica se o cliente **pediria novamente** pelo app.
- Os **deltas** dos KPIs comparam o recorte atual com a base completa ({total} clientes).
- Grupos pequenos (ex.: *Do lar*, *Novo*) têm poucas pessoas: passe o mouse nas barras para ver quantos clientes há em cada uma.
- Todos os clientes do tipo **Novo** têm família de 1 pessoa, padrão que a EDA apontou como possível artefato do dataset.
"""
        )
