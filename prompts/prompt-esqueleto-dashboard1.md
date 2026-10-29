# Prompt usado: rascunho → esqueleto do Dashboard 1 (Aula 21)

Preenchido a partir do template [layout-skeleton-prompt.md](layout-skeleton-prompt.md).

## Contexto

Sou aluno da disciplina Análise e Visualização de Dados (CESAR School, 2026.2). Estou construindo dois dashboards em Streamlit a partir da minha EDA da Aula 11, feita com o **Online Food Ordering Dataset** (Kaggle): 285 clientes de um app de delivery em Bangalore, após remover duplicatas. O Dashboard 1 mostra **correlação e distribuição das variáveis quantitativas**. O repositório segue o modelo da disciplina: `app.py` na raiz, `src/data_loader.py` para ler `data/clean/dataset.csv`, `notebooks/`, `entregas/`, `prompts/`.

## Entrada

- Rascunho: `entregas/rascunho-dashboard1.png` (anexado).
- Colunas quantitativas/ordinais: `idade`, `tamanho_familia`, `renda_nivel` (0–4), `escolaridade_nivel` (0–4), `latitude`, `longitude`. Classe: `pede_novamente` (Sim/Não).
- Perguntas: quais variáveis se relacionam entre si? Como cada uma se distribui? A relação muda quando removo valores extremos?
- Layout: sidebar com seletor de variáveis, método de correlação, toggle por classe e sliders de intervalo; área principal com heatmap à esquerda e histogramas à direita.

## Restrições

- Streamlit + Altair (sem Plotly). Editar só `app.py` e `src/`.
- Carregar dados via `src/data_loader.py`, com `@st.cache_data` e caminho relativo.
- Pelo menos 1 seletor de variáveis e 1 slider de intervalo.
- Tratar 0, 1 e 2+ variáveis selecionadas sem quebrar.
- Não usar `use_container_width` (deprecado) nem CSS customizado.

## Formato de saída

Código completo do `app.py` com comentários curtos por seção e uma explicação breve de cada bloco.
