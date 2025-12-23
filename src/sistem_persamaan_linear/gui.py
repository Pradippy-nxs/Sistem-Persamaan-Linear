import platform
import tkinter as tk
from tkinter import messagebox, ttk

from .methods import run_method, validate_solution
from .utils import check_diagonal_dominance, parse_matrix

MAX_N = 5
METHODS = ["Gauss Eliminasi", "Gauss-Jordan", "Cramer"]

class SPLApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator SPL Edukatif")
        self.configure(bg="#0f172a")
        self.geometry("950x780")

        # Setup Font
        self.font_main = ("Segoe UI", 10) if platform.system() == "Windows" else ("Inter", 10)
        self.font_mono = ("Consolas", 10) if platform.system() == "Windows" else ("Menlo", 10)

        self.style = ttk.Style(self)
        self._config_style()

        self.n_var = tk.IntVar(value=3)
        self.method_var = tk.StringVar(value=METHODS[0])
        self.entries = []

        self._build_layout()

    def _config_style(self):
        self.style.theme_use("clam")
        colors = {
            "bg": "#0f172a", "card": "#1e293b", "fg": "#f1f5f9",
            "accent": "#38bdf8", "btn": "#334155", "btn_act": "#475569"
        }
        self.colors = colors

        self.style.configure(".", background=colors["bg"], foreground=colors["fg"], font=self.font_main)
        self.style.configure("Card.TFrame", background=colors["card"], relief="flat")
        self.style.configure("Title.TLabel", background=colors["bg"], foreground="#38bdf8", font=(self.font_main[0], 18, "bold"))
        self.style.configure("Sub.TLabel", background=colors["bg"], foreground="#94a3b8", font=(self.font_main[0], 11))

        self.style.configure("TButton", background=colors["btn"], foreground="#ffffff", borderwidth=0, padding=8)
        self.style.map("TButton", background=[("active", colors["btn_act"])])

        self.style.configure("TSpinbox", fieldbackground="#ffffff", foreground="#000000", arrowcolor="#000000")
        self.style.configure("TCombobox", fieldbackground="#ffffff", foreground="#000000", arrowcolor="#000000")

        self.option_add("*TCombobox*Listbox*Background", "#ffffff")
        self.option_add("*TCombobox*Listbox*Foreground", "#000000")
        self.option_add("*TCombobox*Listbox*selectBackground", colors["accent"])
        self.option_add("*TCombobox*Listbox*selectForeground", "#ffffff")

        self.style.configure("Grid.TEntry", fieldbackground="#334155", foreground="#ffffff", borderwidth=0, insertcolor="white")

    def _build_layout(self):
        # Header
        header = ttk.Frame(self, padding=20)
        header.pack(fill="x")
        ttk.Label(header, text="Kalkulator SPL & Analisis Langkah", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Masukkan matriks, cek dominansi diagonal, dan pelajari langkah penyelesaiannya.", style="Sub.TLabel").pack(anchor="w")

        # Main Container
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # Left Panel (Input)
        left = ttk.Frame(main, style="Card.TFrame", padding=15)
        left.pack(side="left", fill="y", padx=(0, 10))

        # --- Controls (Ordo & Metode) ---
        ctrl = ttk.Frame(left, style="Card.TFrame")
        ctrl.pack(fill="x", pady=(0, 15))

        ttk.Label(ctrl, text="Ordo Matriks (N)", background=self.colors["card"]).pack(anchor="w")
        ttk.Spinbox(ctrl, from_=2, to=MAX_N, textvariable=self.n_var, command=self.reset_grid, width=10).pack(anchor="w", pady=5)

        ttk.Label(ctrl, text="Metode Penyelesaian", background=self.colors["card"]).pack(anchor="w", pady=(10, 0))
        ttk.Combobox(ctrl, values=METHODS, textvariable=self.method_var, state="readonly").pack(fill="x", pady=5)

        # --- Grid Input (Matrix) ---
        ttk.Label(left, text="Input [A | b]", background=self.colors["card"], font=(self.font_main[0], 10, "bold")).pack(anchor="w", pady=(10,5))
        self.grid_frame = ttk.Frame(left, style="Card.TFrame")
        self.grid_frame.pack(anchor="w") # Pastikan pack anchor w agar rapi
        self.reset_grid()

        ttk.Label(left, text="", background=self.colors["card"]).pack(pady=5)

        btn_frame = ttk.Frame(left, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=10, side="bottom")

        ttk.Button(btn_frame, text="Reset Grid", command=self.reset_grid).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(btn_frame, text="Hitung Solusi", command=self.solve).pack(side="right", fill="x", expand=True, padx=(5, 0))

        # Right Panel (Output)
        right = ttk.Frame(main, style="Card.TFrame", padding=2) # Padding for border look
        right.pack(side="right", fill="both", expand=True)

        self.text = tk.Text(right, wrap="word", bg="#0b1220", fg="#e2e8f0",
                            font=self.font_mono, bd=0, padx=15, pady=15, selectbackground="#2563eb")
        self.text.pack(fill="both", expand=True)

        # Scrollbar
        scroll = ttk.Scrollbar(right, command=self.text.yview)
        scroll.pack(side="right", fill="y")
        self.text.config(yscrollcommand=scroll.set)

        self._setup_tags()

    def _setup_tags(self):
        self.text.tag_config("h1", foreground="#38bdf8", font=(self.font_mono[0], 12, "bold"), spacing3=5)
        self.text.tag_config("h2", foreground="#f472b6", font=(self.font_mono[0], 11, "bold"), spacing1=10, spacing3=5)
        self.text.tag_config("warn", foreground="#facc15") # Kuning untuk analisis
        self.text.tag_config("res", foreground="#4ade80", font=(self.font_mono[0], 11, "bold"))
        self.text.tag_config("matrix", foreground="#94a3b8")
        self.text.tag_config("math", foreground="#c084fc")

    def reset_grid(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        n = self.n_var.get()
        self.entries = []

        # Header Grid
        for j in range(n):
            lbl = ttk.Label(self.grid_frame, text=f"x{j+1}", background=self.colors["card"], foreground="#64748b", font=("Arial", 8))
            lbl.grid(row=0, column=j)
        ttk.Label(self.grid_frame, text="=", background=self.colors["card"]).grid(row=0, column=n)
        ttk.Label(self.grid_frame, text="b", background=self.colors["card"], foreground="#64748b", font=("Arial", 8)).grid(row=0, column=n+1)

        for i in range(n):
            row_entries = []
            for j in range(n):
                e = ttk.Entry(self.grid_frame, width=5, justify="center", style="Grid.TEntry")
                e.grid(row=i+1, column=j, padx=2, pady=2)
                row_entries.append(e)

            ttk.Label(self.grid_frame, text="|", background=self.colors["card"], foreground="#475569").grid(row=i+1, column=n)

            b_ent = ttk.Entry(self.grid_frame, width=5, justify="center", style="Grid.TEntry")
            b_ent.grid(row=i+1, column=n+1, padx=2, pady=2)
            row_entries.append(b_ent)

            self.entries.append(row_entries)

    def solve(self):
        self.text.delete("1.0", tk.END)
        try:
            A, b = parse_matrix(self.entries)
            method = self.method_var.get()

            # 1. Analisis Matriks
            self.text.insert(tk.END, "ANALISIS MATRIKS\n", "h1")
            is_ddm, ddm_logs = check_diagonal_dominance(A)

            for log in ddm_logs:
                self.text.insert(tk.END, f"• {log}\n", "warn")

            if is_ddm:
                self.text.insert(tk.END, "✓ Matriks Dominan Diagonal (Solusi Stabil)\n", "res")
            else:
                self.text.insert(tk.END, "⚠ Matriks TIDAK Dominan Diagonal (Perhatian untuk metode iteratif)\n", "warn")

            self.text.insert(tk.END, "-"*60 + "\n", "matrix")

            # 2. Eksekusi Metode
            self.text.insert(tk.END, f"METODE: {method.upper()}\n", "h1")
            x, steps = run_method(method, A, b)

            # Menampilkan Langkah
            for title, content in steps:
                self.text.insert(tk.END, f"\n{title}\n", "h2")
                self.text.insert(tk.END, content + "\n", "matrix")

            # 3. Hasil Akhir
            self.text.insert(tk.END, "\nSOLUSI AKHIR\n", "h1")
            for i, val in enumerate(x):
                self.text.insert(tk.END, f"x{i+1} = {val:.6f}\n", "res")

            # 4. Validasi Error
            val = validate_solution(A, b, x)
            self.text.insert(tk.END, "\nVALIDASI (Pembuktian)\n", "h1")
            self.text.insert(tk.END, f"Error (Residual) Max = {val['norm_inf_residu']:.2e}\n", "math")

        except Exception as e:
            messagebox.showerror("Error Perhitungan", str(e))
