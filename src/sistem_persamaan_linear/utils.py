import math
from typing import List, Tuple

Number = float
Matrix = List[List[Number]]
Vector = List[Number]

def parse_matrix(entries) -> Tuple[Matrix, Vector]:
    rows = len(entries)
    cols = len(entries[0]) - 1
    A: Matrix = []
    b: Vector = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(float(entries[i][j].get()))
        A.append(row)
        b.append(float(entries[i][cols].get()))
    return A, b

def format_row(row):
    return "[" + "  ".join(f"{v:8.4f}" for v in row) + "]"

def format_matrix(A: Matrix) -> str:
    return "\n".join(format_row(r) for r in A)

def is_square(A: Matrix) -> bool:
    return all(len(r) == len(A) for r in A)

def det_2x2(A: Matrix) -> float:
    return A[0][0]*A[1][1] - A[0][1]*A[1][0]

def pretty_solution(x: Vector) -> str:
    return "\n".join(f"x{i+1} = {v:0.6f}" for i, v in enumerate(x))

def residual(A: Matrix, x: Vector, b: Vector) -> Vector:
    r = []
    for i in range(len(A)):
        r.append(sum(A[i][j]*x[j] for j in range(len(x))) - b[i])
    return r

def vec_norm_inf(v: Vector) -> float:
    return max(abs(x) for x in v) if v else math.nan
