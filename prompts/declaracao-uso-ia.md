# Declaração de Uso de IA

**Nome:** Caio Leimig Rodrigues da Silva
**Data:** 29/10/2026 (Aulas 21, 22 e 23: dashboards em Streamlit)

## Ferramenta

- **Claude Code** (extensão do VS Code), modelo **Claude Opus 5.5** (Anthropic), com as skills do Streamlit instaladas no projeto via `streamlit skills` (`.claude/skills/developing-with-streamlit`).
- Na EDA da Aula 11 (`notebooks/eda.ipynb`) foi usado o Claude (chat), como já declarado no próprio notebook.

## Prompt usado

Pedido inicial, com os slides das três aulas (Streamlit partes 1, 2 e 3) anexados:

> "com base nesses 3 pdfs, faça essa atividade cumprindo todos os requisitos e o checklist final, em geral organize bem a estrutura do repositorio, e tudo que seja necessario"

Em seguida enviei a minha EDA da Aula 11 (Online Food Delivery) como base. Os prompts estruturados (contexto, entrada, restrições, formato) que guiaram cada dashboard estão em:
- [prompt-esqueleto-dashboard1.md](prompt-esqueleto-dashboard1.md)
- [prompt-dashboard2.md](prompt-dashboard2.md)

## Para que a IA foi usada

- Montar o pipeline `notebooks/eda-com-downloads.ipynb`: download do dado bruto, o mesmo tratamento da minha EDA, tradução das categorias, colunas derivadas e exportação para `data/clean/`.
- Escrever o `app.py` e os módulos de `src/` (dados com cache, configuração, gráficos Altair).
- Propor e redigir a justificativa das métricas a partir dos achados da minha EDA.
- Gerar os rascunhos de layout (wireframes desenhados com matplotlib no estilo esboço).
- Escrever testes de borda (`tests/test_app.py`) e revisar o app em screenshots.
- Organizar README, checklists e estrutura do repositório.

## O que foi aceito, modificado ou rejeitado e por quê

- **Aceito:**
  - Estrutura em duas abas, filtros do Dashboard 1 na sidebar e filtros do Dashboard 2 no topo da aba (padrão de filtro superior visto no slide 13 da Aula 21).
  - As 4 métricas do Dashboard 2, porque cada uma sai de um achado da minha EDA (idade × recompra, ocupação × feedback, tamanho dos grupos).
  - `@st.cache_data` no carregamento e caminhos relativos, conforme o checklist de deploy.
- **Modificado:**
  - O dataset só tem duas variáveis quantitativas de fato (idade e tamanho da família). Para o Dashboard 1 não ficar com uma matriz 2×2, renda e escolaridade foram incluídas como **ordinais** (0–4), com Spearman como método padrão e um aviso quando Pearson é usado com elas.
  - A paleta inicial (laranja + cinza) reprovou na checagem de croma/contraste do validador de cores, então foi trocada por laranja `#D45F0A` + azul `#3F6FB5`, aprovado para daltonismo nos temas claro e escuro.
  - Os deltas dos KPIs mostravam "p,p," por causa da troca de ponto por vírgula, e deltas zero apareciam com seta verde. Ambos foram corrigidos depois de revisar os screenshots.
- **Rejeitado:**
  - Mapa com latitude/longitude dos clientes: mesmo sendo centroides de CEP, foi descartado para não expor localização em um app público. A coluna `Pin code` também foi removida do dado tratado.
  - Copiar o Dashboard 1 do repositório-modelo (Heart Disease): o app foi refeito para o meu dataset e as minhas perguntas.

**Validação:** os números do dado tratado foram conferidos com os da EDA (285 linhas, idade média 24,3 × 25,9, 81,1% de feedback positivo). O app foi rodado localmente e os cenários de 0, 1 e 2+ variáveis foram testados (`python tests/test_app.py`).
