#!/usr/bin/env python3
"""Compare the ngspice (Kron two-port) dipole sweep in twoport.raw against the
exact Maxwell induced-EMF result, with the Friis far-field approximation
overlaid.
Usage:  python3 dipole_compare.py [twoport.raw]
"""
import sys
import numpy as np
from scipy.special import sici
import matplotlib.pyplot as plt

# ---- from twoport ----
c, f = 2.99792458e8, 900e6
lam = c / f
k = 2 * np.pi / lam
L = lam / 2                      # half-wave dipole length
eta = 376.730313
Rself = 73.079010                # Re{Z11}
denomZ = 2 * Rself               # |Z11 + ZL| at conjugate match

def Z21(d):
    """Exact mutual impedance (induced-EMF of parallel half-wave dipoles)."""
    r = np.sqrt(d * d + L * L)
    Si0, Ci0 = sici(k * d)
    Si1, Ci1 = sici(k * (r + L))
    Si2, Ci2 = sici(k * (r - L))
    R21 = eta / (4 * np.pi) * (2 * Ci0 - Ci1 - Ci2)
    X21 = -eta / (4 * np.pi) * (2 * Si0 - Si1 - Si2)
    return R21 + 1j * X21

def ratio_maxwell(d):
    """Prx/Ptx = |I2/I1|^2 = |Z21|^2 / |Z11+ZL|^2 """
    return np.abs(Z21(d)) ** 2 / denomZ ** 2

def ratio_friis(d):
    """Far-field Friis: Pr/Pt = Gt*Gr*(lambda/4 pi d)^2, half-wave dipole G = 1.643."""
    G = 1.643
    return G * G * (lam / (4 * np.pi * d)) ** 2

# ---- load ngspice sweep ----
raw = sys.argv[1] if len(sys.argv) > 1 else "twoport.kron.raw"
col = np.loadtxt(raw)
dcm   = col[:, 3]                # r_dcm
spice = col[:, 15]              # ratio = Prx/Ptx
d_m = dcm / 100.0

maxw  = ratio_maxwell(d_m)
friis = ratio_friis(d_m)

# ---- plot ----
fig, (ax, axr) = plt.subplots(
    2, 1, figsize=(8, 6.5), gridspec_kw={"height_ratios": [3, 1]}, sharex=True
)

ax.loglog(dcm, maxw,  "-",  color="#1f4e8c", lw=2.0, label="Maxwell")
ax.loglog(dcm, spice, "o",  color="#e07b39", ms=3.2, mfc="none",
          label="SPICE (Kron two-port)")
ax.loglog(dcm, friis, "--", color="#5a5a5a", lw=1.5, label="Friis far-field (G = 1.64)")

ymin, ymax = ax.get_ylim()
for x, t in [(lam / (2 * np.pi) * 100, r"radian sphere  $\lambda/2\pi$"),
             (lam / 2 * 100,           r"$\lambda/2$")]:
    ax.axvline(x, color="0.8", ls=":", lw=1)
    ax.text(x, ymax, t, rotation=90, va="top", ha="right", fontsize=7, color="0.5")

ax.set_ylabel(r"power transfer: $P_{rx}/P_{tx}=|I_2/I_1|^2$")
ax.set_title("SPICE vs. Maxwell @ 900 MHz")
ax.legend(frameon=False, fontsize=9)
ax.grid(True, which="both", alpha=0.25)

rel = np.abs(spice - maxw) / maxw
axr.loglog(dcm, rel, "-", color="#7a3b8f", lw=1.2)
axr.set_ylabel("|SPICE - Maxwell|")
axr.set_xlabel("dipole separation distance [cm]")
axr.grid(True, which="both", alpha=0.25)

fig.tight_layout()
out = "dipole_spice_vs_maxwell.eps"
fig.savefig(out, format="eps")
print("wrote", out, " worst rel. residual =", f"{rel.max():.2e}")

plt.show()
