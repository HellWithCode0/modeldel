"""
Figures for paper/ADT_foundations.md.  Recomputes everything from the
prime cycle data (see README for how to generate it).

  fig2_collision_vs_depth.png   Pr[depth-K fingerprints of two primes agree]
  fig1_single_probe_collisions.png   prime collisions for one probe vs X
  fig3_least_depth.png          least injective depth vs number of primes
"""
import os
from bisect import bisect_right
from collections import Counter
from statistics import median

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from adt import SCRATCH, load_primes, truncate, zset_canon
from exp_depth import least_depth, INF

SCR = SCRATCH
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
os.makedirs(OUT, exist_ok=True)

# reference palette (validated: all-pairs, light mode) + recessive neutrals
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
MARKERS = ["o", "s", "^"]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "grid.linestyle": "-",
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10.5,
    "axes.titlesize": 12, "axes.titleweight": "semibold", "axes.titlecolor": INK,
    "legend.frameon": False, "legend.labelcolor": INK,
})

GEN = [1, 2, 3, 4, 5, 7, -4, -5]
loc = load_primes(os.path.join(SCR, "data", "primes_c{c}.txt"), GEN)
primes = sorted({p for (p, c) in loc})


def style(ax, title, xlabel, ylabel):
    ax.set_title(title, loc="left", pad=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(length=0)


# ---------------------------------------------------------------- fig 1
win = primes[bisect_right(primes, 40000):]
npairs = len(win) * (len(win) - 1) // 2
Ks = [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64]
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for i, S in enumerate(([2], [2, 5], [2, 5, -4])):
    xs, ys = [], []
    for K in Ks:
        cnt = Counter(tuple(truncate(loc[(p, c)], K) for c in S) for p in win)
        pr = sum(v * (v - 1) // 2 for v in cnt.values()) / npairs
        if pr > 0:
            xs.append(K)
            ys.append(pr)
    ax.plot(xs, ys, color=SERIES[i], lw=2, marker=MARKERS[i], ms=6, mec=SURF, mew=1.5,
            label=f"|S| = {len(S)}   (S = {{{', '.join(map(str, S))}}})")
    # reference power law K^(-2|S|) anchored at the last point
    k0, y0 = xs[-1], ys[-1]
    ref = [y0 * (k / k0) ** (-2 * len(S)) for k in (8, 64)]
    ax.plot([8, 64], ref, color=INK2, lw=1, ls=":", zorder=0)
    ax.annotate(f"slope −{2*len(S)}", (64, ref[1]), textcoords="offset points", xytext=(6, 0),
                ha="left", va="center", color=INK2, fontsize=9)
ax.set_xscale("log", base=2)
ax.set_yscale("log")
ax.set_xlim(1.8, 110)
style(ax, "Two primes' depth-K fingerprints agree w.p. ≍ K^(−2|S|)",
      "depth K", "fraction of prime pairs with equal fingerprint")
ax.legend(loc="lower left")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig2_collision_vs_depth.png"), dpi=160)

# ---------------------------------------------------------------- fig 2
from math import log, sqrt

Xs = [1000, 2000, 5000, 10000, 20000, 50000, 100000]
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for i, c in enumerate((1, 2, 3)):
    ys = []
    for X in Xs:
        b = Counter(zset_canon(loc[(p, c)]) for p in primes if p <= X)
        ys.append(sum(v * (v - 1) // 2 for v in b.values()))
    ax.plot(Xs, ys, color=SERIES[i], lw=2, marker=MARKERS[i], ms=6, mec=SURF, mew=1.5, label=f"c = {c}")
h = [sqrt(X) / log(X) ** 2 for X in Xs]
scale = 120 / h[-1]
ax.plot(Xs, [scale * v for v in h], color=INK2, lw=1, ls=":", zorder=0)
ax.annotate("∝ X^(1/2) / log²X", (Xs[-1], scale * h[-1]), textcoords="offset points",
            xytext=(-6, -14), ha="right", color=INK2, fontsize=9)
ax.set_xscale("log")
ax.set_yscale("log")
style(ax, "One probe: prime collisions keep appearing",
      "X", "pairs p < q ≤ X with Per_c(p) ≅ Per_c(q)")
ax.legend(loc="upper left")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig1_single_probe_collisions.png"), dpi=160)

# ---------------------------------------------------------------- fig 3
sets = {2: [[2, 5], [1, 4], [3, -5]], 3: [[2, 5, -4], [1, 4, -5], [3, 7, -4]], 4: [[1, 2, 5, -4], [3, 4, 7, -5]]}
Xw = [1250, 2500, 5000, 10000, 20000, 40000, 80000]
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for i, (s, Ss) in enumerate(sets.items()):
    xs, ys = [], []
    for X in Xw:
        w = primes[bisect_right(primes, X // 2):bisect_right(primes, X)]
        Kv = [least_depth([tuple(loc[(p, c)] for c in S) for p in w]) for S in Ss]
        Kv = [k for k in Kv if k < INF]
        if Kv:
            xs.append(len(w))
            ys.append(median(Kv))
    ax.plot(xs, ys, color=SERIES[i], lw=2, marker=MARKERS[i], ms=6, mec=SURF, mew=1.5,
            label=f"|S| = {s}  (median of {len(Ss)} probe sets)")
    ref = [ys[-1] * (x / xs[-1]) ** (1 / s) for x in (xs[0], xs[-1])]
    ax.plot([xs[0], xs[-1]], ref, color=INK2, lw=1, ls=":", zorder=0)
    ax.annotate(f"slope 1/{s}", (xs[-1], ref[1]), textcoords="offset points", xytext=(8, 0),
                ha="left", va="center", color=INK2, fontsize=9)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(70, 7000)
style(ax, "Depth needed to separate primes in (X/2, X]",
      "number of primes in the window", "least injective depth K")
ax.legend(loc="upper left")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig3_least_depth.png"), dpi=160)
print("figures written to", os.path.abspath(OUT))
