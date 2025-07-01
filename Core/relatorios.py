import pandas as pd
from datetime import datetime

ARQUIVO = "Gastos.csv"

def relatorio_mensal(ano=None, mes=None):
    df = pd.read_csv(ARQUIVO)

    if ano is None:
        ano = datetime.now().year
    if mes is None:
        mes = datetime.now().month

    df['Data'] = pd.to_datetime(df['Data'])
    filtro = (df['Data'].dt.year == ano) & (df['Data'].dt.month == mes)
    df_filtrado = df[filtro]

    total_receitas = df_filtrado[df_filtrado['Tipo'] == 'Receita']['Valor'].sum()
    total_gastos = df_filtrado[df_filtrado['Tipo'] == 'Gasto']['Valor'].sum()
    saldo = total_receitas - total_gastos

    return df_filtrado, total_receitas, total_gastos, saldo
