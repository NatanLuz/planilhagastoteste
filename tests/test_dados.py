from datetime import datetime

import pandas as pd
import pytest

from Core import dados


@pytest.fixture
def banco_isolado(tmp_path, monkeypatch):
    db_path = tmp_path / "test_gastos.db"
    csv_path = tmp_path / "test_gastos.csv"

    monkeypatch.setattr(dados, "DB_FILE", str(db_path))
    monkeypatch.setattr(dados, "CSV_FILE", str(csv_path))
    return db_path, csv_path


def test_inicializar_banco_cria_estrutura(banco_isolado):
    dados.inicializar_banco()

    assert dados._conexao() is not None
    saldo, receitas, despesas = dados.calcular_saldo()
    assert (saldo, receitas, despesas) == (0, 0, 0)


def test_adicionar_lancamentos_e_calcular_saldo(banco_isolado):
    dados.inicializar_banco()
    dados.adicionar_lancamento("Receita", "Outros", "Freela", 2500.0, "2026-03-01")
    dados.adicionar_lancamento("Gasto", "Alimentação", "Mercado", 350.0, "2026-03-02")
    dados.adicionar_lancamento("Gasto", "Transporte", "Combustivel", 150.0, "2026-03-03")

    saldo, receitas, despesas = dados.calcular_saldo()
    assert receitas == 2500.0
    assert despesas == 500.0
    assert saldo == 2000.0


def test_relatorio_categoria_e_serie_saldo(banco_isolado):
    dados.inicializar_banco()
    dados.adicionar_lancamento("Receita", "Outros", "Salario", 3000.0, "2026-04-01")
    dados.adicionar_lancamento("Gasto", "Alimentação", "Mercado", 400.0, "2026-04-02")
    dados.adicionar_lancamento("Gasto", "Alimentação", "Padaria", 100.0, "2026-04-02")

    df_mes, receitas, gastos, saldo = dados.relatorio_mensal(2026, 4)
    assert not df_mes.empty
    assert receitas == 3000.0
    assert gastos == 500.0
    assert saldo == 2500.0

    resumo = dados.gastos_por_categoria(2026, 4)
    assert resumo["Alimentação"] == 500.0

    serie = dados.serie_saldo_diario(2026, 4)
    assert not serie.empty
    assert list(serie.columns) == ["Data", "Saldo"]

def test_definir_meta_e_progresso(banco_isolado):
    dados.inicializar_banco()
    dados.adicionar_lancamento("Gasto", "Alimentação", "Mercado", 300.0, "2026-05-05")
    dados.definir_meta_categoria("Alimentação", 2026, 5, 500.0)

    progresso = dados.progresso_metas(2026, 5)
    assert len(progresso) == 1

    linha = progresso.iloc[0]
    assert linha["Categoria"] == "Alimentação"
    assert linha["Limite"] == 500.0
    assert linha["Gasto"] == 300.0
    assert pytest.approx(linha["Percentual"], 0.001) == 0.6

def test_migracao_csv_so_uma_vez(banco_isolado):
    _, csv_path = banco_isolado

    df_csv = pd.DataFrame(
        [
            {
                "Data": datetime(2026, 3, 10).strftime("%Y-%m-%d"),
                "Tipo": "Gasto",
                "Categoria": "Contas",
                "Descrição": "Internet",
                "Valor": 120.0,
            }
        ]
    )
    df_csv.to_csv(csv_path, index=False)

    dados.inicializar_banco()
    df = dados.listar_lancamentos()
    assert len(df) == 1

    dados.inicializar_banco()
    df2 = dados.listar_lancamentos()
    assert len(df2) == 1


def test_migracao_csv_normaliza_valor_e_ignora_invalido(banco_isolado):
    _, csv_path = banco_isolado

    df_csv = pd.DataFrame(
        [
            {
                "Data": "2026-03-10",
                "Tipo": "Gasto",
                "Categoria": "Contas",
                "Descrição": "Energia",
                "Valor": "1.234,56",
            },
            {
                "Data": "2026-03-11",
                "Tipo": "Gasto",
                "Categoria": "Contas",
                "Descrição": "Registro inválido",
                "Valor": "abc",
            },
        ]
    )
    df_csv.to_csv(csv_path, index=False)

    dados.inicializar_banco()
    df = dados.listar_lancamentos()

    assert len(df) == 1
    assert df.iloc[0]["Descrição"] == "Energia"
    assert pytest.approx(float(df.iloc[0]["Valor"]), 0.001) == 1234.56

# - testes adicionais podem ser criados para cobrir mais casos, como:
# - Verificar comportamento com dados faltantes ou mal formatados no CSV
# - Testar a função de definir meta com limites inválidos
# - Garantir que o relatório mensal retorna dados corretos para meses sem lançamentos
# - Validar que a série de saldo diário lida corretamente com dias sem movimentações
# - Esses testes ajudam a garantir que o sistema seja robusto e funcione corretamente em diversas situações.        
# - Para rodar os testes, use o comando: pytest tests/test_dados.py
