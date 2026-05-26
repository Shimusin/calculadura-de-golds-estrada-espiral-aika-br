import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import platform

class CalculadoraGoldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Gold - Aika BR")
        self.root.geometry("520x640") 

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

        # --- VARIÁVEIS DO TKINTER (Declaradas no início para evitar erros de ordem de carregamento) ---
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

        # Carregamento de arquivos
        if platform.system() == "Windows":
            base_path = os.getenv('APPDATA')
        else:
            base_path = os.path.expanduser("~") 
            
        pasta_app = os.path.join(base_path, "CalculadoraGoldAika")
        
        if not os.path.exists(pasta_app):
            os.makedirs(pasta_app)
            
        self.arquivo_salvamento = os.path.join(pasta_app, "itens_salvos.json")
        self.carregar_itens_salvos()

        # Configuração das Abas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=10, pady=10, fill='both', expand=True)

        self.tab_calc = ttk.Frame(self.notebook)
        self.tab_add = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_calc, text="Calculadora")
        self.notebook.add(self.tab_add, text="Adicionar Novo Item")

        self.setup_calc_tab()
        self.setup_add_tab()

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

    def setup_calc_tab(self):
        # 1. Seleção da Taxa (Venda)
        tax_frame = ttk.LabelFrame(self.tab_calc, text="Selecione a Taxa da Nação - Venda (%)")
        tax_frame.pack(fill='x', padx=10, pady=5)

        ttk.Radiobutton(tax_frame, text="0%", variable=self.tax_var, value=0, command=self.calculate_total).pack(side='left', padx=10, pady=5)
        ttk.Radiobutton(tax_frame, text="5%", variable=self.tax_var, value=5, command=self.calculate_total).pack(side='left', padx=10, pady=5)
        ttk.Radiobutton(tax_frame, text="15%", variable=self.tax_var, value=15, command=self.calculate_total).pack(side='left', padx=10, pady=5)
        
        ttk.Radiobutton(tax_frame, text="Outra:", variable=self.tax_var, value=-1, command=self.calculate_total).pack(side='left', padx=5, pady=5)
        self.entry_custom_tax = ttk.Entry(tax_frame, textvariable=self.custom_tax_str, width=6)
        self.entry_custom_tax.pack(side='left', padx=2, pady=5)
        self.entry_custom_tax.bind("<KeyRelease>", lambda e: self.on_custom_tax_change())
        ttk.Label(tax_frame, text="%").pack(side='left', pady=5)

        # 2. Lista de Itens (Inventário)
        self.items_frame = ttk.LabelFrame(self.tab_calc, text="Inventário (Nome, Qtd e Proporção de Valor)")
        self.items_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(self.items_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.items_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.build_items_list()

        # 3. Painel de Estratégia de Manufatura
        self.craft_frame = ttk.LabelFrame(self.tab_calc, text="Estratégia de Manufatura (Pesado -> Rígido)")
        self.craft_frame.pack(fill='x', padx=10, pady=5)

        chk_craft = ttk.Checkbutton(self.craft_frame, text="Simular Manufatura (Consome 2 Pesado + 3 Colas Adesivas)", 
                                    variable=self.simular_craft_var, command=self.toggle_craft_options)
        chk_craft.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky='w')

        self.rb_normal = ttk.Radiobutton(self.craft_frame, text="Padrão (Cria 1 Rígido)", variable=self.craft_critico_var, value=False, command=self.calculate_total)
        self.rb_critico = ttk.Radiobutton(self.craft_frame, text="Crítico (Cria 2 Rígidos)", variable=self.craft_critico_var, value=True, command=self.calculate_total)
        
        self.rb_normal.grid(row=1, column=0, padx=20, pady=2, sticky='w')
        self.rb_critico.grid(row=1, column=1, padx=10, pady=2, sticky='w')

        self.lbl_tax_cola = ttk.Label(self.craft_frame, text="Taxa de Compra da Cola:")
        self.lbl_tax_cola.grid(row=2, column=0, padx=20, pady=5, sticky='w')

        self.cola_tax_frame = ttk.Frame(self.craft_frame)
        self.cola_tax_frame.grid(row=2, column=1, columnspan=2, pady=5, sticky='w')

        self.rb_cola_0 = ttk.Radiobutton(self.cola_tax_frame, text="0%", variable=self.craft_tax_var, value=0, command=self.calculate_total)
        self.rb_cola_5 = ttk.Radiobutton(self.cola_tax_frame, text="5%", variable=self.craft_tax_var, value=5, command=self.calculate_total)
        self.rb_cola_15 = ttk.Radiobutton(self.cola_tax_frame, text="15%", variable=self.craft_tax_var, value=15, command=self.calculate_total)

        self.rb_cola_0.pack(side='left', padx=5)
        self.rb_cola_5.pack(side='left', padx=5)
        self.rb_cola_15.pack(side='left', padx=5)

        self.rb_cola_custom = ttk.Radiobutton(self.cola_tax_frame, text="Outra:", variable=self.craft_tax_var, value=-1, command=self.calculate_total)
        self.rb_cola_custom.pack(side='left', padx=5)
        
        self.entry_custom_craft_tax = ttk.Entry(self.cola_tax_frame, textvariable=self.custom_craft_tax_str, width=6)
        self.entry_custom_craft_tax.pack(side='left', padx=2)
        self.entry_custom_craft_tax.bind("<KeyRelease>", lambda e: self.on_custom_craft_tax_change())
        ttk.Label(self.cola_tax_frame, text="%").pack(side='left')

        # 4. Botão Calcular e Resultado
        btn_frame = ttk.Frame(self.tab_calc)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text="Calcular Total", command=self.calculate_total).pack(side='left')

        self.lbl_total = tk.Label(btn_frame, text="Total de Gold: 0", font=("Arial", 11, "bold"), justify="right")
        self.lbl_total.pack(side='right', padx=10)

        self.toggle_craft_options()

    def toggle_craft_options(self):
        pesado_nome = "Couro Cristalino Pesado"
        is_craft_active = self.simular_craft_var.get()

        if is_craft_active:
            self.rb_normal.state(['!disabled'])
            self.rb_critico.state(['!disabled'])
            self.rb_cola_0.state(['!disabled'])
            self.rb_cola_5.state(['!disabled'])
            self.rb_cola_15.state(['!disabled'])
            self.rb_cola_custom.state(['!disabled'])
            self.entry_custom_craft_tax.state(['!disabled'])

            if pesado_nome in self.qty_vars and pesado_nome in self.entries:
                try:
                    self.original_pesado_qty = int(self.qty_vars[pesado_nome].get())
                except ValueError:
                    self.original_pesado_qty = 0

                leftover = self.original_pesado_qty % 2
                self.qty_vars[pesado_nome].set(str(leftover))
                self.entries[pesado_nome].config(state='disabled')
        else:
            self.rb_normal.state(['disabled'])
            self.rb_critico.state(['disabled'])
            self.rb_cola_0.state(['disabled'])
            self.rb_cola_5.state(['disabled'])
            self.rb_cola_15.state(['disabled'])
            self.rb_cola_custom.state(['disabled'])
            self.entry_custom_craft_tax.state(['disabled'])

            if pesado_nome in self.qty_vars and pesado_nome in self.entries:
                self.entries[pesado_nome].config(state='normal')
                self.qty_vars[pesado_nome].set(str(self.original_pesado_qty))

        self.calculate_total()

    def build_items_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.qty_vars.clear()
        self.entries.clear()
        self.pct_labels.clear()

        # Cabeçalhos
        ttk.Label(self.scrollable_frame, text="").grid(row=0, column=0)
        ttk.Label(self.scrollable_frame, text="Nome do Item", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        ttk.Label(self.scrollable_frame, text="Quantidade", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=10, pady=5, sticky='w')
        ttk.Label(self.scrollable_frame, text="Proporção", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=10, pady=5, sticky='w')

        todos_itens = list(self.default_items.keys()) + list(self.custom_items.keys())
        is_craft_active = self.simular_craft_var.get()
        
        row = 1
        for item in todos_itens:
            is_custom = item in self.custom_items
            
            if is_custom:
                btn_del = tk.Button(self.scrollable_frame, text=" X ", fg="red", relief="flat", font=("Arial", 8, "bold"),
                                    cursor="hand2", command=lambda i=item: self.deletar_item(i))
                btn_del.grid(row=row, column=0, padx=5, pady=2)
            else:
                ttk.Label(self.scrollable_frame, text="").grid(row=row, column=0)

            ttk.Label(self.scrollable_frame, text=item).grid(row=row, column=1, padx=5, pady=2, sticky='w')
            
            var = tk.StringVar(value="0")
            self.qty_vars[item] = var
            
            entry = ttk.Entry(self.scrollable_frame, textvariable=var, width=12)
            entry.grid(row=row, column=2, padx=10, pady=2)
            entry.bind("<Return>", self.calculate_total)
            self.entries[item] = entry

            if item == "Couro Cristalino Pesado" and is_craft_active:
                entry.config(state='disabled')
                var.set(str(self.original_pesado_qty % 2))

            lbl_pct = tk.Label(self.scrollable_frame, text="0.0%", font=("Arial", 9), fg="gray")
            lbl_pct.grid(row=row, column=3, padx=10, pady=2, sticky='w')
            self.pct_labels[item] = lbl_pct
            
            row += 1

    def setup_add_tab(self):
        frame = ttk.Frame(self.tab_add)
        frame.pack(padx=10, pady=10, fill='both', expand=True)

        ttk.Label(frame, text="Nome do Item:").grid(row=0, column=0, sticky='w', pady=10)
        ttk.Entry(frame, textvariable=self.new_item_name, width=25).grid(row=0, column=1, pady=10, padx=5)

        ttk.Label(frame, text="Valor Unitário do Item:").grid(row=1, column=0, sticky='w', pady=10)
        ttk.Entry(frame, textvariable=self.new_item_value, width=25).grid(row=1, column=1, pady=10, padx=5)

        ttk.Label(frame, text="Esse valor já é baseado em\nqual % de taxa?").grid(row=2, column=0, sticky='w', pady=10)
        
        tax_cb_frame = ttk.Frame(frame)
        tax_cb_frame.grid(row=2, column=1, pady=10, sticky='w')
        ttk.Radiobutton(tax_cb_frame, text="0%", variable=self.new_item_tax, value=0).pack(side='left', padx=2)
        ttk.Radiobutton(tax_cb_frame, text="5%", variable=self.new_item_tax, value=5).pack(side='left', padx=2)
        ttk.Radiobutton(tax_cb_frame, text="15%", variable=self.new_item_tax, value=15).pack(side='left', padx=2)
        
        ttk.Radiobutton(tax_cb_frame, text="Outra:", variable=self.new_item_tax, value=-1).pack(side='left', padx=2)
        self.entry_custom_new_tax = ttk.Entry(tax_cb_frame, textvariable=self.custom_new_item_tax_str, width=6)
        self.entry_custom_new_tax.pack(side='left', padx=2)
        self.entry_custom_new_tax.bind("<KeyRelease>", lambda e: self.new_item_tax.set(-1))
        ttk.Label(tax_cb_frame, text="%").pack(side='left')

        ttk.Button(frame, text="Adicionar Item", command=self.add_item).grid(row=3, column=0, columnspan=2, pady=20)

    def deletar_item(self, item_name):
        resposta = messagebox.askyesno("Excluir Item", f"Deseja realmente excluir '{item_name}' da sua lista salva?")
        if resposta:
            if item_name in self.custom_items:
                del self.custom_items[item_name] 
                self.salvar_itens_customizados() 
                self.build_items_list()          
                self.calculate_total()           

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

        self.notebook.select(0)

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

            gold_simulado = calcular_gold_do_inventario(qtys_finais_para_proporcao)

            preco_cola_atual = self.preco_base_cola * multiplier_compra
            custo_colas = crafts_possiveis * 3 * preco_cola_atual
            custo_sistema_craft = crafts_possiveis * 10
            
            total_com_craft = gold_simulado - custo_colas - custo_sistema_craft
            diferenca = total_com_craft - total_sem_craft

            tot_str = f"{int(round(total_com_craft)):,}".replace(",", ".")
            dif_str = f"{int(round(abs(diferenca))):,}".replace(",", ".")

            if diferenca > 0:
                self.lbl_total.config(text=f"Total c/ Manufatura: {tot_str}\n(+{dif_str} de Lucro!)", fg="green")
            elif diferenca < 0:
                self.lbl_total.config(text=f"Total c/ Manufatura: {tot_str}\n(-{dif_str} de Prejuízo!)", fg="red")
            else:
                self.lbl_total.config(text=f"Total c/ Manufatura: {tot_str}\n(Elas por Elas / Sem lucro)", fg="black")

        else:
            tot_str = f"{int(round(total_sem_craft)):,}".replace(",", ".")
            self.lbl_total.config(text=f"Total de Gold: {tot_str}", fg="black")

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
                lbl.config(text="0.0%", fg="gray", font=("Arial", 9))
            elif item == max_item and max_pct > 0:
                lbl.config(text=f"▲ {pct:.1f}%", fg="#2e7d32", font=("Arial", 9, "bold"))
            elif item == min_item and itens_ativos > 1:
                lbl.config(text=f"▼ {pct:.1f}%", fg="#d84315", font=("Arial", 9, "bold"))
            else:
                lbl.config(text=f"{pct:.1f}%", fg="black", font=("Arial", 9))

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraGoldApp(root)
    root.mainloop()
