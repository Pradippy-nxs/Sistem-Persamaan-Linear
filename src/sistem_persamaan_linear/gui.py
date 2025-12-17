import tkinter as tk
from tkinter import messagebox, ttk

from .methods import run_method, validate_solution
from .utils import parse_matrix

MAX_N = 6
METHODS = ["Gauss Eliminasi", "Gauss-Jordan", "Cramer", "Jacobi"]

class SPLApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator SPL")
        self.configure(bg="#0b1220")
        self.geometry("860x640")
        self.minsize(820, 600)
        self.style = ttk.Style(self)
        self._config_style()
        self.n_var = tk.IntVar(value=3)
        self.method_var = tk.StringVar(value=METHODS[0])
        self.entries = []
        self._build_layout()

    def _config_style(self):
        palette = {
            "bg": "#0b1220",
            "fg": "#e2e8f0",
            "card": "#111827",
            "accent": "#22d3ee",
            "accent2": "#7c3aed",
        }
        self.style.theme_use("clam")
        self.style.configure(".", background=palette["bg"], foreground=palette["fg"], font=("Inter", 10))
        self.style.configure("Card.TFrame", background=palette["card"], relief="flat", borderwidth=1)
        self.style.configure("Title.TLabel", background=palette["bg"], foreground=palette["fg"], font=("Inter", 16, "bold"))
        self.style.configure("SubTitle.TLabel", background=palette["bg"], foreground="#94a3b8", font=("Inter", 11))
        self.style.configure("TLabel", background=palette["card"], foreground=palette["fg"], font=("Inter", 10))
        self.style.configure("TButton", background=palette["card"], foreground=palette["fg"], padding=8, font=("Inter", 10, "bold"))
        self.style.map("TButton",
                       background=[("active", "#1f2937")],
                       foreground=[("active", palette["accent"])])
        self.style.configure("TEntry", foreground="#000000", fieldbackground="#ffffff", font=("Inter", 10))
        self.style.configure("TSpinbox", foreground="#000000", fieldbackground="#ffffff", font=("Inter", 10))
        self.style.configure("TCombobox", foreground="#000000", fieldbackground="#ffffff", font=("Inter", 10))
        self.palette = palette

    def _build_layout(self):
        # Header
        header = ttk.Frame(self, padding=16, style="Card.TFrame")
        header.pack(fill="x", padx=16, pady=(16, 8))
        ttk.Label(header, text="Kalkulator Sistem Persamaan Linear", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Pilih metode, input matriks A dan vektor b, lalu lihat langkah-langkah penyelesaian.",
                  style="SubTitle.TLabel").pack(anchor="w", pady=(4, 0))

        # Controls
        controls = ttk.Frame(self, padding=12, style="Card.TFrame")
        controls.pack(fill="x", padx=16, pady=8)

        ttk.Label(controls, text="Ordo (n×n):").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        spin = ttk.Spinbox(controls, from_=2, to=MAX_N, width=5, textvariable=self.n_var, command=self.reset_grid, justify="center")
        spin.grid(row=0, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(controls, text="Metode:").grid(row=0, column=2, sticky="w", padx=8, pady=4)
        cb = ttk.Combobox(controls, values=METHODS, textvariable=self.method_var, state="readonly", width=16)
        cb.grid(row=0, column=3, sticky="w", padx=4, pady=4)

        ttk.Button(controls, text="Reset Grid", command=self.reset_grid).grid(row=0, column=4, padx=6, pady=4)
        ttk.Button(controls, text="Contoh Kasus", command=self.fill_sample).grid(row=0, column=5, padx=6, pady=4)
        ttk.Button(controls, text="Hitung", command=self.solve).grid(row=0, column=6, padx=6, pady=4)

        # Matrix input card
        self.grid_card = ttk.Frame(self, padding=12, style="Card.TFrame")
        self.grid_card.pack(fill="x", padx=16, pady=8)
        ttk.Label(self.grid_card, text="Matriks Koefisien (A) dan vektor b", font=("Inter", 11, "bold")).pack(anchor="w", pady=(0, 8))
        self.grid_frame = ttk.Frame(self.grid_card, style="Card.TFrame")
        self.grid_frame.pack()
        self.reset_grid()

        # Output card
        output_card = ttk.Frame(self, padding=12, style="Card.TFrame")
        output_card.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        ttk.Label(output_card, text="Langkah & Hasil", font=("Inter", 11, "bold")).pack(anchor="w")
        self.text = tk.Text(output_card, height=16, bg="#0f172a", fg="#e2e8f0",
                            insertbackground="#e2e8f0", bd=0, relief="flat", font=("JetBrains Mono", 10))
        self.text.pack(fill="both", expand=True, pady=8)
        btns = ttk.Frame(output_card, style="Card.TFrame")
        btns.pack(anchor="e")
        ttk.Button(btns, text="Bersihkan Output", command=lambda: self.text.delete("1.0", tk.END)).pack(side="right", padx=4)

    def reset_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        n = self.n_var.get()
        self.entries = []
        for i in range(n):
            row_entries = []
            for j in range(n + 1):  # n kolom A + 1 kolom b
                e = ttk.Entry(self.grid_frame, width=8, justify="center")
                e.grid(row=i + 1, column=j, padx=4, pady=4)  # offset +1 untuk header
                row_entries.append(e)
            self.entries.append(row_entries)
        # header
        for j in range(n):
            ttk.Label(self.grid_frame, text=f"a{j+1}", font=("Inter", 9, "bold")).grid(row=0, column=j, sticky="s", pady=(0, 2))
        ttk.Label(self.grid_frame, text="b", font=("Inter", 9, "bold")).grid(row=0, column=n, sticky="s", pady=(0, 2))

    def fill_sample(self):
        samples = {
            3: [
                [2, -1, 1, 8],
                [3, 3, 9, 0],
                [3, 3, 5, -6],
            ],
            2: [
                [3, 2, 5],
                [4, -1, 1],
            ],
        }
        n = self.n_var.get()
        sample = samples.get(n)
        if not sample:
            messagebox.showinfo("Info", f"Belum ada sample untuk n={n}")
            return
        for i in range(n):
            for j in range(n + 1):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, str(sample[i][j]))

    def solve(self):
        try:
            A, b = parse_matrix(self.entries)
            method = self.method_var.get()
            x, steps = run_method(method, A, b)
            val = validate_solution(A, b, x)
            self.show_result(method, steps, x, val)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_result(self, method, steps, x, val):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, f"Metode: {method}\n")
        self.text.insert(tk.END, "\n--- Langkah ---\n")
        for s in steps:
            self.text.insert(tk.END, s + "\n")
        self.text.insert(tk.END, "\n--- Solusi ---\n")
        for i, xi in enumerate(x):
            self.text.insert(tk.END, f"x{i+1} = {xi:0.6f}\n")
        self.text.insert(tk.END, "\n--- Validasi ---\n")
        self.text.insert(tk.END, f"||residu||_inf = {val['norm_inf_residu']:.2e}\n")
        self.text.insert(tk.END, f"residu = {val['residu']}\n")
