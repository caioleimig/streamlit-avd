# [IA] Claude Code – sintaxe dos gráficos Altair
import altair as alt
import pandas as pd

from src.config import cor_negativa, cor_positiva, cor_referencia, ordem, rotulo, variaveis

cores_recompra = alt.Scale(domain=ordem["pede_novamente"], range=[cor_positiva, cor_negativa])
cores_feedback = alt.Scale(domain=ordem["feedback"], range=[cor_positiva, cor_negativa])
barra = {"cornerRadiusEnd": 4}


def matriz_correlacao(df, vars_, metodo):
    # formato longo: uma linha por célula do heatmap
    corr = df[vars_].corr(method=metodo)
    corr.index = corr.columns = [rotulo(v) for v in vars_]
    return corr.rename_axis(index="var_y", columns="var_x").stack(future_stack=True).rename("correlacao").reset_index()


def heatmap_correlacao(corr, vars_):
    eixo = [rotulo(v) for v in vars_]
    base = alt.Chart(corr).encode(
        x=alt.X("var_x:N", title=None, sort=eixo, axis=alt.Axis(labelAngle=-40, labelLimit=160, labelOverlap=False)),
        y=alt.Y("var_y:N", title=None, sort=eixo, axis=alt.Axis(labelLimit=160)),
    )
    celulas = base.mark_rect(stroke="white", strokeWidth=2).encode(
        color=alt.Color("correlacao:Q", title="Correlação", scale=alt.Scale(scheme="blueorange", domain=[-1, 1])),
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
    return (celulas + valores).properties(height=max(260, 70 * len(vars_)))


def histograma(df, var, separar):
    info = variaveis[var]
    coluna = info.get("coluna_rotulo", var)
    if info["tipo"] == "continua":
        x = alt.X(f"{var}:Q", bin=alt.Bin(maxbins=20), title=info["rotulo"])
    elif info["tipo"] == "discreta":
        x = alt.X(f"{var}:O", title=info["rotulo"], axis=alt.Axis(labelAngle=0))
    else:
        # ordinal: mostra a categoria original, não o código 0-4
        x = alt.X(
            f"{coluna}:N",
            title=info["rotulo"].replace(" (ordinal)", ""),
            sort=ordem[coluna],
            axis=alt.Axis(labelAngle=-35, labelLimit=120, labelOverlap=False),
        )
    grafico = alt.Chart(df[[coluna, "pede_novamente"]]).encode(x=x, y=alt.Y("count()", title="Clientes"))
    if separar:
        grafico = grafico.mark_bar(**barra, stroke="white", strokeWidth=1).encode(
            color=alt.Color("pede_novamente:N", title="Pediria novamente", scale=cores_recompra),
            order=alt.Order("pede_novamente:N", sort="descending"),
            tooltip=[alt.Tooltip("pede_novamente:N", title="Pediria novamente"), alt.Tooltip("count()", title="Clientes")],
        )
    else:
        grafico = grafico.mark_bar(**barra, color=cor_positiva).encode(tooltip=[alt.Tooltip("count()", title="Clientes")])
    return grafico.properties(height=220)


def taxa_recompra(df, grupo, titulo, media, eixo, largura, selecao=None):
    dados = (
        df.groupby(grupo, observed=True)["pede_novamente"]
        .agg(taxa=lambda s: (s == "Sim").mean(), clientes="size")
        .reset_index()
    )
    base = alt.Chart(dados).encode(x=alt.X(f"{grupo}:N", title=titulo, sort=ordem[grupo], axis=eixo))
    barras = base.mark_bar(**barra, color=cor_positiva, size=largura).encode(
        y=alt.Y("taxa:Q", title="Taxa de recompra", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
        tooltip=[
            alt.Tooltip(f"{grupo}:N", title=titulo),
            alt.Tooltip("taxa:Q", title="Taxa de recompra", format=".1%"),
            alt.Tooltip("clientes:Q", title="Clientes"),
        ],
    )
    if selecao is not None:
        barras = barras.encode(opacity=alt.condition(selecao, alt.value(1), alt.value(0.3))).add_params(selecao)
    rotulos = base.mark_text(dy=-8, fontWeight="bold").encode(y="taxa:Q", text=alt.Text("taxa:Q", format=".0%"))
    linha = pd.DataFrame({"taxa": [media], "rotulo": [f"Média: {media:.1%}"]})
    referencia = alt.Chart(linha).mark_rule(color=cor_referencia, strokeDash=[6, 4], strokeWidth=2).encode(
        y="taxa:Q", tooltip=[alt.Tooltip("rotulo:N", title="Referência")]
    )
    return (barras + rotulos + referencia).properties(height=280)


def feedback_por_ocupacao(df):
    dados = df.groupby(["ocupacao", "feedback"]).size().rename("clientes").reset_index()
    dados["proporcao"] = dados["clientes"] / dados.groupby("ocupacao")["clientes"].transform("sum")
    return (
        alt.Chart(dados)
        .mark_bar(stroke="white", strokeWidth=2)
        .encode(
            y=alt.Y("ocupacao:N", title=None, sort=ordem["ocupacao"], axis=alt.Axis(minExtent=95, labelLimit=140)),
            x=alt.X("proporcao:Q", title="Proporção de clientes", stack="normalize", axis=alt.Axis(format="%")),
            color=alt.Color("feedback:N", title="Feedback", scale=cores_feedback, legend=alt.Legend(orient="top")),
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


def recompra_por_tipo_cliente(df):
    return (
        alt.Chart(df[["tipo_cliente", "pede_novamente"]])
        .mark_bar(stroke="white", strokeWidth=2)
        .encode(
            y=alt.Y("tipo_cliente:N", title=None, sort=ordem["tipo_cliente"], axis=alt.Axis(minExtent=95)),
            x=alt.X("count()", title="Clientes"),
            color=alt.Color("pede_novamente:N", title="Pediria novamente", scale=cores_recompra, legend=alt.Legend(orient="top")),
            order=alt.Order("pede_novamente:N", sort="descending"),
            tooltip=[
                alt.Tooltip("tipo_cliente:N", title="Tipo de cliente"),
                alt.Tooltip("pede_novamente:N", title="Pediria novamente"),
                alt.Tooltip("count()", title="Clientes"),
            ],
        )
        .properties(height=280)
    )
