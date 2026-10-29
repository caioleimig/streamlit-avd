"""Funções que montam os gráficos Altair dos dois dashboards.

Cada função recebe um DataFrame já filtrado e devolve um gráfico pronto para st.altair_chart.
"""
import altair as alt
import pandas as pd

from src.config import COR_NEGATIVA, COR_POSITIVA, COR_REFERENCIA, ORDEM, VARIAVEIS, rotulo

CORES_RECOMPRA = alt.Scale(domain=ORDEM["pede_novamente"], range=[COR_POSITIVA, COR_NEGATIVA])
CORES_FEEDBACK = alt.Scale(domain=ORDEM["feedback"], range=[COR_POSITIVA, COR_NEGATIVA])

# Barras com cantos arredondados só na ponta e um respiro entre elas
BARRA = {"cornerRadiusEnd": 4}


# ---------------------------------------------------------------- Dashboard 1


def matriz_correlacao(df, variaveis, metodo):
    """Matriz de correlação em formato longo (uma linha por célula), com rótulos legíveis."""
    corr = df[variaveis].corr(method=metodo)
    corr.index = corr.columns = [rotulo(v) for v in variaveis]
    return corr.rename_axis(index="var_y", columns="var_x").stack(future_stack=True).rename("correlacao").reset_index()


def heatmap_correlacao(corr_longo, variaveis):
    ordem = [rotulo(v) for v in variaveis]
    base = alt.Chart(corr_longo).encode(
        x=alt.X("var_x:N", title=None, sort=ordem, axis=alt.Axis(labelAngle=-40, labelLimit=160, labelOverlap=False)),
        y=alt.Y("var_y:N", title=None, sort=ordem, axis=alt.Axis(labelLimit=160)),
    )
    celulas = base.mark_rect(stroke="white", strokeWidth=2).encode(
        # Divergente: azul (negativa) → cinza (zero) → laranja (positiva), escala fixa em [-1, 1]
        color=alt.Color(
            "correlacao:Q",
            title="Correlação",
            scale=alt.Scale(scheme="blueorange", domain=[-1, 1]),
        ),
        tooltip=[
            alt.Tooltip("var_y:N", title="Variável 1"),
            alt.Tooltip("var_x:N", title="Variável 2"),
            alt.Tooltip("correlacao:Q", title="Correlação", format=".2f"),
        ],
    )
    valores = base.mark_text(fontSize=14, fontWeight="bold").encode(
        text=alt.Text("correlacao:Q", format=".2f"),
        color=alt.condition("abs(datum.correlacao) > 0.6", alt.value("white"), alt.value("#2B2118")),
    )
    return (celulas + valores).properties(height=max(260, 70 * len(variaveis)))


def histograma(df, var, separar_por_recompra):
    """Distribuição de uma variável: histograma (contínua) ou barras por valor (discreta/ordinal)."""
    info = VARIAVEIS[var]
    if info["tipo"] == "continua":
        x = alt.X(f"{var}:Q", bin=alt.Bin(maxbins=20), title=info["rotulo"])
        colunas = [var]
    elif info["tipo"] == "discreta":
        x = alt.X(f"{var}:O", title=info["rotulo"], axis=alt.Axis(labelAngle=0))
        colunas = [var]
    else:
        coluna_rotulo = info["coluna_rotulo"]
        x = alt.X(
            f"{coluna_rotulo}:N",
            title=info["rotulo"].replace(" (ordinal)", ""),
            sort=ORDEM[coluna_rotulo],
            axis=alt.Axis(labelAngle=-35, labelLimit=120, labelOverlap=False),
        )
        colunas = [coluna_rotulo]

    grafico = alt.Chart(df[colunas + ["pede_novamente"]]).encode(
        x=x,
        y=alt.Y("count()", title="Clientes"),
    )
    if separar_por_recompra:
        return grafico.mark_bar(**BARRA, stroke="white", strokeWidth=1).encode(
            color=alt.Color("pede_novamente:N", title="Pediria novamente", scale=CORES_RECOMPRA),
            order=alt.Order("pede_novamente:N", sort="descending"),
            tooltip=[alt.Tooltip("pede_novamente:N", title="Pediria novamente"), alt.Tooltip("count()", title="Clientes")],
        ).properties(height=220)
    return grafico.mark_bar(**BARRA, color=COR_POSITIVA).encode(
        tooltip=[alt.Tooltip("count()", title="Clientes")],
    ).properties(height=220)


# ---------------------------------------------------------------- Dashboard 2


def _taxa_por_grupo(df, grupo):
    """Taxa de recompra (proporção de 'Sim') e número de clientes por categoria."""
    agrupado = (
        df.groupby(grupo, observed=True)["pede_novamente"]
        .agg(taxa=lambda s: (s == "Sim").mean(), clientes="size")
        .reset_index()
    )
    return agrupado


def recompra_por_faixa(df, selecao, taxa_media):
    """Barras clicáveis: a faixa etária escolhida filtra KPIs e os demais gráficos (via on_select)."""
    dados = _taxa_por_grupo(df, "faixa_etaria")
    base = alt.Chart(dados).encode(
        x=alt.X("faixa_etaria:N", title="Faixa etária", sort=ORDEM["faixa_etaria"], axis=alt.Axis(labelAngle=0)),
    )
    barras = (
        base.mark_bar(**BARRA, color=COR_POSITIVA, size=48)
        .encode(
            y=alt.Y("taxa:Q", title="Taxa de recompra", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
            opacity=alt.condition(selecao, alt.value(1), alt.value(0.3)),
            tooltip=[
                alt.Tooltip("faixa_etaria:N", title="Faixa etária"),
                alt.Tooltip("taxa:Q", title="Taxa de recompra", format=".1%"),
                alt.Tooltip("clientes:Q", title="Clientes"),
            ],
        )
        .add_params(selecao)
    )
    rotulos = base.mark_text(dy=-8, fontWeight="bold").encode(
        y="taxa:Q",
        text=alt.Text("taxa:Q", format=".0%"),
    )
    return (barras + rotulos + _linha_media(taxa_media)).properties(height=280)


def feedback_por_ocupacao(df):
    """Barras 100% empilhadas: proporção de feedback positivo/negativo em cada ocupação."""
    dados = df.groupby(["ocupacao", "feedback"]).size().rename("clientes").reset_index()
    dados["proporcao"] = dados["clientes"] / dados.groupby("ocupacao")["clientes"].transform("sum")
    return (
        alt.Chart(dados)
        .mark_bar(stroke="white", strokeWidth=2)
        .encode(
            y=alt.Y("ocupacao:N", title=None, sort=ORDEM["ocupacao"], axis=alt.Axis(minExtent=95, labelLimit=140)),
            x=alt.X("proporcao:Q", title="Proporção de clientes", stack="normalize", axis=alt.Axis(format="%")),
            color=alt.Color("feedback:N", title="Feedback", scale=CORES_FEEDBACK, legend=alt.Legend(orient="top")),
            order=alt.Order("feedback:N", sort="descending"),
            tooltip=[
                alt.Tooltip("ocupacao:N", title="Ocupação"),
                alt.Tooltip("feedback:N", title="Feedback"),
                alt.Tooltip("proporcao:Q", title="Proporção", format=".1%"),
                alt.Tooltip("clientes:Q", title="Clientes"),
            ],
        )
        .properties(height=280)
    )


def recompra_por_renda(df, taxa_media):
    dados = _taxa_por_grupo(df, "renda_mensal")
    base = alt.Chart(dados).encode(
        x=alt.X("renda_mensal:N", title="Renda mensal", sort=ORDEM["renda_mensal"], axis=alt.Axis(labelAngle=-25, labelLimit=130, labelOverlap=False)),
    )
    barras = base.mark_bar(**BARRA, color=COR_POSITIVA, size=40).encode(
        y=alt.Y("taxa:Q", title="Taxa de recompra", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
        tooltip=[
            alt.Tooltip("renda_mensal:N", title="Renda mensal"),
            alt.Tooltip("taxa:Q", title="Taxa de recompra", format=".1%"),
            alt.Tooltip("clientes:Q", title="Clientes"),
        ],
    )
    rotulos = base.mark_text(dy=-8, fontWeight="bold").encode(y="taxa:Q", text=alt.Text("taxa:Q", format=".0%"))
    return (barras + rotulos + _linha_media(taxa_media)).properties(height=280)


def recompra_por_tipo_cliente(df):
    """Contagem de clientes por tipo, dividida entre quem pediria novamente ou não."""
    return (
        alt.Chart(df[["tipo_cliente", "pede_novamente"]])
        .mark_bar(stroke="white", strokeWidth=2)
        .encode(
            y=alt.Y("tipo_cliente:N", title=None, sort=ORDEM["tipo_cliente"], axis=alt.Axis(minExtent=95)),
            x=alt.X("count()", title="Clientes"),
            color=alt.Color("pede_novamente:N", title="Pediria novamente", scale=CORES_RECOMPRA, legend=alt.Legend(orient="top")),
            order=alt.Order("pede_novamente:N", sort="descending"),
            tooltip=[
                alt.Tooltip("tipo_cliente:N", title="Tipo de cliente"),
                alt.Tooltip("pede_novamente:N", title="Pediria novamente"),
                alt.Tooltip("count()", title="Clientes"),
            ],
        )
        .properties(height=280)
    )


def _linha_media(taxa_media):
    """Linha tracejada de referência com a taxa de recompra média (valor exato no tooltip)."""
    referencia = pd.DataFrame({"taxa": [taxa_media], "rotulo": [f"Média: {taxa_media:.1%}"]})
    return alt.Chart(referencia).mark_rule(color=COR_REFERENCIA, strokeDash=[6, 4], strokeWidth=2).encode(
        y="taxa:Q", tooltip=[alt.Tooltip("rotulo:N", title="Referência")]
    )
