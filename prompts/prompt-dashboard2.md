# Prompt usado: Dashboard 2 (Aulas 22 e 23)

## Contexto

Mesmo projeto do Dashboard 1 (ver [prompt-esqueleto-dashboard1.md](prompt-esqueleto-dashboard1.md)). Agora preciso do **Dashboard 2: KPIs**, numa segunda aba (`st.tabs`) do mesmo `app.py`. Público-alvo: equipe de produto/marketing de um app de delivery.

## Entrada

- Rascunho: `entregas/rascunho-dashboard2.png` (anexado).
- Métricas já planejadas e testadas no notebook (`notebooks/eda-com-downloads.ipynb`, seção 5) e justificadas em `entregas/justificativa-metricas.md`: clientes no recorte, taxa de recompra, feedback positivo, idade média.
- Widgets: barra de filtros no topo da aba (gênero, ocupação, tipo de cliente, idade) e clique no gráfico de faixa etária como filtro cruzado.

## Restrições

- Altair para todos os visuais, com seleção cruzada via `on_select="rerun"` (guia `ALTAIR-CROSSFILTER.md`).
- 3 a 5 métricas (`st.metric`) com delta contra a base completa; no mínimo 3 visuais além das métricas.
- Cores coerentes com `.streamlit/config.toml`: laranja `#D45F0A` = resposta positiva, azul `#3F6FB5` = negativa (par validado para daltonismo).
- Proteger casos vazios (filtro sem clientes → "—" nos KPIs, sem erro).

## Formato de saída

Código do bloco do Dashboard 2 e das funções de gráfico em `src/graficos.py`, mais testes de borda com `st.testing.v1.AppTest`.
