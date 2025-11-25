# Linear System Solver (Sistem Persamaan Linear)

Proyek ini berisi implementasi beberapa metode numerik untuk menyelesaikan Sistem Persamaan Linear (SPL) menggunakan Python.

## Fitur

- Input matriks koefisien \(A\) dan vektor ruas kanan \(b\).
- Penyelesaian SPL dengan **minimal 2 metode**, misalnya:
  - Eliminasi Gauss
  - Gauss–Jordan
- (Opsional) Metode iteratif:
  - Jacobi
  - Gauss–Seidel
- Antarmuka **Command Line (CLI)** sederhana.
- Notebook Jupyter (`notebooks/demo.ipynb`) untuk demo dan eksperimen.
- Unit test dengan `pytest`.
- Tooling modern:
  - `ruff` (linter)
  - `black` (formatter)
  - `mypy` (static type checking)
  - `pre-commit` hooks

## Tech Stack (per 25 November 2025)

- Python 3.11–3.14 (direkomendasikan 3.14.0)
- NumPy >= 1.26.3
- SciPy >= 1.13.0
- JupyterLab >= 4.1.0
- Ruff >= 0.3.7
- Black >= 24.11.0
- Mypy >= 1.8.0
- Pytest >= 8.3.0

## Cara Setup

```bash
# 1. Clone repo
git clone https://github.com/raflyrzp/sistem-persamaan-linear.git
cd linear-system-solver

# 2. (Opsional) Buat virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
# .venv\Scripts\activate   # Windows

# 3. Install dependencies utama + dev
pip install -e ".[dev]"

# 4. (Opsional) install pre-commit
pip install pre-commit
pre-commit install
```

## Menjalankan Program

```bash
# Jalankan CLI
python -m linear_system.cli

# atau jika sudah terinstall sebagai script
linear-solver
```

Program akan meminta:

- Ordo matriks (n)
- Elemen-elemen matriks A
- Elemen vektor b
- Metode yang ingin digunakan (Gauss / Gauss-Jordan / lainnya)

## Menjalankan Test

```bash
pytest
```

## Menjalankan Notebook

```bash
jupyter lab
```

Lalu buka `notebooks/demo.ipynb`.

## Struktur Proyek

```text
src/linear_system/
  methods.py  # Implementasi metode SPL
  utils.py    # Fungsi bantuan (validasi, dll)
  cli.py      # Program utama (CLI)
tests/
  test_methods.py
notebooks/
  demo.ipynb
```

## Lisensi

Silakan disesuaikan dengan kebutuhan tugas (misalnya: tidak pakai lisensi / MIT).
