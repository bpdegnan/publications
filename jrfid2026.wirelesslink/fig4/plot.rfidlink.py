#!/usr/bin/env python3
"""Plot the rfidlink ngspice output: a 900 MHz UHF-RFID backscatter link with
reader carrier cancellation, as an EPS figure for the paper.

The deck (rfidlink.cir) is the full 900 MHz link: reader -> free space (1 m) ->
tag dipole -> match -> charge pump -> backscatter modulator -> reader carrier
canceller -> homodyne. It writes its results with ngspice ``wrdata``::

    wrdata rfidlink.raw v(vdd) v(rfp) v(rfn) v(bsmag0) v(bsmag) v(dif) v(qbb) v(gmod)


Signals
-------
tag side
    gmod           modulator gate = the backscatter data the tag sends (1 0 1 1 0 0)
    vdd            harvested DC supply (droops in the modulated "state B")
    rfp, rfn       differential RF input to the rectifier (not plotted by default)
reader side
    bsmag0         homodyne magnitude BEFORE carrier cancellation -- the ~82 mV
                   monostatic self-jam pedestal (the 0 dBc / +30 dBm reference)
    bsmag          homodyne magnitude AFTER carrier cancellation -- the self-jam is
                   nulled (~67-81 dB) and the backscatter data is recovered
    dif, qbb       recovered I/Q baseband after cancellation


Usage
-----
    python3 plot.rfidlink.py [csv_file] [-o out.eps]

Defaults: reads ./rfidlink.csv, writes ./rfidlink.eps
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless / file-only backend
import matplotlib.pyplot as plt
import numpy as np

# ngspice wrdata column order (value columns; time is column 0 of each pair)
SIGNALS = ["vdd", "rfp", "rfn", "bsmag0", "bsmag", "dif", "qbb", "gmod"]

# data pattern the tag backscatters: first bit at 300 ns, 200 ns/bit (see deck)
BITS = "1 0 1 1 0 0".split()
BIT0_NS = 300.0
BIT_NS = 200.0


def load_wrdata(path: Path) -> dict[str, np.ndarray]:
    """Read an ngspice wrdata file into a {name: array} dict plus 'time'."""
    raw = np.loadtxt(path)
    n_expected = 2 * len(SIGNALS)
    if raw.shape[1] != n_expected:
        raise ValueError(
            f"{path}: expected {n_expected} columns "
            f"({len(SIGNALS)} signals x 2), found {raw.shape[1]}"
        )
    data = {"time": raw[:, 0]}
    for i, name in enumerate(SIGNALS):
        data[name] = raw[:, 2 * i + 1]
    return data


def make_figure(data: dict[str, np.ndarray]) -> plt.Figure:
    t_ns = data["time"] * 1e9  # seconds -> ns

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

    fig, axes = plt.subplots(3, 1, figsize=(5.4, 5.4), sharex=True)
    ax_data, ax_vdd, ax_rdr = axes

    # modulated ("state B") intervals: gmod high
    hi = data["gmod"].max() or 1.0
    modulated = data["gmod"] > 0.5 * hi

    def shade_stateB(ax):
        """Light shading wherever the tag is backscattering (state B)."""
        edges = np.diff(modulated.astype(int))
        starts = np.where(edges == 1)[0] + 1
        stops = np.where(edges == -1)[0] + 1
        if modulated[0]:
            starts = np.r_[0, starts]
        if modulated[-1]:
            stops = np.r_[stops, len(modulated) - 1]
        for s, e in zip(starts, stops):
            ax.axvspan(t_ns[s], t_ns[e], color="0.90", lw=0, zorder=0)

    # --- Panel 1: the backscatter data the tag sends ----------------------
    shade_stateB(ax_data)
    ax_data.plot(t_ns, data["gmod"], color="C7", drawstyle="steps-post")
    ax_data.set_ylabel("tag data\n$v_{\\mathrm{gmod}}$ (V)")
    ax_data.set_title(
        "900 MHz UHF RFID backscatter link with reader carrier cancellation",
        fontsize=9.5,
        loc="left",
    )
    ax_data.set_ylim(-0.3 * hi, 1.45 * hi)
    ax_data.grid(True, axis="x")
    for k, b in enumerate(BITS):
        tc = BIT0_NS + BIT_NS * k + BIT_NS / 2
        if tc < t_ns.max():
            ax_data.text(
                tc, 1.18 * hi, b, ha="center", va="center", fontsize=8, color="0.25"
            )

    # --- Panel 2: harvested DC supply (load-modulation, tag side) ----------
    shade_stateB(ax_vdd)
    ax_vdd.plot(t_ns, data["vdd"], color="C3")
    ax_vdd.set_ylabel(r"tag supply" "\n" r"$v_{\mathrm{dd}}$ (V)")
    ax_vdd.set_ylim(0, 2.7)
    ax_vdd.grid(True)

    # --- Panel 3: reader homodyne, before vs after cancellation -----------
    # Single log/dB axis referenced to the reader's own self-jam carrier (dBc):
    # gain-independent because both traces come from the same homodyne. The deck
    # transmits Pin = 1 W = +30 dBm, so 0 dBc = +30 dBm -> a rigorous dBm axis on
    # the right. Focus on the data window; skip the pre-300 ns canceller settling.
    t0 = 200.0
    settled = t_ns >= t0
    cref = np.mean(data["bsmag0"][settled])  # self-jam carrier reference (0 dBc)

    def to_dbc(x):
        return 20.0 * np.log10(np.maximum(x, 1e-15) / cref)

    shade_stateB(ax_rdr)
    (l_raw,) = ax_rdr.plot(
        t_ns, to_dbc(data["bsmag0"]), color="0.45", label="raw (before)"
    )
    (l_can,) = ax_rdr.plot(
        t_ns, to_dbc(data["bsmag"]), color="C0", label="cancelled (after)"
    )
    # comparitor threshold: midway (in dB) between the recovered "0" and "1" levels
    # RF people prefer "slicer", so we use that
    lo = np.percentile(data["bsmag"][settled], 15)
    hi_lvl = np.percentile(data["bsmag"][settled], 85)
    thr_db = 0.5 * (to_dbc(lo) + to_dbc(hi_lvl))
    (l_slc,) = ax_rdr.plot(
        [t0, t_ns.max()], [thr_db, thr_db], color="C3", lw=0.7, ls="--", label="slicer"
    )
    ax_rdr.set_ylabel("reader $|I{+}jQ|$ (dBc)")
    ax_rdr.set_xlabel("time (ns)")
    ax_rdr.set_ylim(to_dbc(lo) - 12, 8)
    ax_rdr.grid(True)
    ax_rdr.legend(
        handles=[l_raw, l_can, l_slc],
        loc="center right",
        ncol=1,
        fontsize=7.5,
        handlelength=1.6,
    )
    # right axis in absolute power: carrier Pin = 1 W = +30 dBm, so dBm = dBc + 30
    P_CARRIER_DBM = 30.0
    ax_dbm = ax_rdr.secondary_yaxis(
        "right",
        functions=(lambda d: d + P_CARRIER_DBM, lambda d: d - P_CARRIER_DBM),
    )
    ax_dbm.set_ylabel("power (dBm), carrier $=+30$ dBm")
    ax_rdr.set_xlim(t0, t_ns.max())
    fig.tight_layout(pad=0.5)
    return fig


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "raw_file",
        nargs="?",
        default="rfidlink.csv",
        type=Path,
        help="ngspice wrdata output (default: rfidlink.csv)",
    )
    p.add_argument(
        "-o",
        "--out",
        type=Path,
        default=None,
        help="output EPS path (default: <csv_file stem>.eps)",
    )
    args = p.parse_args()

    out = args.out or args.raw_file.with_suffix(".eps")
    data = load_wrdata(args.raw_file)
    fig = make_figure(data)
    fig.savefig(out, format="eps", bbox_inches="tight")
    print(f"wrote {out}  ({len(data['time'])} samples)")


if __name__ == "__main__":
    main()
