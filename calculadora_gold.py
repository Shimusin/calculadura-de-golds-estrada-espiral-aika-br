import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import platform
import sys
import urllib.request  # Biblioteca nativa para conectar com a internet

def obter_caminho_recurso(relative_path):
    """Retorna o caminho correto para o recurso, seja no Python puro ou embutido no .exe pelo PyInstaller"""
    try:
        # O PyInstaller cria uma pasta temporária em sys._MEIPASS ao rodar o .exe
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CalculadoraGoldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Gold - Aika BR")
        self.root.geometry("540x680") 

        # --- PALETAS DE CORES (DUAL THEME) ---
        self.current_theme = "dark" # "dark" ou "light"

        # Tema Escuro (Midnight)
        self.bg_dark = "#0b0f19"      
        self.bg_card = "#151b2d"      
        self.border_color = "#232d4b"  
        self.fg_white = "#f8fafc"      
        self.fg_gray = "#64748b"       
        self.accent_gold = "#f59e0b"   

        # Tema Claro (Daylight)
        self.bg_dark_light = "#f1f5f9"      
        self.bg_card_light = "#ffffff"      
        self.border_color_light = "#cbd5e1"  
        self.fg_white_light = "#0f172a"      
        self.fg_gray_light = "#475569"       
        self.accent_gold_light = "#d97706" 

        # Cores de feedback visual brilhantes
        self.color_success = "#10b981" 
        self.color_danger = "#ef4444"  
        self.color_warning = "#f97316" 

        # Configuração inicial do fundo
        self.root.configure(bg=self.bg_dark)

        # --- DEFINIR ÍCONE DA JANELA (.ICO) ---
        try:
            caminho_icone = obter_caminho_recurso("icone_gold.ico")
            if os.path.exists(caminho_icone):
                self.root.iconbitmap(caminho_icone)
        except Exception:
            pass

        # --- VARIÁVEIS DE DADOS ---
        self.preco_base_cola = 800.0 
        self.default_items = {
            "Lingote de Heliotropo": 34452.0,
            "Couro Cristalino Rígido": 20640.0,
            "Couro Cristalino Pesado": 8720.0,
            "Vaizan Grande": 3130.0,
            "Tecido de Scotia": 7768.0
        }
        self.custom_items = {}
        self.qty_vars = {}
        self.entries = {}      
        self.pct_labels = {}   
        
        # Variáveis de controle de travamento de inventário
        self.original_pesado_qty = 0
        self.original_rigido_qty = 0
        self.current_tab = "calc"

        # --- BANCO DE DADOS DE DROP BASE (Consid. tempo base de 1 hora) ---
        # Inicializado de acordo com o seu histórico empírico sem hiras/kaizes
        self.drop_base_database = {
            "0.0": {
                "Lingote de Heliotropo": 14.0,
                "Couro Cristalino Rígido": 9.0,
                "Couro Cristalino Pesado": 24.0,
                "Vaizan Grande": 94.0,
                "Tecido de Scotia": 9.0
            },
            "30.0": {
                "Lingote de Heliotropo": 10.0,
                "Couro Cristalino Rígido": 5.0,
                "Couro Cristalino Pesado": 22.0,
                "Vaizan Grande": 82.0,
                "Tecido de Scotia": 11.0
            },
            "60.0": {
                "Lingote de Heliotropo": 21.0,
                "Couro Cristalino Rígido": 22.0,
                "Couro Cristalino Pesado": 34.0,
                "Vaizan Grande": 215.0,
                "Tecido de Scotia": 20.0
            },
            "75.0": {
                "Lingote de Heliotropo": 71.0,
                "Couro Cristalino Rígido": 53.0,
                "Couro Cristalino Pesado": 172.0,
                "Vaizan Grande": 186.0,
                "Tecido de Scotia": 70.0
            },
            "85.0": {
                "Lingote de Heliotropo": 86.0,
                "Couro Cristalino Rígido": 53.0,
                "Couro Cristalino Pesado": 172.0,
                "Vaizan Grande": 163.0,
                "Tecido de Scotia": 75.75
            },
            "90.0": {
                "Lingote de Heliotropo": 190.64,
                "Couro Cristalino Rígido": 53.0,
                "Couro Cristalino Pesado": 172.0,
                "Vaizan Grande": 78.55,
                "Tecido de Scotia": 58.45
            }
        }

        # --- VARIÁVEIS DO TKINTER ---
        self.tax_var = tk.IntVar(value=5) 
        self.custom_tax_str = tk.StringVar(value="")
        
        self.simular_craft_var = tk.BooleanVar(value=False)
        self.craft_critico_var = tk.BooleanVar(value=False)
        self.craft_tax_var = tk.IntVar(value=5)
        self.custom_craft_tax_str = tk.StringVar(value="")

        self.new_item_name = tk.StringVar()
        self.new_item_value = tk.StringVar()
        self.new_item_tax = tk.IntVar(value=0)
        self.custom_new_item_tax_str = tk.StringVar(value="")

        # Variáveis da Aba de Simulação de Drops
        self.reliquia_rivera_lvl = tk.IntVar(value=0) 
        self.reliquia_morfhis_lvl = tk.IntVar(value=0) 
        self.bençao_aika_var = tk.BooleanVar(value=False)
        self.valente_var = tk.BooleanVar(value=False)
        self.item_drop_30_var = tk.BooleanVar(value=False)
        self.estimated_run_time_var = tk.StringVar(value="10") 

        # --- ESTILIZAÇÃO DO SCROLLBAR (TTK) ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.update_scrollbar_theme()

        # Determina local de salvamento seguro
        if platform.system() == "Windows":
            base_path = os.getenv('APPDATA')
        else:
            base_path = os.path.expanduser("~") 
            
        pasta_app = os.path.join(base_path, "CalculadoraGoldAika")
        if not os.path.exists(pasta_app):
            os.makedirs(pasta_app)
            
        self.arquivo_salvamento = os.path.join(pasta_app, "itens_salvos.json")
        self.carregar_itens_salvos()

        # --- CRIAÇÃO DO MENU DE NAVEGAÇÃO SUPERIOR (Otimizado) ---
        self.nav_frame = tk.Frame(root, bg=self.bg_dark)
        self.nav_frame.pack(fill='x', padx=10, pady=(15, 0))

        self.btn_nav_calc = tk.Button(self.nav_frame, text="Calculadora", font=("Arial", 10, "bold"), 
                                      bg=self.bg_card, fg=self.accent_gold, activebackground=self.bg_card, 
                                      activeforeground=self.accent_gold, bd=0, padx=12, pady=6, relief="flat", cursor="hand2",
                                      command=self.show_calc_tab)
        self.btn_nav_calc.pack(side='left', padx=(0, 4)) 

        # Nome alterado para "Cadastrar Item" para economizar espaço e dar um visual limpo
        self.btn_nav_add = tk.Button(self.nav_frame, text="Cadastrar Item", font=("Arial", 10, "bold"), 
                                     bg=self.bg_dark, fg=self.fg_gray, activebackground=self.bg_dark, 
                                     activeforeground=self.accent_gold, bd=0, padx=12, pady=6, relief="flat", cursor="hand2",
                                     command=self.show_add_tab)
        self.btn_nav_add.pack(side='left', padx=(0, 4))

        self.btn_nav_sim = tk.Button(self.nav_frame, text="Simular Drops", font=("Arial", 10, "bold"), 
                                     bg=self.bg_dark, fg=self.fg_gray, activebackground=self.bg_dark, 
                                     activeforeground=self.accent_gold, bd=0, padx=12, pady=6, relief="flat", cursor="hand2",
                                     command=self.show_sim_tab)
        self.btn_nav_sim.pack(side='left')

        # --- SELETOR DE TEMA EM CANVAS (DISJUNTOR FLUIDO / MODERNO) ---
        self.theme_canvas = tk.Canvas(self.nav_frame, width=80, height=28, bg=self.bg_dark, highlightthickness=0, cursor="hand2")
        self.theme_canvas.pack(side='right', pady=5, padx=10)
        
        # Clicar em QUALQUER lugar do disjuntor alterna o tema
        self.theme_canvas.bind("<Button-1>", lambda e: self.toggle_theme())

        # --- CONTAINERS DAS ABAS ---
        self.tab_calc = tk.Frame(root, bg=self.bg_dark)
        self.tab_calc.pack(fill='both', expand=True, padx=15, pady=10)

        self.tab_add = tk.Frame(root, bg=self.bg_dark)
        self.tab_sim = tk.Frame(root, bg=self.bg_dark)

        # Forçar barra de título escura no Windows
        self.aplicar_dark_bar_windows()

        self.setup_calc_tab()
        self.setup_add_tab()
        self.setup_sim_tab()

        self.reapply_theme()

    # --- CARREGAR E SALVAR AUXILIARES ---
    def carregar_itens_salvos(self):
        if os.path.exists(self.arquivo_salvamento):
            try:
                with open(self.arquivo_salvamento, 'r', encoding='utf-8') as f:
                    self.custom_items = json.load(f)
            except Exception:
                self.custom_items = {}

    def salvar_itens_customizados(self):
        try:
            with open(self.arquivo_salvamento, 'w', encoding='utf-8') as f:
                json.dump(self.custom_items, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Erro de permissão ao salvar: {e}")

    # --- SISTEMA DE TEMAS (DARK / LIGHT) ---
    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.btn_theme_toggle.config(text="☀️")
        else:
            self.current_theme = "dark"
            self.btn_theme_toggle.config(text="🌙")
        
        self.reapply_theme()
        self.aplicar_dark_bar_windows()

    def get_color(self, name):
        if self.current_theme == "dark":
            colors = {
                "bg_dark": self.bg_dark, "bg_card": self.bg_card, "border": self.border_color,
                "fg_white": self.fg_white, "fg_gray": self.fg_gray, "accent": self.accent_gold
            }
        else:
            colors = {
                "bg_dark": self.bg_dark_light, "bg_card": self.bg_card_light, "border": self.border_color_light,
                "fg_white": self.fg_white_light, "fg_gray": self.fg_gray_light, "accent": self.accent_gold_light
            }
        return colors.get(name)

    def update_scrollbar_theme(self):
        bg_card = self.get_color("bg_card")
        bg_dark = self.get_color("bg_dark")
        fg_gray = self.get_color("fg_gray")
        self.style.configure("Vertical.TScrollbar", 
                             background=bg_card, troughcolor=bg_dark, arrowcolor=fg_gray, 
                             bordercolor=bg_dark, shadowcolor=bg_dark, lightcolor=bg_card)

    def reapply_theme(self):
        bg_dark = self.get_color("bg_dark")
        bg_card = self.get_color("bg_card")
        border = self.get_color("border")
        fg_white = self.get_color("fg_white")
        fg_gray = self.get_color("fg_gray")
        accent = self.get_color("accent")

        self.root.configure(bg=bg_dark)
        self.update_scrollbar_theme()

        self.nav_frame.config(bg=bg_dark)
        self.update_theme_buttons_visuals()
        
        self.build_items_list()
        self.toggle_craft_options()
        self.atualizar_visual_navegacao()
        self.reapply_theme_widgets(self.root, bg_dark, bg_card, border, fg_white, fg_gray, accent)

    def atualizar_visual_navegacao(self):
        """Atualiza as cores dos botões de navegação conforme a aba ativa e o tema"""
        bg_dark = self.get_color("bg_dark")
        bg_card = self.get_color("bg_card")
        fg_gray = self.get_color("fg_gray")
        accent = self.get_color("accent")

        # Reseta todos os botões para o estado inativo (cinza) de uma vez só
        self.btn_nav_calc.config(bg=bg_dark, fg=fg_gray)
        self.btn_nav_add.config(bg=bg_dark, fg=fg_gray)
        self.btn_nav_sim.config(bg=bg_dark, fg=fg_gray)

        # Destaca em dourado apenas o botão da aba que está ativa na memória
        if self.current_tab == "calc":
            self.btn_nav_calc.config(bg=bg_card, fg=accent)
        elif self.current_tab == "add":
            self.btn_nav_add.config(bg=bg_card, fg=accent)
        elif self.current_tab == "sim":
            self.btn_nav_sim.config(bg=bg_card, fg=accent)

    def reapply_theme_widgets(self, parent, bg_dark, bg_card, border, fg_white, fg_gray, accent):
        for child in parent.winfo_children():
            w_type = child.winfo_class()
            
            if child in [self.btn_nav_calc, self.btn_nav_add, self.btn_nav_sim, self.theme_canvas]:
                continue

            if w_type == "Frame":
                if child in [self.tab_calc, self.tab_add, self.tab_sim, self.nav_frame]:
                    child.config(bg=bg_dark)
                else:
                    child.config(bg=bg_card)
                self.reapply_theme_widgets(child, bg_dark, bg_card, border, fg_white, fg_gray, accent)
            elif w_type == "Label":
                font_info = child.cget("font")
                if "bold" in str(font_info) and child.cget("text").isupper():
                    child.config(bg=child.master.cget("bg"), fg=accent)
                #elif child == self.lbl_warning_sim:
                    child.config(bg=child.master.cget("bg"), fg=self.color_warning)
                elif child == self.lbl_total:
                    child.config(bg=bg_dark)
                elif child in self.pct_labels.values():
                    child.config(bg=child.master.cget("bg"))
                else:
                    child.config(bg=child.master.cget("bg"), fg=fg_white)
            elif w_type == "Entry":
                child.config(bg=bg_dark, fg=fg_white, highlightbackground=border, highlightcolor=accent, insertbackground=fg_white)
            elif w_type == "Radiobutton":
                child.config(bg=child.master.cget("bg"), fg=fg_white, selectcolor=bg_dark, activebackground=child.master.cget("bg"), activeforeground=accent)
            elif w_type == "Checkbutton":
                child.config(bg=child.master.cget("bg"), fg=fg_white, selectcolor=bg_dark, activebackground=child.master.cget("bg"), activeforeground=accent)
            elif w_type == "Button":
                if child in [self.btn_calcular, self.btn_salvar, self.btn_calcular_sim]:
                    child.config(bg=accent, fg=bg_dark, activebackground=accent, activeforeground=bg_dark)
                else:
                    child.config(bg=bg_card, fg=fg_white, activebackground=bg_dark, activeforeground=accent)
            elif w_type == "Canvas":
                child.config(bg=bg_dark)
                self.reapply_theme_widgets(child, bg_dark, bg_card, border, fg_white, fg_gray, accent)
            else:
                self.reapply_theme_widgets(child, bg_dark, bg_card, border, fg_white, fg_gray, accent)

    def aplicar_dark_bar_windows(self):
        try:
            import ctypes
            self.root.update()
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
            get_parent = ctypes.windll.user32.GetParent
            hwnd = get_parent(self.root.winfo_id())
            value = ctypes.c_int(2 if self.current_theme == "dark" else 0) 
            set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
        except Exception:
            pass

    # --- ALTERNAÇÃO DE ABAS ---
    def show_calc_tab(self):
        self.tab_add.pack_forget()
        self.tab_sim.pack_forget()
        self.tab_calc.pack(fill='both', expand=True, padx=15, pady=10)
        self.current_tab = "calc"
        self.atualizar_visual_navegacao()

    def show_add_tab(self):
        self.tab_calc.pack_forget()
        self.tab_sim.pack_forget()
        self.tab_add.pack(fill='both', expand=True, padx=15, pady=10)
        self.current_tab = "add"
        self.atualizar_visual_navegacao()

    def show_sim_tab(self):
        self.tab_calc.pack_forget()
        self.tab_add.pack_forget()
        self.tab_sim.pack(fill='both', expand=True, padx=15, pady=10)
        self.current_tab = "sim"
        self.atualizar_visual_navegacao()
        self.conectar_banco_dados()

    def conectar_banco_dados(self):
        url_banco_dados = "https://raw.githubusercontent.com/Shimusin/drops_base/refs/heads/main/drops_base.json"
        try:
            req = urllib.request.Request(url_banco_dados, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2) as response:
                dados_recebidos = json.loads(response.read().decode('utf-8'))
                self.drop_base_database.update(dados_recebidos)
                print("Conectado à internet: Banco de dados de drops atualizado!")
        except Exception as e:
            print(f"Sem internet ou falha: usando banco de dados local. ({e})")

    # --- ABA DE SIMULAÇÃO DE DROPS ---
    def setup_sim_tab(self):
        self.sim_card = tk.Frame(self.tab_sim, bg=self.get_color("bg_card"), padx=15, pady=10)
        self.sim_card.pack(fill='both', expand=True, pady=(0, 10))

        tk.Label(self.sim_card, text="SIMULAR DROPS - CONFIGURAÇÃO", font=("Arial", 9, "bold"), bg=self.get_color("bg_card"), fg=self.get_color("accent")).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))

        tk.Label(self.sim_card, text="Chave Rivera:", bg=self.get_color("bg_card")).grid(row=1, column=0, sticky='w', pady=5)
        self.cb_rivera = ttk.Combobox(self.sim_card, values=["Nenhum", "Lvl 1 (+5%)", "Lvl 2 (+10%)", "Lvl 3 (+15%)"], state="readonly", width=15)
        self.cb_rivera.current(0)
        self.cb_rivera.grid(row=1, column=1, sticky='w', pady=5)

        tk.Label(self.sim_card, text="Chave Morfhis:", bg=self.get_color("bg_card")).grid(row=2, column=0, sticky='w', pady=5)
        self.cb_morfhis = ttk.Combobox(self.sim_card, values=["Nenhum", "Lvl 1 (+5%)", "Lvl 2 (+10%)", "Lvl 3 (+15%)"], state="readonly", width=15)
        self.cb_morfhis.current(0)
        self.cb_morfhis.grid(row=2, column=1, sticky='w', pady=5)

        self.chk_bençao = tk.Checkbutton(self.sim_card, text="Bênção de Aika (+30% Drop)", variable=self.bençao_aika_var,
                                         bg=self.get_color("bg_card"), fg=self.get_color("fg_white"), selectcolor=self.get_color("bg_dark"), font=("Arial", 9, "bold"), bd=0)
        self.chk_bençao.grid(row=3, column=0, columnspan=2, sticky='w', pady=5)

        self.chk_valente = tk.Checkbutton(self.sim_card, text="Relíquia Valente (+15% de bônus nas Chaves)", variable=self.valente_var,
                                          bg=self.get_color("bg_card"), fg=self.get_color("fg_white"), selectcolor=self.get_color("bg_dark"), font=("Arial", 9, "bold"), bd=0)
        self.chk_valente.grid(row=4, column=0, columnspan=2, sticky='w', pady=5)

        self.chk_itens_drop = tk.Checkbutton(self.sim_card, text="Item Consumível de Drop (+30% Max)", variable=self.item_drop_30_var,
                                             bg=self.get_color("bg_card"), fg=self.get_color("fg_white"), selectcolor=self.get_color("bg_dark"), font=("Arial", 9, "bold"), bd=0)
        self.chk_itens_drop.grid(row=5, column=0, columnspan=2, sticky='w', pady=5)

        tk.Label(self.sim_card, text="Tempo Médio da Run (min):", bg=self.get_color("bg_card")).grid(row=6, column=0, sticky='w', pady=10)
        self.entry_run_time = tk.Entry(self.sim_card, textvariable=self.estimated_run_time_var, width=10, bg=self.get_color("bg_dark"), fg=self.get_color("fg_white"),
                                       insertbackground=self.get_color("fg_white"), bd=0, highlightthickness=1, highlightbackground=self.get_color("border"), highlightcolor=self.get_color("accent"))
        self.entry_run_time.grid(row=6, column=1, sticky='w', pady=10)

        sim_btn_frame = tk.Frame(self.tab_sim, bg=self.get_color("bg_dark"))
        sim_btn_frame.pack(fill='x', pady=5)

        self.btn_calcular_sim = tk.Button(sim_btn_frame, text="Calcular Simulação", font=("Arial", 10, "bold"), bg=self.get_color("accent"), fg=self.get_color("bg_dark"),
                                          activebackground="#d97706", activeforeground=self.get_color("bg_dark"), bd=0, padx=15, pady=8, relief="flat", cursor="hand2",
                                          command=self.calcular_simulaçao_drops)
        self.btn_calcular_sim.pack(side='left')

        self.lbl_result_sim = tk.Label(sim_btn_frame, text="Gold / Run: 0\nGold / Hora: 0", font=("Arial", 11, "bold"), justify="right", 
                                       bg=self.get_color("bg_dark"), fg=self.get_color("fg_white"))
        self.lbl_result_sim.pack(side='right', padx=10)

    def calcular_simulaçao_drops(self):
        # 1. MATEMÁTICA CORRIGIDA DAS RELÍQUIAS DO AIKA
        taxa_drop_extra = 0.0
        reliquia_valores = {0: 0.0, 1: 5.0, 2: 10.0, 3: 15.0}
        
        rivera_idx = self.cb_rivera.current()
        morfhis_idx = self.cb_morfhis.current()

        # Efeito da Relíquia Valente (+15% de bônus nas chaves ativas)
        rivera_final = reliquia_valores[rivera_idx] * (1.15 if self.valente_var.get() else 1.0)
        morfhis_final = reliquia_valores[morfhis_idx] * (1.15 if self.valente_var.get() else 1.0)

        taxa_drop_extra += rivera_final + morfhis_final

        if self.bençao_aika_var.get():
            taxa_drop_extra += 30.0
        if self.item_drop_30_var.get():
            taxa_drop_extra += 30.0

        banco_float = {}
        for k, v in self.drop_base_database.items():
            try:
                banco_float[float(k)] = v
            except ValueError:
                pass

        if not banco_float:
            messagebox.showerror("Erro", "Banco de dados de drops vazio ou corrompido.")
            return

        # 2. ENCONTRA A PORCENTAGEM DISPONÍVEL MAIS PRÓXIMA (Nearest Neighbor)
        porcentagens_disponiveis = list(banco_float.keys())
        closest_tax = min(porcentagens_disponiveis, key=lambda x: abs(x - taxa_drop_extra))

        # 3. VERIFICA E EXIBE O AVISO EM UM POPUP (Se não for match exato)
        if abs(closest_tax - taxa_drop_extra) > 0.01:
            taxa_original_str = f"{taxa_drop_extra:.2f}%" if taxa_drop_extra % 1 != 0 else f"{int(taxa_drop_extra)}%"
            taxa_closest_str = f"{closest_tax:.2f}%" if closest_tax % 1 != 0 else f"{int(closest_tax)}%"
            aviso_msg = f"Não há dados sobre essa % de drop atualmente.\nMostrando dados de {taxa_closest_str} (o mais próximo disponível)."
            messagebox.showwarning("Simulação de Drop", aviso_msg)

        # Puxa os dados reais da tabela mais próxima
        drops_base_finais = banco_float[closest_tax]

        # 4. CÁLCULO DOS DROPS SÃO DE 1 RUN (Matemática correta do faturamento)
        tax_venda = self.safe_get_tax(self.tax_var, self.custom_tax_str)
        multiplier_venda = 1 - (tax_venda / 100.0)

        gold_simulado_run = 0.0
        for item in self.default_items.keys():
            qty_media = drops_base_finais.get(item, 0.0)
            base_val = self.default_items[item]
            gold_simulado_run += (base_val * multiplier_venda) * qty_media

        # 5. CÁLCULO DAS MÉTRICAS POR TEMPO (Run -> Hora)
        try:
            tempo_run = float(self.estimated_run_time_var.get().replace(',', '.'))
            if tempo_run <= 0: raise ValueError
        except ValueError:
            tempo_run = 10.0 # Fallback seguro

        runs_por_hora = 60.0 / tempo_run
        gold_simulado_hora = gold_simulado_run * runs_por_hora

        # Formatação final
        g_run_str = f"{int(round(gold_por_run := gold_simulado_run)):,}".replace(",", ".")
        g_hora_str = f"{int(round(gold_simulado_hora)):,}".replace(",", ".")

        self.lbl_result_sim.config(text=f"Gold / Run: {g_run_str}\nGold / Hora: {g_hora_str}", fg=self.color_success)

    def safe_get_tax(self, radio_var, string_var):
        val = radio_var.get()
        if val == -1: 
            try:
                txt = string_var.get().replace(',', '.').strip()
                if not txt:
                    return 0.0
                return float(txt)
            except ValueError:
                return 0.0
        return float(val)

    def on_custom_tax_change(self):
        self.tax_var.set(-1)
        self.calculate_total()

    def on_custom_craft_tax_change(self):
        self.craft_tax_var.set(-1)
        self.calculate_total()

    def setup_calc_tab(self):
        tax_frame = tk.Frame(self.tab_calc, bg=self.bg_card, padx=15, pady=10)
        tax_frame.pack(fill='x', pady=(0, 10))

        tk.Label(tax_frame, text="TAXA DA NAÇÃO - VENDA", font=("Arial", 9, "bold"), bg=self.bg_card, fg=self.accent_gold).pack(anchor='w', pady=(0, 5))

        radios_frame = tk.Frame(tax_frame, bg=self.bg_card)
        radios_frame.pack(fill='x')

        opts = [("0%", 0), ("5%", 5), ("15%", 15)]
        for text, val in opts:
            tk.Radiobutton(radios_frame, text=text, variable=self.tax_var, value=val, command=self.calculate_total,
                           bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, activebackground=self.bg_card, 
                           activeforeground=self.accent_gold, font=("Arial", 9, "bold"), bd=0, cursor="hand2").pack(side='left', padx=(0, 15))
        
        tk.Radiobutton(radios_frame, text="Outra:", variable=self.tax_var, value=-1, command=self.calculate_total,
                       bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, activebackground=self.bg_card, 
                       activeforeground=self.accent_gold, font=("Arial", 9, "bold"), bd=0, cursor="hand2").pack(side='left')
        
        self.entry_custom_tax = tk.Entry(radios_frame, textvariable=self.custom_tax_str, width=6, bg=self.bg_dark, fg=self.fg_white,
                                         insertbackground=self.fg_white, bd=0, highlightthickness=1, highlightbackground=self.border_color,
                                         highlightcolor=self.accent_gold, font=("Arial", 9, "bold"))
        self.entry_custom_tax.pack(side='left', padx=5)
        self.entry_custom_tax.bind("<KeyRelease>", lambda e: self.on_custom_tax_change())
        tk.Label(radios_frame, text="%", bg=self.bg_card, fg=self.fg_white, font=("Arial", 9, "bold")).pack(side='left')

        self.items_card = tk.Frame(self.tab_calc, bg=self.bg_card, padx=15, pady=10)
        self.items_card.pack(fill='both', expand=True, pady=(0, 10))

        tk.Label(self.items_card, text="INVENTÁRIO DE DROPS", font=("Arial", 9, "bold"), bg=self.bg_card, fg=self.accent_gold).pack(anchor='w', pady=(0, 5))

        self.canvas = tk.Canvas(self.items_card, highlightthickness=0, bg=self.bg_card)
        self.scrollbar = ttk.Scrollbar(self.items_card, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_card)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.build_items_list()

        self.craft_card = tk.Frame(self.tab_calc, bg=self.bg_card, padx=15, pady=10)
        self.craft_card.pack(fill='x', pady=(0, 10))

        tk.Label(self.craft_card, text="ESTRATÉGIA DE MANUFATURA", font=("Arial", 9, "bold"), bg=self.bg_card, fg=self.accent_gold).grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 5))

        self.chk_craft = tk.Checkbutton(self.craft_card, text="Simular Manufatura (Consome 2 Pesado + 3 Colas)", 
                                        variable=self.simular_craft_var, command=self.toggle_craft_options,
                                        bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, activebackground=self.bg_card,
                                        activeforeground=self.accent_gold, font=("Arial", 9, "bold"), bd=0, cursor="hand2")
        self.chk_craft.grid(row=1, column=0, columnspan=3, sticky='w', pady=5)

        self.rb_normal = tk.Radiobutton(self.craft_card, text="Padrão (Cria 1 Rígido)", variable=self.craft_critico_var, value=False, command=self.calculate_total,
                                        bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, activebackground=self.bg_card,
                                        activeforeground=self.accent_gold, font=("Arial", 9, "bold"), bd=0, cursor="hand2")
        self.rb_critico = tk.Radiobutton(self.craft_card, text="Crítico (Cria 2 Rígidos)", variable=self.craft_critico_var, value=True, command=self.calculate_total,
                                         bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, activebackground=self.bg_card,
                                         activeforeground=self.accent_gold, font=("Arial", 9, "bold"), bd=0, cursor="hand2")
        
        self.rb_normal.grid(row=2, column=0, padx=(10, 20), pady=2, sticky='w')
        self.rb_critico.grid(row=2, column=1, padx=10, pady=2, sticky='w')

        self.lbl_tax_cola = tk.Label(self.craft_card, text="Taxa da Cola:", bg=self.bg_card, fg=self.fg_white, font=("Arial", 9, "bold"))
        self.lbl_tax_cola.grid(row=3, column=0, padx=(10, 5), pady=10, sticky='w')

        self.cola_tax_frame = tk.Frame(self.craft_card, bg=self.bg_card)
        self.cola_tax_frame.grid(row=3, column=1, columnspan=2, pady=5, sticky='w')

        self.rb_cola_0 = tk.Radiobutton(self.cola_tax_frame, text="0%", variable=self.craft_tax_var, value=0, command=self.calculate_total,
                                        bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, activebackground=self.bg_card,
                                        font=("Arial", 9, "bold"), bd=0, cursor="hand2")
        self.rb_cola_5 = tk.Radiobutton(self.cola_tax_frame, text="5%", variable=self.craft_tax_var, value=5, command=self.calculate_total,
                                        bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, activebackground=self.bg_card,
                                        font=("Arial", 9, "bold"), bd=0, cursor="hand2")
        self.rb_cola_15 = tk.Radiobutton(self.cola_tax_frame, text="15%", variable=self.craft_tax_var, value=15, command=self.calculate_total,
                                         bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, activebackground=self.bg_card,
                                         font=("Arial", 9, "bold"), bd=0, cursor="hand2")

        self.rb_cola_0.pack(side='left', padx=(0, 10))
        self.rb_cola_5.pack(side='left', padx=(0, 10))
        self.rb_cola_15.pack(side='left', padx=(0, 10))

        self.rb_cola_custom = tk.Radiobutton(self.cola_tax_frame, text="Outra:", variable=self.craft_tax_var, value=-1, command=self.calculate_total,
                                             bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, activebackground=self.bg_card,
                                             font=("Arial", 9, "bold"), bd=0, cursor="hand2")
        self.rb_cola_custom.pack(side='left')
        
        self.entry_custom_craft_tax = tk.Entry(self.cola_tax_frame, textvariable=self.custom_craft_tax_str, width=6, bg=self.bg_dark, fg=self.fg_white,
                                               insertbackground=self.fg_white, bd=0, highlightthickness=1, highlightbackground=self.border_color,
                                               highlightcolor=self.accent_gold, font=("Arial", 9, "bold"))
        self.entry_custom_craft_tax.pack(side='left', padx=5)
        self.entry_custom_craft_tax.bind("<KeyRelease>", lambda e: self.on_custom_craft_tax_change())
        tk.Label(self.cola_tax_frame, text="%", bg=self.bg_card, fg=self.fg_white, font=("Arial", 9, "bold")).pack(side='left')

        btn_frame = tk.Frame(self.tab_calc, bg=self.bg_dark)
        btn_frame.pack(fill='x', pady=5)

        self.btn_calcular = tk.Button(btn_frame, text="Calcular Gold", font=("Arial", 10, "bold"), bg=self.accent_gold, fg=self.bg_dark,
                                      activebackground="#d97706", activeforeground=self.bg_dark, bd=0, padx=15, pady=8, relief="flat", cursor="hand2",
                                      command=self.calculate_total)
        self.btn_calcular.pack(side='left')

        self.lbl_total = tk.Label(btn_frame, text="Total de Gold: 0", font=("Arial", 11, "bold"), justify="right", 
                                  bg=self.bg_dark, fg=self.fg_white)
        self.lbl_total.pack(side='right', padx=10)

        self.toggle_craft_options()

    def toggle_craft_options(self):
        pesado_nome = "Couro Cristalino Pesado"
        rigido_nome = "Couro Cristalino Rígido"
        is_craft_active = self.simular_craft_var.get()

        if is_craft_active:
            self.rb_normal.config(state='normal')
            self.rb_critico.config(state='normal')
            self.rb_cola_0.config(state='normal')
            self.rb_cola_5.config(state='normal')
            self.rb_cola_15.config(state='normal')
            self.rb_cola_custom.config(state='normal')
            self.entry_custom_craft_tax.config(state='normal')

            if pesado_nome in self.qty_vars and rigido_nome in self.qty_vars:
                try:
                    self.original_pesado_qty = int(self.qty_vars[pesado_nome].get())
                except ValueError:
                    self.original_pesado_qty = 0

                try:
                    self.original_rigido_qty = int(self.qty_vars[rigido_nome].get())
                except ValueError:
                    self.original_rigido_qty = 0

                self.entries[pesado_nome].config(state='disabled')
                self.entries[rigido_nome].config(state='disabled')
        else:
            self.rb_normal.config(state='disabled')
            self.rb_critico.config(state='disabled')
            self.rb_cola_0.config(state='disabled')
            self.rb_cola_5.config(state='disabled')
            self.rb_cola_15.config(state='disabled')
            self.rb_cola_custom.config(state='disabled')
            self.entry_custom_craft_tax.config(state='disabled')

            if pesado_nome in self.qty_vars and rigido_nome in self.qty_vars:
                self.entries[pesado_nome].config(state='normal')
                self.entries[rigido_nome].config(state='normal')
                self.qty_vars[pesado_nome].set(str(self.original_pesado_qty))
                self.qty_vars[rigido_nome].set(str(self.original_rigido_qty))

        self.calculate_total()

    def build_items_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.qty_vars.clear()
        self.entries.clear()
        self.pct_labels.clear()

        tk.Label(self.scrollable_frame, text="", bg=self.get_color("bg_card")).grid(row=0, column=0)
        tk.Label(self.scrollable_frame, text="Nome do Item", font=("Arial", 9, "bold"), bg=self.get_color("bg_card"), fg=self.get_color("accent")).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        tk.Label(self.scrollable_frame, text="Quantidade", font=("Arial", 9, "bold"), bg=self.get_color("bg_card"), fg=self.get_color("accent")).grid(row=0, column=2, padx=10, pady=5, sticky='w')
        tk.Label(self.scrollable_frame, text="Proporção", font=("Arial", 9, "bold"), bg=self.get_color("bg_card"), fg=self.get_color("accent")).grid(row=0, column=3, padx=10, pady=5, sticky='w')

        todos_itens = list(self.default_items.keys()) + list(self.custom_items.keys())
        is_craft_active = self.simular_craft_var.get()
        
        row = 1
        for item in todos_itens:
            is_custom = item in self.custom_items
            
            if is_custom:
                btn_del = tk.Button(self.scrollable_frame, text=" X ", fg=self.color_danger, bg=self.get_color("bg_card"), 
                                    activebackground=self.get_color("bg_dark"), activeforeground=self.color_danger, 
                                    relief="flat", font=("Arial", 8, "bold"), cursor="hand2", bd=0)
                btn_del.grid(row=row, column=0, padx=5, pady=2)
                btn_del.config(command=lambda i=item: self.deletar_item(i))
            else:
                tk.Label(self.scrollable_frame, text="", bg=self.get_color("bg_card")).grid(row=row, column=0)

            tk.Label(self.scrollable_frame, text=item, bg=self.get_color("bg_card"), fg=self.get_color("fg_white")).grid(row=row, column=1, padx=5, pady=2, sticky='w')
            
            var = tk.StringVar(value="0")
            self.qty_vars[item] = var
            
            entry = tk.Entry(self.scrollable_frame, textvariable=var, width=12, bg=self.get_color("bg_dark"), fg=self.get_color("fg_white"),
                             insertbackground=self.fg_white, disabledbackground="#0a0d16", disabledforeground=self.get_color("fg_gray"),
                             bd=0, highlightthickness=1, highlightbackground=self.get_color("border"), highlightcolor=self.get_color("accent"))
            entry.grid(row=row, column=2, padx=10, pady=2)
            entry.bind("<Return>", self.calculate_total)
            self.entries[item] = entry

            if is_craft_active:
                if item == "Couro Cristalino Pesado":
                    entry.config(state='disabled')
                    var.set(str(self.original_pesado_qty % 2))
                elif item == "Couro Cristalino Rígido":
                    entry.config(state='disabled')
                    crafts = self.original_pesado_qty // 2
                    gained = crafts * 2 if self.craft_critico_var.get() else crafts * 1
                    var.set(str(self.original_rigido_qty + gained))

            lbl_pct = tk.Label(self.scrollable_frame, text="0.0%", font=("Arial", 9), bg=self.get_color("bg_card"), fg=self.get_color("fg_gray"))
            lbl_pct.grid(row=row, column=3, padx=10, pady=2, sticky='w')
            self.pct_labels[item] = lbl_pct
            
            row += 1
    
    def setup_add_tab(self):
        """Monta visualmente o painel de cadastro de novos itens"""
        add_card = tk.Frame(self.tab_add, bg=self.bg_card, padx=20, pady=20)
        add_card.pack(fill='both', expand=True, pady=10)

        tk.Label(add_card, text="CADASTRAR NOVO ITEM", font=("Arial", 10, "bold"), bg=self.bg_card, fg=self.accent_gold).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 15))

        tk.Label(add_card, text="Nome do Item:", bg=self.bg_card, fg=self.fg_white).grid(row=1, column=0, sticky='w', pady=10)
        self.entry_name = tk.Entry(add_card, textvariable=self.new_item_name, width=25, bg=self.bg_dark, fg=self.fg_white,
                                   insertbackground=self.fg_white, bd=0, highlightthickness=1, highlightbackground=self.border_color, highlightcolor=self.accent_gold)
        self.entry_name.grid(row=1, column=1, pady=10, padx=5, sticky='w')

        tk.Label(add_card, text="Valor Unitário do Item:", bg=self.bg_card, fg=self.fg_white).grid(row=2, column=0, sticky='w', pady=10)
        self.entry_val = tk.Entry(add_card, textvariable=self.new_item_value, width=25, bg=self.bg_dark, fg=self.fg_white,
                                  insertbackground=self.fg_white, bd=0, highlightthickness=1, highlightbackground=self.border_color, highlightcolor=self.accent_gold)
        self.entry_val.grid(row=2, column=1, pady=10, padx=5, sticky='w')

        tk.Label(add_card, text="Taxa do valor digitado:", bg=self.bg_card, fg=self.fg_white).grid(row=3, column=0, sticky='w', pady=10)
        
        tax_cb_frame = tk.Frame(add_card, bg=self.bg_card)
        tax_cb_frame.grid(row=3, column=1, pady=10, sticky='w')
        
        tk.Radiobutton(tax_cb_frame, text="0%", variable=self.new_item_tax, value=0, bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, font=("Arial", 9, "bold"), bd=0, cursor="hand2").pack(side='left', padx=(0, 10))
        tk.Radiobutton(tax_cb_frame, text="5%", variable=self.new_item_tax, value=5, bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, font=("Arial", 9, "bold"), bd=0, cursor="hand2").pack(side='left', padx=(0, 10))
        tk.Radiobutton(tax_cb_frame, text="15%", variable=self.new_item_tax, value=15, bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, font=("Arial", 9, "bold"), bd=0, cursor="hand2").pack(side='left', padx=(0, 10))
        
        tk.Radiobutton(tax_cb_frame, text="Outra:", variable=self.new_item_tax, value=-1, bg=self.bg_card, fg=self.fg_white, selectcolor=self.bg_dark, font=("Arial", 9, "bold"), bd=0, cursor="hand2").pack(side='left')
        self.entry_custom_new_tax = tk.Entry(tax_cb_frame, textvariable=self.custom_new_item_tax_str, width=6, bg=self.bg_dark, fg=self.fg_white,
                                             insertbackground=self.fg_white, bd=0, highlightthickness=1, highlightbackground=self.border_color, highlightcolor=self.accent_gold)
        self.entry_custom_new_tax.pack(side='left', padx=5)
        self.entry_custom_new_tax.bind("<KeyRelease>", lambda e: self.new_item_tax.set(-1))
        tk.Label(tax_cb_frame, text="%", bg=self.bg_card, fg=self.fg_white, font=("Arial", 9, "bold")).pack(side='left')

        self.btn_salvar = tk.Button(add_card, text="Salvar Novo Item", font=("Arial", 10, "bold"), bg=self.accent_gold, fg=self.bg_dark,
                                    activebackground="#d97706", activeforeground=self.bg_dark, bd=0, padx=20, pady=8, relief="flat", cursor="hand2",
                                    command=self.add_item)
        self.btn_salvar.grid(row=4, column=0, columnspan=2, pady=30, sticky='w')

    def add_item(self):
        """Lógica para calcular o valor base e salvar o item customizado"""
        name = self.new_item_name.get().strip()
        val_str = self.new_item_value.get().replace(',', '.')
        tax = self.safe_get_tax(self.new_item_tax, self.custom_new_item_tax_str)

        if not name:
            messagebox.showerror("Erro", "O nome do item não pode estar vazio.")
            return

        if name in self.default_items or name in self.custom_items:
            messagebox.showwarning("Aviso", "Já existe um item com esse nome na sua lista.")
            return

        try:
            val = float(val_str)
            if val < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Insira um valor numérico positivo para o item.")
            return

        if tax >= 100.0:
            messagebox.showerror("Erro", "A taxa não pode ser igual ou maior que 100%.")
            return

        base_value = val / (1 - tax / 100.0)

        self.custom_items[name] = base_value
        self.salvar_itens_customizados()
        self.build_items_list()

        base_formatada = f"{int(round(base_value)):,}".replace(",", ".")
        messagebox.showinfo("Sucesso", f"Item '{name}' salvo!\nValor base (0%): {base_formatada}")

        self.new_item_name.set("")
        self.new_item_value.set("")
        self.new_item_tax.set(0)
        self.custom_new_item_tax_str.set("")

        self.show_calc_tab()

    def deletar_item(self, item_name):
        resposta = messagebox.askyesno("Excluir Item", f"Deseja realmente excluir '{item_name}' da sua lista salva?")
        if resposta:
            if item_name in self.custom_items:
                del self.custom_items[item_name] 
                self.salvar_itens_customizados() 
                self.build_items_list()          
                self.calculate_total()           

    def calculate_total(self, event=None):
        tax_venda = self.safe_get_tax(self.tax_var, self.custom_tax_str)
        tax_compra_cola = self.safe_get_tax(self.craft_tax_var, self.custom_craft_tax_str)
        
        multiplier_venda = 1 - (tax_venda / 100.0)
        multiplier_compra = 1 + (tax_compra_cola / 100.0)

        qtys_digitadas = {}
        for item, var in self.qty_vars.items():
            try:
                qtys_digitadas[item] = int(var.get())
            except ValueError:
                qtys_digitadas[item] = 0

        nome_pesado = "Couro Cristalino Pesado"
        nome_rigido = "Couro Cristalino Rígido"

        if self.simular_craft_var.get():
            qtys_digitadas[nome_pesado] = self.original_pesado_qty
            qtys_digitadas[nome_rigido] = self.original_rigido_qty

        def calcular_gold_do_inventario(dicionario_quantidades):
            gold = 0.0
            for item, qty in dicionario_quantidades.items():
                if item in self.default_items:
                    base_val = self.default_items[item]
                elif item in self.custom_items:
                    base_val = self.custom_items[item]
                else:
                    base_val = 0.0
                gold += (base_val * multiplier_venda) * qty
            return gold

        total_sem_craft = calcular_gold_do_inventario(qtys_digitadas)

        qtys_finais_para_proporcao = qtys_digitadas.copy()

        if self.simular_craft_var.get():
            qtd_pesado = qtys_digitadas.get(nome_pesado, 0)
            qtd_rigido = qtys_digitadas.get(nome_rigido, 0)

            crafts_possiveis = qtd_pesado // 2
            pesados_sobrando = qtd_pesado % 2 

            if self.craft_critico_var.get():
                rigidos_ganhos = crafts_possiveis * 2 
            else:
                rigidos_ganhos = crafts_possiveis * 1 

            qtys_finais_para_proporcao[nome_pesado] = pesados_sobrando
            qtys_finais_para_proporcao[nome_rigido] = qtd_rigido + rigidos_ganhos

            if nome_pesado in self.entries and nome_rigido in self.entries:
                self.entries[nome_pesado].config(state='normal')
                self.entries[nome_rigido].config(state='normal')
                
                self.qty_vars[nome_pesado].set(str(pesados_sobrando))
                self.qty_vars[nome_rigido].set(str(qtd_rigido + rigidos_ganhos))
                
                self.entries[nome_pesado].config(state='disabled')
                self.entries[nome_rigido].config(state='disabled')

            gold_simulado = calcular_gold_do_inventario(qtys_finais_para_proporcao)

            preco_cola_atual = self.preco_base_cola * multiplier_compra
            custo_colas = crafts_possiveis * 3 * preco_cola_atual
            custo_sistema_craft = crafts_possiveis * 10
            
            total_com_craft = gold_simulado - custo_colas - custo_sistema_craft
            diferenca = total_com_craft - total_sem_craft

            tot_str = f"{int(round(total_com_craft)):,}".replace(",", ".")
            dif_str = f"{int(round(abs(diferenca))):,}".replace(",", ".")

            if diferenca > 0:
                self.lbl_total.config(text=f"Total c/ Manufatura: {tot_str}\n(+{dif_str} de Lucro!)", fg=self.color_success)
            elif diferenca < 0:
                self.lbl_total.config(text=f"Total c/ Manufatura: {tot_str}\n(-{dif_str} de Prejuízo!)", fg=self.color_danger)
            else:
                self.lbl_total.config(text=f"Total c/ Manufatura: {tot_str}\n(Elas por Elas)", fg=self.fg_white)

        else:
            tot_str = f"{int(round(total_sem_craft)):,}".replace(",", ".")
            self.lbl_total.config(text=f"Total de Gold: {tot_str}", fg=self.fg_white)

        # --- ATUALIZAÇÃO DA COLUNA DE PROPORÇÕES (PORCENTAGENS) ---
        valores_gold_finais = {}
        total_gold_bruto_finais = 0.0

        for item, qty in qtys_finais_para_proporcao.items():
            if item in self.default_items:
                base_val = self.default_items[item]
            elif item in self.custom_items:
                base_val = self.custom_items[item]
            else:
                base_val = 0.0
            
            valor_item = (base_val * multiplier_venda) * qty
            valores_gold_finais[item] = valor_item
            total_gold_bruto_finais += valor_item

        porcentagens = {}
        max_pct = -1.0
        max_item = None
        min_pct = 101.0
        min_item = None

        for item, valor in valores_gold_finais.items():
            if total_gold_bruto_finais > 0:
                pct = (valor / total_gold_bruto_finais) * 100.0
            else:
                pct = 0.0
            porcentagens[item] = pct

            if pct > max_pct and pct > 0:
                max_pct = pct
                max_item = item
            if pct < min_pct and pct > 0:
                min_pct = pct
                min_item = item

        itens_ativos = sum(1 for p in porcentagens.values() if p > 0)

        for item, lbl in self.pct_labels.items():
            pct = porcentagens.get(item, 0.0)
            
            if total_gold_bruto_finais == 0 or pct == 0:
                lbl.config(text="0.0%", fg=self.fg_gray, font=("Arial", 9))
            elif item == max_item and max_pct > 0:
                lbl.config(text=f"▲ {pct:.1f}%", fg=self.color_success, font=("Arial", 9, "bold"))
            elif item == min_item and itens_ativos > 1:
                lbl.config(text=f"▼ {pct:.1f}%", fg=self.color_warning, font=("Arial", 9, "bold"))
            else:
                lbl.config(text=f"{pct:.1f}%", fg=self.fg_white, font=("Arial", 9))

    def toggle_theme(self):
        """Alterna entre o modo claro e escuro de forma fluida"""
        if self.current_theme == "dark":
            self.current_theme = "light"
        else:
            self.current_theme = "dark"
        self.reapply_theme()
        self.aplicar_dark_bar_windows()

    def update_theme_buttons_visuals(self):
        """Desenha o disjuntor minimalista com ícones do Sol e Lua do lado de fora"""
        # Limpa desenhos anteriores
        self.theme_canvas.delete("all")
        
        bg_dark = self.get_color("bg_dark")
        bg_card = self.get_color("bg_card")
        fg_gray = self.get_color("fg_gray")
        accent = self.get_color("accent")
        
        # Sincroniza o fundo do canvas com o tema atual
        self.theme_canvas.config(bg=bg_dark)
        
        # 1. Desenha a pílula de fundo (Trough) centralizada
        # O trilho vai de x=30 a x=50, criando um switch compacto e clean
        self.theme_canvas.create_line(30, 14, 50, 14, width=18, capstyle="round", fill=bg_card)
        
        # 2. Configura a posição da bolinha e a cor ativa dos ícones externos
        if self.current_theme == "dark":
            knob_x = 50
            knob_color = accent      # Bolinha ouro ativo na direita
            sun_color = fg_gray      # Sol inativo (cinza na esquerda)
            moon_color = accent      # Lua ativa (ouro na direita)
        else:
            knob_x = 30
            knob_color = fg_gray     # Bolinha cinza ativo na esquerda
            sun_color = accent       # Sol ativo (ouro na esquerda)
            moon_color = fg_gray     # Lua inativa (cinza na direita)
            
        # 3. Desenha os ícones do lado de fora (Sol na esquerda, Lua na direita)
        # Posicionados estrategicamente nas pontas externa (x=12 e x=68)
        self.theme_canvas.create_text(16, 14, text="☀️", font=("Arial", 9), fill=sun_color)
        self.theme_canvas.create_text(68, 12, text="🌙", font=("Arial", 9), fill=moon_color)
        
        # 4. Desenha a bolinha deslizante lisa e minimalista (sem nada dentro)
        # Raio de 7 para deslizar perfeitamente dentro do trilho de largura 18
        r = 7  
        self.theme_canvas.create_oval(knob_x - r, 14 - r, knob_x + r, 14 + r, fill=knob_color, outline="")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraGoldApp(root)
    root.mainloop()
