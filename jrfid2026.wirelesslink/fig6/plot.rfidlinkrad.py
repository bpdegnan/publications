#!/usr/bin/env python3
"""Plot the rfidlink rotation sweep: how the 900 MHz backscatter link rolls off
as the tag dipole is rotated about the line of sight, as an EPS for the paper.

The deck (rfidlink.rad.cir) sweeps the receive-antenna rotation psi and, for each
angle, runs the full two-pass (carrier-cancelled) link and writes ONE row of
scalars with ngspice ``echo`` redirection::

    psideg  cos(psi)  vdd_ss  vdd_mod  bs_off  bs_on

Columns
-------
psideg     tag dipole rotation [deg]
cos_psi    cos(psi) -- the far-field polarization factor (ideal-law overlay)
vdd_ss     tag harvested DC supply during the CW quiet window [V]
vdd_mod    deepest vdd droop while the tag is modulating [V]
bs_off     reader recovered homodyne magnitude, 'data 0' bit (state A)
bs_on      reader recovered homodyne magnitude, 'data 1' bit (state B)

Two panels:
  (top)    forward link -- tag harvested supply vdd vs angle, with the ideal
           cos^2 power law (power ~ |Z21|^2 ~ cos^2 psi) for reference.
  (bottom) round-trip link -- reader recovered backscatter modulation depth
           |bs_on - bs_off| vs angle, in dB relative to broadside, against the
           ideal cos^2 (round trip ~ cos^2) reference.

Usage
-----
    python3 plot.rfidlinkrad.py [dat_file] [-o out.eps]

Defaults: reads ./rfidlink.rad.dat, writes ./rfidlink.rad.eps
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless / file-only backend
import matplotlib.pyplot as plt
import numpy as np

COLS = ["psideg", "cos_psi", "vdd_ss", "vdd_mod", "bs_off", "bs_on"]


def load(path: Path) -> dict[str, np.ndarray]:
    raw = np.loadtxt(path, comments="*")  # '*'-prefixed header line is a comment
    if raw.ndim == 1:
        raw = raw[None, :]
    if raw.shape[1] != len(COLS):
        raise ValueError(f"{path}: expected {len(COLS)} columns, found {raw.shape[1]}")
    return {name: raw[:, i] for i, name in enumerate(COLS)}


def make_figure(d: dict[str, np.ndarray]) -> plt.Figure:
    psi = d["psideg"]
    cpsi = d["cos_psi"]
    vdd = d["vdd_ss"]
    depth = np.abs(d["bs_on"] - d["bs_off"])  # reader modulation depth

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

    fig, (ax_f, ax_r) = plt.subplots(2, 1, figsize=(5.4, 4.6), sharex=True)

    # smooth angle grid for the ideal-law curves
    pg = np.linspace(psi.min(), psi.max(), 200)
    cg = np.cos(np.deg2rad(pg))

    # --- top: forward link, tag harvested supply -----------------------------
    ax_f.plot(psi, vdd, "o-", color="C3", ms=3.5, label=r"tag $v_{\mathrm{dd}}$ (sim)")
    # ideal cos^2 power law, scaled to the broadside (psi=0) harvested supply
    ax_f.plot(pg, vdd[0] * cg**2, color="0.55", ls="--",
              label=r"$v_{\mathrm{dd}}(0)\,\cos^2\psi$")
    ax_f.set_ylabel(r"tag supply $v_{\mathrm{dd}}$ (V)")
    ax_f.set_ylim(0, 1.1 * vdd.max())
    ax_f.grid(True)
    ax_f.legend(loc="lower left")
    ax_f.set_title(
        "Tag rotation: 900 MHz backscatter link roll-off vs polarization angle",
        fontsize=9.5, loc="left",
    )

    # --- bottom: round-trip link, reader recovered modulation depth (dB) ------
    ref = depth[0]  # broadside modulation depth = 0 dB
    depth_db = 20.0 * np.log10(np.maximum(depth, 1e-18) / ref)
    ax_r.plot(psi, depth_db, "s-", color="C0", ms=3.5,
              label=r"reader $|bs_{\mathrm{on}}-bs_{\mathrm{off}}|$ (sim)")
    # round trip ~ cos^2 (forward field x return field, both ~cos): in dB = 40log10 cos
    ideal_db = 40.0 * np.log10(np.maximum(cg, 1e-9))
    ax_r.plot(pg, ideal_db, color="0.55", ls="--", label=r"$40\log_{10}\cos\psi$")
    ax_r.set_xlabel(r"tag rotation $\psi$ (deg)")
    ax_r.set_ylabel("reader modulation\ndepth (dB rel. broadside)")
    ax_r.grid(True)
    ax_r.legend(loc="lower left")
    ax_r.set_xlim(psi.min(), psi.max())

    fig.tight_layout(pad=0.5)
    return fig


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("dat_file", nargs="?", default="rfidlink.rad.dat", type=Path)
    p.add_argument("-o", "--out", type=Path, default=None)
    args = p.parse_args()

    out = args.out or args.dat_file.with_suffix(".eps")
    d = load(args.dat_file)
    fig = make_figure(d)
    fig.savefig(out, format="eps", bbox_inches="tight")
    print(f"wrote {out}  ({len(d['psideg'])} angles)")


if __name__ == "__main__":
    main()
