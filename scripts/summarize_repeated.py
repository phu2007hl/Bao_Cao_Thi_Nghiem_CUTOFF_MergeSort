from pathlib import Path
import csv
import statistics

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "repeated"
OUTPUT = INPUT / "summary"
OUTPUT.mkdir(parents=True, exist_ok=True)
datasets = sorted(path.stem for path in (INPUT / "batch_1").glob("*.csv") if not path.name.startswith("runs_"))
all_rows = []
for dataset in datasets:
    batches = []
    for batch in range(1, 6):
        with (INPUT / f"batch_{batch}" / f"{dataset}.csv").open(newline="") as f:
            batches.append({int(row["cutoff"]): float(row["median_ms"]) for row in csv.DictReader(f)})
    cutoffs = sorted(batches[0])
    best_by_batch = [min(batch, key=batch.get) for batch in batches]
    for cutoff in cutoffs:
        values = [batch[cutoff] for batch in batches]
        all_rows.append({"dataset": dataset, "cutoff": cutoff, "mean_median_ms": f"{statistics.mean(values):.3f}", "stdev_median_ms": f"{statistics.stdev(values):.3f}", "best_batch_count": best_by_batch.count(cutoff), "relative_to_best_pct": f"{100 * (statistics.mean(values) / min(statistics.mean(batch[c] for batch in batches) for c in cutoffs) - 1):.2f}"})
with (OUTPUT / "cutoff_stability.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
    writer.writeheader(); writer.writerows(all_rows)
overview = []
for dataset in datasets:
    rows = [row for row in all_rows if row["dataset"] == dataset]
    best = min(rows, key=lambda row: float(row["mean_median_ms"]))
    overview.append({"dataset": dataset, "stable_cutoff": best["cutoff"], "mean_median_ms": best["mean_median_ms"], "stdev_median_ms": best["stdev_median_ms"], "best_batch_count": best["best_batch_count"]})
with (OUTPUT / "stable_best_cutoffs.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=overview[0].keys())
    writer.writeheader(); writer.writerows(overview)
random_names = [row["dataset"] for row in overview if row["dataset"].startswith("random_")]
comparison = []
for dataset in random_names:
    rows = {int(row["cutoff"]): row for row in all_rows if row["dataset"] == dataset}
    comparison.append({"dataset": dataset, **{f"cutoff_{cutoff}_mean_ms": rows[cutoff]["mean_median_ms"] for cutoff in (7, 10, 12)}, **{f"cutoff_{cutoff}_stdev_ms": rows[cutoff]["stdev_median_ms"] for cutoff in (7, 10, 12)}})
with (OUTPUT / "compare_7_10_12.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=comparison[0].keys())
    writer.writeheader(); writer.writerows(comparison)

random_datasets = sorted(random_names, key=lambda name: int(name.rsplit("_", 1)[-1]))
aggregate_rows = []
for cutoff in sorted({int(row["cutoff"]) for row in all_rows}):
    batch_relative = []
    for batch_index in range(1, 6):
        relative_values = []
        for dataset in random_datasets:
            values = {int(row["cutoff"]): float(row["mean_median_ms"]) for row in all_rows if row["dataset"] == dataset and int(row["cutoff"]) == cutoff}
            batch_file = INPUT / f"batch_{batch_index}" / f"{dataset}.csv"
            with batch_file.open(newline="") as f:
                batch_values = {int(row["cutoff"]): float(row["median_ms"]) for row in csv.DictReader(f)}
            relative_values.append(batch_values[cutoff] / min(batch_values.values()))
        batch_relative.append(sum(relative_values) / len(relative_values))
    aggregate_rows.append({"cutoff": cutoff, "mean_relative_to_batch_best": f"{statistics.mean(batch_relative):.6f}", "stdev_across_batches": f"{statistics.stdev(batch_relative):.6f}"})
with (OUTPUT / "random_aggregate_repeated.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=aggregate_rows[0].keys())
    writer.writeheader(); writer.writerows(aggregate_rows)
