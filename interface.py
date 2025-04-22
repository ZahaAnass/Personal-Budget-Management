import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import csv

class BudgetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Budget Manager")
        self.root.geometry("1200x700")
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#f0f0f0",
                        fieldbackground="#ffffff", foreground="#333333")
        style.configure("TButton", padding=6)
        style.configure("Success.TButton", background="#28a745")
        style.configure("Danger.TButton", background="#dc3545")

    def create_widgets(self):
        # Create main container
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Transactions
        self.left_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.left_frame, weight=2)

        # Transaction controls
        controls_frame = ttk.Frame(self.left_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(controls_frame, text="Add Transaction", 
                    command=self.show_transaction_form, style="Success.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Delete Selected", 
                    command=self.delete_transaction, style="Danger.TButton").pack(side=tk.LEFT, padx=5)

        # Search and filters
        filter_frame = ttk.LabelFrame(self.left_frame, text="Filters")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT, padx=5)
        self.category_filter = ttk.Combobox(filter_frame, width=15)
        self.category_filter.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.type_filter = ttk.Combobox(filter_frame, width=10, 
                                        values=["All", "Income", "Expense"])
        self.type_filter.pack(side=tk.LEFT, padx=5)
        self.type_filter.set("All")

        ttk.Button(filter_frame, text="Apply Filters", 
                    command=self.apply_filters).pack(side=tk.LEFT, padx=5)

        # Transactions table
        columns = ("ID", "Date", "Type", "Category", "Amount", "Description")
        self.tree = ttk.Treeview(self.left_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            width = 100 if col != "Description" else 200
            self.tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right panel - Charts and Budget
        self.right_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.right_frame, weight=1)

        # Monthly summary
        self.summary_frame = ttk.LabelFrame(self.right_frame, text="Monthly Summary")
        self.summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.summary_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Budget section
        budget_frame = ttk.LabelFrame(self.right_frame, text="Budget Management")
        budget_frame.pack(fill=tk.X)
        
        ttk.Button(budget_frame, text="Set Budget", 
                    command=self.show_budget_form).pack(pady=5)
        
        self.budget_tree = ttk.Treeview(budget_frame, columns=("Category", "Budget", "Spent", "Remaining"),
                                        show="headings", height=8)
        for col in ("Category", "Budget", "Spent", "Remaining"):
            self.budget_tree.heading(col, text=col)
            self.budget_tree.column(col, width=80)
        self.budget_tree.pack(fill=tk.X, pady=5)

        # Export button
        ttk.Button(self.right_frame, text="Export to CSV", 
                    command=self.export_to_csv).pack(pady=10)

        self.update_display()

    def show_transaction_form(self, transaction=None):
        form = tk.Toplevel(self.root)
        form.title("Add Transaction" if not transaction else "Edit Transaction")
        form.geometry("400x450")
        
        # Form fields
        ttk.Label(form, text="Date:").pack(pady=5)
        date_entry = DateEntry(form, width=20, background='darkblue', 
                                foreground='white', borderwidth=2)
        date_entry.pack(pady=5)
        
        ttk.Label(form, text="Type:").pack(pady=5)
        type_combo = ttk.Combobox(form, values=["Income", "Expense"])
        type_combo.pack(pady=5)
        
        ttk.Label(form, text="Category:").pack(pady=5)
        category_combo = ttk.Combobox(form, values=["Food", "Transport", "Utilities", "Entertainment"])
        category_combo.pack(pady=5)
        
        ttk.Label(form, text="Amount:").pack(pady=5)
        amount_entry = ttk.Entry(form)
        amount_entry.pack(pady=5)
        
        ttk.Label(form, text="Description:").pack(pady=5)
        desc_entry = ttk.Entry(form)
        desc_entry.pack(pady=5)

        def save_transaction():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                
                date = date_entry.get_date().strftime("%Y-%m-%d")
                type_ = type_combo.get()
                category = category_combo.get()
                description = desc_entry.get()

                if not all([type_, category]):
                    raise ValueError("Please fill all required fields")

                # Mock saving transaction
                print(f"Transaction saved: {date}, {type_}, {category}, {amount}, {description}")
                self.update_display()
                form.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(form, text="Save", command=save_transaction).pack(pady=20)

    def show_budget_form(self):
        form = tk.Toplevel(self.root)
        form.title("Set Budget")
        form.geometry("300x200")
        
        ttk.Label(form, text="Category:").pack(pady=5)
        category_combo = ttk.Combobox(form, values=["Food", "Transport", "Utilities", "Entertainment"])
        category_combo.pack(pady=5)
        
        ttk.Label(form, text="Monthly Budget:").pack(pady=5)
        amount_entry = ttk.Entry(form)
        amount_entry.pack(pady=5)

        def save_budget():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError("Budget must be positive")
                
                category = category_combo.get()
                if not category:
                    raise ValueError("Please select a category")

                # Mock saving budget
                print(f"Budget set: {category}, {amount}")
                self.update_display()
                form.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(form, text="Save", command=save_budget).pack(pady=20)

    def delete_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a transaction to delete")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?"):
            # Mock deleting transaction
            print(f"Transaction deleted: {selected_item}")
            self.update_display()

    def apply_filters(self):
        self.update_display()

    def update_display(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Mock transactions
        transactions = [
            (1, "2023-10-01", "Income", "Salary", 5000, "Monthly salary"),
            (2, "2023-10-05", "Expense", "Food", -50, "Groceries"),
            (3, "2023-10-10", "Expense", "Transport", -20, "Bus ticket")
        ]
        
        # Apply filters
        for trans in transactions:
            self.tree.insert('', 'end', values=trans)

        # Update charts
        self.update_charts()
        
        # Update budget display
        self.update_budget_display()

    def update_charts(self):
        self.ax.clear()
        # Mock data for chart
        categories = ["Food", "Transport", "Utilities"]
        amounts = [200, 100, 300]
        
        self.ax.pie(amounts, labels=categories, autopct='%1.1f%%')
        self.ax.set_title("Monthly Spending Distribution")
        self.canvas.draw()

    def update_budget_display(self):
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
            
        # Mock budget data
        budgets = [
            ("Food", 300, 200, 100),
            ("Transport", 150, 100, 50),
            ("Utilities", 400, 300, 100)
        ]
        
        for budget in budgets:
            self.budget_tree.insert('', 'end', values=(
                budget[0],
                f"${budget[1]:.2f}",
                f"${budget[2]:.2f}",
                f"${budget[3]:.2f}"
            ))

    def export_to_csv(self):
        filename = f"budget_export_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Type", "Category", "Amount", "Description"])
            
            # Mock transactions
            transactions = [
                ("2023-10-01", "Income", "Salary", 5000, "Monthly salary"),
                ("2023-10-05", "Expense", "Food", -50, "Groceries"),
                ("2023-10-10", "Expense", "Transport", -20, "Bus ticket")
            ]
            for trans in transactions:
                writer.writerow(trans)
                
        messagebox.showinfo("Success", f"Data exported to {filename}")

    def sort_treeview(self, col):
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        items.sort()
        
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

    def run(self):
        self.root.mainloop()
