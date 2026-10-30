# Declaração de Uso de IA

**Nome:** Caio Leimig Rodrigues da Silva
**Data:** 29/10/2026 (Aulas 21, 22 e 23: dashboards em Streamlit)

## Ferramenta

**Claude Code** (VS Code, Claude Opus 5.5) com as skills do Streamlit (`streamlit skills`). Na EDA da Aula 11 foi usado o Claude (chat), como declarado no notebook.

## Prompt usado

Pedido inicial, com os slides das três aulas (Streamlit partes 1, 2 e 3) anexados:

> "com base nesses 3 pdfs, me ajude a fazer essa atividade montando a estrutura de repositorio necessaria."

Em seguida enviei a minha EDA da Aula 11 (Online Food Delivery) como base. Os prompts estruturados (contexto, entrada, restrições, formato) que guiaram cada dashboard estão em:
- [prompt-esqueleto-dashboard1.md](prompt-esqueleto-dashboard1.md)
- [prompt-dashboard2.md](prompt-dashboard2.md)

## Para que a IA foi usada

- Pipeline de dados (`notebooks/eda-com-downloads.ipynb`), `app.py`, `src/` e testes.
- Implementar no app as métricas do Dashboard 2, que eu escolhi e justifiquei a partir da minha EDA.
- Gerar os wireframes (`entregas/wireframe-dashboard*.png`); os rascunhos à mão são meus.
- Organizar README e estrutura do repositório.

## O que foi aceito, modificado ou rejeitado

- **Aceito:** o código que implementa o layout dos meus rascunhos (duas abas, filtros na sidebar no Dashboard 1 e no topo no Dashboard 2) e as 4 métricas que defini; cache e caminhos relativos.
- **Modificado:** pedi para incluir renda e escolaridade como ordinais (Spearman padrão); paleta trocada por laranja + azul, legível para daltonismo; correção da formatação dos deltas dos KPIs.
- **Rejeitado:** mapa com localização dos clientes (latitude, longitude e `Pin code` foram removidos do dado tratado por precaução) e cópia do Dashboard 1 do repositório-modelo.

**Validação:** números do dado tratado conferidos com a EDA (285 linhas, 81,1% de feedback positivo) e testes de borda com `python tests/test_app.py`.
