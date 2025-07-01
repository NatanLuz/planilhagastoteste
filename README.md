# 💸 Controle Financeiro Pessoal

Um aplicativo simples de controle financeiro feito em **Python** com **CustomTkinter**, para registrar receitas, despesas, visualizar o saldo, gerar gráficos e salvar relatórios mensais em **Excel** e **PDF**.

Este projeto foi desenvolvido como um exercício para aprimorar meus conhecimentos em Python e no uso prático de bibliotecas importantes, como CustomTkinter, Pandas, Matplotlib e FPDF. Ele reúne funcionalidades que já utilizei em projetos acadêmicos e trabalhos freelancers, integrando-as em um aplicativo simples e funcional de controle financeiro pessoal.

---
## ⚙️ Funcionalidades

- ✅ Adição de **receitas** e **despesas**
- ✅ Classificação por **categoria** (Alimentação, Lazer, etc.)
- ✅ Cálculo automático de **saldo, total de receitas e gastos**
- ✅ **Gráfico de pizza** com os gastos por categoria
- ✅ Geração de **relatório mensal** (texto, Excel, PDF)
- ✅ Abertura da planilha `.csv` com um clique

---

## 🖥️ Tecnologias usadas

- Python 3
- CustomTkinter
- Pandas
- Matplotlib
- FPDF

---

## ▶️ Como executar

1. Clone este repositório:
   ```bash
   git clone https://github.com/NatanLuz/planilhagastoteste.git
   cd planilhagastoteste

   Instale as dependências:

pip install -r requirements.txt

Execute o app:

python app.py


📁 Estrutura do projeto
├── app.py                # Interface principal (CustomTkinter)
├── Core/
│   ├── dados.py          # Funções de dados (CSV)
│   └── relatorios.py     # Relatórios (mensais, Excel, PDF)
├── Gastos.csv            # Planilha de dados gerada automaticamente
├── Relatorio_2025_7.pdf  # Exemplo de relatório mensal em PDF
├── Relatorio_2025_7.xlsx # Exemplo de relatório mensal em Excel
├── requirements.txt      # Dependências do projeto
└── README.md             # Este arquivo



