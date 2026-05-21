import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import platform

class CalculadoraGoldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Gold - Aika BR")
        self.root.geometry("480x600")

        # --- VARIÁVEL DA COLA ADESIVA ---
        # Preço base (0% de taxa) descoberto pela matemática do jogo
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

        if platform.system() == "Windows":
            base_path = os.getenv('APPDATA')
        else:
            base_path = os.path.expanduser("~") 
            
        pasta_app = os.path.join(base_path, "CalculadoraGoldAika")
        
        if not os.path.exists(pasta_app):
            os.makedirs(pasta_app)
            
        self.arquivo_salvamento = os.path.join(pasta_app, "itens_salvos.json")
        self.carregar_itens_salvos()

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

    def setup_calc_tab(self):
        tax_frame = ttk.LabelFrame(self.tab_calc, text="Selecione a Taxa da Nação (%)")
        tax_frame.pack(fill='x', padx=10, pady=5)

        self.tax_var = tk.IntVar(value=5) 
        ttk.Radiobutton(tax_frame, text="0%", variable=self.tax_var, value=0, command=self.calculate_total).pack(side='left', padx=15, pady=5)
        ttk.Radiobutton(tax_frame, text="5%", variable=self.tax_var, value=5, command=self.calculate_total).pack(side='left', padx=15, pady=5)
        ttk.Radiobutton(tax_frame, text="15%", variable=self.tax_var, value=15, command=self.calculate_total).pack(side='left', padx=15, pady=5)

        self.items_frame = ttk.LabelFrame(self.tab_calc, text="Inventário (Nome e Quantidade)")
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

        self.craft_frame = ttk.LabelFrame(self.tab_calc, text="Estratégia de Manufatura (Pesado -> Rígido)")
        self.craft_frame.pack(fill='x', padx=10, pady=5)

        self.simular_craft_var = tk.BooleanVar(value=False)
        self.craft_critico_var = tk.BooleanVar(value=False)

        chk_craft = ttk.Checkbutton(self.craft_frame, text="Simular Manufatura (Consome 2 Pesado + 3 Colas Adesivas)", 
                                    variable=self.simular_craft_var, command=self.toggle_craft_options)
        chk_craft.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky='w')

        self.rb_normal = ttk.Radiobutton(self.craft_frame, text="Padrão (Cria 1 Rígido)", variable=self.craft_critico_var, value=False, command=self.calculate_total)
        self.rb_critico = ttk.Radiobutton(self.craft_frame, text="Crítico (Cria 2 Rígidos)", variable=self.craft_critico_var, value=True, command=self.calculate_total)
        
        self.rb_normal.grid(row=1, column=0, padx=20, pady=2, sticky='w')
        self.rb_critico.grid(row=1, column=1, padx=10, pady=2, sticky='w')

        # === CORREÇÃO: CRIAR O TEXTO DO TOTAL PRIMEIRO ===
        btn_frame = ttk.Frame(self.tab_calc)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text="Calcular Total", command=self.calculate_total).pack(side='left')

        self.lbl_total = tk.Label(btn_frame, text="Total de Gold: 0", font=("Arial", 11, "bold"), justify="right")
        self.lbl_total.pack(side='right', padx=10)

        # Agora sim a gente manda o programa testar as opções, porque a label já existe!
        self.toggle_craft_options()

    def toggle_craft_options(self):
        if self.simular_craft_var.get():
            self.rb_normal.state(['!disabled'])
            self.rb_critico.state(['!disabled'])
        else:
            self.rb_normal.state(['disabled'])
            self.rb_critico.state(['disabled'])
        self.calculate_total()

    def build_items_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.qty_vars.clear()

        ttk.Label(self.scrollable_frame, text="").grid(row=0, column=0)
        ttk.Label(self.scrollable_frame, text="Nome do Item", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        ttk.Label(self.scrollable_frame, text="Quantidade", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=10, pady=5, sticky='w')

        todos_itens = list(self.default_items.keys()) + list(self.custom_items.keys())
        
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
            
            entry = ttk.Entry(self.scrollable_frame, textvariable=var, width=15)
            entry.grid(row=row, column=2, padx=10, pady=2)
            entry.bind("<Return>", self.calculate_total)
            
            row += 1

    def setup_add_tab(self):
        frame = ttk.Frame(self.tab_add)
        frame.pack(padx=10, pady=10, fill='both', expand=True)

        ttk.Label(frame, text="Nome do Item:").grid(row=0, column=0, sticky='w', pady=10)
        self.new_item_name = tk.StringVar()
        ttk.Entry(frame, textvariable=self.new_item_name, width=25).grid(row=0, column=1, pady=10, padx=5)

        ttk.Label(frame, text="Valor Unitário do Item:").grid(row=1, column=0, sticky='w', pady=10)
        self.new_item_value = tk.StringVar()
        ttk.Entry(frame, textvariable=self.new_item_value, width=25).grid(row=1, column=1, pady=10, padx=5)

        ttk.Label(frame, text="Esse valor já é baseado em\nqual % de taxa?").grid(row=2, column=0, sticky='w', pady=10)
        self.new_item_tax = tk.IntVar(value=0)
        
        tax_cb_frame = ttk.Frame(frame)
        tax_cb_frame.grid(row=2, column=1, pady=10, sticky='w')
        ttk.Radiobutton(tax_cb_frame, text="0%", variable=self.new_item_tax, value=0).pack(side='left', padx=2)
        ttk.Radiobutton(tax_cb_frame, text="5%", variable=self.new_item_tax, value=5).pack(side='left', padx=2)
        ttk.Radiobutton(tax_cb_frame, text="15%", variable=self.new_item_tax, value=15).pack(side='left', padx=2)

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
        tax = self.new_item_tax.get()

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

        base_value = val / (1 - tax / 100.0)

        self.custom_items[name] = base_value
        self.salvar_itens_customizados()
        self.build_items_list()

        base_formatada = f"{int(round(base_value)):,}".replace(",", ".")
        messagebox.showinfo("Sucesso", f"Item '{name}' salvo com sucesso!\nValor base (0% de taxa) registrado como: {base_formatada}")

        self.new_item_name.set("")
        self.new_item_value.set("")
        self.new_item_tax.set(0)

        self.notebook.select(0)

    def calculate_total(self, event=None):
        tax = self.tax_var.get()
        # VENDER = -TAXA
        multiplier_venda = 1 - (tax / 100.0)
        # COMPRAR = +TAXA
        multiplier_compra = 1 + (tax / 100.0)

        qtys_digitadas = {}
        for item, var in self.qty_vars.items():
            try:
                qtys_digitadas[item] = int(var.get())
            except ValueError:
                qtys_digitadas[item] = 0

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

        if self.simular_craft_var.get():
            qtys_simuladas = qtys_digitadas.copy()
            nome_pesado = "Couro Cristalino Pesado"
            nome_rigido = "Couro Cristalino Rígido"
            
            qtd_pesado = qtys_simuladas.get(nome_pesado, 0)
            qtd_rigido = qtys_simuladas.get(nome_rigido, 0)

            crafts_possiveis = qtd_pesado // 2
            pesados_sobrando = qtd_pesado % 2 

            if self.craft_critico_var.get():
                rigidos_ganhos = crafts_possiveis * 2 
            else:
                rigidos_ganhos = crafts_possiveis * 1 

            qtys_simuladas[nome_pesado] = pesados_sobrando
            qtys_simuladas[nome_rigido] = qtd_rigido + rigidos_ganhos

            gold_simulado = calcular_gold_do_inventario(qtys_simuladas)

            # CÁLCULO DA COLA ADESIVA AJUSTADO PELA TAXA
            preco_cola_atual = self.preco_base_cola * multiplier_compra
            custo_colas = crafts_possiveis * 3 * preco_cola_atual
            
            total_com_craft = gold_simulado - custo_colas
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

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraGoldApp(root)
    root.mainloop()
