"""Pick a fair, reproducible QA audit sample from a batch of labeled tasks.

Instead of reviewing random rows, the sample is stratified: every annotator and
every label gets reviewed, so rare labels and new annotators aren't missed.

Input CSV columns (others are kept and copied to the output):
    task_id, annotator, label

Usage:
    python audit_sampler.py tasks.csv --rate 0.1 --min-per-group 2 --seed 42 --out audit.csv
"""
import argparse
import csv
import math
import random
from collections import defaultdict


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    missing = {"task_id", "annotator", "label"} - set(rows[0] if rows else {})
    if missing:
        raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
    return rows


def sample(rows, rate=0.1, min_per_group=2, seed=42, by=("annotator", "label")):
    """Stratified sample: from each (annotator, label) group take ceil(rate * size),
    but at least `min_per_group` (or the whole group if it is smaller)."""
    if not 0 < rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    groups = defaultdict(list)
    for r in rows:
        groups[tuple(r[k] for k in by)].append(r)
    rng = random.Random(seed)
    picked = []
    for key in sorted(groups):
        members = groups[key]
        n = min(len(members), max(min_per_group, math.ceil(rate * len(members))))
        picked += rng.sample(members, n)
    return sorted(picked, key=lambda r: r["task_id"])


def coverage(rows, picked, field):
    """How many rows per value of `field` exist vs. were sampled."""
    total, chosen = defaultdict(int), defaultdict(int)
    for r in rows:
        total[r[field]] += 1
    for r in picked:
        chosen[r[field]] += 1
    return {k: (chosen[k], total[k]) for k in sorted(total)}


def summary(rows, picked):
    lines = [f"Sampled {len(picked)} of {len(rows)} tasks ({len(picked) / len(rows):.0%})", ""]
    for field in ("annotator", "label"):
        lines.append(f"By {field}:")
        cov = coverage(rows, picked, field)
        width = max(len(k) for k in cov)
        for k, (c, t) in cov.items():
            lines.append(f"  {k:<{width}}  {c:>3} / {t}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("csv")
    p.add_argument("--rate", type=float, default=0.1, help="share of each group to review (default 0.1)")
    p.add_argument("--min-per-group", type=int, default=2, help="minimum items per annotator/label group")
    p.add_argument("--seed", type=int, default=42, help="random seed, so the same sample can be recreated")
    p.add_argument("--out", help="write the sample to this CSV")
    a = p.parse_args(argv)
    rows = load(a.csv)
    picked = sample(rows, a.rate, a.min_per_group, a.seed)
    print(summary(rows, picked))
    if a.out:
        with open(a.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(picked)
        print(f"\nWrote {a.out}")


if __name__ == "__main__":
    main()
