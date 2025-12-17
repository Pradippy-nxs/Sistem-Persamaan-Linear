from copy import deepcopy
from typing import Dict, List, Tuple, Union

from .utils import Matrix, Vector, residual, vec_norm_inf

StepLog = List[str]


def gauss_elimination(A: Matrix, b: Vector) -> Tuple[Vector, StepLog]:
    A = deepcopy(A)
    b = deepcopy(b)
    n = len(A)
    steps: StepLog = []
    for k in range(n - 1):
        pivot_row = max(range(k, n), key=lambda i: abs(A[i][k]))
        if abs(A[pivot_row][k]) < 1e-12:
            raise ValueError("Matriks singular pada kolom pivot")
        if pivot_row != k:
            A[k], A[pivot_row] = A[pivot_row], A[k]
            b[k], b[pivot_row] = b[pivot_row], b[k]
            steps.append(f"Tukar baris {k+1} dengan {pivot_row+1}")
        for i in range(k + 1, n):
            m = A[i][k] / A[k][k]
            steps.append(f"B{i+1} = B{i+1} - ({m:.4f})*B{k+1}")
            for j in range(k, n):
                A[i][j] -= m * A[k][j]
            b[i] -= m * b[k]
        steps.append(f"Setelah eliminasi kolom {k+1}:\nA=\n{format_matrix(A)}\nb={b}")
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = sum(A[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (b[i] - s) / A[i][i]
    steps.append("Back substitution selesai.")
    return x, steps


def gauss_jordan(A: Matrix, b: Vector) -> Tuple[Vector, StepLog]:
    A = deepcopy(A)
    b = deepcopy(b)
    n = len(A)
    steps: StepLog = []
    for k in range(n):
        pivot_row = max(range(k, n), key=lambda i: abs(A[i][k]))
        if abs(A[pivot_row][k]) < 1e-12:
            raise ValueError("Matriks singular")
        if pivot_row != k:
            A[k], A[pivot_row] = A[pivot_row], A[k]
            b[k], b[pivot_row] = b[pivot_row], b[k]
            steps.append(f"Tukar baris {k+1} dengan {pivot_row+1}")
        pivot = A[k][k]
        for j in range(k, n):
            A[k][j] /= pivot
        b[k] /= pivot
        steps.append(f"Normalisasi baris {k+1} pivot=1")
        for i in range(n):
            if i == k:
                continue
            m = A[i][k]
            for j in range(k, n):
                A[i][j] -= m * A[k][j]
            b[i] -= m * b[k]
            steps.append(f"B{i+1} = B{i+1} - ({m:.4f})*B{k+1}")
        steps.append(f"Setelah kolom {k+1}:\nA=\n{format_matrix(A)}\nb={b}")
    steps.append("Reduced Row Echelon Form selesai.")
    return b, steps


def cramer(A: Matrix, b: Vector) -> Tuple[Vector, StepLog]:
    import numpy as np
    from numpy.linalg import det
    A_np = np.array(A, dtype=float)
    b_np = np.array(b, dtype=float)
    d = det(A_np)
    if abs(d) < 1e-12:
        raise ValueError("Determinan nol, tidak ada solusi unik.")
    steps: StepLog = [f"det(A) = {d:.6f}"]
    x = []
    for i in range(len(A)):
        Ai = A_np.copy()
        Ai[:, i] = b_np
        di = det(Ai)
        xi = di / d
        x.append(float(xi))
        steps.append(f"det(A{i+1}) = {di:.6f}; x{i+1} = det(A{i+1})/det(A) = {xi:.6f}")
    return x, steps


def jacobi(
    A: Matrix, b: Vector, tol: float = 1e-6, max_iter: int = 50
) -> Tuple[Vector, StepLog]:
    import numpy as np
    A_np = np.array(A, dtype=float)
    b_np = np.array(b, dtype=float)
    n = len(A_np)
    x = np.zeros(n)
    steps: StepLog = []
    for it in range(max_iter):
        x_new = b_np - (A_np @ x) + np.multiply(np.diag(A_np), x)
        x_new = x_new / np.diag(A_np)
        err = float(vec_norm_inf(list(x_new - x)))
        steps.append(f"Iter {it+1}: x={x_new}, error={err:.2e}")
        if err < tol:
            x = x_new
            break
        x = x_new
    result: Vector = [float(xi) for xi in x]
    return result, steps


def format_matrix(A: Matrix) -> str:
    return "\n".join(" ".join(f"{v:8.4f}" for v in row) for row in A)


def run_method(method_name: str, A: Matrix, b: Vector):
    methods = {
        "Gauss Eliminasi": gauss_elimination,
        "Gauss-Jordan": gauss_jordan,
        "Cramer": cramer,
        "Jacobi": jacobi,
    }
    if method_name not in methods:
        raise ValueError(f"Metode {method_name} belum didukung.")
    return methods[method_name](A, b)


def validate_solution(
    A: Matrix, b: Vector, x: Vector
) -> Dict[str, Union[float, Vector]]:
    r = residual(A, x, b)
    return {
        "norm_inf_residu": vec_norm_inf(r),
        "residu": r,
    }
