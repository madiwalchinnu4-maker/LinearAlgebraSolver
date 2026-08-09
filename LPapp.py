from flask import Flask, render_template, request
import sympy as sp

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

def parse_matrix(text):
    rows = []
    for line in text.strip().splitlines():
        if line.strip():
            rows.append([sp.sympify(x.strip()) for x in line.split(",")])
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("Enter a rectangular matrix.")
    return sp.Matrix(rows)

@app.route("/solve", methods=["POST"])
def solve():
    operation = request.form.get("operation", "")
    matrix_text = request.form.get("matrix", "")
    try:
        A = parse_matrix(matrix_text)

        if operation == "determinant":
            if A.rows != A.cols:
                raise ValueError("Determinant requires a square matrix.")
            result = A.det()
            steps = f"det(A) = {result}"

        elif operation == "inverse":
            if A.rows != A.cols:
                raise ValueError("Inverse requires a square matrix.")
            if A.det() == 0:
                result = "No inverse exists because det(A) = 0."
                steps = "A matrix is invertible only when its determinant is non-zero."
            else:
                result = A.inv()
                steps = "The inverse A⁻¹ was calculated using exact arithmetic."

        elif operation == "transpose":
            result = A.T
            steps = "Transpose: interchange rows and columns."
            
        elif operation == "linear_equations":
            if A.cols < 2:
                raise ValueError("Enter an augmented matrix with coefficients and constants.")

            coeff = A[:, :-1]
            constants = A[:, -1]
            variables = sp.symbols(f"x1:{coeff.cols + 1}")

            result = sp.linsolve((coeff, constants), variables)
            steps = "The system was solved using exact arithmetic."

        elif operation == "vectors":
            if A.rows < 2:
                raise ValueError("Enter at least two vectors.")

            v1 = A.row(0)
            v2 = A.row(1)

            dot_product = v1.dot(v2)

            result = f"Vector 1: {v1}\nVector 2: {v2}\nDot Product: {dot_product}"

            if A.cols == 3:
                result += f"\nCross Product: {v1.cross(v2)}"

            steps = "Vector operations were calculated using exact arithmetic."

        elif operation == "eigenvalues": 
         if A.rows != A.cols:
                raise ValueError("Eigenvalues require a square matrix.")

         eigenvalues = A.eigenvals()

         result = f"Eigenvalues: {eigenvalues}"

         if A.is_diagonalizable():
                P, D = A.diagonalize()
                result += f"\n\nP Matrix:\n{P}\n\nD Matrix:\n{D}"
                steps = "The eigenvalues were calculated and the matrix was diagonalized."
         else:
                steps = "The eigenvalues were calculated. The matrix is not diagonalizable."

        return render_template("result.html", operation=operation.title(),
                               result=result, steps=steps, error=None)
    except Exception as e:
        return render_template("result.html", operation="Error",
                               result=None, steps=None, error=str(e))

if __name__ == "__main__":
    app.run(debug=True)
