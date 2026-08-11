#!/usr/bin/env python3
"""Plot the complete.cir ngspice output: the COMPLETE bidirectional UHF-RFID
exchange in one figure -- tag charging, reader downlink command + tag demod,
turnaround, tag backscatter reply + reader homodyne decode. EPS for the paper.

The deck (complete.cir) writes its results with ngspice ``wrdata``::

    wrdata full.out v(dlenv) v(vdd) v(env) v(ref) v(demod) v(gmod) \\
                    v(bsmag0) v(bsmag) v(dif) v(qbb)

``wrdata`` emits each variable as an independent ``(time, value)`` column pair, so
the file has 20 whitespace-separated columns (10 signals x 2). Every time column
is identical; we read the first one as the shared time base.

Signals
-------
reader / downlink
    dlenv     ASK/PIE command envelope the reader transmits (1.0 full, 0.1 notch)
tag
    vdd       harvested DC supply: charges from 0, rides through the ASK notches,
              droops during backscatter (state B)
    env       on-chip envelope-detector output (tracks the carrier envelope)
    ref       slicer reference (slow average of env) -- the decision threshold
    demod     comparator output (env > ref) -- the recovered downlink command
    gmod      backscatter modulator gate = the uplink data the tag sends
reader / uplink
    bsmag0    homodyne magnitude BEFORE carrier cancellation (self-jam pedestal)
    bsmag     homodyne magnitude AFTER cancellation (the recovered reply)
    dif, qbb  recovered I/Q baseband after cancellation

Usage
-----
    python3 plot.complete.py [out_file] [-o figure.eps]

Defaults: reads ./complete.out, writes ./complete.eps
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless / file-only backend
import matplotlib.pyplot as plt
import numpy as np

# ngspice wrdata column order (value columns; time is column 0 of each pair)
SIGNALS = ["dlenv", "vdd", "env", "ref", "demod", "gmod", "bsmag0", "bsmag", "dif", "qbb"]

# phase windows [start_ns, stop_ns, label, tint] -- must match full.cir timeline
PHASES = [
    (0.0, 400.0, "charge", "#fff2cc"),
    (400.0, 1300.0, "downlink cmd", "#dbe9f5"),
    (1300.0, 2000.0, "turnaround", "#eeeeee"),
    (2000.0, 2800.0, "uplink reply", "#e2f0d9"),
]

# bit-cell centres (ns) for the annotations, from the full.cir PWLs
DL_BITS = [("1", 525), ("0", 725), ("1", 925), ("1", 1175)]
UL_BITS = [("1", 2100), ("0", 2300), ("1", 2500), ("1", 2700)]

# carrier reference (0 dBc): mean |I+jQ| before cancellation over the settled
# turnaround (the canceller's calibration window), pure CW self-jam
CREF_WIN = (1800.0, 1980.0)
UPLINK_WIN = (2000.0, 2800.0)
P_CARRIER_DBM = 30.0  # Pin = 1 W = +30 dBm


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
            "legend.fontsize": 7.5,
            "grid.color": "0.85",
            "grid.linewidth": 0.4,
        }
    )

    fig, axes = plt.subplots(4, 1, figsize=(6.2, 7.0), sharex=True)
    ax_cmd, ax_vdd, ax_dem, ax_rdr = axes

    def shade_phases(ax, label=False):
        """Tint the four exchange phases behind every panel."""
        for s, e, name, tint in PHASES:
            ax.axvspan(s, e, color=tint, lw=0, zorder=0)
            if label:
                ax.text(
                    0.5 * (s + e), 1.04, name, transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=8, color="0.30",
                )

    # --- Panel 1: reader downlink command envelope -----------------------
    shade_phases(ax_cmd, label=True)
    ax_cmd.plot(t_ns, data["dlenv"], color="C7")
    ax_cmd.set_ylabel("reader cmd\n$v_{\\mathrm{dlenv}}$")
    ax_cmd.set_ylim(-0.1, 1.25)
    ax_cmd.grid(True, axis="x")
    for b, tc in DL_BITS:
        ax_cmd.text(tc, 1.12, b, ha="center", va="center", fontsize=8, color="0.25")
    ax_cmd.set_title(
        "Full UHF-RFID: charge → downlink command → backscatter reply → decode",
        #"Full UHF-RFID exchange: charge → downlink command → backscatter reply → decode",
        fontsize=9.5, loc="left", pad=18,
    )

    # --- Panel 2: tag supply (charging, ride-through, droop) --------------
    shade_phases(ax_vdd)
    ax_vdd.plot(t_ns, data["vdd"], color="C3")
    ax_vdd.set_ylabel("tag supply\n$v_{\\mathrm{dd}}$ (V)")
    ax_vdd.set_ylim(0, max(0.1, data["vdd"].max() * 1.15))
    ax_vdd.grid(True)

    # --- Panel 3: tag demodulator (recover the downlink command) ----------
    shade_phases(ax_dem)
    (l_env,) = ax_dem.plot(t_ns, data["env"], color="C0", label=r"$v_{\mathrm{env}}$ (detector)")
    (l_ref,) = ax_dem.plot(
        t_ns, data["ref"], color="C3", lw=0.8, ls="--", label=r"$v_{\mathrm{ref}}$ (threshold)"
    )
    env_hi = np.percentile(data["env"], 95) or 1.0
    dem_lo, dem_hi = data["demod"].min(), (data["demod"].max() or 1.0)
    dem_scaled = (data["demod"] - dem_lo) / (dem_hi - dem_lo) * env_hi
    (l_dem,) = ax_dem.plot(
        t_ns, dem_scaled, color="C2", lw=0.7, drawstyle="steps-post", zorder=1.5,
        label=r"$v_{\mathrm{demod}}$ (sliced)",
    )
    ax_dem.set_ylabel("tag demod\n(V)")
    ax_dem.grid(True)
    leg = ax_dem.legend(
        handles=[l_env, l_ref, l_dem], loc="lower center", ncol=3, handlelength=1.4
    )
    leg.get_frame().set_alpha(0.85)
    leg.get_frame().set_edgecolor("none")
    # clarify: the slicer recovers the command during downlink; during the tag's
    # own backscatter it grazes threshold (a real tag blanks its Rx while sending)
    ax_dem.annotate(
        "command\nrecovered", xy=(850, 0.06), ha="center", va="center",
        fontsize=7.5, color="0.30",
    )
    ax_dem.annotate(
        "tag TX\n(Rx blanked\nin practice)", xy=(2400, 0.06), ha="center", va="center",
        fontsize=7.5, color="0.30",
    )

    # --- Panel 4: reader homodyne decode of the backscatter reply ---------
    cwin = (t_ns >= CREF_WIN[0]) & (t_ns <= CREF_WIN[1])
    cref = np.mean(data["bsmag0"][cwin])  # 0 dBc = self-jam carrier

    def to_dbc(x):
        return 20.0 * np.log10(np.maximum(x, 1e-15) / cref)

    # shade state-B (tag backscattering) within the uplink window
    modulated = data["gmod"] > 0.5 * (data["gmod"].max() or 1.0)
    edges = np.diff(modulated.astype(int))
    starts = np.where(edges == 1)[0] + 1
    stops = np.where(edges == -1)[0] + 1
    if modulated[0]:
        starts = np.r_[0, starts]
    if modulated[-1]:
        stops = np.r_[stops, len(modulated) - 1]
    for s, e in zip(starts, stops):
        ax_rdr.axvspan(t_ns[s], t_ns[e], color="0.82", lw=0, zorder=1)

    (l_raw,) = ax_rdr.plot(t_ns, to_dbc(data["bsmag0"]), color="0.45", label="raw (before)")
    (l_can,) = ax_rdr.plot(t_ns, to_dbc(data["bsmag"]), color="C0", label="cancelled (after)")
    # slicer threshold midway (in dB) between recovered 0 and 1 levels (uplink only)
    ul = (t_ns >= UPLINK_WIN[0]) & (t_ns <= UPLINK_WIN[1])
    lo = np.percentile(data["bsmag"][ul], 15)
    hi = np.percentile(data["bsmag"][ul], 85)
    thr_db = 0.5 * (to_dbc(lo) + to_dbc(hi))
    (l_slc,) = ax_rdr.plot(
        list(UPLINK_WIN), [thr_db, thr_db], color="C3", lw=0.8, ls="--", label="slicer"
    )
    for b, tc in UL_BITS:
        ax_rdr.text(tc, 6.0, b, ha="center", va="center", fontsize=8, color="0.25")
    ax_rdr.set_ylabel("reader $|I{+}jQ|$ (dBc)")
    ax_rdr.set_xlabel("time (ns)")
    ax_rdr.set_ylim(to_dbc(lo) - 12, 10)
    ax_rdr.grid(True)
    ax_rdr.legend(handles=[l_raw, l_can, l_slc], loc="lower right", ncol=3, handlelength=1.4)
    ax_dbm = ax_rdr.secondary_yaxis(
        "right", functions=(lambda d: d + P_CARRIER_DBM, lambda d: d - P_CARRIER_DBM)
    )
    ax_dbm.set_ylabel("power (dBm)")

    ax_rdr.set_xlim(0, t_ns.max())
    fig.tight_layout(pad=0.5)
    fig.subplots_adjust(top=0.93)
    return fig


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "out_file", nargs="?", default="complete.out", type=Path,
        help="ngspice wrdata output (default: complete.out)",
    )
    p.add_argument(
        "-o", "--out", type=Path, default=None,
        help="output EPS path (default: <out_file stem>.eps)",
    )
    args = p.parse_args()

    out = args.out or args.out_file.with_suffix(".eps")
    data = load_wrdata(args.out_file)
    fig = make_figure(data)
    fig.savefig(out, format="eps", bbox_inches="tight")
    print(f"wrote {out}  ({len(data['time'])} samples)")


if __name__ == "__main__":
    main()
