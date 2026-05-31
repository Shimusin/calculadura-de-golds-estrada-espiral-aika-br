import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import platform

class CalculadoraGoldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Gold - Aika BR")
        self.root.geometry("520x680") 

        # --- PALETA DE CORES PREMIUM ---
        self.bg_dark = "#0b0f19"      # Azul Espacial Profundo (Fundo principal)
        self.bg_card = "#151b2d"      # Azul de Alta Tecnologia (Cards e inputs)
        self.border_color = "#232d4b"  # Slate escuro para bordas sutis
        self.fg_white = "#f8fafc"      # Branco Suave para textos principais
        self.fg_gray = "#64748b"       # Cinza Slate para textos secundários
        self.accent_gold = "#f59e0b"   # Ouro/Amber para destaques ativos
        
        # Cores de feedback visual brilhantes
        self.color_success = "#10b981" # Verde Esmeralda
        self.color_danger = "#ef4444"  # Vermelho Coral
        self.color_warning = "#f97316" # Laranja

        self.root.configure(bg=self.bg_dark)

        # --- FORÇAR BARRA DE TÍTULO ESCURA NO WINDOWS ---
        try:
            import ctypes
            self.root.update()
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
            get_parent = ctypes.windll.user32.GetParent
            hwnd = get_parent(self.root.winfo_id())
            value = ctypes.c_int(2)  # Ativa o modo escuro imersivo nativo
            set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
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
        
        self.original_pesado_qty = 0
        self.original_rigido_qty = 0

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

        # --- ESTILIZAÇÃO DO SCROLLBAR ESCURO (TTK) ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Vertical.TScrollbar", 
                             background=self.bg_card, 
                             troughcolor=self.bg_dark, 
                             arrowcolor=self.fg_gray, 
                             bordercolor=self.bg_dark, 
                             shadowcolor=self.bg_dark, 
                             lightcolor=self.bg_card)

        # Carregar arquivos salvos
        if platform.system() == "Windows":
            base_path = os.getenv('APPDATA')
        else:
            base_path = os.path.expanduser("~") 
            
        pasta_app = os.path.join(base_path, "CalculadoraGoldAika")
        if not os.path.exists(pasta_app):
            os.makedirs(pasta_app)
            
        self.arquivo_salvamento = os.path.join(pasta_app, "itens_salvos.json")
        self.carregar_itens_salvos()

        # --- CRIAÇÃO DO MENU DE NAVEGAÇÃO SUPERIOR ---
        self.nav_frame = tk.Frame(root, bg=self.bg_dark)
        self.nav_frame.pack(fill='x', padx=15, pady=(15, 0))

        # CORREGIDO: Trocado marginRight por padx=(0, 5)
        self.btn_nav_calc = tk.Button(self.nav_frame, text="Calculadora", font=("Arial", 10, "bold"), 
                                      bg=self.bg_card, fg=self.accent_gold, activebackground=self.bg_card, 
                                      activeforeground=self.accent_gold, bd=0, padx=20, pady=8, relief="flat", cursor="hand2",
                                      command=self.show_calc_tab)
        self.btn_nav_calc.pack(side='left', padx=(0, 5)) 

        self.btn_nav_add = tk.Button(self.nav_frame, text="Adicionar Novo Item", font=("Arial", 10, "bold"), 
                                     bg=self.bg_dark, fg=self.fg_gray, activebackground=self.bg_dark, 
                                     activeforeground=self.accent_gold, bd=0, padx=20, pady=8, relief="flat", cursor="hand2",
                                     command=self.show_add_tab)
        self.btn_nav_add.pack(side='left')

        # --- CONTAINERS DAS ABAS ---
        self.tab_calc = tk.Frame(root, bg=self.bg_dark)
        self.tab_calc.pack(fill='both', expand=True, padx=15, pady=10)

        self.tab_add = tk.Frame(root, bg=self.bg_dark)

        self.setup_calc_tab()
        self.setup_add_tab()

    def show_calc_tab(self):
        self.tab_add.pack_forget()
        self.tab_calc.pack(fill='both', expand=True, padx=15, pady=10)
        self.btn_nav_calc.config(bg=self.bg_card, fg=self.accent_gold)
        self.btn_nav_add.config(bg=self.bg_dark, fg=self.fg_gray)

    def show_add_tab(self):
        self.tab_calc.pack_forget()
        self.tab_add.pack(fill='both', expand=True, padx=15, pady=10)
        self.btn_nav_calc.config(bg=self.bg_dark, fg=self.fg_gray)
        self.btn_nav_add.config(bg=self.bg_card, fg=self.accent_gold)

    # --- SISTEMA DE SALVAMENTO ---
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

    # --- MONTAGEM DA INTERFACE ---
    def setup_calc_tab(self):
        # 1. CARD: Seleção da Taxa de Venda
        tax_card = tk.Frame(self.tab_calc, bg=self.bg_card, padx=15, pady=10)
        tax_card.pack(fill='x', pady=(0, 10))

        tk.Label(tax_card, text="TAXA DA NAÇÃO - VENDA", font=("Arial", 9, "bold"), bg=self.bg_card, fg=self.accent_gold).pack(anchor='w', pady=(0, 5))

        radios_frame = tk.Frame(tax_card, bg=self.bg_card)
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

        # 2. CARD: Inventário de Itens
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

        # 3. CARD: Painel de Estratégia de Manufatura
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

        # 4. RODAPÉ: Botão de Calcular e Resultado
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

        # Cabeçalhos
        tk.Label(self.scrollable_frame, text="", bg=self.bg_card).grid(row=0, column=0)
        tk.Label(self.scrollable_frame, text="Nome do Item", font=("Arial", 9, "bold"), bg=self.bg_card, fg=self.accent_gold).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        tk.Label(self.scrollable_frame, text="Quantidade", font=("Arial", 9, "bold"), bg=self.bg_card, fg=self.accent_gold).grid(row=0, column=2, padx=10, pady=5, sticky='w')
        tk.Label(self.scrollable_frame, text="Proporção", font=("Arial", 9, "bold"), bg=self.bg_card, fg=self.accent_gold).grid(row=0, column=3, padx=10, pady=5, sticky='w')

        todos_itens = list(self.default_items.keys()) + list(self.custom_items.keys())
        is_craft_active = self.simular_craft_var.get()
        
        row = 1
        for item in todos_itens:
            is_custom = item in self.custom_items
            
            if is_custom:
                btn_del = tk.Button(self.scrollable_frame, text=" X ", fg=self.color_danger, bg=self.bg_card, 
                                    activebackground=self.bg_dark, activeforeground=self.color_danger, 
                                    relief="flat", font=("Arial", 8, "bold"), cursor="hand2", bd=0)
                btn_del.grid(row=row, column=0, padx=5, pady=2)
                btn_del.config(command=lambda i=item: self.deletar_item(i))
            else:
                tk.Label(self.scrollable_frame, text="", bg=self.bg_card).grid(row=row, column=0)

            tk.Label(self.scrollable_frame, text=item, bg=self.bg_card, fg=self.fg_white).grid(row=row, column=1, padx=5, pady=2, sticky='w')
            
            var = tk.StringVar(value="0")
            self.qty_vars[item] = var
            
            entry = tk.Entry(self.scrollable_frame, textvariable=var, width=12, bg=self.bg_dark, fg=self.fg_white,
                             insertbackground=self.fg_white, disabledbackground="#0a0d16", disabledforeground=self.fg_gray,
                             bd=0, highlightthickness=1, highlightbackground=self.border_color, highlightcolor=self.accent_gold)
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

            lbl_pct = tk.Label(self.scrollable_frame, text="0.0%", font=("Arial", 9), bg=self.bg_card, fg=self.fg_gray)
            lbl_pct.grid(row=row, column=3, padx=10, pady=2, sticky='w')
            self.pct_labels[item] = lbl_pct
            
            row += 1

    def setup_add_tab(self):
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

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraGoldApp(root)
    root.mainloop()
