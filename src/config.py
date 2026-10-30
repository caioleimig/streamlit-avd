# [IA] Claude Code – identidade visual (paleta validada para daltonismo)
# laranja = resposta positiva, azul = negativa (mesmas cores do .streamlit/config.toml)
cor_positiva = "#D45F0A"
cor_negativa = "#3F6FB5"
cor_referencia = "#8C8279"

# continua vira histograma; discreta e ordinal viram barras por valor
variaveis = {
    "idade": {"rotulo": "Idade (anos)", "tipo": "continua"},
    "tamanho_familia": {"rotulo": "Tamanho da família", "tipo": "discreta"},
    "renda_nivel": {"rotulo": "Renda mensal (ordinal)", "tipo": "ordinal", "coluna_rotulo": "renda_mensal"},
    "escolaridade_nivel": {"rotulo": "Escolaridade (ordinal)", "tipo": "ordinal", "coluna_rotulo": "escolaridade"},
}

ordem = {
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
    return variaveis[var]["rotulo"]
