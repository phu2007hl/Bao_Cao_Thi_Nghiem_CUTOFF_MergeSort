"""Vẽ biểu đồ từ results/raw/runs_*.csv và results/summary/analysis_aggregate.csv.

Chạy sau summarize_results.py (script đó tạo analysis_aggregate.csv).
Đầu ra: results/charts/chart1..5_*.png và report/figures/chart1..5.png
Chạy  : python scripts/plot_results.py
"""
import glob
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "results", "raw")
SUM = os.path.join(ROOT, "results", "summary")
OUT = os.path.join(ROOT, "results", "charts")
FIG = os.path.join(ROOT, "report", "figures")
for d in (OUT, FIG):
    os.makedirs(d, exist_ok=True)

NS = [10000, 20000, 50000, 100000, 200000, 500000, 1000000]

D = {}
for p in glob.glob(os.path.join(RAW, "runs_*.csv")):
    name = os.path.basename(p)[5:-4]
    df = pd.read_csv(p)
    D[name] = {c: g.sort_values("run_index")["elapsed_ms"].to_numpy() for c, g in df.groupby("cutoff")}
CUT = sorted(D["random_100000"])
med = lambda ds, c: float(np.median(D[ds][c]))


plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
    "axes.spines.right": False, "axes.edgecolor": "#8a8985", "axes.labelcolor": "#52514e",
    "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.titlecolor": "#0b0b0b", "axes.grid": True, "grid.color": "#e6e5e1", "grid.linewidth": .8,
    "axes.axisbelow": True, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    "savefig.facecolor": "#fcfcfb"})
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]
INK = "#0b0b0b"
fmtN = lambda n: f"{n:,}".replace(",", ".")


def save(fig, idx, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"chart{idx}_{name}.png"), dpi=200)
    fig.savefig(os.path.join(FIG, f"chart{idx}.png"), dpi=200)
    plt.close(fig)


def cutoff_axis(ax):
    ax.set_xscale("log")
    ax.set_xticks([1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 100])
    ax.get_xaxis().set_major_formatter(FuncFormatter(lambda v, _: str(int(v))))
    ax.minorticks_off()
    ax.set_xlabel("Giá trị CUTOFF (thang log)")


def chart1():
    fig, ax = plt.subplots(figsize=(9, 5.2))
    line_colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7",
                   "#E69F00", "#56B4E9", "#8B5A2B"]
    R = []
    for n, color in zip(NS, line_colors):
        r = np.array([med(f"random_{n}", c) / med(f"random_{n}", 1) for c in CUT]); R.append(r)
        ax.plot(CUT, r, color=color, lw=1.8, marker="o", ms=3.8, label=f"N = {fmtN(n)}")
    ax.plot(CUT, np.mean(R, 0), color=INK, lw=3, label="Trung bình 7 giá trị N")
    ax.axhline(1, color="#8a8985", ls="--", lw=1, label="Baseline: CUTOFF = 1")
    for c, color, style, label in (
        (7, "#E69F00", ":", "CUTOFF = 7"),
        (10, "#7B2CBF", "-.", "CUTOFF = 10"),
    ):
        ax.axvline(c, color=color, ls=style, lw=1.8, label=label)
    yb = ax.get_ylim()[0]
    ax.text(7 / 1.04, yb * 1.01, "7 ", color="#E69F00", ha="right", va="bottom", fontsize=10)
    ax.text(10 * 1.04, yb * 1.01, " 10", color="#7B2CBF", ha="left", va="bottom", fontsize=10)
    cutoff_axis(ax)
    ax.set_ylabel("T(CUTOFF) / T(CUTOFF = 1)  (thấp hơn = nhanh hơn)")
    ax.set_title("Thời gian median chuẩn hoá theo CUTOFF = 1 (dữ liệu random)", loc="left")
    ax.legend(ncol=2, fontsize=9, frameon=False, loc="upper center")
    save(fig, 1, "cutoff_normalized")


def chart2(agg):
    fig, ax = plt.subplots(figsize=(9, 5.0))
    x = np.arange(len(CUT))
    ax.fill_between(x, agg.ci_lo, agg.ci_hi, color=CAT[0], alpha=.15, lw=0, label="Khoảng tin cậy bootstrap 95% (median)")
    ax.plot(x, agg.mean_median, color=CAT[0], lw=2.2, marker="o", ms=5, label="Trung bình độ chậm tương đối (median)")
    ax.plot(x, agg.mean_min, color=CAT[1], lw=2.2, marker="s", ms=5, ls="--", label="Trung bình độ chậm tương đối (min)")
    for c in (7, 10, 12):
        i = CUT.index(c)
        ax.annotate(str(c), (i, agg.mean_median[i]), textcoords="offset points", xytext=(0, -16),
                    ha="center", fontsize=10, color=INK, fontweight="bold")
    ax.axhline(1, color="#8a8985", ls="--", lw=1, label="Mức tối ưu tương đối = 1,00")
    ax.set_xticks(x); ax.set_xticklabels(CUT)
    ax.set_xlabel("Giá trị CUTOFF"); ax.set_ylabel("Thời gian / thời gian tốt nhất của cùng N")
    ax.set_title("Độ chậm tương đối trung bình trên 7 kích thước N (1,00 = tối ưu)", loc="left")
    ax.legend(frameon=False, fontsize=9.5, loc="upper center")
    save(fig, 2, "aggregate")


def chart3():
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for c, col, m, lab in ((1, CAT[1], "s", "CUTOFF = 1 (mergesort thuần)"), (12, CAT[0], "o", "CUTOFF = 12")):
        y = [med(f"random_{n}", c) * 1e6 / (n * np.log2(n)) for n in NS]
        ax.plot(range(len(NS)), y, color=col, marker=m, lw=2.2, ms=6, label=lab)
    ax.set_xticks(range(len(NS))); ax.set_xticklabels([fmtN(n) for n in NS], fontsize=9.5)
    ax.set_xlabel("Kích thước mảng N"); ax.set_ylabel("T / (N·log₂N)  (ns)"); ax.set_ylim(0, None)
    ax.set_title("Thời gian median chia cho N·log₂N (dữ liệu random)", loc="left")
    ax.legend(frameon=False)
    save(fig, 3, "growth_N")


def chart4():
    fig, ax = plt.subplots(figsize=(9, 5.2))
    names = [("random_100000", "random", "o"), ("sorted_100000", "sorted", "s"), ("reversed_100000", "reversed", "^"),
             ("nearly_sorted_100000", "nearly sorted", "D"), ("few_distinct_100000", "few distinct", "v"),
             ("all_equal_100000", "all equal", "P")]
    for (nm, lab, m), col in zip(names, CAT):
        r = np.array([med(nm, c) / med(nm, 1) for c in CUT])
        ax.plot(CUT, r, color=col, marker=m, ms=4.5, lw=1.9, label=lab)
        b = int(np.argmin(r))
        ax.scatter([CUT[b]], [r[b]], marker="*", s=150, color=col, edgecolor=INK, zorder=5)
    ax.axhline(1, color="#8a8985", ls="--", lw=1, label="Baseline: CUTOFF = 1")
    for c, color, style, label in (
        (7, "#E69F00", ":", "CUTOFF = 7"),
        (10, "#7B2CBF", "-.", "CUTOFF = 10"),
    ):
        ax.axvline(c, color=color, ls=style, lw=1.5, label=label)
    cutoff_axis(ax)
    ax.set_ylabel("T(CUTOFF) / T(CUTOFF = 1)")
    ax.set_title("Ảnh hưởng của dạng dữ liệu (N = 100.000; ★ = CUTOFF tốt nhất)", loc="left")
    ax.legend(ncol=3, frameon=False, fontsize=9.5, loc="upper left")
    save(fig, 4, "distributions_100k")


def chart5():
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.6))
    for ax, n, col in zip(axs, (100000, 500000), (CAT[0], CAT[1])):
        nm = f"random_{n}"
        for i, c in enumerate(CUT):
            ax.scatter([i] * len(D[nm][c]), D[nm][c], s=12, color=col, alpha=.45, lw=0)
        ax.plot(range(len(CUT)), [med(nm, c) for c in CUT], color=INK, lw=1.8, label="Median")
        ax.plot(range(len(CUT)), [D[nm][c].min() for c in CUT], color=INK, lw=1.2, ls="--", label="Min")
        ax.set_xticks(range(len(CUT))); ax.set_xticklabels(CUT, fontsize=8)
        ax.set_xlabel("CUTOFF"); ax.set_ylabel("Thời gian (ms)")
        ax.set_title(f"N = {fmtN(n)}: các lần đo mỗi CUTOFF", loc="left", fontsize=11.5)
    axs[0].legend(frameon=False, fontsize=9, loc="upper left")
    save(fig, 5, "noise")


if __name__ == "__main__":
    agg = pd.read_csv(os.path.join(SUM, "analysis_aggregate.csv"))
    chart1(); chart2(agg); chart3(); chart4(); chart5()
    print("Đã ghi biểu đồ vào", OUT, "và", FIG)

