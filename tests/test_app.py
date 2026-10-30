# [IA] Claude Code – testes de borda com AppTest
"""Testes de borda dos dois dashboards, sem abrir navegador (st.testing.v1.AppTest).

Rode da raiz do projeto:  python tests/test_app.py
"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))


def novo_app():
    app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=60)
    app.run()
    assert not app.exception, app.exception
    return app


def textos(app):
    """Todo o texto de avisos, markdown e captions renderizados."""
    blocos = list(app.info) + list(app.warning) + list(app.markdown) + list(app.caption)
    return " ".join(b.value for b in blocos)


def caso_padrao():
    app = novo_app()
    assert len(app.tabs) == 2
    assert len(app.metric) == 4, "Dashboard 2 deve ter 4 KPIs"
    assert "Par mais forte" in textos(app)
    print("ok  padrão: 2 abas, 4 KPIs, heatmap com par mais forte")


def caso_zero_variaveis():
    app = novo_app()
    app.multiselect(key="d1_variaveis").set_value([]).run()
    assert not app.exception
    t = textos(app)
    assert "pelo menos 2 variáveis" in t and "pelo menos 1 variável" in t
    print("ok  0 variáveis: avisos na correlação e na distribuição")


def caso_uma_variavel():
    app = novo_app()
    app.multiselect(key="d1_variaveis").set_value(["idade"]).run()
    assert not app.exception
    assert "pelo menos 2 variáveis" in textos(app)
    assert len(app.slider) == 2, "1 slider do Dashboard 1 + 1 do Dashboard 2"
    print("ok  1 variável: só distribuição, aviso na correlação")


def caso_todas_variaveis_e_metodos():
    app = novo_app()
    app.multiselect(key="d1_variaveis").set_value(["idade", "tamanho_familia", "renda_nivel", "escolaridade_nivel"]).run()
    for metodo in ["pearson", "kendall", "spearman"]:
        app.segmented_control(key="d1_metodo").set_value(metodo).run()
        assert not app.exception, metodo
    app.toggle(key="d1_separar").set_value(True).run()
    app.toggle(key="d1_outliers").set_value(True).run()
    assert not app.exception
    print("ok  4 variáveis × 3 métodos + separar por recompra + remover outliers")


def caso_intervalo_estreito():
    app = novo_app()
    # Idade só 33 anos: sobram pouquíssimos clientes
    app.slider(key="d1_intervalo_idade").set_value((33, 33)).run()
    assert not app.exception
    assert "Poucos clientes" in textos(app)
    # Tamanho da família fixo em 1: variável constante no recorte
    app.slider(key="d1_intervalo_idade").set_value((18, 33)).run()
    app.slider(key="d1_intervalo_tamanho_familia").set_value((1, 1)).run()
    assert not app.exception
    assert "Sem variação" in textos(app)
    print("ok  intervalo estreito e variável constante tratados")


def caso_dashboard2_filtros():
    app = novo_app()
    app.multiselect(key="d2_ocupacao").set_value(["Do lar"]).run()
    assert not app.exception
    app.pills(key="d2_genero").set_value([]).run()
    assert not app.exception
    assert all(m.value == "—" for m in app.metric), "KPIs vazios devem mostrar '—'"
    assert "Nenhum cliente atende" in textos(app)
    print("ok  Dashboard 2: filtro restritivo e filtro vazio")


if __name__ == "__main__":
    for caso in [caso_padrao, caso_zero_variaveis, caso_uma_variavel, caso_todas_variaveis_e_metodos, caso_intervalo_estreito, caso_dashboard2_filtros]:
        caso()
    print("\nTodos os testes passaram.")
