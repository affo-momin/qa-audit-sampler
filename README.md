# 🎯 QA Audit Sampler

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white) ![No dependencies](https://img.shields.io/badge/dependencies-none-2ea44f?style=flat-square) ![Tests](https://img.shields.io/badge/tests-unittest-2ea44f?style=flat-square) ![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)

Pick a fair, reproducible QA audit sample from a batch of labeled tasks, stratified by annotator and label so nobody and nothing gets skipped.

## Why this exists

Random spot checks tend to miss rare labels and new annotators, which is exactly where errors hide. This tool samples a set share of every annotator-and-label group, with a minimum per group, and a fixed seed so the same audit can be recreated later.

## Features

- **Stratified sampling** by annotator and label
- **Sample rate** plus a **minimum per group**, so small groups are always covered
- **Reproducible**: the same `--seed` gives the same sample
- **Coverage summary** showing sampled vs. total per annotator and per label
- Writes the audit list to a CSV, keeping all original columns
- Command-line options via `argparse` (`--help` lists them)

## Quick start

No installs needed, just Python 3.9+.

```bash
git clone https://github.com/affo-momin/qa-audit-sampler.git
cd qa-audit-sampler
python audit_sampler.py sample_tasks.csv --rate 0.1 --min-per-group 2
```

## Input

A CSV with at least `task_id, annotator, label`. Extra columns (like `query`) are kept in the output.

## Sample output

Running `python audit_sampler.py sample_tasks.csv --rate 0.1 --min-per-group 2` on the included sample data:

```text
Sampled 19 of 120 tasks (16%)

By annotator:
  ann_a    8 / 60
  ann_b    6 / 31
  ann_c    5 / 29

By label:
  off_topic             5 / 17
  partially_relevant    7 / 43
  relevant              7 / 60
```

## Tests

```bash
python -m unittest -v test_audit_sampler
```

## License

MIT
