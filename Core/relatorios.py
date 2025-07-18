# Importa as bibliotecas necessárias neste caso 
import pandas as pd
from datetime import datetime

# Nome do arquivo com os dados csv
ARQUIVO = "Gastos.csv"

# Função que gera um relatório mensal de receitas, gastos e saldo
def relatorio_mensal(ano=None, mes=None):
    # Lê os dados do arquivo CSV
    df = pd.read_csv(ARQUIVO)

    # Se ano ou mês não forem informados, usa o ano e mês atual
    if ano is None:
        ano = datetime.now().year
    if mes is None:
        mes = datetime.now().month

    # Converte a coluna "Data" para o formato "datetime"
    df['Data'] = pd.to_datetime(df['Data'])

    # Filtra os dados para o > ano e mês informados
    filtro = (df['Data'].dt.year == ano) & (df['Data'].dt.month == mes)
    df_filtrado = df[filtro]

    # Calcula o total de receitas, gastos e o saldo
    total_receitas = df_filtrado[df_filtrado['Tipo'] == 'Receita']['Valor'].sum()
    total_gastos = df_filtrado[df_filtrado['Tipo'] == 'Gasto']['Valor'].sum()
    saldo = total_receitas - total_gastos

    # Retorna os dados filtrados e os totais calculados com seu perspectivo resultado
    return df_filtrado, total_receitas, total_gastos, saldo
