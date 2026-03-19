import os
import subprocess
import tempfile
import calendar
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk
from fpdf import FPDF
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from Core.dados import (
    CATEGORIAS,
    DB_FILE,
    adicionar_lancamento,
    calcular_saldo,
    definir_meta_categoria,
    gastos_por_categoria,
    inicializar_banco,
    listar_lancamentos,
    progresso_metas,
    relatorio_mensal,
    serie_saldo_diario,
)


class AppFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Controle Financeiro Pessoal")
        self.geometry("1240x780")
        self.minsize(1080, 700)
        self.protocol("WM_DELETE_WINDOW", self._encerrar)

        inicializar_banco()
        self.alertas_disparados = set()
        self.auto_refresh_ms = 10000
        self.auto_refresh_job = None

        hoje = datetime.now()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.painel_esquerdo = ctk.CTkFrame(self, corner_radius=16)
        self.painel_esquerdo.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.painel_esquerdo.grid_columnconfigure(0, weight=1)

        self.painel_direito = ctk.CTkFrame(self, corner_radius=16)
        self.painel_direito.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=12)
        self.painel_direito.grid_columnconfigure(0, weight=1)
        self.painel_direito.grid_rowconfigure(1, weight=1)

        self._montar_controles_principais(hoje)
        self._montar_lista_lancamentos()
        self._montar_dashboard()
        self._montar_metas()
        self._validar_periodo_inputs()

        self.atualizar_tudo()
        self._agendar_autoatualizacao()
        self.bind("<Control-Return>", lambda _e: self.adicionar())
        self.bind("<Control-f>", lambda _e: self.filtro_entry.focus_set())

    def _montar_controles_principais(self, hoje):
        ctk.CTkLabel(self.painel_esquerdo, text="Lançamentos", font=("Segoe UI", 22, "bold")).grid(
            row=0, column=0, padx=10, pady=(12, 6), sticky="w"
        )

        self.tipo_var = ctk.CTkOptionMenu(self.painel_esquerdo, values=["Receita", "Gasto"])
        self.tipo_var.set("Gasto")
        self.tipo_var.grid(row=1, column=0, padx=10, pady=6, sticky="ew")

        self.categoria_var = ctk.CTkOptionMenu(self.painel_esquerdo, values=CATEGORIAS)
        self.categoria_var.set(CATEGORIAS[0])
        self.categoria_var.grid(row=2, column=0, padx=10, pady=6, sticky="ew")

        self.desc_entry = ctk.CTkEntry(self.painel_esquerdo, placeholder_text="Descrição")
        self.desc_entry.grid(row=3, column=0, padx=10, pady=6, sticky="ew")

        self.valor_entry = ctk.CTkEntry(self.painel_esquerdo, placeholder_text="Valor (ex: 50.00)")
        self.valor_entry.grid(row=4, column=0, padx=10, pady=6, sticky="ew")

        self.btn_adicionar = ctk.CTkButton(
            self.painel_esquerdo,
            text="Adicionar lançamento",
            command=self.adicionar,
            corner_radius=10,
            height=36,
        )
        self.btn_adicionar.grid(row=5, column=0, padx=10, pady=(8, 6), sticky="ew")

        self.saldo_label = ctk.CTkLabel(self.painel_esquerdo, text="")
        self.saldo_label.grid(row=6, column=0, padx=10, pady=6, sticky="w")

        self.filtro_entry = ctk.CTkEntry(self.painel_esquerdo, placeholder_text="Buscar por descrição/categoria")
        self.filtro_entry.grid(row=7, column=0, padx=10, pady=(10, 6), sticky="ew")
        self.filtro_entry.bind("<KeyRelease>", lambda _e: self.atualizar_lista())

        self.mes_entry = ctk.CTkEntry(self.painel_esquerdo, placeholder_text="Mês (1 a 12)")
        self.mes_entry.insert(0, str(hoje.month))
        self.mes_entry.grid(row=8, column=0, padx=10, pady=4, sticky="ew")
        self.mes_entry.bind("<KeyPress>", self._bloquear_nao_numericos)
        self.mes_entry.bind("<KeyRelease>", lambda _e: self._validar_periodo_inputs())
        self.mes_entry.bind("<FocusOut>", lambda _e: self._validar_periodo_inputs())

        self.ano_entry = ctk.CTkEntry(self.painel_esquerdo, placeholder_text="Ano (ex: 2026)")
        self.ano_entry.insert(0, str(hoje.year))
        self.ano_entry.grid(row=9, column=0, padx=10, pady=4, sticky="ew")
        self.ano_entry.bind("<KeyPress>", self._bloquear_nao_numericos)
        self.ano_entry.bind("<KeyRelease>", lambda _e: self._validar_periodo_inputs())
        self.ano_entry.bind("<FocusOut>", lambda _e: self._validar_periodo_inputs())

        self.periodo_status_label = ctk.CTkLabel(self.painel_esquerdo, text="", font=("Segoe UI", 11))
        self.periodo_status_label.grid(row=10, column=0, padx=10, pady=(0, 4), sticky="w")

        self.btn_atualizar = ctk.CTkButton(
            self.painel_esquerdo,
            text="Atualizar painel",
            command=self.atualizar_tudo,
            corner_radius=10,
            height=34,
        )
        self.btn_atualizar.grid(row=11, column=0, padx=10, pady=6, sticky="ew")

        self.auto_refresh_switch = ctk.CTkSwitch(
            self.painel_esquerdo,
            text="Autoatualizar (10s)",
            command=self._alternar_autoatualizacao,
        )
        self.auto_refresh_switch.grid(row=12, column=0, padx=10, pady=6, sticky="w")
        self.auto_refresh_switch.select()

        self.btn_relatorio = ctk.CTkButton(
            self.painel_esquerdo,
            text="Relatório do mês escolhido",
            command=self.mostrar_relatorio_mensal,
            corner_radius=10,
            height=34,
        )
        self.btn_relatorio.grid(row=13, column=0, padx=10, pady=6, sticky="ew")

        self.btn_salvar_excel = ctk.CTkButton(
            self.painel_esquerdo,
            text="Salvar relatório em Excel",
            command=self.salvar_excel,
            corner_radius=10,
            height=32,
        )
        self.btn_salvar_excel.grid(row=14, column=0, padx=10, pady=4, sticky="ew")

        self.btn_salvar_pdf = ctk.CTkButton(
            self.painel_esquerdo,
            text="Salvar relatório em PDF com gráfico",
            command=self.salvar_pdf,
            corner_radius=10,
            height=32,
        )
        self.btn_salvar_pdf.grid(row=15, column=0, padx=10, pady=4, sticky="ew")

        self.btn_abrir_banco = ctk.CTkButton(
            self.painel_esquerdo,
            text="Abrir banco local (.db)",
            command=self.abrir_banco,
            corner_radius=10,
            height=32,
        )
        self.btn_abrir_banco.grid(row=16, column=0, padx=10, pady=(4, 10), sticky="ew")

    def _montar_lista_lancamentos(self):
        ctk.CTkLabel(self.painel_esquerdo, text="Transações", font=("Arial", 16, "bold")).grid(
            row=17, column=0, padx=10, pady=(2, 4), sticky="w"
        )
        self.lancamentos_text = ctk.CTkTextbox(self.painel_esquerdo, height=190)
        self.lancamentos_text.grid(row=18, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.painel_esquerdo.grid_rowconfigure(18, weight=1)

    def _bloquear_nao_numericos(self, event):
        limites = {
            self.mes_entry: 2,
            self.ano_entry: 4,
        }
        teclas_livres = {
            "BackSpace",
            "Delete",
            "Left",
            "Right",
            "Home",
            "End",
            "Tab",
            "Return",
        }

        if event.keysym in teclas_livres:
            return None

        if event.state & 0x4 and event.keysym.lower() in {"a", "c", "v", "x"}:
            return None

        limite = limites.get(event.widget)
        if limite is not None and event.char.isdigit():
            atual = event.widget.get()
            if len(atual) >= limite:
                try:
                    if event.widget.selection_present():
                        return None
                except Exception:
                    pass
                return "break"

        if event.char.isdigit():
            return None

        return "break"

    def _aplicar_limite_tamanho_periodo(self):
        mes_txt = self.mes_entry.get()
        if len(mes_txt) > 2:
            self.mes_entry.delete(2, "end")

        ano_txt = self.ano_entry.get()
        if len(ano_txt) > 4:
            self.ano_entry.delete(4, "end")

    def _validar_periodo_inputs(self):
        self._aplicar_limite_tamanho_periodo()
        mes_txt = self.mes_entry.get().strip()
        ano_txt = self.ano_entry.get().strip()

        mes_valido = mes_txt.isdigit() and 1 <= int(mes_txt) <= 12
        ano_valido = ano_txt.isdigit() and 2000 <= int(ano_txt) <= 2100

        def _aplicar_borda(entry, valor_txt, valido):
            if valor_txt == "":
                entry.configure(border_width=2, border_color="#F9A825")
            elif valido:
                entry.configure(border_width=2, border_color="#1F6AA5")
            else:
                entry.configure(border_width=2, border_color="#D32F2F")

        _aplicar_borda(self.mes_entry, mes_txt, mes_valido)
        _aplicar_borda(self.ano_entry, ano_txt, ano_valido)

        if mes_valido and ano_valido:
            self.periodo_status_label.configure(
                text=f"Período válido: {mes_txt}/{ano_txt}",
                text_color="#2E7D32",
            )
            self.btn_relatorio.configure(state="normal")
            self.btn_salvar_excel.configure(state="normal")
            self.btn_salvar_pdf.configure(state="normal")
            self.btn_salvar_meta.configure(state="normal")
            return True

        if mes_txt == "" or ano_txt == "":
            self.periodo_status_label.configure(
                text="Preencha mês (1-12) e ano (2000-2100)",
                text_color="#F9A825",
            )
        else:
            self.periodo_status_label.configure(
                text="Período inválido. Corrija mês/ano para gerar relatórios.",
                text_color="#D32F2F",
            )

        self.btn_relatorio.configure(state="disabled")
        self.btn_salvar_excel.configure(state="disabled")
        self.btn_salvar_pdf.configure(state="disabled")
        self.btn_salvar_meta.configure(state="disabled")
        return False

    def _montar_dashboard(self):
        header = ctk.CTkFrame(self.painel_direito, fg_color="transparent")
        header.grid(row=0, column=0, padx=12, pady=(10, 2), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(header, text="Dashboard ao vivo", font=("Segoe UI", 24, "bold"))
        titulo.grid(row=0, column=0, padx=2, pady=(0, 6), sticky="w")

        self.tema_menu = ctk.CTkOptionMenu(header, values=["System", "Dark", "Light"], command=self._mudar_tema, width=120)
        self.tema_menu.grid(row=0, column=1, padx=2, pady=(0, 6), sticky="e")
        self.tema_menu.set("System")

        self.ultimo_update_label = ctk.CTkLabel(header, text="Atualizado: --:--:--", font=("Segoe UI", 12))
        self.ultimo_update_label.grid(row=1, column=0, columnspan=2, padx=2, pady=(0, 2), sticky="w")

        self.figura = Figure(figsize=(9, 4), dpi=100)
        self.ax_pizza = self.figura.add_subplot(121)
        self.ax_linha = self.figura.add_subplot(122)
        self.figura.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.figura, master=self.painel_direito)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=0, padx=12, pady=8, sticky="nsew")

    def _montar_metas(self):
        self.metas_frame = ctk.CTkFrame(self.painel_direito)
        self.metas_frame.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")
        self.metas_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.metas_frame, text="Metas de gastos por categoria", font=("Arial", 16, "bold")).grid(
            row=0, column=0, padx=10, pady=(10, 6), sticky="w"
        )

        self.meta_categoria_var = ctk.CTkOptionMenu(self.metas_frame, values=CATEGORIAS)
        self.meta_categoria_var.set(CATEGORIAS[0])
        self.meta_categoria_var.grid(row=1, column=0, padx=10, pady=4, sticky="ew")

        self.meta_valor_entry = ctk.CTkEntry(self.metas_frame, placeholder_text="Limite mensal (ex: 500)")
        self.meta_valor_entry.grid(row=2, column=0, padx=10, pady=4, sticky="ew")

        self.btn_salvar_meta = ctk.CTkButton(self.metas_frame, text="Salvar meta", command=self.salvar_meta)
        self.btn_salvar_meta.grid(row=3, column=0, padx=10, pady=(4, 8), sticky="ew")

        self.metas_container = ctk.CTkFrame(self.metas_frame)
        self.metas_container.grid(row=4, column=0, padx=10, pady=(4, 10), sticky="ew")
        self.metas_container.grid_columnconfigure(0, weight=1)

    def _obter_periodo(self, estrito=False):
        hoje = datetime.now()
        mes_txt = self.mes_entry.get().strip()
        ano_txt = self.ano_entry.get().strip()

        mes_valido = mes_txt.isdigit() and 1 <= int(mes_txt) <= 12
        ano_valido = ano_txt.isdigit() and 2000 <= int(ano_txt) <= 2100

        if estrito and not (mes_valido and ano_valido):
            raise ValueError("Período inválido")

        mes = hoje.month
        ano = hoje.year

        if mes_valido:
            mes = int(mes_txt)
        if ano_valido:
            ano = int(ano_txt)

        return ano, mes

    def adicionar(self):
        tipo = self.tipo_var.get()
        categoria = self.categoria_var.get()
        descricao = self.desc_entry.get().strip()
        valor_texto = self.valor_entry.get().strip().replace(",", ".")

        if not valor_texto:
            self.saldo_label.configure(text="Erro: valor não pode estar vazio.", text_color="red")
            return

        try:
            valor = float(valor_texto)
            if valor <= 0:
                raise ValueError
        except ValueError:
            self.saldo_label.configure(text="Erro: valor inválido.", text_color="red")
            return

        adicionar_lancamento(tipo, categoria, descricao, valor)
        self.desc_entry.delete(0, "end")
        self.valor_entry.delete(0, "end")

        self.saldo_label.configure(text="Lançamento adicionado.", text_color="green")
        self.atualizar_tudo()

    def salvar_meta(self):
        if not self._validar_periodo_inputs():
            messagebox.showwarning("Período inválido", "Corrija mês/ano antes de salvar meta.")
            return

        ano, mes = self._obter_periodo(estrito=True)
        categoria = self.meta_categoria_var.get()
        limite_texto = self.meta_valor_entry.get().strip().replace(",", ".")

        try:
            limite = float(limite_texto)
            if limite <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Meta inválida", "Informe um limite numérico positivo.")
            return

        definir_meta_categoria(categoria, ano, mes, limite)
        self.meta_valor_entry.delete(0, "end")
        messagebox.showinfo("Meta salva", f"Meta salva para {categoria}: R$ {limite:.2f} ({mes}/{ano})")
        self.atualizar_tudo()

    def atualizar_tudo(self):
        periodo_valido = self._validar_periodo_inputs()
        self.atualizar_lista()
        self.atualizar_saldo()
        self.atualizar_dashboard(periodo_valido=periodo_valido)
        self.atualizar_metas(periodo_valido=periodo_valido)
        self.verificar_alertas_metas(periodo_valido=periodo_valido)
        self._registrar_atualizacao()

    def _mudar_tema(self, tema):
        ctk.set_appearance_mode(tema)

    def _registrar_atualizacao(self):
        if hasattr(self, "ultimo_update_label"):
            self.ultimo_update_label.configure(text=f"Atualizado: {datetime.now().strftime('%H:%M:%S')}")

    def _alternar_autoatualizacao(self):
        if self.auto_refresh_switch.get() == 1:
            self._agendar_autoatualizacao()
        elif self.auto_refresh_job is not None:
            self.after_cancel(self.auto_refresh_job)
            self.auto_refresh_job = None

    def _agendar_autoatualizacao(self):
        if self.auto_refresh_job is not None:
            self.after_cancel(self.auto_refresh_job)
            self.auto_refresh_job = None

        if self.auto_refresh_switch.get() == 1:
            self.auto_refresh_job = self.after(self.auto_refresh_ms, self._tick_autoatualizacao)

    def _tick_autoatualizacao(self):
        self.auto_refresh_job = None
        if self.auto_refresh_switch.get() == 1:
            self.atualizar_tudo()
            self._agendar_autoatualizacao()

    def _encerrar(self):
        if self.auto_refresh_job is not None:
            self.after_cancel(self.auto_refresh_job)
            self.auto_refresh_job = None
        self.destroy()

    def atualizar_lista(self):
        self.lancamentos_text.delete("1.0", "end")
        filtro = self.filtro_entry.get().strip().lower()

        df = listar_lancamentos()
        if df.empty:
            self.lancamentos_text.insert("end", "Nenhum lançamento registrado.\n")
            return

        if filtro:
            df = df[
                df["Descrição"].astype(str).str.lower().str.contains(filtro)
                | df["Categoria"].astype(str).str.lower().str.contains(filtro)
            ]

        if df.empty:
            self.lancamentos_text.insert("end", "Nenhum lançamento encontrado para o filtro atual.\n")
            return

        for _, row in df.iterrows():
            linha = (
                f"{row['Data']} - {row['Tipo']} - {row['Categoria']} - "
                f"R$ {row['Valor']:.2f} - {row['Descrição']}\n"
            )
            self.lancamentos_text.insert("end", linha)

    def atualizar_saldo(self):
        saldo, receitas, despesas = calcular_saldo()
        if saldo > 0:
            cor = "#2E7D32"
        elif saldo < 0:
            cor = "#C62828"
        else:
            cor = "#B0BEC5"

        self.saldo_label.configure(
            text=(
                f"Saldo: R$ {saldo:.2f}\n"
                f"Receitas: R$ {receitas:.2f} | Despesas: R$ {despesas:.2f}"
            ),
            text_color=cor,
            justify="left",
        )

    def atualizar_dashboard(self, periodo_valido=True):
        if not periodo_valido:
            self.ax_pizza.clear()
            self.ax_linha.clear()
            self.ax_pizza.text(0.5, 0.5, "Período inválido", ha="center", va="center")
            self.ax_linha.text(0.5, 0.5, "Corrija mês/ano para atualizar", ha="center", va="center")
            self.ax_pizza.set_title("Gastos por categoria")
            self.ax_linha.set_title("Linha do tempo do saldo")
            self.figura.tight_layout()
            self.canvas.draw()
            return

        ano, mes = self._obter_periodo()
        resumo = gastos_por_categoria(ano, mes)
        serie = serie_saldo_diario(ano, mes)

        self.ax_pizza.clear()
        self.ax_linha.clear()

        resumo_plot = resumo[resumo > 0]
        total_gastos = resumo_plot.sum()
        if total_gastos > 0:
            self.ax_pizza.pie(
                resumo_plot.values,
                labels=resumo_plot.index,
                autopct="%1.1f%%",
                startangle=90,
            )
            self.ax_pizza.set_title(f"Gastos por categoria ({mes}/{ano})")
        else:
            self.ax_pizza.text(0.5, 0.5, "Sem gastos no período", ha="center", va="center")
            self.ax_pizza.set_title("Gastos por categoria")

        if not serie.empty:
            self.ax_linha.plot(serie["Data"], serie["Saldo"], marker="o")
            self.ax_linha.set_title("Linha do tempo do saldo")
            self.ax_linha.set_xlabel("Data")
            self.ax_linha.set_ylabel("Saldo acumulado")
            inicio = datetime(ano, mes, 1)
            fim = datetime(ano, mes, calendar.monthrange(ano, mes)[1], 23, 59, 59)
            self.ax_linha.set_xlim(inicio, fim)
            self.ax_linha.xaxis.set_major_locator(mdates.AutoDateLocator())
            self.ax_linha.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
            self.ax_linha.tick_params(axis="x", rotation=35)
        else:
            self.ax_linha.text(0.5, 0.5, "Sem dados no período", ha="center", va="center")
            self.ax_linha.set_title("Linha do tempo do saldo")

        self.figura.tight_layout()
        self.canvas.draw()

    def atualizar_metas(self, periodo_valido=True):
        for widget in self.metas_container.winfo_children():
            widget.destroy()

        if not periodo_valido:
            ctk.CTkLabel(self.metas_container, text="Período inválido. Corrija mês/ano para ver metas.").grid(
                row=0, column=0, padx=8, pady=6, sticky="w"
            )
            return

        ano, mes = self._obter_periodo()
        df = progresso_metas(ano, mes)

        if df.empty:
            ctk.CTkLabel(self.metas_container, text="Nenhuma meta definida para o período.").grid(
                row=0, column=0, padx=8, pady=6, sticky="w"
            )
            return

        for i, row in df.iterrows():
            percentual = float(row["Percentual"])
            progresso = min(percentual, 1.0)
            categoria = row["Categoria"]
            gasto = float(row["Gasto"])
            limite = float(row["Limite"])

            linha = ctk.CTkFrame(self.metas_container)
            linha.grid(row=i, column=0, padx=6, pady=4, sticky="ew")
            linha.grid_columnconfigure(0, weight=1)

            texto = f"{categoria}: R$ {gasto:.2f} / R$ {limite:.2f}"
            ctk.CTkLabel(linha, text=texto).grid(row=0, column=0, padx=8, pady=(6, 2), sticky="w")

            bar = ctk.CTkProgressBar(linha)
            bar.grid(row=1, column=0, padx=8, pady=(0, 6), sticky="ew")
            bar.set(progresso)

            if percentual >= 1.0:
                status = "Limite atingido"
                cor = "red"
            elif percentual >= 0.8:
                status = "Próximo do limite"
                cor = "orange"
            else:
                status = "Dentro da meta"
                cor = "green"

            ctk.CTkLabel(linha, text=status, text_color=cor).grid(row=0, column=1, padx=8, pady=(6, 2))

    def verificar_alertas_metas(self, periodo_valido=True):
        if not periodo_valido:
            return

        ano, mes = self._obter_periodo()
        df = progresso_metas(ano, mes)
        if df.empty:
            return

        for _, row in df.iterrows():
            categoria = row["Categoria"]
            percentual = float(row["Percentual"])
            chave_base = f"{ano}-{mes}-{categoria}"
            chave_80 = f"{chave_base}-80"
            chave_100 = f"{chave_base}-100"

            if percentual >= 1.0 and chave_100 not in self.alertas_disparados:
                messagebox.showwarning(
                    "Meta estourada",
                    f"A categoria {categoria} ultrapassou o limite mensal.",
                )
                self.alertas_disparados.add(chave_100)
            elif percentual >= 0.8 and chave_80 not in self.alertas_disparados:
                messagebox.showinfo(
                    "Atenção à meta",
                    f"A categoria {categoria} já atingiu {percentual * 100:.0f}% da meta mensal.",
                )
                self.alertas_disparados.add(chave_80)

    def mostrar_relatorio_mensal(self):
        if not self._validar_periodo_inputs():
            messagebox.showwarning("Período inválido", "Corrija mês/ano antes de gerar relatório.")
            return

        ano, mes = self._obter_periodo(estrito=True)
        df, receitas, gastos, saldo = relatorio_mensal(ano, mes)

        if df is None or df.empty:
            messagebox.showinfo("Relatório", "Nenhum dado para o período informado.")
            return

        relatorio = f"Relatório ({mes}/{ano}):\n"
        relatorio += f"Receitas: R$ {receitas:.2f}\n"
        relatorio += f"Gastos: R$ {gastos:.2f}\n"
        relatorio += f"Saldo: R$ {saldo:.2f}\n\n"
        relatorio += "Lançamentos:\n"

        for _, row in df.iterrows():
            relatorio += (
                f"{row['Data']} - {row['Tipo']} - {row['Categoria']} - "
                f"R$ {row['Valor']:.2f} - {row['Descrição']}\n"
            )

        messagebox.showinfo("Relatório Mensal", relatorio)

    def salvar_excel(self):
        if not self._validar_periodo_inputs():
            messagebox.showwarning("Período inválido", "Corrija mês/ano antes de exportar para Excel.")
            return

        ano, mes = self._obter_periodo(estrito=True)
        df, receitas, gastos, saldo = relatorio_mensal(ano, mes)
        if df is None or df.empty:
            messagebox.showinfo("Relatório", "Nenhum dado para este mês.")
            return

        nome_arquivo = f"Relatorio_{ano}_{mes}.xlsx"
        df.to_excel(nome_arquivo, index=False)
        messagebox.showinfo("Relatório Excel", f"Relatório salvo como {nome_arquivo}")

    def salvar_pdf(self):
        if not self._validar_periodo_inputs():
            messagebox.showwarning("Período inválido", "Corrija mês/ano antes de exportar para PDF.")
            return

        ano, mes = self._obter_periodo(estrito=True)
        df, receitas, gastos, saldo = relatorio_mensal(ano, mes)
        if df is None or df.empty:
            messagebox.showinfo("Relatório", "Nenhum dado para este mês.")
            return

        nome_arquivo = f"Relatorio_{ano}_{mes}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Relatório Mensal ({mes}/{ano})", ln=True, align="C")
        pdf.ln(6)
        pdf.cell(200, 10, txt=f"Receitas: R$ {receitas:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Gastos: R$ {gastos:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Saldo: R$ {saldo:.2f}", ln=True)
        pdf.ln(8)

        caminho_img = None
        resumo = gastos_por_categoria(ano, mes)
        try:
            if resumo.sum() > 0:
                figura = Figure(figsize=(4, 4), dpi=120)
                eixo = figura.add_subplot(111)
                eixo.pie(resumo.values, labels=resumo.index, autopct="%1.1f%%", startangle=90)
                eixo.set_title("Gastos por categoria")

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    caminho_img = tmp.name

                figura.savefig(caminho_img, bbox_inches="tight")
                pdf.image(caminho_img, x=55, y=40, w=100)
                pdf.ln(85)

            for _, row in df.iterrows():
                linha = (
                    f"{row['Data']} - {row['Tipo']} - {row['Categoria']} - "
                    f"R$ {row['Valor']:.2f} - {row['Descrição']}"
                )
                pdf.multi_cell(0, 7, linha)

            pdf.output(nome_arquivo)
            messagebox.showinfo("Relatório PDF", f"Relatório salvo como {nome_arquivo}")
        finally:
            if caminho_img and os.path.exists(caminho_img):
                try:
                    os.remove(caminho_img)
                except OSError:
                    pass

    def abrir_banco(self):
        if os.path.exists(DB_FILE):
            try:
                os.startfile(DB_FILE)
            except AttributeError:
                subprocess.call(["open", DB_FILE])
        else:
            messagebox.showinfo("Informação", "Arquivo do banco ainda não foi criado.")


if __name__ == "__main__":
    app = AppFinanceiro()
    app.mainloop()
