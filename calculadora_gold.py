import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import platform

class CalculadoraGoldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Gold - Aika BR")
        self.root.geometry("480x500")

        self.default_items = {
            "Lingote de Heliotropo": 34452.0,
            "Couro Cristalino Rígido": 20640.0,
            "Couro Cristalino Pesado": 8720.0,
            "Vaizan Grande": 3130.0,
            "Tecido de Scotia": 7768.0
        }

        self.custom_items = {}
        self.qty_vars = {}

        # --- CORREÇÃO DO ERRO DE PERMISSÃO ---
        # Descobre qual é a pasta segura do sistema (AppData no Windows)
        if platform.system() == "Windows":
            base_path = os.getenv('APPDATA')
        else:
            base_path = os.path.expanduser("~") # Para quem usar Mac/Linux
            
        # Cria uma pastinha oficial do seu programa lá dentro
        pasta_app = os.path.join(base_path, "CalculadoraGoldAika")
        
        if not os.path.exists(pasta_app):
            os.makedirs(pasta_app)
            
        # O arquivo será salvo com segurança sem problemas de permissão
        self.arquivo_salvamento = os.path.join(pasta_app, "itens_salvos.json")
        
        self.carregar_itens_salvos()

        # Criando as Abas
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
        tax_frame = ttk.LabelFrame(self.tab_calc, text="Selecione a Taxa de Venda (%)")
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

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.build_items_list()

        btn_frame = ttk.Frame(self.tab_calc)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text="Calcular Total", command=self.calculate_total).pack(side='left')

        self.lbl_total = ttk.Label(btn_frame, text="Total de Gold: 0", font=("Arial", 12, "bold"))
        self.lbl_total.pack(side='right', padx=10)

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
        
        # Agora o erro não vai acontecer!
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
        multiplier = 1 - (tax / 100.0)
        total_gold = 0.0

        for item, var in self.qty_vars.items():
            qty_str = var.get()
            try:
                qty = int(qty_str)
            except ValueError:
                qty = 0

            if item in self.default_items:
                base_val = self.default_items[item]
            else:
                base_val = self.custom_items[item]
                
            total_gold += (base_val * multiplier) * qty

        total_arredondado = int(round(total_gold))
        total_formatado = f"{total_arredondado:,}".replace(",", ".")

        self.lbl_total.config(text=f"Total de Gold: {total_formatado}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraGoldApp(root)
    root.mainloop()
