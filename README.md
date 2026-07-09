# Controle Financeiro Pessoal

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)]()
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-FF6F61?style=flat&logo=python&logoColor=white)]()
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)]()
[![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat&logo=matplotlib&logoColor=white)]()
[![FPDF](https://img.shields.io/badge/FPDF-000000?style=flat&logo=python&logoColor=white)]()

## 📖 Sobre o projeto

O **Controle Financeiro Pessoal** é uma aplicação desktop desenvolvida em Python com uma interface moderna construída em CustomTkinter. O sistema oferece uma forma local, objetiva e sem dependência de serviços em nuvem para registrar e acompanhar receitas, gastos, metas e relatórios financeiros.

Os dados são armazenados localmente em um banco SQLite. O projeto também oferece suporte à geração de executável para Windows e à criação de releases versionadas por meio de scripts PowerShell.

## ✨ Funcionalidades

- Cadastro de transações do tipo Receita e Gasto;
- categorias predefinidas: Alimentação, Transporte, Lazer, Contas, Remédios e Outros;
- cálculo automático de saldo, total de receitas e total de despesas;
- dashboard com gráfico de pizza por categoria e série temporal do saldo;
- definição de metas por categoria, com barra de progresso e alertas de limite;
- busca de transações por descrição ou categoria;
- temas System, Dark e Light;
- atalhos de teclado:
  - `Ctrl+Enter`: adiciona um lançamento;
  - `Ctrl+F`: direciona o foco para o campo de busca;
- visualização de relatórios mensais;
- exportação de relatórios para Excel e PDF;
- abertura rápida do banco local `gastos.db` no aplicativo padrão do sistema;
- criação automática do banco de dados na primeira execução;
- migração automática dos dados do arquivo legado `Gastos.csv` na primeira execução.

### Dados e relatórios

O banco `gastos.db` utiliza as seguintes tabelas:

- `lancamentos`: armazena `Data` (YYYY-MM-DD), `Tipo` (`Receita` ou `Gasto`), `Categoria`, `Descrição` e `Valor`;
- `metas`: armazena `categoria`, `ano`, `mes` e `limite`.

Na área de relatórios, é possível informar o mês e o ano para visualizar os lançamentos correspondentes. As exportações geram:

- `Relatorio_<ANO>_<MES>.xlsx`, utilizando OpenPyXL;
- `Relatorio_<ANO>_<MES>.pdf`, utilizando FPDF e incluindo um gráfico.

O repositório possui os arquivos de exemplo `Relatorio_2025_7.xlsx` e `Relatorio_2025_7.pdf`.

## 🖼️ Screenshots

![Tela principal do Controle Financeiro Pessoal](Docs/printprojeto.PNG)

![Dashboard e metas](Docs/printprojeto2.PNG)

[![Captura adicional do projeto](https://i.postimg.cc/cCLSVbmt/capturaprojetoplanilhagastopython.png)](https://postimg.cc/TLFFbQBT)

## 🚀 Tecnologias

- Python 3.10+
- CustomTkinter
- SQLite, por meio do módulo nativo `sqlite3`
- Pandas
- Matplotlib
- FPDF
- OpenPyXL
- Pytest

> O SQLite não exige instalação adicional. O OpenPyXL é necessário para gerar os arquivos `.xlsx`.

## ⚙️ Como executar

### Instalação

```bash
git clone https://github.com/NatanLuz/planilhagastoteste.git
cd planilhagastoteste

# Opcional: criar e ativar um ambiente virtual no Windows
python -m venv .venv
.venv\Scripts\activate

# Instalar as dependências
pip install -r requirements.txt
```

### Execução

```bash
python app.py
```

### Testes automatizados

Instale as dependências de desenvolvimento e execute os testes:

```bash
pip install -r requirements-dev.txt
pytest
```

Os testes cobrem principalmente a camada `Core/dados.py`, incluindo:

- inicialização do banco;
- inclusão de lançamentos e cálculo do saldo;
- relatório mensal, resumo por categoria e série temporal do saldo;
- metas por categoria e cálculo do progresso;
- migração de CSV para SQLite.

### Build do executável para Windows

```powershell
.\build_exe.ps1
```

O build gera os seguintes arquivos:

- `dist/ControleFinanceiro/ControleFinanceiro.exe`;
- `dist/ControleFinanceiro-<versao>.exe`;
- `dist/ControleFinanceiro-<versao>-win64.zip`.

### Release com versionamento automático

O script `release.ps1` determina a versão com base nas tags semânticas do Git. Quando `-Version` é informado, utiliza a versão fornecida, como `v1.2.3`. Sem esse parâmetro, calcula o próximo patch a partir da última tag, por exemplo, de `v1.2.3` para `v1.2.4`.

Gerar uma release local, sem criar tag:

```powershell
.\release.ps1 -PythonCommand ".\.venv\Scripts\python.exe"
```

Gerar uma release com versão explícita:

```powershell
.\release.ps1 -PythonCommand ".\.venv\Scripts\python.exe" -Version v1.3.0
```

Criar uma tag e gerar a release:

```powershell
.\release.ps1 -PythonCommand ".\.venv\Scripts\python.exe" -Version v1.3.0 -CreateTag
```

Criar a tag, enviá-la para o `origin` e gerar a release:

```powershell
.\release.ps1 -PythonCommand ".\.venv\Scripts\python.exe" -Version v1.3.0 -CreateTag -PushTag
```

As releases são criadas em `releases/vX.Y.Z/` e contêm:

- executável versionado;
- arquivo ZIP versionado;
- `SHA256SUMS.txt`;
- `RELEASE_NOTES.md`.

## 📂 Estrutura do projeto

```text
planilhagastoteste/
├── Core/
│   ├── dados.py          # SQLite, migração do CSV e gerenciamento de metas
│   └── relatorios.py     # Funções auxiliares para relatórios
├── Docs/
│   ├── printprojeto.PNG
│   └── printprojeto2.PNG
├── app.py                # Aplicação principal e interface gráfica
├── build_exe.ps1         # Geração do executável para Windows
├── gastos.db             # Banco de dados local SQLite
├── release.ps1           # Criação de releases versionadas
├── requirements.txt      # Dependências da aplicação
└── requirements-dev.txt  # Dependências de desenvolvimento e testes
```

## 🌐 Deploy

Por ser uma aplicação desktop, o projeto não possui um deploy web tradicional. A distribuição para Windows é feita por meio do executável gerado com `build_exe.ps1`.

Para entregas versionadas, o script `release.ps1` organiza o executável, o arquivo ZIP, as somas de verificação e as notas da versão no diretório `releases/vX.Y.Z/`.

## 👤 Autor

**Natan Da Luz**

- LinkedIn: [linkedin.com/in/natandaluz](https://www.linkedin.com/in/natandaluz/)
- Portfólio: [portfolionatan.vercel.app](https://portfolionatan.vercel.app/)
- E-mail: [natandaluz01@gmail.com](mailto:natandaluz01@gmail.com)

## 📄 Licença

Este projeto está sem uma licença definida no momento.
