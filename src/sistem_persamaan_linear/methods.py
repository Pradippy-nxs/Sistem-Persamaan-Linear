from copy import deepcopy
from typing import Dict, List, Tuple, Union

import numpy as np

from .utils import Matrix, Vector, fmt_num, residual, vec_norm_inf

StepLog = List[Tuple[str, str]]

def format_aug(A, b):
    lines = []
    for r, val in zip(A, b, strict=False):
        row_str = "  ".join(fmt_num(x).rjust(6) for x in r)
        lines.append(f"| {row_str} | {fmt_num(val).rjust(6)} |")
    return "\n".join(lines)

def gauss_elimination_adaptive(A: Matrix, b: Vector) -> Tuple[Vector, StepLog]:
    A = deepcopy(A)
    b = deepcopy(b)
    n = len(A)
    steps: StepLog = []

    total_swaps = 0
    swap_details = []

    steps.append(("Status Awal", f"Matriks Awal:\n{format_aug(A, b)}"))

    for k in range(n - 1):
        current_pivot = A[k][k]
        best_row_idx = max(range(k, n), key=lambda i: abs(A[i][k]))
        max_val = A[best_row_idx][k]

        steps.append((f"--- Cek Kondisi Kolom {k+1} ---",
                      f"Pivot saat ini: {fmt_num(current_pivot)}\n"
                      f"Kandidat terbaik: {fmt_num(max_val)} (Baris {best_row_idx+1})"))

        should_swap = False
        reason = ""

        if abs(current_pivot) < 1e-12:
            if abs(max_val) < 1e-12:
                raise ValueError(f"Sistem Singular: Kolom {k+1} isinya nol semua.")
            should_swap = True
            reason = "Pivot bernilai 0 (Wajib Tukar)."
        elif best_row_idx != k:
            should_swap = True
            reason = "Optimasi stabilitas (Partial Pivoting)."
        else:
            should_swap = False
            reason = "Pivot sudah optimal (Naive)."

        if should_swap:
            total_swaps += 1
            swap_details.append(f"Iterasi {k+1}: Tukar Baris {k+1} <-> {best_row_idx+1}")

            A[k], A[best_row_idx] = A[best_row_idx], A[k]
            b[k], b[best_row_idx] = b[best_row_idx], b[k]
            steps.append(("KEPUTUSAN: Lakukan Pivoting", f"{reason}\n-> Tukar Baris {k+1} dengan {best_row_idx+1}."))
        else:
            steps.append(("KEPUTUSAN: Lanjut Tanpa Tukar", reason))

        pivot = A[k][k]
        ops = []
        for i in range(k + 1, n):
            if abs(A[i][k]) < 1e-12:
                continue
            factor = A[i][k] / pivot
            ops.append(f"B{i+1} = B{i+1} - ({fmt_num(factor)}) * B{k+1}")
            for j in range(k, n):
                A[i][j] -= factor * A[k][j]
            b[i] -= factor * b[k]

        if ops:
            steps.append(("Eliminasi Baris di Bawahnya", "\n".join(ops)))
        steps.append((f"Status Matriks (Iterasi {k+1})", format_aug(A, b)))

    if total_swaps > 0:
        mode_title = "MODE EKSEKUSI: GAUSS PARTIAL PIVOTING"
        mode_desc = (f"Program mendeteksi kondisi yang memerlukan {total_swaps}x penukaran baris.\n"
                     f"Oleh karena itu, metode otomatis beralih ke Partial Pivoting.\n\n"
                     f"Detail Penukaran:\n" + "\n".join(f"- {d}" for d in swap_details))
    else:
        mode_title = "MODE EKSEKUSI: GAUSS NAIVE"
        mode_desc = ("Tidak terjadi penukaran baris sama sekali selama proses.\n"
                     "Ini berarti pivot diagonal sudah aman/optimal sejak awal.\n"
                     "Metode berjalan murni secara Naive.")

    steps.insert(0, (mode_title, mode_desc))

    return back_substitution(A, b, n, steps)

def back_substitution(A, b, n, steps):
    x = [0.0] * n
    back_steps = []
    for i in range(n - 1, -1, -1):
        s = sum(A[i][j] * x[j] for j in range(i + 1, n))
        if abs(A[i][i]) < 1e-12:
             raise ValueError("Solusi infinite atau tidak ada solusi.")
        x[i] = (b[i] - s) / A[i][i]
        expr = f"({fmt_num(b[i])} - {fmt_num(s)}) / {fmt_num(A[i][i])}"
        back_steps.append(f"x{i+1} = {expr} = {fmt_num(x[i])}")

    steps.append(("Substitusi Mundur", "\n".join(back_steps)))
    return x, steps

def gauss_jordan(A: Matrix, b: Vector) -> Tuple[Vector, StepLog]:
    A = deepcopy(A)
    b = deepcopy(b)
    n = len(A)
    steps: StepLog = []
    steps.append(("Status Awal", f"{format_aug(A, b)}"))
    for k in range(n):
        steps.append((f"--- Fokus Diagonal {k+1} ---", ""))
        pivot_row = max(range(k, n), key=lambda i: abs(A[i][k]))
        if abs(A[pivot_row][k]) < 1e-12: raise ValueError("Singular")
        if pivot_row != k:
            A[k], A[pivot_row] = A[pivot_row], A[k]
            b[k], b[pivot_row] = b[pivot_row], b[k]
            steps.append(("Pivoting", f"Tukar B{k+1} <-> B{pivot_row+1}"))
        pivot = A[k][k]
        for j in range(k, n): A[k][j] /= pivot
        b[k] /= pivot
        steps.append(("Normalisasi", f"B{k+1} dibagi {fmt_num(pivot)} agar pivot jadi 1"))
        ops = []
        for i in range(n):
            if i == k or abs(A[i][k]) < 1e-12: continue
            factor = A[i][k]
            for j in range(k, n): A[i][j] -= factor * A[k][j]
            b[i] -= factor * b[k]
            ops.append(f"B{i+1} - ({fmt_num(factor)})xB{k+1}")
        if ops: steps.append(("Eliminasi", "\n".join(ops)))
        steps.append((f"Matriks Iterasi {k+1}", format_aug(A, b)))
    return b, steps

def cramer(A: Matrix, b: Vector) -> Tuple[Vector, StepLog]:
    A_np = np.array(A, dtype=float)
    b_np = np.array(b, dtype=float)
    n = len(A)
    steps: StepLog = []
    d_main = np.linalg.det(A_np)
    steps.append(("Determinan Utama", f"Det(A) = {fmt_num(d_main)}"))
    if abs(d_main) < 1e-12:
        raise ValueError("Det(A) = 0. Cramer gagal.")
    x = []
    for i in range(n):
        Ai = A_np.copy()
        Ai[:, i] = b_np
        di = np.linalg.det(Ai)
        xi = di / d_main
        x.append(xi)
        steps.append((f"Mencari x{i+1}",
                      f"Det(A{i+1}) = {fmt_num(di)}\n"
                      f"x{i+1} = {fmt_num(di)} / {fmt_num(d_main)} = {fmt_num(xi)}"))
    return x, steps

def run_method(method_name: str, A: Matrix, b: Vector):
    methods = {
        "Gauss Eliminasi": gauss_elimination_adaptive,
        "Gauss-Jordan": gauss_jordan,
        "Cramer": cramer,
    }
    if method_name not in methods:
        raise ValueError(f"Metode {method_name} tidak dikenali.")
    return methods[method_name](A, b)

def validate_solution(A: Matrix, b: Vector, x: Vector) -> Dict[str, Union[float, Vector]]:
    r = residual(A, x, b)
    return {
        "norm_inf_residu": vec_norm_inf(r),
        "residu": r,
    }
