# Importando as bibliotecas necessárias
import customtkinter as ctk  # Para a interface gráfica moderna
import pandas as pd  # Para manipulação de dados em tabelas
import matplotlib.pyplot as plt  # Para criação de gráficos
from datetime import datetime  # Para trabalhar com datas
import os  # Para operações com arquivos e diretórios
from tkinter import messagebox  # Para exibir mensagens popup
import subprocess  # Para abrir arquivos externos
from fpdf import FPDF  # Para gerar relatórios em PDF

# Constantes do programa
ARQUIVO = "Gastos.csv"  # Nome do arquivo CSV onde os dados serão salvos
CATEGORIAS = ["Alimentação", "Transporte", "Lazer", "Contas", "Remédios", "Outros"]  # Categorias de gastos disponíveis

# Função para criar o arquivo CSV se ele não existir
def criar_arquivo():
    if not os.path.exists(ARQUIVO):
        # Cria um DataFrame vazio com as colunas especificadas
        df = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])
        # Salva o DataFrame no arquivo CSV
        df.to_csv(ARQUIVO, index=False)

# Função para adicionar um novo lançamento (receita ou gasto)
def adicionar_lancamento(tipo, categoria, descricao, valor):
    # Lê o arquivo CSV existente
    df = pd.read_csv(ARQUIVO)
    # Cria um dicionário com os dados do novo lançamento
    novo = {
        "Data": datetime.now().strftime("%Y-%m-%d"),  # Data atual formatada
        "Tipo": tipo,  # Receita ou Gasto
        "Categoria": categoria,  # Categoria selecionada
        "Descrição": descricao,  # Descrição fornecida
        "Valor": abs(float(valor))  # Valor absoluto (sempre positivo)
    }
    # Adiciona o novo lançamento ao DataFrame
    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
    # Salva o DataFrame atualizado no arquivo CSV
    df.to_csv(ARQUIVO, index=False)

# Função para calcular o saldo total
def calcular_saldo():
    df = pd.read_csv(ARQUIVO)
    # Soma todas as receitas
    receitas = df[df['Tipo'] == 'Receita']['Valor'].sum()
    # Soma todas as despesas
    despesas = df[df['Tipo'] == 'Gasto']['Valor'].sum()
    # Calcula o saldo (receitas - despesas)
    saldo = receitas - despesas
    return saldo, receitas, despesas

# Função para agrupar gastos por categoria
def gastos_por_categoria():
    df = pd.read_csv(ARQUIVO)
    # Filtra apenas os gastos
    gastos = df[df['Tipo'] == 'Gasto']
    # Agrupa por categoria e soma os valores
    resumo = gastos.groupby('Categoria')['Valor'].sum()
    return resumo

# Função para mostrar um gráfico de pizza dos gastos por categoria
def mostrar_grafico_pizza():
    resumo = gastos_por_categoria()
    # Verifica se há dados para mostrar
    if resumo.empty:
        messagebox.showinfo("Informação", "Nenhum gasto registrado para gerar gráfico.")
        return
    # Configura o gráfico
    plt.figure(figsize=(6,6))
    resumo.plot.pie(autopct='%1.1f%%', startangle=90)
    plt.title("Distribuição de Gastos por Categoria")
    plt.ylabel("")
    plt.tight_layout()
    plt.show()

# Função para gerar um relatório mensal
def relatorio_mensal(ano=None, mes=None):
    df = pd.read_csv(ARQUIVO)
    # Verifica se o DataFrame está vazio
    if df.empty:
        return None, 0, 0, 0

    # Converte a coluna Data para o tipo datetime
    df['Data'] = pd.to_datetime(df['Data'])

    # Se ano ou mês não forem fornecidos, usa o mês/ano atual
    if ano is None or mes is None:
        hoje = datetime.now()
        ano = hoje.year
        mes = hoje.month

    # Filtra os lançamentos do mês/ano especificado
    filtro = (df['Data'].dt.year == int(ano)) & (df['Data'].dt.month == int(mes))
    df_mes = df[filtro]

    # Calcula totais
    receitas = df_mes[df_mes['Tipo'] == 'Receita']['Valor'].sum()
    gastos = df_mes[df_mes['Tipo'] == 'Gasto']['Valor'].sum()
    saldo = receitas - gastos

    return df_mes, receitas, gastos, saldo

# Função para abrir o arquivo CSV no programa padrão do sistema
def abrir_csv():
    if os.path.exists(ARQUIVO):
        try:
            os.startfile(ARQUIVO)  # função de Windows
        except AttributeError:
            subprocess.call(['open', ARQUIVO])  # função de MacOS
    else:
        messagebox.showinfo("Informação", "Arquivo ainda não foi criado.")

# Classe principal da aplicação
class AppFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Configurações da janela principal
        self.title("Controle Financeiro")
        self.geometry("600x700")
        criar_arquivo()  # Garante que o arquivo CSV existe sem erros

        # Widgets da interface
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

        self.atualizar_lista()  # Atualiza a lista de lançamentos na inicialização

    # Método para adicionar um novo lançamento
    def adicionar(self):
        tipo = self.tipo_var.get()
        categoria = self.categoria_var.get()
        descricao = self.desc_entry.get().strip()
        valor_texto = self.valor_entry.get().strip()

        # Validação do valor
        if not valor_texto:
            self.saldo_label.configure(text="Erro: valor não pode estar vazio.", text_color="red")
            return

        try:
            valor = float(valor_texto.replace(",", "."))
        except ValueError:
            self.saldo_label.configure(text="Erro: valor inválido.", text_color="red")
            return

        # Adiciona o lançamento e limpa os campos
        adicionar_lancamento(tipo, categoria, descricao, valor)
        self.desc_entry.delete(0, "end")
        self.valor_entry.delete(0, "end")

        self.saldo_label.configure(text="Lançamento adicionado.", text_color="green")
        self.atualizar_lista()  # Atualiza a lista de lançamentos

    # Método para atualizar a lista de lançamentos na interface
    def atualizar_lista(self):
        self.lancamentos_text.delete("1.0", "end")  # Limpa o texto atual
        df = pd.read_csv(ARQUIVO)

        if df.empty:
            self.lancamentos_text.insert("end", "Nenhum lançamento registrado.\n")
            self.saldo_label.configure(text="Saldo: R$ 0.00")
            return

        # Adiciona cada lançamento ao texto
        for _, row in df.iterrows():
            linha = f"{row['Data']} - {row['Tipo']} - {row['Categoria']} - R$ {row['Valor']:.2f} - {row['Descrição']}\n"
            self.lancamentos_text.insert("end", linha)

        # Atualiza o saldo
        saldo, receitas, despesas = calcular_saldo()
        self.saldo_label.configure(
            text=f"Saldo: R$ {saldo:.2f} (Receitas: R$ {receitas:.2f} | Despesas: R$ {despesas:.2f})"
        )

    # Método para mostrar o relatório mensal
    def mostrar_relatorio_mensal(self):
        mes = self.mes_entry.get().strip()
        ano = self.ano_entry.get().strip()

        # Validação das entradas
        if not (mes.isdigit() and ano.isdigit()):
            messagebox.showwarning("Entrada inválida", "Digite mês e ano válidos (ex: 6 e 2025)")
            return

        df, receitas, gastos, saldo = relatorio_mensal(int(ano), int(mes))

        if df is None or df.empty:
            messagebox.showinfo("Relatório", "Nenhum dado para o período informado.")
            return

        # Formata o relatório
        relatorio = f"Relatório ({mes}/{ano}):\n"
        relatorio += f"Receitas: R$ {receitas:.2f}\n"
        relatorio += f"Gastos: R$ {gastos:.2f}\n"
        relatorio += f"Saldo: R$ {saldo:.2f}\n\n"
        relatorio += "Lançamentos:\n"

        for _, row in df.iterrows():
            relatorio += f"{row['Data'].date()} - {row['Tipo']} - {row['Categoria']} - R$ {row['Valor']:.2f} - {row['Descrição']}\n"

        messagebox.showinfo("Relatório Mensal", relatorio)

    # Método para salvar o relatório em Excel
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

    # Método para salvar o relatório em PDF
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

# Ponto de entrada do programa
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Define o tema escuro
    ctk.set_default_color_theme("blue")  # Define o tema azul pois vi que seria melhor visivel do que o tom branco que no qual fica mt forte pela sua transparência
    app = AppFinanceiro()  # Cria a aplicação
    app.mainloop()  # Inicia o loop principal da interface
