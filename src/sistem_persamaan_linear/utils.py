from typing import List, Tuple

Number = float
Matrix = List[List[Number]]
Vector = List[Number]

def fmt_num(val: float) -> str:
    if abs(val - round(val)) < 1e-9:
        return str(int(round(val)))

    formatted = f"{val:.4f}".rstrip('0').rstrip('.')
    return formatted

def parse_matrix(entries) -> Tuple[Matrix, Vector]:
    rows = len(entries)
    cols = len(entries[0]) - 1
    A: Matrix = []
    b: Vector = []
    for i in range(rows):
        row = []
        for j in range(cols):
            try:
                val = float(entries[i][j].get())
            except ValueError:
                val = 0.0
            row.append(val)
        A.append(row)
        try:
            b_val = float(entries[i][cols].get())
        except ValueError:
            b_val = 0.0
        b.append(b_val)
    return A, b

def format_row(row):
    content = "  ".join(fmt_num(v).rjust(6) for v in row)
    return f"| {content} |"

def format_matrix(A: Matrix) -> str:
    return "\n".join(format_row(r) for r in A)

def check_diagonal_dominance(A: Matrix) -> Tuple[bool, List[str]]:
    n = len(A)
    is_dominant = True
    details = []

    details.append("--- Cek Syarat: |aii| >= sum(|aij|) ---")

    for i in range(n):
        diag = abs(A[i][i])
        off_diag_sum = sum(abs(A[i][j]) for j in range(n) if i != j)

        if diag >= off_diag_sum:
            status = "OK"
        else:
            status = "GAGAL"
            is_dominant = False

        details.append(
            f"Baris {i+1}: |{fmt_num(A[i][i])}| >= {fmt_num(off_diag_sum)} ? -> {status}"
        )

    return is_dominant, details

def residual(A: Matrix, x: Vector, b: Vector) -> Vector:
    r = []
    for i in range(len(A)):
        val = sum(A[i][j] * x[j] for j in range(len(x))) - b[i]
        r.append(val)
    return r

def vec_norm_inf(v: Vector) -> float:
    return max(abs(x) for x in v) if v else 0.0
