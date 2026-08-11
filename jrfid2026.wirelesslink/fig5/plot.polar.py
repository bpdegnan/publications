#!/usr/bin/env python3
"""Polar polarization pattern: received power vs RX rotation psi about the line
of sight, at fixed distance and transmit power. Far field Z21(psi)=Z21(d)cos psi
-> Prx(psi)=Prx(0) cos^2 psi (Malus). The Kron/SPICE psi-sweep
(twoport.kron.rad.cir) is overlaid on the analytic Maxwell pattern.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy.special import sici

import matplotlib

matplotlib.use("Agg")  # headless / file-only backend
import matplotlib.pyplot as plt

# ---- scenario (matches the deck) ----
DCM = 100.0  # separation [cm]
PIN = 1.0    # transmit power [W]

# ---- physics ----
c, f = 2.99792458e8, 900e6
lam = c / f
k = 2 * np.pi / lam
L = lam / 2
eta = 376.730313
Rself = 73.079010
denomZ = 2 * Rself

# ngspice wrdata columns 
COL_PSI = 5
COL_PRX = 11


def Z21(d: float) -> complex:
    r = np.sqrt(d * d + L * L)
    Si0, Ci0 = sici(k * d)
    Si1, Ci1 = sici(k * (r + L))
    Si2, Ci2 = sici(k * (r - L))
    return eta / (4 * np.pi) * (2 * Ci0 - Ci1 - Ci2) \
        - 1j * eta / (4 * np.pi) * (2 * Si0 - Si1 - Si2)


def make_figure(raw_path: Path | None) -> plt.Figure:
    Vsrc = np.sqrt(8 * Rself * PIN)              # deck drive for this Pin
    Z = Z21(DCM / 100)
    I1 = Vsrc / (denomZ - Z ** 2 / denomZ)
    I2 = -Z * I1 / denomZ
    Prx0 = 0.5 * Rself * abs(I2) ** 2            # W, matches deck Prx at psi=0

    psi = np.linspace(0, 2 * np.pi, 721)
    Prx = Prx0 * np.cos(psi) ** 2                # Maxwell cos^2 pattern

    plt.rcParams.update(
        {
            "font.size": 9,
            "font.family": "serif",
            "axes.linewidth": 0.6,
            "lines.linewidth": 1.0,
            "legend.frameon": False,
            "legend.fontsize": 8,
            "grid.color": "0.85",
            "grid.linewidth": 0.4,
        }
    )

    fig = plt.figure(figsize=(3.4, 3.4))
    ax = fig.add_subplot(111, projection="polar")
    ax.plot(psi, Prx * 1e3, "-", color="#1f4e8c", lw=1.4,
            label=r"Maxwell $\cos^2\psi$")

    if raw_path is not None and raw_path.exists():
        col = np.loadtxt(raw_path)
        ax.plot(np.radians(col[:, COL_PSI]), col[:, COL_PRX] * 1e3, "o",
                color="#e07b39", ms=4, mfc="none", label="Kron/SPICE")

    # half-power (45 deg) markers
    for a in (np.pi / 4, 3 * np.pi / 4, 5 * np.pi / 4, 7 * np.pi / 4):
        ax.plot([a], [Prx0 / 2 * 1e3], "k.", ms=3)

    ax.set_rticks([0.5, 1.0, 1.5])              # fewer rings; lobe lies on 0/180
    ax.set_rlabel_position(65)                   # labels in the sparse direction
    ax.tick_params(labelsize=7)
    ax.set_title(r"$P_{rx}$ (mW) vs RX rotation $\psi$", fontsize=9, pad=12)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22), ncol=2,
              fontsize=7.5, handlelength=1.4, columnspacing=1.2)
    fig.tight_layout(pad=0.4)
    return fig


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("raw_file", nargs="?", default="twoport.kron.rad.csv", type=Path)
    p.add_argument("-o", "--out", type=Path, default=None)
    args = p.parse_args()

    out = args.out or args.raw_file.with_suffix(".eps")
    fig = make_figure(args.raw_file)
    fig.savefig(out, format="eps", bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
