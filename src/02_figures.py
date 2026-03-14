#!/usr/bin/env python3
"""
02_figures.py
=============
Generate Figures 1-4 for the Regulatory Waterbed paper.
Reads from data/openalex_raw.json if available, otherwise uses hardcoded values.

Usage: python src/02_figures.py
"""
import numpy as np
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif", "font.size": 10, "axes.labelsize": 11,
    "figure.dpi": 300, "mathtext.fontset": "cm",
    "axes.spines.top": False, "axes.spines.right": False,
})

FIG_DIR = Path(__file__).parent.parent / "figures"
FIG_DIR.mkdir(exist_ok=True)
DATA_DIR = Path(__file__).parent.parent / "data"

# ---- Load or hardcode data ----
years = np.arange(2015, 2026)

try:
    with open(DATA_DIR / "openalex_raw.json") as f:
        raw = json.load(f)
    disagreement = np.array([raw["esg_rating_disagreement"].get(str(y), 0) for y in years])
    disclosure = np.array([raw["esg_disclosure"].get(str(y), 1) for y in years])
    scope3 = np.array([raw["scope3_emissions"].get(str(y), 0) for y in years])
    scope12 = np.array([raw["scope1_scope2_emissions"].get(str(y), 1) for y in years])
    assurance = np.array([raw["sustainability_assurance"].get(str(y), 0) for y in years])
    greenwashing = np.array([raw["greenwashing"].get(str(y), 0) for y in years])
    data_quality = np.array([raw["esg_data_quality"].get(str(y), 0) for y in years])
    double_mat = np.array([raw["double_materiality"].get(str(y), 0) for y in years])
    print("  Loaded data from openalex_raw.json")
except FileNotFoundError:
    print("  Using hardcoded values (run 01_openalex_query.py first for live data)")
    disagreement = np.array([0, 2, 5, 8, 18, 45, 89, 156, 267, 412, 531])
    disclosure = np.array([1200, 1450, 1680, 1950, 2300, 3050, 4200, 5800, 7500, 9200, 10800])
    scope3 = np.array([320, 380, 410, 350, 390, 520, 580, 610, 650, 780, 920])
    scope12 = np.array([200, 220, 230, 210, 230, 280, 310, 340, 370, 410, 430])
    assurance = np.array([100, 110, 120, 135, 150, 198, 280, 450, 700, 950, 1191])
    greenwashing = np.array([636, 780, 920, 1100, 1400, 2200, 3800, 5600, 7200, 9100, 10901])
    data_quality = np.array([0, 0, 0, 0, 2, 5, 12, 22, 35, 48, 61])
    double_mat = np.array([21, 28, 35, 48, 72, 120, 210, 350, 520, 650, 741])

ratio_process = disagreement / np.maximum(disclosure, 1)
ratio_supply = scope3 / np.maximum(scope12, 1)

# KPMG survey data
kpmg_years = [2005, 2008, 2011, 2013, 2015, 2017, 2020, 2022, 2024]
assurance_g250 = [30, 40, 46, 59, 63, 67, 51, 58, 69]
assurance_n100 = [33, 39, 38, 44, 44, 41, 47, 47, 54]


# ============================================================
# FIGURE 1: Migration Evidence (3 panels)
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))

ax = axes[0]
ax.plot(years, ratio_process, "ko-", ms=4, lw=1.5)
ax.axvline(2020, color="gray", ls="--", lw=0.8, alpha=0.5)
ax.fill_between(years, ratio_process, alpha=0.1, color="k")
ax.set_ylabel("Disagreement / Disclosure ratio")
ax.set_title("(a) Processing layer", fontweight="normal", fontsize=10)
ax.set_xlabel("Year")
ax.grid(True, alpha=0.2)

ax = axes[1]
ax.plot(years, ratio_supply, "ko-", ms=4, lw=1.5)
ax.axvline(2020, color="gray", ls="--", lw=0.8, alpha=0.5)
ax.axhline(1.0, color="gray", ls=":", lw=0.5, alpha=0.3)
ax.fill_between(years, 1.0, ratio_supply, where=ratio_supply > 1, alpha=0.1, color="k")
ax.set_ylabel("Scope-3 / Scope-1,2 ratio")
ax.set_title("(b) Supply chain layer", fontweight="normal", fontsize=10)
ax.set_xlabel("Year")
ax.grid(True, alpha=0.2)

ax = axes[2]
ax.plot(years, assurance, "ko-", ms=4, lw=1.5)
ax.axvline(2020, color="gray", ls="--", lw=0.8, alpha=0.5)
ax.fill_between(years, assurance, alpha=0.1, color="k")
ax.set_ylabel("Papers on sustainability assurance")
ax.set_title("(c) Audit layer", fontweight="normal", fontsize=10)
ax.set_xlabel("Year")
ax.grid(True, alpha=0.2)

plt.tight_layout(w_pad=2)
plt.savefig(FIG_DIR / "fig1_migration_evidence_v2.pdf", bbox_inches="tight")
plt.close()
print("  Figure 1 saved")

# ============================================================
# FIGURE 2: Extended Evidence (2x3)
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(12, 6.5))

for i, (y, lbl, ttl) in enumerate([
    (ratio_process, "Disagree./Disclosure", "(a) Processing"),
    (ratio_supply, "Scope-3/Scope-1,2", "(b) Supply chain"),
    (assurance, "Assurance papers", "(c) Audit"),
]):
    ax = axes[0, i]
    ax.plot(years, y, "ko-", ms=3, lw=1.2)
    ax.axvline(2020, color="gray", ls="--", lw=0.8, alpha=0.5)
    ax.set_ylabel(lbl, fontsize=9)
    ax.set_title(ttl, fontweight="normal", fontsize=10)
    ax.grid(True, alpha=0.2)

for i, (y, lbl, ttl) in enumerate([
    (greenwashing, "Greenwashing papers", "(d) Greenwashing"),
    (data_quality, "Data quality papers", "(e) ESG data quality"),
    (double_mat, "Double materiality papers", "(f) Double materiality"),
]):
    ax = axes[1, i]
    ax.plot(years, y, "ko-", ms=3, lw=1.2)
    ax.axvline(2020, color="gray", ls="--", lw=0.8, alpha=0.5)
    ax.fill_between(years, y, alpha=0.08, color="k")
    ax.set_ylabel(lbl, fontsize=9)
    ax.set_title(ttl, fontweight="normal", fontsize=10)
    ax.set_xlabel("Year")
    ax.grid(True, alpha=0.2)

plt.tight_layout(h_pad=2, w_pad=2)
plt.savefig(FIG_DIR / "fig2_extended_evidence.pdf", bbox_inches="tight")
plt.close()
print("  Figure 2 saved")

# ============================================================
# FIGURE 3: Assurance Gap (2 panels)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(11, 4))

ax = axes[0]
ax.plot(kpmg_years, assurance_g250, "ks-", ms=5, lw=1.5, label="G250")
ax.plot(kpmg_years, assurance_n100, "ko--", ms=4, lw=1.2, alpha=0.6, label="N100")
ax.set_ylabel("% with sustainability assurance")
ax.set_xlabel("Year")
ax.set_title("(a) Assurance adoption (KPMG)", fontweight="normal", fontsize=10)
ax.legend(fontsize=9)
ax.set_ylim([0, 100])
ax.grid(True, alpha=0.2)

ax = axes[1]
categories = ["Report\npublicly", "Have some\nassurance", "Audit\nready", "Data\nchallenging"]
values = [77, 54, 29, 83]
colors_bar = ["#888780", "#888780", "#D85A30", "#D85A30"]
bars = ax.bar(categories, values, color=colors_bar, alpha=0.6, edgecolor="k", linewidth=0.5)
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
            f"{val}%", ha="center", fontsize=10, fontweight="bold")
ax.set_ylabel("% of N100 companies")
ax.set_title("(b) CSRD readiness gap (2024)", fontweight="normal", fontsize=10)
ax.set_ylim([0, 100])
ax.grid(True, alpha=0.2, axis="y")

plt.tight_layout(w_pad=3)
plt.savefig(FIG_DIR / "fig3_assurance_gap.pdf", bbox_inches="tight")
plt.close()
print("  Figure 3 saved")

# ============================================================
# FIGURE 4: Arrival Times (2 panels)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(11, 4))

audit_n = assurance / assurance[0]
supply_n = scope3 / scope3[0]
process_n = disagreement.copy().astype(float)
process_n[process_n == 0] = 0.5
process_n = process_n / process_n[0]

clrs = ["#534AB7", "#1D9E75", "#D85A30"]
lbls = ["Audit", "Supply chain", "Processing"]

ax = axes[0]
for s, c, l in zip([audit_n, supply_n, process_n], clrs, lbls):
    ax.plot(years, s, "o-", color=c, ms=4, lw=1.5, label=l)
ax.axvline(2020, color="gray", ls="--", lw=0.8, alpha=0.5)
ax.set_ylabel("Growth (2015 = 1)")
ax.set_xlabel("Year")
ax.set_title("(a) Growth trajectories (normalized)", fontweight="normal", fontsize=10)
ax.legend(fontsize=8)
ax.set_yscale("log")
ax.grid(True, alpha=0.2)

def yoy(x):
    return np.concatenate([[0], np.diff(x) / np.maximum(x[:-1], 1) * 100])

ax = axes[1]
for s, c, l in zip([assurance, scope3, disagreement], clrs, lbls):
    ax.plot(years[1:], yoy(s)[1:], "o-", color=c, ms=4, lw=1.2, label=l)
ax.axhline(50, color="gray", ls=":", lw=0.8, alpha=0.5, label=">50% threshold")
ax.axvline(2020, color="gray", ls="--", lw=0.8, alpha=0.5)
ax.set_ylabel("Year-over-year growth (%)")
ax.set_xlabel("Year")
ax.set_title("(b) YoY growth rates", fontweight="normal", fontsize=10)
ax.legend(fontsize=7, ncol=2)
ax.set_ylim([-20, 200])
ax.grid(True, alpha=0.2)

plt.tight_layout(w_pad=2)
plt.savefig(FIG_DIR / "fig4_arrival_times.pdf", bbox_inches="tight")
plt.close()
print("  Figure 4 saved")

print("\nAll figures generated.")
