Controle Financeiro Pessoal (Python + CustomTkinter)

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)]()
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-FF6F61?style=flat&logo=python&logoColor=white)]()
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)]()
[![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat&logo=matplotlib&logoColor=white)]()
[![FPDF](https://img.shields.io/badge/FPDF-000000?style=flat&logo=python&logoColor=white)]()

Aplicativo simples e objetivo para controle financeiro pessoal em Windows, feito em Python com interface moderna via CustomTkinter. Permite registrar receitas e gastos, visualizar saldo, gerar gráfico por categoria e exportar relatórios mensais em Excel e PDF.

**Público-alvo:** usuários que desejam um controle básico, direto e local dos lançamentos financeiros (sem banco de dados, usando arquivo CSV).

## Captura de Tela

[![capturaprojetoplanilhagastopython.png](https://i.postimg.cc/cCLSVbmt/capturaprojetoplanilhagastopython.png)](https://postimg.cc/TLFFbQBT)

## Funcionalidades

- Adicionar lançamentos de **Receita** e **Gasto**
- **Categorias** pré-definidas (Alimentação, Transporte, Lazer, Contas, Remédios, Outros)
- **Cálculo automático** de saldo, total de receitas e total de despesas
- **Gráfico de pizza** com distribuição de gastos por categoria
- **Relatórios mensais** (visualização, Excel e PDF)
- **Abertura rápida** da planilha `Gastos.csv` no app padrão do sistema

## Requisitos

- Python 3.10 ou superior
- Pacotes: `customtkinter`, `pandas`, `matplotlib`, `fpdf`, `openpyxl`

> Observação: o `openpyxl` é necessário para salvar relatórios em Excel (`.xlsx`).

## Instalação

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/NatanLuz/planilhagastoteste.git
cd planilhagastoteste

# (Opcional) criar ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar pacotes necessários
pip install customtkinter pandas matplotlib fpdf openpyxl
```

## Execução

Inicie a aplicação:

```bash
python app.py
```

Ao iniciar, o sistema cria automaticamente o arquivo `Gastos.csv` (se não existir).

## Estrutura dos Dados (CSV)

Arquivo: `Gastos.csv`

Colunas:

- `Data` (YYYY-MM-DD)
- `Tipo` (`Receita` ou `Gasto`)
- `Categoria` (uma das categorias pré-definidas)
- `Descrição` (texto livre)
- `Valor` (número positivo)

## Relatórios

- **Visualização do relatório mensal:** informar mês e ano na interface e clicar em "Relatório do mês escolhido".
- **Salvar em Excel:** gera `Relatorio_<ANO>_<MES>.xlsx` usando `openpyxl`.
- **Salvar em PDF:** gera `Relatorio_<ANO>_<MES>.pdf` usando `FPDF`.

Arquivos de exemplo presentes no repositório:

- `Relatorio_2025_7.xlsx`
- `Relatorio_2025_7.pdf`

## Estrutura do Projeto

- `app.py`: aplicação principal com a interface gráfica
- `Core/dados.py`: utilitários e manipulação de dados
- `Core/relatorios.py`: funções para relatórios (apoio)
- `Gastos.csv`: base de dados local (CSV)

## Autor

Natan Luz
