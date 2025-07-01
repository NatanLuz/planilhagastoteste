import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from tkinter import messagebox
import subprocess
from fpdf import FPDF

ARQUIVO = "Gastos.csv"
CATEGORIAS = ["Alimentação", "Transporte", "Lazer", "Contas", "Remédios", "Outros"]

def criar_arquivo():
    if not os.path.exists(ARQUIVO):
        df = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])
        df.to_csv(ARQUIVO, index=False)

def adicionar_lancamento(tipo, categoria, descricao, valor):
    df = pd.read_csv(ARQUIVO)
    novo = {
        "Data": datetime.now().strftime("%Y-%m-%d"),
        "Tipo": tipo,
        "Categoria": categoria,
        "Descrição": descricao,
        "Valor": abs(float(valor))
    }
    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
    df.to_csv(ARQUIVO, index=False)

def calcular_saldo():
    df = pd.read_csv(ARQUIVO)
    receitas = df[df['Tipo'] == 'Receita']['Valor'].sum()
    despesas = df[df['Tipo'] == 'Gasto']['Valor'].sum()
    saldo = receitas - despesas
    return saldo, receitas, despesas

def gastos_por_categoria():
    df = pd.read_csv(ARQUIVO)
    gastos = df[df['Tipo'] == 'Gasto']
    resumo = gastos.groupby('Categoria')['Valor'].sum()
    return resumo

def mostrar_grafico_pizza():
    resumo = gastos_por_categoria()
    if resumo.empty:
        messagebox.showinfo("Informação", "Nenhum gasto registrado para gerar gráfico.")
        return
    plt.figure(figsize=(6,6))
    resumo.plot.pie(autopct='%1.1f%%', startangle=90)
    plt.title("Distribuição de Gastos por Categoria")
    plt.ylabel("")
    plt.tight_layout()
    plt.show()

def relatorio_mensal(ano=None, mes=None):
    df = pd.read_csv(ARQUIVO)
    if df.empty:
        return None, 0, 0, 0

    df['Data'] = pd.to_datetime(df['Data'])

    if ano is None or mes is None:
        hoje = datetime.now()
        ano = hoje.year
        mes = hoje.month

    filtro = (df['Data'].dt.year == int(ano)) & (df['Data'].dt.month == int(mes))
    df_mes = df[filtro]

    receitas = df_mes[df_mes['Tipo'] == 'Receita']['Valor'].sum()
    gastos = df_mes[df_mes['Tipo'] == 'Gasto']['Valor'].sum()
    saldo = receitas - gastos

    return df_mes, receitas, gastos, saldo

def abrir_csv():
    if os.path.exists(ARQUIVO):
        try:
            os.startfile(ARQUIVO)
        except AttributeError:
            subprocess.call(['open', ARQUIVO])
    else:
        messagebox.showinfo("Informação", "Arquivo ainda não foi criado.")

class AppFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Controle Financeiro")
        self.geometry("600x700")
        criar_arquivo()

        self.tipo_var = ctk.CTkOptionMenu(self, values=["Receita", "Gasto"])
        self.tipo_var.set("Gasto")
        self.tipo_var.pack(pady=8)

        self.categoria_var = ctk.CTkOptionMenu(self, values=CATEGORIAS)
        self.categoria_var.set(CATEGORIAS[0])
        self.categoria_var.pack(pady=8)

        self.desc_entry = ctk.CTkEntry(self, placeholder_text="Descrição")
        self.desc_entry.pack(pady=8)

        self.valor_entry = ctk.CTkEntry(self, placeholder_text="Valor (ex: 50.00)")
        self.valor_entry.pack(pady=8)

        self.btn_adicionar = ctk.CTkButton(self, text="Adicionar lançamento", command=self.adicionar)
        self.btn_adicionar.pack(pady=10)

        self.saldo_label = ctk.CTkLabel(self, text="")
        self.saldo_label.pack(pady=10)

        self.btn_grafico = ctk.CTkButton(self, text="Mostrar gráfico de gastos", command=mostrar_grafico_pizza)
        self.btn_grafico.pack(pady=6)

        self.mes_entry = ctk.CTkEntry(self, placeholder_text="Mês (1 a 12)")
        self.mes_entry.pack(pady=4)

        self.ano_entry = ctk.CTkEntry(self, placeholder_text="Ano (ex: 2025)")
        self.ano_entry.pack(pady=4)

        self.btn_relatorio = ctk.CTkButton(self, text="Relatório do mês escolhido", command=self.mostrar_relatorio_mensal)
        self.btn_relatorio.pack(pady=6)

        self.btn_abrir_csv = ctk.CTkButton(self, text="Abrir planilha (.csv)", command=abrir_csv)
        self.btn_abrir_csv.pack(pady=6)

        self.btn_salvar_excel = ctk.CTkButton(self, text="Salvar relatório em Excel", command=self.salvar_excel)
        self.btn_salvar_excel.pack(pady=4)

        self.btn_salvar_pdf = ctk.CTkButton(self, text="Salvar relatório em PDF", command=self.salvar_pdf)
        self.btn_salvar_pdf.pack(pady=4)

        self.lancamentos_text = ctk.CTkTextbox(self, height=200)
        self.lancamentos_text.pack(pady=10)

        self.atualizar_lista()

    def adicionar(self):
        tipo = self.tipo_var.get()
        categoria = self.categoria_var.get()
        descricao = self.desc_entry.get().strip()
        valor_texto = self.valor_entry.get().strip()

        if not valor_texto:
            self.saldo_label.configure(text="Erro: valor não pode estar vazio.", text_color="red")
            return

        try:
            valor = float(valor_texto.replace(",", "."))
        except ValueError:
            self.saldo_label.configure(text="Erro: valor inválido.", text_color="red")
            return

        adicionar_lancamento(tipo, categoria, descricao, valor)
        self.desc_entry.delete(0, "end")
        self.valor_entry.delete(0, "end")

        self.saldo_label.configure(text="Lançamento adicionado.", text_color="green")
        self.atualizar_lista()

    def atualizar_lista(self):
        self.lancamentos_text.delete("1.0", "end")  # corrigido para "1.0"
        df = pd.read_csv(ARQUIVO)

        if df.empty:
            self.lancamentos_text.insert("end", "Nenhum lançamento registrado.\n")
            self.saldo_label.configure(text="Saldo: R$ 0.00")
            return

        for _, row in df.iterrows():
            linha = f"{row['Data']} - {row['Tipo']} - {row['Categoria']} - R$ {row['Valor']:.2f} - {row['Descrição']}\n"
            self.lancamentos_text.insert("end", linha)

        saldo, receitas, despesas = calcular_saldo()
        self.saldo_label.configure(
            text=f"Saldo: R$ {saldo:.2f} (Receitas: R$ {receitas:.2f} | Despesas: R$ {despesas:.2f})"
        )

    def mostrar_relatorio_mensal(self):
        mes = self.mes_entry.get().strip()
        ano = self.ano_entry.get().strip()

        if not (mes.isdigit() and ano.isdigit()):
            messagebox.showwarning("Entrada inválida", "Digite mês e ano válidos (ex: 6 e 2025)")
            return

        df, receitas, gastos, saldo = relatorio_mensal(int(ano), int(mes))

        if df is None or df.empty:
            messagebox.showinfo("Relatório", "Nenhum dado para o período informado.")
            return

        relatorio = f"Relatório ({mes}/{ano}):\n"
        relatorio += f"Receitas: R$ {receitas:.2f}\n"
        relatorio += f"Gastos: R$ {gastos:.2f}\n"
        relatorio += f"Saldo: R$ {saldo:.2f}\n\n"
        relatorio += "Lançamentos:\n"

        for _, row in df.iterrows():
            relatorio += f"{row['Data'].date()} - {row['Tipo']} - {row['Categoria']} - R$ {row['Valor']:.2f} - {row['Descrição']}\n"

        messagebox.showinfo("Relatório Mensal", relatorio)

    def salvar_excel(self):
        mes = self.mes_entry.get().strip()
        ano = self.ano_entry.get().strip()

        if not (mes.isdigit() and ano.isdigit()):
            messagebox.showwarning("Entrada inválida", "Digite mês e ano válidos (ex: 6 e 2025)")
            return

        df, receitas, gastos, saldo = relatorio_mensal(int(ano), int(mes))
        if df is None or df.empty:
            messagebox.showinfo("Relatório", "Nenhum dado para este mês.")
            return

        nome_arquivo = f"Relatorio_{ano}_{mes}.xlsx"
        df.to_excel(nome_arquivo, index=False)
        messagebox.showinfo("Relatório Excel", f"Relatório salvo como {nome_arquivo}")

    def salvar_pdf(self):
        mes = self.mes_entry.get().strip()
        ano = self.ano_entry.get().strip()

        if not (mes.isdigit() and ano.isdigit()):
            messagebox.showwarning("Entrada inválida", "Digite mês e ano válidos (ex: 6 e 2025)")
            return

        df, receitas, gastos, saldo = relatorio_mensal(int(ano), int(mes))
        if df is None or df.empty:
            messagebox.showinfo("Relatório", "Nenhum dado para este mês.")
            return

        nome_arquivo = f"Relatorio_{ano}_{mes}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Relatório Mensal ({mes}/{ano})", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Receitas: R$ {receitas:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Gastos: R$ {gastos:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Saldo: R$ {saldo:.2f}", ln=True)
        pdf.ln(10)

        for _, row in df.iterrows():
            linha = f"{row['Data'].date()} - {row['Tipo']} - {row['Categoria']} - R$ {row['Valor']:.2f} - {row['Descrição']}"
            pdf.multi_cell(0, 8, linha)

        pdf.output(nome_arquivo)
        messagebox.showinfo("Relatório PDF", f"Relatório salvo como {nome_arquivo}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = AppFinanceiro()
    app.mainloop()


