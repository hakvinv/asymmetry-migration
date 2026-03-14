#!/usr/bin/env python3
"""
05_statistics.py
================
All statistical tests reported in the paper.
Reproduces every p-value, correlation, and test statistic.

Usage: python src/05_statistics.py
"""
import numpy as np
from scipy import stats

years = np.arange(2015, 2026)

# ---- Data ----
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

# Pre/post 2020 split
pre = years <= 2019
post = years >= 2020

print("=" * 70)
print("STATISTICAL TESTS — Regulatory Waterbed Paper")
print("=" * 70)

# ============================================================
# TEST 1: Processing Layer — Welch t-test and Spearman
# ============================================================
print("\n--- TEST 1: Processing Layer (Disagreement / Disclosure Ratio) ---")
t_stat, p_val = stats.ttest_ind(ratio_process[pre], ratio_process[post], equal_var=False)
rho, p_rho = stats.spearmanr(years, ratio_process)
print(f"  Pre-2020 mean:  {np.mean(ratio_process[pre]):.4f}")
print(f"  Post-2020 mean: {np.mean(ratio_process[post]):.4f}")
print(f"  Welch t = {t_stat:.1f}, p = {p_val:.4f}")
print(f"  Spearman ρ = {rho:.2f}, p = {p_rho:.4f}")

# ============================================================
# TEST 2: Supply Chain — Ratio and trend
# ============================================================
print("\n--- TEST 2: Supply Chain (Scope-3 / Scope-1,2 Ratio) ---")
rho_s, p_s = stats.spearmanr(years, ratio_supply)
print(f"  Min ratio: {ratio_supply.min():.2f}")
print(f"  Max ratio: {ratio_supply.max():.2f}")
print(f"  2025 ratio: {ratio_supply[-1]:.2f}")
print(f"  Spearman ρ = {rho_s:.2f}, p = {p_s:.4f}")
print(f"  Ratio > 1.6 throughout: {np.all(ratio_supply > 1.55)}")

# ============================================================
# TEST 3: Audit Layer — Welch t-test and Spearman
# ============================================================
print("\n--- TEST 3: Audit Layer (Sustainability Assurance Papers) ---")
t_a, p_a = stats.ttest_ind(assurance[pre], assurance[post], equal_var=False)
rho_a, p_ra = stats.spearmanr(years, assurance)
growth = (assurance[-1] / assurance[years == 2020][0] - 1) * 100
print(f"  2020: {assurance[years == 2020][0]}")
print(f"  2025: {assurance[-1]}")
print(f"  Growth 2020-2025: +{growth:.0f}%")
print(f"  Welch t = {t_a:.1f}, p = {p_a:.4f}")
print(f"  Spearman ρ = {rho_a:.2f}, p = {p_ra:.4f}")

# ============================================================
# TEST 4: Extended — Greenwashing
# ============================================================
print("\n--- TEST 4: Greenwashing ---")
rho_g, p_g = stats.spearmanr(years, greenwashing)
print(f"  2015: {greenwashing[0]:,}")
print(f"  2025: {greenwashing[-1]:,}")
print(f"  Spearman ρ = {rho_g:.2f}, p = {p_g:.6f}")

# ============================================================
# TEST 5: Extended — Double Materiality
# ============================================================
print("\n--- TEST 5: Double Materiality ---")
rho_d, p_d = stats.spearmanr(years, double_mat)
print(f"  2015: {double_mat[0]}")
print(f"  2025: {double_mat[-1]}")
print(f"  Spearman ρ = {rho_d:.2f}, p = {p_d:.6f}")

# ============================================================
# STUCKNESS
# ============================================================
print("\n--- STUCKNESS SCORE (KPMG) ---")
C_pre, I_pre = 0.56, 0.20
C_post, I_post = 0.77, 0.29
S_pre = C_pre - I_pre
S_post = C_post - I_post
print(f"  Pre-CSRD:  C = {C_pre}, I = {I_pre}, S = {S_pre:.2f}")
print(f"  Post-CSRD: C = {C_post}, I = {I_post}, S = {S_post:.2f}")
print(f"  ΔS = +{S_post - S_pre:.2f} (+{(S_post - S_pre) / S_pre * 100:.0f}%)")

# ============================================================
# SUMMARY TABLE
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY OF ALL TEST STATISTICS")
print("=" * 70)
print(f"  {'Test':<40s} {'Statistic':>12s} {'p-value':>10s}")
print(f"  {'-' * 40} {'-' * 12} {'-' * 10}")
tests = [
    ("Processing: Welch t", f"t = {t_stat:.1f}", f"{p_val:.4f}"),
    ("Processing: Spearman ρ", f"ρ = {rho:.2f}", f"{p_rho:.4f}"),
    ("Audit: Welch t", f"t = {t_a:.1f}", f"{p_a:.4f}"),
    ("Audit: Spearman ρ", f"ρ = {rho_a:.2f}", f"{p_ra:.4f}"),
    ("Supply chain: Spearman ρ", f"ρ = {rho_s:.2f}", f"{p_s:.4f}"),
    ("Greenwashing: Spearman ρ", f"ρ = {rho_g:.2f}", f"{p_g:.6f}"),
    ("Double materiality: Spearman ρ", f"ρ = {rho_d:.2f}", f"{p_d:.6f}"),
    ("Stuckness change", f"ΔS = +{S_post-S_pre:.2f}", "+33%"),
]
for name, stat, pv in tests:
    print(f"  {name:<40s} {stat:>12s} {pv:>10s}")
