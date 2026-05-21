import tkinter as tk
from tkinter import ttk, messagebox

class CalculadoraGoldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Gold - Estrada Espiral")
        self.root.geometry("450x450")

        # 1. Os 5 itens setados por padrão definidos por você
        self.items = {
            "Lingote de Heliotropo": 34452.0,
            "Couro Cristalino Rígido": 20640.0,
            "Couro Cristalino Pesado": 8720.0,
            "Vaizan Grande": 3130.0,
            "Tecido de Scotia": 7768.0
        }

        self.qty_vars = {}

        # 2. Criando as Abas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=10, pady=10, fill='both', expand=True)

        self.tab_calc = ttk.Frame(self.notebook)
        self.tab_add = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_calc, text="Calculadora")
        self.notebook.add(self.tab_add, text="Adicionar Novo Item")

        self.setup_calc_tab()
        self.setup_add_tab()

    def setup_calc_tab(self):
        # --- Seção de Botões de Seleção da Taxa ---
        tax_frame = ttk.LabelFrame(self.tab_calc, text="Selecione a Taxa de Venda (%)")
        tax_frame.pack(fill='x', padx=10, pady=5)

        self.tax_var = tk.IntVar(value=5) # 5% como padrão
        ttk.Radiobutton(tax_frame, text="0%", variable=self.tax_var, value=0, command=self.calculate_total).pack(side='left', padx=15, pady=5)
        ttk.Radiobutton(tax_frame, text="5%", variable=self.tax_var, value=5, command=self.calculate_total).pack(side='left', padx=15, pady=5)
        ttk.Radiobutton(tax_frame, text="15%", variable=self.tax_var, value=15, command=self.calculate_total).pack(side='left', padx=15, pady=5)

        # --- Seção da Lista de Itens ---
        self.items_frame = ttk.LabelFrame(self.tab_calc, text="Inventário (Nome e Quantidade)")
        self.items_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.build_items_list()

        # --- Botão de Calcular e Resultado ---
        btn_frame = ttk.Frame(self.tab_calc)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text="Calcular Total", command=self.calculate_total).pack(side='left')

        self.lbl_total = ttk.Label(btn_frame, text="Total de Gold: 0", font=("Arial", 12, "bold"))
        self.lbl_total.pack(side='right', padx=10)

    def build_items_list(self):
        # Limpa a lista atual 
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        self.qty_vars.clear()

        # Cabeçalho
        ttk.Label(self.items_frame, text="Nome do Item", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        ttk.Label(self.items_frame, text="Quantidade", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=10, pady=5, sticky='w')

        # Cria uma linha para cada item
        row = 1
        for item in self.items:
            ttk.Label(self.items_frame, text=item).grid(row=row, column=0, padx=10, pady=2, sticky='w')
            
            var = tk.StringVar(value="0")
            self.qty_vars[item] = var
            
            # Caixa de digitação da quantidade
            entry = ttk.Entry(self.items_frame, textvariable=var, width=15)
            entry.grid(row=row, column=1, padx=10, pady=2)
            
            # Faz a tecla "Enter" acionar o cálculo automático
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

    def add_item(self):
        name = self.new_item_name.get().strip()
        val_str = self.new_item_value.get().replace(',', '.')
        tax = self.new_item_tax.get()

        if not name:
            messagebox.showerror("Erro", "O nome do item não pode estar vazio.")
            return

        try:
            val = float(val_str)
            if val < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Insira um valor numérico positivo para o item.")
            return

        base_value = val / (1 - tax / 100.0)

        self.items[name] = base_value
        self.build_items_list()

        # O formata_base apenas arredonda e coloca o ponto para exibir na mensagem de sucesso
        base_formatada = f"{int(round(base_value)):,}".replace(",", ".")
        messagebox.showinfo("Sucesso", f"Item '{name}' adicionado com sucesso!\nValor base (0% de taxa) registrado como: {base_formatada}")

        self.new_item_name.set("")
        self.new_item_value.set("")
        self.new_item_tax.set(0)

        self.notebook.select(0)

    # O "event=None" é necessário para que a tecla "Enter" consiga chamar a função
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

            base_val = self.items[item]
            total_gold += (base_val * multiplier) * qty

        # Arredonda o valor total (tira os centavos)
        total_arredondado = int(round(total_gold))
        
        # Formata o número colocando ponto na grandeza de milhar (Ex: 1000 -> 1.000)
        total_formatado = f"{total_arredondado:,}".replace(",", ".")

        self.lbl_total.config(text=f"Total de Gold: {total_formatado}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraGoldApp(root)
    root.mainloop()