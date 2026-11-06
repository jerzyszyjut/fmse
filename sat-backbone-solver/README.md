# SAT Backbone Solver

A simple Python program for computing the backbone of a SAT formula in CNF format.

## Requirements

- Python 3.12+
- `uv`

## Run

```bash
uv run python backbone_szyjut_12634056.py test_instances/mini_example.cnf
```

The program prints:
- a `b ... 0` line with backbone literals,
- a `c <count>` line with their total count.

## Tests

Run all tests and compare outputs using `diff`:

```fish
./run_tests.fish
```
