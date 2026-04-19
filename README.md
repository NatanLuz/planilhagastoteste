# Controle Financeiro Pessoal (Python + CustomTkinter)

Aplicação desktop para controle financeiro pessoal, desenvolvida em Python com interface moderna em CustomTkinter.

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)]()
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-FF6F61?style=flat&logo=python&logoColor=white)]()
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)]()
[![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat&logo=matplotlib&logoColor=white)]()
[![FPDF](https://img.shields.io/badge/FPDF-000000?style=flat&logo=python&logoColor=white)]()

O sistema permite registrar receitas e despesas, visualizar saldo em tempo real, acompanhar dashboard analítico (gráfico de pizza e linha do tempo), definir metas por categoria e exportar relatórios mensais em Excel e PDF.

Público-alvo: usuários que buscam controle financeiro local, objetivo e sem dependência de serviços em nuvem.

## Visão Geral

Projeto em evolução contínua, com expansão de funcionalidades a cada versão.

[![capturaprojetoplanilhagastopython.png](https://i.postimg.cc/cCLSVbmt/capturaprojetoplanilhagastopython.png)](https://postimg.cc/TLFFbQBT)

## Prints do Projeto

![Tela principal](Docs/printprojeto.PNG)
![Dashboard e metas](Docs/printprojeto2.PNG)

## Funcionalidades

- Lançamento de transações de Receita e Gasto
- Categorias pré-definidas: Alimentação, Transporte, Lazer, Contas, Remédios e Outros
- Cálculo automático de saldo, total de receitas e total de despesas
- Dashboard com gráfico de pizza por categoria e série temporal de saldo
- Metas por categoria com barra de progresso e alertas de limite
- Tema dinâmico: System, Dark e Light
- Atalhos de teclado: `Ctrl+Enter` para adicionar lançamento e `Ctrl+F` para busca
- Busca de transações por descrição ou categoria
- Relatórios mensais com visualização, exportação Excel e exportação PDF
- Abertura rápida do banco local `gastos.db` no aplicativo padrão do sistema

## Requisitos

- Python 3.10+
- Pacotes: `customtkinter`, `pandas`, `matplotlib`, `fpdf`, `openpyxl`

Observações:

- SQLite é nativo do Python via módulo `sqlite3` e não requer instalação adicional
- `openpyxl` é necessário para geração de arquivos `.xlsx`

## Instalação

```bash
git clone https://github.com/NatanLuz/planilhagastoteste.git
cd planilhagastoteste

# Opcional: criar ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## Execução

```bash
python app.py
```

Atalhos disponíveis na interface:

- `Ctrl+Enter`: adiciona lançamento
- `Ctrl+F`: foca no campo de busca

Ao iniciar, o sistema:

- cria automaticamente o banco `gastos.db` se não existir
- migra automaticamente dados de `Gastos.csv` legado na primeira execução

## Estrutura dos Dados (SQLite)

Arquivo de banco: `gastos.db`

Tabela `lancamentos`:

- `Data` (YYYY-MM-DD)
- `Tipo` (`Receita` ou `Gasto`)
- `Categoria` (categoria pré-definida)
- `Descrição` (texto livre)
- `Valor` (número positivo)

Tabela `metas`:

- `categoria`
- `ano`
- `mes`
- `limite`

## Relatórios

- Visualização mensal: informar mês e ano e clicar em "Relatório do mês escolhido"
- Exportação Excel: gera `Relatorio_<ANO>_<MES>.xlsx` com `openpyxl`
- Exportação PDF: gera `Relatorio_<ANO>_<MES>.pdf` com `FPDF` e gráfico embutido

Arquivos de exemplo no repositório:

- `Relatorio_2025_7.xlsx`
- `Relatorio_2025_7.pdf`

## Estrutura do Projeto

- `app.py`: aplicação principal com interface gráfica
- `Core/dados.py`: camada de dados (SQLite, migração CSV e metas)
- `Core/relatorios.py`: funções auxiliares de relatório
- `gastos.db`: base local SQLite

## Testes Automatizados

Instalar dependências de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

Executar testes:

```bash
pytest
```

Cobertura principal em `Core/dados.py`:

- Inicialização do banco
- Inclusão de lançamentos e cálculo de saldo
- Relatório mensal, resumo por categoria e série temporal de saldo
- Metas por categoria e cálculo de progresso
- Migração CSV -> SQLite

## Empacotamento .exe (Windows)

```powershell
.\build_exe.ps1
```

Saídas geradas:

- `dist/ControleFinanceiro/ControleFinanceiro.exe`
- `dist/ControleFinanceiro-<versao>.exe`
- `dist/ControleFinanceiro-<versao>-win64.zip`

## Release com Versionamento Automático

O script `release.ps1` resolve a versão automaticamente com base em tags semânticas do Git.

Regras:

- Se informar `-Version`, utiliza a versão fornecida (exemplo: `v1.2.3`)
- Se não informar, calcula o próximo patch a partir da última tag (exemplo: `v1.2.3` -> `v1.2.4`)

### Exemplos

Gerar release local (sem criar tag):

```powershell
.\release.ps1 -PythonCommand ".\.venv\Scripts\python.exe"
```

Gerar release com versão explícita:

```powershell
.\release.ps1 -PythonCommand ".\.venv\Scripts\python.exe" -Version v1.3.0
```

Criar tag e gerar release:

```powershell
.\release.ps1 -PythonCommand ".\.venv\Scripts\python.exe" -Version v1.3.0 -CreateTag
```

Criar tag, enviar para origin e gerar release:

```powershell
.\release.ps1 -PythonCommand ".\.venv\Scripts\python.exe" -Version v1.3.0 -CreateTag -PushTag
```

Ao final do processo, a release é criada em:

- `releases/vX.Y.Z/`

Conteúdo padrão da release:

- executável versionado
- zip versionado
- `SHA256SUMS.txt`
- `RELEASE_NOTES.md`

## Autor

Natan Luz  
Contato: natandaluz01@gmail.com
