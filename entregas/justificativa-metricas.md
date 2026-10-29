# Justificativa das métricas — Dashboard 2

**Dataset:** Online Food Ordering Dataset (Kaggle), 285 clientes após remover duplicatas (ver `notebooks/eda.ipynb` e `notebooks/eda-com-downloads.ipynb`).

**Público-alvo do dashboard:** equipe de produto, marketing e CRM do app de delivery: pessoas que decidem campanhas, segmentação e melhorias de serviço, mas que não precisam ler histogramas nem testes estatísticos.

**Pergunta que o dashboard responde:** *quem são os clientes que pediriam novamente e quem está insatisfeito?*

**Widgets que controlam o dashboard** (definidos antes do rascunho `rascunho-dashboard2.png`):
- Barra de filtros no topo: gênero (`st.pills`), ocupação (`st.multiselect`), tipo de cliente (`st.pills`) e idade (`st.slider`).
- Clique no gráfico de faixa etária (seleção Altair com `on_select="rerun"`): recorta KPIs e os outros três gráficos para a(s) faixa(s) escolhida(s).

> Observação sobre `Output`: o dataset não documenta formalmente essa coluna. Seguimos a leitura mais comum dele, de que `Output = Yes` indica que o cliente **pediria novamente** pelo app. Essa ressalva aparece também no próprio dashboard ("Como ler este dashboard").

---

## Métrica 1: Clientes no recorte
- **Variável:** contagem de linhas após filtros (base: 285 clientes).
- **Tipo:** contagem.
- **O que mede:** quantos clientes atendem aos filtros e à faixa etária selecionada, com o percentual que isso representa da base.
- **Por que foi escolhida:** dá a escala de todas as outras métricas. Uma taxa de 90% em 9 pessoas não vale o mesmo que em 140; a EDA mostrou grupos muito pequenos (ex.: 9 clientes "Do lar", 18 clientes "Novo").
- **Público-alvo:** toda a equipe que usa o dashboard.
- **Qual decisão pode ser apoiada por essa métrica?** Se um segmento é grande o bastante para justificar uma campanha ou ação dedicada, ou se um resultado vem de um grupo pequeno demais para agir com confiança.
- **O que comunica ao público-alvo:** "estamos olhando para N pessoas (x% dos clientes)": o tamanho do segmento antes de interpretar as taxas.

## Métrica 2: Taxa de recompra
- **Variável:** `pede_novamente` (original `Output`, Sim/Não).
- **Tipo:** proporção (% de "Sim"), com delta em pontos percentuais contra a base completa (76,1%).
- **O que mede:** a parcela de clientes do recorte que pediria novamente pelo app.
- **Por que foi escolhida:** é a variável-alvo da EDA e o indicador mais próximo de retenção, que é o objetivo de negócio de um app de delivery. A EDA mostrou que ela varia de forma significativa com a idade (Qui² p≈0,0001: ~80–88% até 24 anos contra ~62–65% a partir dos 25).
- **Público-alvo:** marketing/CRM e liderança de produto.
- **Qual decisão pode ser apoiada por essa métrica?** Onde investir em retenção (cupons, programas de fidelidade, comunicação) e quais segmentos estão abaixo da média da base.
- **O que comunica ao público-alvo:** "de cada 100 clientes deste grupo, X voltariam a pedir", e se o grupo está acima ou abaixo da média geral (seta verde/vermelha).

## Métrica 3: Feedback positivo
- **Variável:** `feedback` (Positivo/Negativo).
- **Tipo:** proporção (% de "Positivo"), com delta em pontos percentuais contra a base completa (81,1%).
- **O que mede:** a satisfação declarada dos clientes do recorte com o serviço.
- **Por que foi escolhida:** satisfação e retenção são coisas diferentes, e o dashboard precisa mostrar as duas. A EDA mostrou que o feedback está associado à ocupação (Qui² p≈0,011), enquanto o tipo de cliente não se associa à recompra (p≈0,864).
- **Público-alvo:** equipe de produto e operações (qualidade de entrega, atendimento).
- **Qual decisão pode ser apoiada por essa métrica?** Priorizar melhorias de serviço ou pesquisas qualitativas nos segmentos com mais avaliações negativas (ex.: empregados e autônomos).
- **O que comunica ao público-alvo:** "X% deste grupo avaliou o serviço positivamente": se o grupo está satisfeito, independente de voltar a pedir.

## Métrica 4: Idade média
- **Variável:** `idade` (anos).
- **Tipo:** média, com delta em anos contra a base completa (24,7 anos).
- **O que mede:** o perfil etário do recorte.
- **Por que foi escolhida:** idade foi o fator que mais diferenciou quem pediria novamente de quem não pediria (24,3 contra 25,9 anos; Mann-Whitney p<0,001). Ver a idade ao lado da taxa de recompra deixa essa relação visível ao filtrar. O delta fica em cinza de propósito: um grupo mais velho ou mais novo não é "melhor" nem "pior".
- **Público-alvo:** marketing (segmentação e linguagem de campanha).
- **Qual decisão pode ser apoiada por essa métrica?** Ajustar público e tom das campanhas: o app é majoritariamente jovem e perde retenção a partir dos 25 anos.
- **O que comunica ao público-alvo:** "o cliente típico deste grupo tem X anos" e se o grupo é mais velho ou mais novo que a média.

---

## Visuais (além das métricas)

| Visual | Variável agrupada | Por que |
|---|---|---|
| Taxa de recompra por faixa etária (clicável) | `faixa_etaria` (mesmas faixas da EDA) | Mostra o achado principal da EDA (queda após os 25) e serve de filtro cruzado para KPIs e outros gráficos. |
| Feedback por ocupação (100% empilhado) | `ocupacao` × `feedback` | Associação significativa da EDA: onde está a insatisfação. |
| Taxa de recompra por renda mensal | `renda_mensal` | Renda tem correlação forte com idade (Spearman ≈ 0,57): ajuda a separar "jovem sem renda" de "adulto com renda". |
| Recompra por tipo de cliente (contagem) | `tipo_cliente` × `pede_novamente` | Mostra que frequência de uso sozinha não garante recompra (achado da EDA) e o tamanho de cada grupo. |
