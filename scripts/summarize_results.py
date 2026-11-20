from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
raw = ROOT / "results" / "raw"
summary = ROOT / "results" / "summary"
summary.mkdir(parents=True, exist_ok=True)
rows = []
all_results = {}
for file in sorted(raw.glob("*.csv")):
    if file.name.startswith("runs_"):
        continue
    with file.open(newline="") as f:
        data = list(csv.DictReader(f))
    all_results[file.stem] = data
    best = min(data, key=lambda r: float(r["median_ms"]))
    baseline = float(data[0]["median_ms"])
    rows.append({"dataset": file.stem, "best_cutoff": best["cutoff"], "best_median_ms": best["median_ms"], "improvement_pct": f"{100 * (baseline - float(best['median_ms'])) / baseline:.2f}"})
with (summary / "summary.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else ["dataset"])
    writer.writeheader(); writer.writerows(rows)

random_results = {
    name: data for name, data in all_results.items()
    if name.startswith("random_") and name.rsplit("_", 1)[-1].isdigit()
}
ranges = [("baseline_1", 1, 1), ("cutoff_2_5", 2, 5), ("cutoff_6_10", 6, 10),
          ("cutoff_11_15", 11, 15), ("cutoff_16_25", 16, 25),
          ("cutoff_26_40", 26, 40), ("cutoff_50_100", 50, 100)]
range_rows = []
for name, data in sorted(random_results.items(), key=lambda item: int(item[0].rsplit("_", 1)[-1])):
    base = float(data[0]["median_ms"])
    best = min(data, key=lambda r: float(r["median_ms"]))
    record = {"N": int(name.rsplit("_", 1)[-1]), "best_cutoff": int(best["cutoff"]),
              "max_speedup_pct": round(100 * (base - float(best["median_ms"])) / base, 2)}
    for label, lo, hi in ranges:
        values = [float(r["median_ms"]) for r in data if lo <= int(r["cutoff"]) <= hi]
        record[label + "_mean_ms"] = round(sum(values) / len(values), 3) if values else ""
    range_rows.append(record)
with (summary / "table_cutoff_ranges_by_N.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=range_rows[0].keys())
    writer.writeheader(); writer.writerows(range_rows)

targets = ["random_100000", "sorted_100000", "reversed_100000", "nearly_sorted_100000",
           "few_distinct_100000", "all_equal_100000", "edge_values_10000"]
key_cutoffs = [1, 7, 10, 12, 15, 20, 30, 40, 100]
distribution_rows = []
for name in targets:
    if name not in all_results:
        continue
    data = all_results[name]
    lookup = {int(r["cutoff"]): float(r["median_ms"]) for r in data}
    base = lookup[1]
    best = min(data, key=lambda r: float(r["median_ms"]))
    record = {"dataset": name, "best_cutoff": int(best["cutoff"]),
              "best_time_ms": round(float(best["median_ms"]), 3),
              "improvement_pct": round(100 * (base - float(best["median_ms"])) / base, 2)}
    for cutoff in key_cutoffs:
        record["cutoff_" + str(cutoff) + "_ms"] = round(lookup[cutoff], 3)
    distribution_rows.append(record)
with (summary / "table_cutoff_by_distributions.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=distribution_rows[0].keys())
    writer.writeheader(); writer.writerows(distribution_rows)


import glob
import os
import numpy as np
import pandas as pd
from scipy import stats

RAW = str(raw)
SUM = str(summary)
NS = [10000, 20000, 50000, 100000, 200000, 500000, 1000000]
BOOTSTRAP = 4000
rng = np.random.default_rng(20261116)

D = {}
for p in glob.glob(os.path.join(RAW, "runs_*.csv")):
    name = os.path.basename(p)[5:-4]
    df = pd.read_csv(p)
    D[name] = {c: g.sort_values("run_index")["elapsed_ms"].to_numpy() for c, g in df.groupby("cutoff")}
CUT = sorted(D["random_100000"])
med = lambda ds, c: float(np.median(D[ds][c]))


def stats_table():
    rows = []
    for name, d in D.items():
        for c in CUT:
            v = d[c]
            rows.append(dict(dataset=name, cutoff=c, n_runs=len(v), median=np.median(v), min=v.min(),
                             mean=v.mean(), sd=v.std(ddof=1), cv_pct=100 * v.std(ddof=1) / v.mean()))
    return pd.DataFrame(rows)


def best_by_n(S):
    rows = []
    for n in NS:
        s = S[S.dataset == f"random_{n}"].set_index("cutoff")
        t, tn = s["median"].min(), s["min"].min()
        zone = [c for c in CUT if s.loc[c, "median"] <= 1.02 * t]
        zonen = [c for c in CUT if s.loc[c, "min"] <= 1.02 * tn]
        r = dict(N=n, best_median=s["median"].idxmin(), T_best=t, gain_pct=100 * (1 - t / s.loc[1, "median"]),
                 zone_median=f"{min(zone)}-{max(zone)}", best_min=s["min"].idxmin(), zone_min=f"{min(zonen)}-{max(zonen)}")
        for c in (7, 10, 12):
            r[f"slower_{c}_pct"] = 100 * (s.loc[c, "median"] / t - 1)
        rows.append(r)
    return pd.DataFrame(rows)


def relative_matrix(S, stat):
    M = np.zeros((len(CUT), len(NS)))
    for j, n in enumerate(NS):
        s = S[S.dataset == f"random_{n}"].set_index("cutoff")[stat]
        M[:, j] = s.loc[CUT].to_numpy() / s.min()
    return M


def aggregate(S):
    Rm, Rn = relative_matrix(S, "median"), relative_matrix(S, "min")
    agg = pd.DataFrame(dict(cutoff=CUT, mean_median=Rm.mean(1), worst_median=Rm.max(1),
                            mean_min=Rn.mean(1), worst_min=Rn.max(1)))
    boot = np.zeros((BOOTSTRAP, len(CUT)))
    for b in range(BOOTSTRAP):
        M = np.zeros((len(CUT), len(NS)))
        for j, n in enumerate(NS):
            d = D[f"random_{n}"]
            m = np.array([np.median(rng.choice(d[c], size=len(d[c]), replace=True)) for c in CUT])
            M[:, j] = m / m.min()
        boot[b] = M.mean(1)
    agg["ci_lo"] = np.percentile(boot, 2.5, axis=0)
    agg["ci_hi"] = np.percentile(boot, 97.5, axis=0)
    winner = boot.argmin(1)
    agg["p_best"] = [np.mean(winner == i) for i in range(len(CUT))]
    idx = {c: k for k, c in enumerate(CUT)}
    rows = []
    for a, b in [(7, 10), (7, 12), (10, 12), (1, 12)]:
        diff = boot[:, idx[a]] - boot[:, idx[b]]
        rows.append(dict(a=a, b=b, mean_diff=diff.mean(), ci_lo=np.percentile(diff, 2.5),
                         ci_hi=np.percentile(diff, 97.5), p_a_slower=np.mean(diff > 0)))
    return agg, pd.DataFrame(rows)


def mann_whitney():
    rows = []
    for n in NS:
        d = D[f"random_{n}"]
        r = dict(N=n)
        for a, b in [(7, 10), (7, 12), (10, 12), (1, 10), (1, 12)]:
            r[f"{a}_vs_{b}"] = stats.mannwhitneyu(d[a], d[b], alternative="two-sided").pvalue
        rows.append(r)
    return pd.DataFrame(rows)


def distributions(S):
    names = ["random_100000", "sorted_100000", "reversed_100000", "nearly_sorted_100000",
             "few_distinct_100000", "all_equal_100000", "edge_values_10000"]
    rows = []
    for name in names:
        if name not in D:
            continue
        s = S[S.dataset == name].set_index("cutoff")
        t = s["median"].min()
        zone = [c for c in CUT if s.loc[c, "median"] <= 1.02 * t]
        rows.append(dict(dataset=name, best_median=s["median"].idxmin(), T_best=t, T1=s.loc[1, "median"],
                         T7=s.loc[7, "median"], T10=s.loc[10, "median"], T12=s.loc[12, "median"],
                         T100=s.loc[100, "median"], gain_pct=100 * (1 - t / s.loc[1, "median"]),
                         zone=f"{min(zone)}-{max(zone)}"))
    return pd.DataFrame(rows)



S = stats_table()
S.to_csv(os.path.join(SUM, "analysis_stats_all.csv"), index=False)
best_by_n(S).to_csv(os.path.join(SUM, "analysis_best_by_N.csv"), index=False)
agg, pair = aggregate(S)
agg.to_csv(os.path.join(SUM, "analysis_aggregate.csv"), index=False)
pair.to_csv(os.path.join(SUM, "analysis_bootstrap_pairs.csv"), index=False)
mann_whitney().to_csv(os.path.join(SUM, "analysis_mann_whitney.csv"), index=False)
distributions(S).to_csv(os.path.join(SUM, "analysis_distributions.csv"), index=False)

