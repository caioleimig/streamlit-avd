"""Rótulos, ordens de categorias e cores compartilhados pelos dois dashboards."""

# Cores dos gráficos (mesmas do .streamlit/config.toml).
# Laranja = resposta positiva (pediria novamente / feedback positivo); azul = negativa.
COR_POSITIVA = "#D45F0A"
COR_NEGATIVA = "#3F6FB5"
COR_REFERENCIA = "#8C8279"  # linhas de média: elemento de apoio, não é série de dados

# Variáveis disponíveis para correlação/distribuição no Dashboard 1.
# tipo: "continua" vira histograma com bins; "discreta" e "ordinal" viram barras por valor.
# Para as ordinais, o histograma mostra a categoria original (coluna_rotulo), não o código 0-4.
VARIAVEIS = {
    "idade": {"rotulo": "Idade (anos)", "tipo": "continua"},
    "tamanho_familia": {"rotulo": "Tamanho da família", "tipo": "discreta"},
    "renda_nivel": {"rotulo": "Renda mensal (ordinal)", "tipo": "ordinal", "coluna_rotulo": "renda_mensal"},
    "escolaridade_nivel": {"rotulo": "Escolaridade (ordinal)", "tipo": "ordinal", "coluna_rotulo": "escolaridade"},
    "latitude": {"rotulo": "Latitude", "tipo": "continua"},
    "longitude": {"rotulo": "Longitude", "tipo": "continua"},
}
VARIAVEIS_PADRAO = ["idade", "tamanho_familia", "renda_nivel", "escolaridade_nivel"]

ORDEM = {
    "renda_mensal": ["Sem renda", "Até Rs.10 mil", "Rs.10–25 mil", "Rs.25–50 mil", "Acima de Rs.50 mil"],
    "escolaridade": ["Sem escolaridade", "Ensino básico", "Graduação", "Pós-graduação", "Doutorado"],
    "faixa_etaria": ["18-21", "22-24", "25-27", "28+"],
    "tipo_cliente": ["Novo", "Regular", "Frequente"],
    "ocupacao": ["Estudante", "Empregado(a)", "Autônomo(a)", "Do lar"],
    "genero": ["Feminino", "Masculino"],
    "pede_novamente": ["Sim", "Não"],
    "feedback": ["Positivo", "Negativo"],
}


def rotulo(var):
    return VARIAVEIS[var]["rotulo"]
