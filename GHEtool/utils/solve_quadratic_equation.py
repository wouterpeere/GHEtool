import math


def solve_quadratic(a: float, b: float, c: float) -> tuple[float, float]:
    """
    solves the quadratic equation a*x^2 + b* x +c = 0
    Parameters
    ----------
    a: float
        quadratic term
    b: float
        linear term
    c: float
        constant term
    Returns
    -------
        tuple[float, float]
    """
    print(a,b,c)
    discriminant = math.sqrt(b**2 - 4*a*c)
    root1 = (-b + discriminant) / (2*a)
    root2 = (-b - discriminant) / (2*a)
    return root1, root2