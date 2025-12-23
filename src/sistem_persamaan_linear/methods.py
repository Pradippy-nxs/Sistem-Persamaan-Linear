from copy import deepcopy
from typing import Dict, List, Tuple, Union

import numpy as np  # Pastikan install numpy: pip install numpy

from .utils import Matrix, Vector, format_matrix, residual, vec_norm_inf

StepLog = List[Tuple[str, str]] # (Title, Content)

def format_aug(A, b):
    # Helper untuk menampilkan Augmented Matrix
    lines = []
    for r, val in zip(A, b):
        row_str = "  ".join(f"{x:8.4f}" for x in r)
        lines.append(f"| {row_str} | {val:8.4f} |")
    return "\n".join(lines)

def gauss_elimination(A: Matrix, b: Vector) -> Tuple[Vector, StepLog]:
    A = deepcopy(A)
    b = deepcopy(b)
    n = len(A)
    steps: StepLog = []

    steps.append(("Status Awal", f"Matriks Augmented Awal:\n{format_aug(A, b)}"))

    # Eliminasi Maju
    for k in range(n - 1):
        steps.append((f"--- Iterasi Kolom {k+1} ---", f"Tujuan: Membuat nol di bawah elemen pivot A[{k+1},{k+1}]"))

        # Pivoting
        pivot_row = max(range(k, n), key=lambda i: abs(A[i][k]))
        if abs(A[pivot_row][k]) < 1e-12:
            raise ValueError(f"Pivot nol terdeteksi di kolom {k+1}. Matriks singular.")

        if pivot_row != k:
            A[k], A[pivot_row] = A[pivot_row], A[k]
            b[k], b[pivot_row] = b[pivot_row], b[k]
            steps.append(("Partial Pivoting", f"Menukar Baris {k+1} dengan Baris {pivot_row+1} agar pivot lebih besar."))

        pivot = A[k][k]

        # Eliminasi
        ops = []
        for i in range(k + 1, n):
            factor = A[i][k] / pivot
            ops.append(f"B{i+1} = B{i+1} - ({factor:.4f}) * B{k+1}")
            for j in range(k, n):
                A[i][j] -= factor * A[k][j]
            b[i] -= factor * b[k]

        if ops:
            steps.append((f"Eliminasi di Kolom {k+1}", "\n".join(ops)))
            steps.append((f"Hasil Iterasi {k+1}", format_aug(A, b)))

    # Back Substitution
    x = [0.0] * n
    back_steps = []
    for i in range(n - 1, -1, -1):
        s = sum(A[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (b[i] - s) / A[i][i]
        expr = f"({b[i]:.4f} - {s:.4f}) / {A[i][i]:.4f}"
        back_steps.append(f"x{i+1} = {expr} = {x[i]:.6f}")

    steps.append(("Substitusi Mundur (Back Substitution)", "\n".join(back_steps)))
    return x, steps

def gauss_jordan(A: Matrix, b: Vector) -> Tuple[Vector, StepLog]:
    A = deepcopy(A)
    b = deepcopy(b)
    n = len(A)
    steps: StepLog = []

    steps.append(("Status Awal", f"Matriks Augmented Awal:\n{format_aug(A, b)}"))

    for k in range(n):
        steps.append((f"--- Fokus Diagonal Utama {k+1} ---", ""))

        # Pivoting
        pivot_row = max(range(k, n), key=lambda i: abs(A[i][k]))
        if abs(A[pivot_row][k]) < 1e-12:
            raise ValueError("Matriks singular.")

        if pivot_row != k:
            A[k], A[pivot_row] = A[pivot_row], A[k]
            b[k], b[pivot_row] = b[pivot_row], b[k]
            steps.append(("Pivoting", f"Tukar Baris {k+1} <-> {pivot_row+1}"))

        # Normalisasi (Membuat pivot menjadi 1)
        pivot = A[k][k]
        if abs(pivot - 1.0) > 1e-12:
            for j in range(k, n):
                A[k][j] /= pivot
            b[k] /= pivot
            steps.append(("Normalisasi Pivot", f"B{k+1} = B{k+1} / {pivot:.4f} (Agar diagonal jadi 1)"))

        # Eliminasi (Membuat 0 di atas dan bawah pivot)
        ops = []
        for i in range(n):
            if i == k or abs(A[i][k]) < 1e-12:
                continue
            factor = A[i][k]
            for j in range(k, n):
                A[i][j] -= factor * A[k][j]
            b[i] -= factor * b[k]
            ops.append(f"B{i+1} = B{i+1} - ({factor:.4f}) * B{k+1}")

        if ops:
            steps.append((f"Eliminasi Kolom {k+1}", "\n".join(ops)))

        steps.append((f"Posisi Matriks (Iterasi {k+1})", format_aug(A, b)))

    return b, steps

def cramer(A: Matrix, b: Vector) -> Tuple[Vector, StepLog]:
    A_np = np.array(A, dtype=float)
    b_np = np.array(b, dtype=float)
    n = len(A)
    steps: StepLog = []

    d_main = np.linalg.det(A_np)
    steps.append(("Determinan Utama", f"Matriks A:\n{format_matrix(A)}\n\nDet(A) = {d_main:.6f}"))

    if abs(d_main) < 1e-12:
        raise ValueError("Determinan nol (atau mendekati nol). Cramer tidak bisa digunakan.")

    x = []
    for i in range(n):
        Ai = A_np.copy()
        Ai[:, i] = b_np
        di = np.linalg.det(Ai)
        xi = di / d_main
        x.append(xi)

        # Konversi ke list untuk display
        Ai_list = Ai.tolist()
        steps.append((f"--- Mencari x{i+1} ---",
                      f"Ganti kolom {i+1} dengan vektor b:\n{format_matrix(Ai_list)}\n\n"
                      f"Det(A{i+1}) = {di:.6f}\n"
                      f"x{i+1} = {di:.6f} / {d_main:.6f} = {xi:.6f}"))

    return x, steps

def run_method(method_name: str, A: Matrix, b: Vector):
    methods = {
        "Gauss Eliminasi": gauss_elimination,
        "Gauss-Jordan": gauss_jordan,
        "Cramer": cramer,
    }
    if method_name not in methods:
        raise ValueError(f"Metode {method_name} belum didukung.")
    return methods[method_name](A, b)

def validate_solution(A: Matrix, b: Vector, x: Vector) -> Dict[str, Union[float, Vector]]:
    r = residual(A, x, b)
    return {
        "norm_inf_residu": vec_norm_inf(r),
        "residu": r,
    }
