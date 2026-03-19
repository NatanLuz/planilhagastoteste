import os
import sqlite3
from datetime import date, datetime

import pandas as pd

DB_FILE = "gastos.db"
CSV_FILE = "Gastos.csv"
CATEGORIAS = ["Alimentação", "Transporte", "Lazer", "Contas", "Remédios", "Outros"]


def _normalizar_valor(valor_bruto):
	if pd.isna(valor_bruto):
		raise ValueError("valor ausente")

	texto = str(valor_bruto).strip()
	if not texto:
		raise ValueError("valor vazio")

	texto = texto.replace(" ", "")

	if "," in texto and "." in texto:
		if texto.rfind(",") > texto.rfind("."):
			texto = texto.replace(".", "").replace(",", ".")
		else:
			texto = texto.replace(",", "")
	elif "," in texto:
		texto = texto.replace(".", "").replace(",", ".")
	elif texto.count(".") > 1:
		texto = texto.replace(".", "")

	return abs(float(texto))


def _conexao():
	return sqlite3.connect(DB_FILE)


def inicializar_banco():
	with _conexao() as conn:
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS lancamentos (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				data TEXT NOT NULL,
				tipo TEXT NOT NULL CHECK (tipo IN ('Receita', 'Gasto')),
				categoria TEXT NOT NULL,
				descricao TEXT,
				valor REAL NOT NULL CHECK (valor >= 0)
			)
			"""
		)
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS metas (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				categoria TEXT NOT NULL,
				ano INTEGER NOT NULL,
				mes INTEGER NOT NULL,
				limite REAL NOT NULL CHECK (limite > 0),
				UNIQUE(categoria, ano, mes)
			)
			"""
		)
		conn.commit()

	migrar_csv_para_sqlite_se_necessario()


def migrar_csv_para_sqlite_se_necessario():
	if not os.path.exists(CSV_FILE):
		return

	with _conexao() as conn:
		total = conn.execute("SELECT COUNT(*) FROM lancamentos").fetchone()[0]
		if total > 0:
			return

	try:
		df = pd.read_csv(CSV_FILE)
	except UnicodeDecodeError:
		try:
			df = pd.read_csv(CSV_FILE, encoding="latin-1")
		except Exception:
			return
	except Exception:
		return

	if df.empty:
		return

	colunas_esperadas = {"Data", "Tipo", "Categoria", "Descrição", "Valor"}
	if not colunas_esperadas.issubset(set(df.columns)):
		return

	linhas_invalidas = 0

	with _conexao() as conn:
		for _, row in df.iterrows():
			data_bruta = str(row.get("Data", "")).strip()
			data = pd.to_datetime(data_bruta, errors="coerce")
			data_txt = data.strftime("%Y-%m-%d") if pd.notna(data) else date.today().strftime("%Y-%m-%d")

			tipo = str(row.get("Tipo", "Gasto")).strip()
			if tipo not in ("Receita", "Gasto"):
				tipo = "Gasto"

			categoria = str(row.get("Categoria", "Outros")).strip() or "Outros"
			descricao = str(row.get("Descrição", "")).strip()

			valor = row.get("Valor", 0)
			try:
				valor_num = _normalizar_valor(valor)
			except (TypeError, ValueError):
				linhas_invalidas += 1
				continue

			conn.execute(
				"""
				INSERT INTO lancamentos (data, tipo, categoria, descricao, valor)
				VALUES (?, ?, ?, ?, ?)
				""",
				(data_txt, tipo, categoria, descricao, valor_num),
			)
		conn.commit()

	if linhas_invalidas > 0:
		print(f"Aviso: {linhas_invalidas} linha(s) do CSV foram ignoradas por valor inválido.")


def adicionar_lancamento(tipo, categoria, descricao, valor, data_txt=None):
	if data_txt is None:
		data_txt = datetime.now().strftime("%Y-%m-%d")

	with _conexao() as conn:
		conn.execute(
			"""
			INSERT INTO lancamentos (data, tipo, categoria, descricao, valor)
			VALUES (?, ?, ?, ?, ?)
			""",
			(data_txt, tipo, categoria, descricao, abs(float(valor))),
		)
		conn.commit()


def listar_lancamentos():
	with _conexao() as conn:
		df = pd.read_sql_query(
			"""
			SELECT data AS Data, tipo AS Tipo, categoria AS Categoria, descricao AS Descrição, valor AS Valor
			FROM lancamentos
			ORDER BY data DESC, id DESC
			""",
			conn,
		)
	return df


def calcular_saldo():
	with _conexao() as conn:
		receitas, despesas = conn.execute(
			"""
			SELECT
				COALESCE(SUM(CASE WHEN tipo = 'Receita' THEN valor END), 0),
				COALESCE(SUM(CASE WHEN tipo = 'Gasto' THEN valor END), 0)
			FROM lancamentos
			"""
		).fetchone()

	saldo = receitas - despesas
	return saldo, receitas, despesas


def relatorio_mensal(ano=None, mes=None):
	if ano is None or mes is None:
		hoje = datetime.now()
		ano = hoje.year
		mes = hoje.month

	with _conexao() as conn:
		df_mes = pd.read_sql_query(
			"""
			SELECT data AS Data, tipo AS Tipo, categoria AS Categoria, descricao AS Descrição, valor AS Valor
			FROM lancamentos
			WHERE CAST(strftime('%Y', data) AS INTEGER) = ?
			  AND CAST(strftime('%m', data) AS INTEGER) = ?
			ORDER BY data ASC, id ASC
			""",
			conn,
			params=(int(ano), int(mes)),
		)

	if df_mes.empty:
		return df_mes, 0.0, 0.0, 0.0

	receitas = df_mes[df_mes["Tipo"] == "Receita"]["Valor"].sum()
	gastos = df_mes[df_mes["Tipo"] == "Gasto"]["Valor"].sum()
	saldo = receitas - gastos
	return df_mes, float(receitas), float(gastos), float(saldo)


def gastos_por_categoria(ano=None, mes=None):
	if ano is None or mes is None:
		hoje = datetime.now()
		ano = hoje.year
		mes = hoje.month

	with _conexao() as conn:
		df = pd.read_sql_query(
			"""
			SELECT categoria AS Categoria, COALESCE(SUM(valor), 0) AS Valor
			FROM lancamentos
			WHERE tipo = 'Gasto'
			  AND CAST(strftime('%Y', data) AS INTEGER) = ?
			  AND CAST(strftime('%m', data) AS INTEGER) = ?
			GROUP BY categoria
			""",
			conn,
			params=(int(ano), int(mes)),
		)

	resumo = pd.Series(0.0, index=CATEGORIAS)
	for _, row in df.iterrows():
		resumo[row["Categoria"]] = float(row["Valor"])
	return resumo


def serie_saldo_diario(ano=None, mes=None):
	if ano is None or mes is None:
		hoje = datetime.now()
		ano = hoje.year
		mes = hoje.month

	with _conexao() as conn:
		df = pd.read_sql_query(
			"""
			SELECT data AS Data, tipo AS Tipo, valor AS Valor
			FROM lancamentos
			WHERE CAST(strftime('%Y', data) AS INTEGER) = ?
			  AND CAST(strftime('%m', data) AS INTEGER) = ?
			""",
			conn,
			params=(int(ano), int(mes)),
		)

	if df.empty:
		return pd.DataFrame(columns=["Data", "Saldo"])

	df["Data"] = pd.to_datetime(df["Data"])
	df["Delta"] = df.apply(lambda r: r["Valor"] if r["Tipo"] == "Receita" else -r["Valor"], axis=1)
	diario = df.groupby("Data", as_index=False)["Delta"].sum().sort_values("Data")
	diario["Saldo"] = diario["Delta"].cumsum()
	return diario[["Data", "Saldo"]]


def definir_meta_categoria(categoria, ano, mes, limite):
	with _conexao() as conn:
		conn.execute(
			"""
			INSERT INTO metas (categoria, ano, mes, limite)
			VALUES (?, ?, ?, ?)
			ON CONFLICT(categoria, ano, mes)
			DO UPDATE SET limite = excluded.limite
			""",
			(categoria, int(ano), int(mes), float(limite)),
		)
		conn.commit()


def progresso_metas(ano=None, mes=None):
	if ano is None or mes is None:
		hoje = datetime.now()
		ano = hoje.year
		mes = hoje.month

	with _conexao() as conn:
		metas_df = pd.read_sql_query(
			"""
			SELECT categoria AS Categoria, limite AS Limite
			FROM metas
			WHERE ano = ? AND mes = ?
			""",
			conn,
			params=(int(ano), int(mes)),
		)

	if metas_df.empty:
		return pd.DataFrame(columns=["Categoria", "Limite", "Gasto", "Percentual"])

	gastos = gastos_por_categoria(ano, mes)
	metas_df["Gasto"] = metas_df["Categoria"].map(lambda cat: float(gastos.get(cat, 0.0)))
	metas_df["Percentual"] = metas_df["Gasto"] / metas_df["Limite"]
	return metas_df
