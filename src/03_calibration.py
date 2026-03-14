#!/usr/bin/env python3
"""
03_calibration.py
=================
Calibrate the graph-Laplacian model from OpenAlex data.
Generates Figure 5 (4-panel calibration figure).

Model: φ_i(t) = φ₀_i · exp(-λ_i · t) + A_i · sigmoid(t - t₀, k)
       (diagonal approximation of the Laplacian system)

Usage: python src/03_calibration.py
"""
import numpy as np
from scipy import optimize
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams.update({
    "font.family": "serif", "font.size": 10, "figure.dpi": 300,
    "mathtext.fontset": "cm", "axes.spines.top": False, "axes.spines.right": False,
})

FIG_DIR = Path(__file__).parent.parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

# ---- Data ----
years = np.arange(2015, 2026)
t = years - 2015.0

audit_raw = np.array([100, 110, 120, 135, 150, 198, 280, 450, 700, 950, 1191])
supply_raw = np.array([1.6, 1.7, 1.8, 1.65, 1.7, 1.9, 1.85, 1.8, 1.75, 1.9, 2.14])
process_raw = np.array([0.001, 0.001, 0.002, 0.003, 0.008, 0.015, 0.020, 0.025, 0.028, 0.030, 0.035])


def norm01(x):
    return (x - x.min()) / (x.max() - x.min())


data = np.vstack([norm01(audit_raw), norm01(supply_raw), norm01(process_raw)])
LABELS = ["Audit", "Supply chain", "Processing"]
COLORS = ["#534AB7", "#1D9E75", "#D85A30"]


# ---- Model ----
def model(params, t_eval):
    phi = np.zeros((3, len(t_eval)))
    for i in range(3):
        phi0 = params[i]
        decay = params[3 + i]
        amp = params[6 + i]
        t0 = params[9]
        k = params[10]
        sig = 1.0 / (1.0 + np.exp(-k * (t_eval - t0)))
        phi[i] = phi0 * np.exp(-decay * t_eval) + amp * sig
    return phi


def objective(params):
    phi = model(params, t)
    cost = 0
    for i in range(3):
        mn, mx = phi[i].min(), phi[i].max()
        if mx - mn < 1e-10:
            return 1e10
        phi_n = (phi[i] - mn) / (mx - mn)
        cost += np.sum((phi_n - data[i]) ** 2)
    return cost


# ---- Fit ----
print("Calibrating model (500 random starts)...")
best_cost = 1e10
best_p = None
np.random.seed(42)

bounds = (
    [(0, 2)] * 3        # phi0
    + [(0, 1)] * 3      # decay rates
    + [(0.01, 5)] * 3   # source amplitudes
    + [(2, 8)]           # onset
    + [(0.3, 5)]         # rise rate
)

for trial in range(500):
    x0 = np.array([
        np.random.uniform(0, 1),
        np.random.uniform(0.5, 1.5),
        np.random.uniform(0, 0.3),
        np.random.uniform(0, 0.5),
        np.random.uniform(0, 0.2),
        np.random.uniform(0, 0.5),
        np.random.uniform(0.5, 3),
        np.random.uniform(0, 1),
        np.random.uniform(0, 0.5),
        np.random.uniform(3, 7),
        np.random.uniform(0.5, 3),
    ])
    try:
        res = optimize.minimize(objective, x0, method="L-BFGS-B", bounds=bounds,
                                options={"maxiter": 300})
        if res.fun < best_cost:
            best_cost = res.fun
            best_p = res.x.copy()
    except Exception:
        pass

p = best_p
print(f"Best cost: {best_cost:.6f}")

# ---- Extract results ----
phi0 = p[:3]
decays = p[3:6]
amps = p[6:9]
t_onset = p[9]
k_rise = p[10]

print(f"\nCalibrated parameters:")
print(f"  {'Channel':<20s} {'φ₀':>6s} {'λ':>8s} {'τ=1/λ':>8s} {'Amp':>6s}")
for i in range(3):
    tau = f"{1/decays[i]:.1f}yr" if decays[i] > 0.01 else "∞"
    print(f"  {LABELS[i]:<20s} {phi0[i]:6.3f} {decays[i]:8.4f} {tau:>8s} {amps[i]:6.3f}")
print(f"  Onset: {2015 + t_onset:.1f}, Rise rate: {k_rise:.2f}/yr")

# R² per channel
phi_cal = model(p, t)
for i in range(3):
    mn, mx = phi_cal[i].min(), phi_cal[i].max()
    phi_n = (phi_cal[i] - mn) / (mx - mn)
    r2 = 1 - np.sum((phi_n - data[i]) ** 2) / np.sum((data[i] - data[i].mean()) ** 2)
    print(f"  {LABELS[i]:<20s}: R² = {r2:.4f}")

# ---- Forward prediction ----
t_fwd = np.linspace(0, 17, 170)
yr_fwd = 2015 + t_fwd
phi_fwd = model(p, t_fwd)

inh = np.zeros_like(phi_fwd)
trg = np.zeros_like(phi_fwd)
for i in range(3):
    inh[i] = phi0[i] * np.exp(-decays[i] * t_fwd)
    trg[i] = amps[i] / (1 + np.exp(-k_rise * (t_fwd - t_onset)))

total = np.sum(phi_fwd, axis=0)
peak_yr = yr_fwd[np.argmax(total)]
print(f"\nPredicted peak total asymmetry: ~{peak_yr:.0f}")

# ---- Figure 5 ----
fig, axes = plt.subplots(2, 2, figsize=(11, 8))

# (a) Model fit
ax = axes[0, 0]
for i in range(3):
    mn, mx = phi_cal[i].min(), phi_cal[i].max()
    if mx - mn < 1e-10:
        mn, mx = 0, 1
    model_n = (phi_cal[i] - mn) / (mx - mn)
    ax.plot(years, data[i], "o", color=COLORS[i], ms=5, alpha=0.7)
    ax.plot(years, model_n, "-", color=COLORS[i], lw=2, label=LABELS[i])
ax.axvline(2015 + t_onset, color="k", ls=":", alpha=0.3, label=f"Onset ~{2015+t_onset:.0f}")
ax.set_xlabel("Year")
ax.set_ylabel("Normalized $\\phi_i$")
ax.set_title("(a)  Calibrated model vs. OpenAlex data", fontweight="normal")
ax.legend(fontsize=7, ncol=2)
ax.grid(True, alpha=0.2)

# (b) Forward prediction
ax = axes[0, 1]
for i in range(3):
    ax.plot(yr_fwd, phi_fwd[i], "-", color=COLORS[i], lw=2, label=LABELS[i])
ax.plot(yr_fwd, total, "k--", lw=1.5, alpha=0.5, label="Total")
ax.axvline(2025, color="k", ls=":", alpha=0.3)
ax.axvline(peak_yr, color="#993C1D", ls="--", alpha=0.4)
ax.text(peak_yr + 0.3, max(total) * 0.85, f"~{peak_yr:.0f}", fontsize=8, color="#993C1D")
ax.set_xlabel("Year")
ax.set_ylabel("$\\phi_i(t)$")
ax.set_title("(b)  Forward prediction", fontweight="normal")
ax.legend(fontsize=7)
ax.set_xlim([2015, 2032])
ax.grid(True, alpha=0.2)

# (c) Inherited vs triggered
ax = axes[1, 0]
for i in range(3):
    ax.plot(yr_fwd, inh[i], "--", color=COLORS[i], lw=1, alpha=0.5)
    ax.plot(yr_fwd, trg[i], "-", color=COLORS[i], lw=2)
leg = [
    Line2D([0], [0], color="k", ls="--", lw=1, label="Inherited $\\phi_0 e^{-\\lambda t}$"),
    Line2D([0], [0], color="k", ls="-", lw=2, label="Triggered $A\\cdot\\sigma(t)$"),
]
for i in range(3):
    leg.append(Line2D([0], [0], color=COLORS[i], lw=2, label=LABELS[i]))
ax.legend(handles=leg, fontsize=7)
ax.set_xlim([2015, 2032])
ax.set_xlabel("Year")
ax.set_ylabel("$\\phi_i$ components")
ax.set_title("(c)  Inherited (dashed) vs. triggered (solid)", fontweight="normal")
ax.grid(True, alpha=0.2)

# (d) Stuckness
ax = axes[1, 1]
S_model = (phi_fwd[1] + phi_fwd[2]) / 2 - phi_fwd[0] / 3
S_n = S_model / max(np.max(np.abs(S_model)), 1e-10)
ax.plot(yr_fwd, S_n, "k-", lw=2)
ax.fill_between(yr_fwd, 0, S_n, where=S_n > 0, alpha=0.08, color="#D85A30")
ax.axhline(0, color="gray", alpha=0.3)
ax.plot(2024, 0.5, "k^", ms=8, zorder=5)
ax.annotate("KPMG: $S=0.48$", (2024, 0.5), xytext=(2018, 0.72),
            arrowprops=dict(arrowstyle="->", color="k", alpha=0.5), fontsize=8)
ax.set_xlabel("Year")
ax.set_ylabel("System stuckness $S = C - I$")
ax.set_title("(d)  Stuckness trajectory", fontweight="normal")
ax.set_xlim([2015, 2032])
ax.grid(True, alpha=0.2)

plt.tight_layout(h_pad=2, w_pad=2)
plt.savefig(FIG_DIR / "fig5_calibration.pdf", bbox_inches="tight")
plt.close()
print("Figure 5 saved.")
