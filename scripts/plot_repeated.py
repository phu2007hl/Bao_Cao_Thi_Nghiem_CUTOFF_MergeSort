import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "repeated"
OUTPUT = INPUT / "charts"
REPORT = ROOT / "report" / "figures"
OUTPUT.mkdir(parents=True, exist_ok=True)
REPORT.mkdir(parents=True, exist_ok=True)

names = ["random_10000", "random_20000", "random_50000", "random_100000", "random_200000", "random_500000", "random_1000000"]
cutoffs = [7, 10, 12]
values = {}
best = {}
for name in names:
    values[name] = {cutoff: [] for cutoff in cutoffs}
    best[name] = []
    for batch in range(1, 6):
        with (INPUT / f"batch_{batch}" / f"{name}.csv").open(newline="") as f:
            rows = list(csv.DictReader(f))
        lookup = {int(row["cutoff"]): float(row["median_ms"]) for row in rows}
        for cutoff in cutoffs:
            values[name][cutoff].append(lookup[cutoff])
        best[name].append(min(lookup, key=lookup.get))

fig, axes = plt.subplots(2, 4, figsize=(19, 9), dpi=150, sharey=False)
colors = {7: "#d95f02", 10: "#1b9e77", 12: "#7570b3"}
for axis, name in zip(axes.flat, names):
    batches = np.arange(1, 6)
    for cutoff in cutoffs:
        axis.plot(batches, values[name][cutoff], marker="o", linewidth=2.2, markersize=5, color=colors[cutoff], label=f"CUTOFF = {cutoff}")
    axis.set_title(f"N = {int(name.rsplit('_', 1)[1]):,}", fontsize=11, fontweight="bold")
    axis.set_xlabel("Batch", fontsize=9)
    axis.set_ylabel("Median (ms)", fontsize=9)
    axis.set_xticks(batches)
    axis.grid(True, linestyle="--", alpha=.4)
axes.flat[-1].axis("off")
handles, labels = axes.flat[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=3, frameon=True, fontsize=11)
fig.suptitle("Độ dao động thời gian qua 5 batch độc lập trên dữ liệu Random", fontsize=18, fontweight="bold")
fig.tight_layout(rect=[0, .08, 1, .94])
fig.savefig(OUTPUT / "batch_variation_random.png", dpi=150)
fig.savefig(REPORT / "batch_variation_random.png", dpi=150)
plt.close(fig)

fig, axis = plt.subplots(figsize=(13, 7), dpi=150)
x = np.arange(len(names))
for batch in range(5):
    axis.plot(x, [best[name][batch] for name in names], marker="o", linewidth=2, label=f"Batch {batch + 1}")
axis.set_xticks(x, [f"{int(name.rsplit('_', 1)[1]) // 1000}k" if int(name.rsplit('_', 1)[1]) < 1000000 else "1M" for name in names])
axis.set_xlabel("Kích thước mảng N")
axis.set_ylabel("CUTOFF tốt nhất trong batch")
axis.set_title("CUTOFF tốt nhất thay đổi qua 5 batch", fontsize=18, fontweight="bold")
axis.set_yticks(sorted(set(value for series in best.values() for value in series)))
axis.grid(True, linestyle="--", alpha=.4)
axis.legend(ncol=3, frameon=True)
fig.tight_layout()
fig.savefig(OUTPUT / "best_cutoff_across_batches.png", dpi=150)
fig.savefig(REPORT / "best_cutoff_across_batches.png", dpi=150)
plt.close(fig)
