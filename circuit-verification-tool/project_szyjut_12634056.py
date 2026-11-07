#!/usr/bin/env python3
"""Block 2 project: a circuit verification tool with Buchberger's algorithm in SageMath.

Rename this file to  project_<surname>_<matrnr>.py  and implement the four functions marked TODO.
Do not change their names, their arguments, or the form of their results, and do not change the
given code for input and output.

Run:  sage -python project_<surname>_<matrnr>.py tests/multiplier_2bit.ideal
      (with passagemath installed, use python3 instead of sage -python)
"""
import ast
import sys

try:
    from sage.all import PolynomialRing, QQ
except ImportError:                                    # pip-installed passagemath
    from sage.all__sagemath_singular import PolynomialRing, QQ


# ========================================================================================
# Your implementation
#
# All polynomials are elements of a SageMath polynomial ring over QQ with a fixed monomial order;
# for a polynomial f, you get its ring as f.parent(). See the project description for the
# SageMath functions you must not use.
# ========================================================================================
def divide(f, F):
    """The division algorithm: divide f by the list F = [f_1, ..., f_s] of nonzero
    polynomials. Return the remainder r (the quotients are not needed)."""
    R = f.parent()
    r = R(0)
    p = f

    while p != 0:
        lm_p = p.lm()
        for g in F:
            if R.monomial_divides(g.lm(), lm_p):
                term = (p.lc() / g.lc()) * R.monomial_quotient(lm_p, g.lm())
                p -= term * g
                break
        else:
            lt_p = p.lt()
            r += lt_p
            p -= lt_p

    return r


def spoly(f, g):
    """The S-polynomial of two nonzero polynomials f and g."""
    R = f.parent()
    lcm = R.monomial_lcm(f.lm(), g.lm())
    term_f = (1 / f.lc()) * R.monomial_quotient(lcm, f.lm())
    term_g = (1 / g.lc()) * R.monomial_quotient(lcm, g.lm())
    return term_f * f - term_g * g


def buchberger(F):
    """Buchberger's algorithm with the shortcut for pairs with relatively prime leading
    monomials, for a nonempty list F of nonzero polynomials.

    Return (G, stats): the list G computed by the algorithm, and a dict stats with four integers:
        stats["pairs"]    number of pairs that were chosen and marked,
        stats["skipped"]  how many of them were skipped by the shortcut,
        stats["zero"]     how many of them had an S-polynomial with remainder 0,
        stats["added"]    how many of them had a nonzero remainder that was added to G."""
    R = F[0].parent()
    G = list(F)
    pairs = [(G[i], G[j]) for i in range(len(G)) for j in range(i + 1, len(G))]
    stats = {"pairs": 0, "skipped": 0, "zero": 0, "added": 0}

    while pairs:
        f, g = pairs.pop(0)
        stats["pairs"] += 1

        if R.monomial_lcm(f.lm(), g.lm()) == f.lm() * g.lm():
            stats["skipped"] += 1
            continue

        h = divide(spoly(f, g), G)
        if h == 0:
            stats["zero"] += 1
        else:
            stats["added"] += 1
            pairs.extend((g_old, h) for g_old in G)
            G.append(h)

    return G, stats


def member(f, F):
    """Whether f lies in the ideal <F>, for a polynomial f and a nonempty list F of nonzero
    polynomials. 
    Return (answer, r): answer is True if f is in <F> and False otherwise, and r is the
    remainder of f on division by G."""
    G, _ = buchberger(F)
    r = divide(f, G)
    return r == 0, r


# ========================================================================================
# Input and output (given, do not change)
# ========================================================================================
def parse_poly(R, text):
    """Parse a polynomial like  3*x^2*y - 1/2*z + 1  as an element of the polynomial ring R."""
    gens = {str(v): v for v in R.gens()}

    def ev(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return R(node.value)
        if isinstance(node, ast.Name) and node.id in gens:
            return gens[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            v = ev(node.operand)
            return -v if isinstance(node.op, ast.USub) else v
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            e = node.right
            if isinstance(e, ast.Constant) and type(e.value) is int and e.value >= 0:
                return ev(node.left) ** e.value
        elif isinstance(node, ast.BinOp):
            a, b = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Add):
                return a + b
            if isinstance(node.op, ast.Sub):
                return a - b
            if isinstance(node.op, ast.Mult):
                return a * b
            if isinstance(node.op, ast.Div) and b.is_constant() and b != 0:
                return a * (1 / b.constant_coefficient())
        raise ValueError(f"cannot parse the polynomial {text!r}")
    return ev(ast.parse(text.replace("^", "**"), mode="eval").body)


def parse_circuit(path):
    """Input format:
         vars s1 s0 a0 b0
         order lex             (lex | deglex | degrevlex)
         spec <polynomial>     (the specification S)
         <one polynomial per line: the gate polynomials and the Boolean constraints>
    Lines starting with # are comments. Returns the polynomial ring, S, and the list F of polynomials."""
    with open(path) as fh:
        lines = [l.strip() for l in fh if l.strip() and not l.strip().startswith("#")]
    names = lines[0].split()[1:]
    order = lines[1].split()[1]
    R = PolynomialRing(QQ, names, len(names), order=order)     # multivariate, even for one variable
    if lines[2].split()[0] != "spec":
        raise ValueError("the third line must be  spec <polynomial>")
    return R, parse_poly(R, lines[2][4:].strip()), [parse_poly(R, l) for l in lines[3:]]


def main(path):
    R, S, F = parse_circuit(path)
    correct, r = member(S, F)                          # the circuit is correct iff S is in <F>
    print("s CORRECT" if correct else "s INCORRECT")
    print(f"r {r}")


if __name__ == "__main__":
    main(sys.argv[1])
