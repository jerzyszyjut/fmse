import argparse
from pathlib import Path
from pysat.formula import CNF
from pysat.solvers import Cadical195


def compute_backbone(cnf_path: Path) -> list[int]:
    formula = CNF(from_file=cnf_path)

    with Cadical195(bootstrap_with=formula) as solver:
        solver.solve()

        candidates = set(solver.get_model())
        backbone = set()

        while candidates:
            lit = candidates.pop()

            answer = solver.solve(assumptions=[-lit])

            if not answer:
                backbone.add(lit)
                solver.add_clause([lit])
            else:
                candidates &= set(solver.get_model())

    return sorted(backbone)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf_file", type=Path)
    args = parser.parse_args()

    backbone = compute_backbone(args.cnf_file)

    print("b", *backbone, 0)
    print("c", len(backbone))


if __name__ == "__main__":
    main()