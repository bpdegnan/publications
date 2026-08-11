#!/usr/bin/env python3
"""Plot the downlink ngspice output: a reader->tag ASK/PIE downlink that is
rectified, rides through the ASK notches on a storage cap, and is recovered by an
on-chip envelope detector + slicer. 

The deck (downlink.cir) writes its results with ngspice ``wrdata``::

    wrdata downlink.csv v(env_cmd) v(vdd) v(vrect) v(env) v(ref) v(demod)


Signals
-------
env_cmd   ASK/PIE command envelope the reader transmits (1.0 = full power,
          0.1 = notch). This is the modulation that rides on the 900 MHz carrier.
vrect     cross-coupled charge-pump output (rectified RF, pre-storage).
vdd       harvested DC supply after the blocking diode + large Cstor. The point of
          the deck: vdd rides *through* the brief ASK notches so the tag stays
          powered while still seeing the command.
env       on-chip envelope-detector output (fast RC) -- tracks the command envelope.
ref       slicer reference (slow RC average of env) -- the decision threshold.
demod     comparator output (env > ref) -- the recovered, sliced command waveform.

PIE symbol-time decoding into bits (1 0 1 1 0 0 1) is done offline from the demod
transitions; this figure shows the recovered sliced waveform, not the decoded bits.

Usage
-----
    python3 plot.downlink.py [out_file] [-o figure.eps]

Defaults: reads ./downlink.csv, writes ./downlink.eps
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless / file-only backend
import matplotlib.pyplot as plt
import numpy as np

# ngspice wrdata column order (value columns; time is column 0 of each pair)
SIGNALS = ["env_cmd", "vdd", "vrect", "env", "ref", "demod"]


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
    ax_cmd, ax_pwr, ax_dem = axes

    # notch ("low power") intervals: command envelope below the 0.55 midpoint
    cmd = data["env_cmd"]
    notch = cmd < 0.55 * cmd.max()

    def shade_notches(ax):
        """Light shading wherever the reader is in an ASK notch (low power)."""
        edges = np.diff(notch.astype(int))
        starts = np.where(edges == 1)[0] + 1
        stops = np.where(edges == -1)[0] + 1
        if notch[0]:
            starts = np.r_[0, starts]
        if notch[-1]:
            stops = np.r_[stops, len(notch) - 1]
        for s, e in zip(starts, stops):
            ax.axvspan(t_ns[s], t_ns[e], color="0.90", lw=0, zorder=0)

    # --- Panel 1: the ASK/PIE command envelope the reader transmits --------
    shade_notches(ax_cmd)
    ax_cmd.plot(t_ns, cmd, color="C7")
    ax_cmd.set_ylabel("reader cmd\n$v_{\\mathrm{env\\_cmd}}$ (V)")
    ax_cmd.set_title(
        "Reader to tag ASK/PIE downlink",
        fontsize=9.5,
        loc="left",
    )
    ax_cmd.set_ylim(-0.1, 1.2)
    ax_cmd.grid(True, axis="x")

    # --- Panel 2: rectified pump and harvested supply riding through notches
    shade_notches(ax_pwr)
    (l_vr,) = ax_pwr.plot(t_ns, data["vrect"], color="0.55", label=r"$v_{\mathrm{rect}}$ (pump)")
    (l_vd,) = ax_pwr.plot(t_ns, data["vdd"], color="C3", label=r"$v_{\mathrm{dd}}$ (supply)")
    ax_pwr.set_ylabel("rectifier\n(V)")
    ax_pwr.grid(True)
    ax_pwr.legend(loc="center right", fontsize=7.5, handlelength=1.6)

    # --- Panel 3: envelope detector vs slicer threshold, and sliced output --
    shade_notches(ax_dem)
    (l_env,) = ax_dem.plot(t_ns, data["env"], color="C0", label=r"$v_{\mathrm{env}}$ (detector)")
    (l_ref,) = ax_dem.plot(
        t_ns, data["ref"], color="C3", lw=0.8, ls="--", label=r"$v_{\mathrm{ref}}$ (threshold)"
    )
    # demod swings 0..pvdd; scale it onto the env axis so it reads as an overlay
    env_hi = np.percentile(data["env"], 95)
    dem_lo = data["demod"].min()
    dem_hi = data["demod"].max() or 1.0
    dem_scaled = (data["demod"] - dem_lo) / (dem_hi - dem_lo) * env_hi
    (l_dem,) = ax_dem.plot(
        t_ns, dem_scaled, color="C2", lw=0.8, drawstyle="steps-post",
        label=r"$v_{\mathrm{demod}}$ (sliced)",
    )
    ax_dem.set_ylabel("detector /\nslicer (V)")
    ax_dem.set_xlabel("time (ns)")
    ax_dem.grid(True)
    ax_dem.legend(
        handles=[l_env, l_ref, l_dem], loc="center right", fontsize=7.5, handlelength=1.6
    )

    ax_dem.set_xlim(0, t_ns.max())
    fig.tight_layout(pad=0.5)
    return fig


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "out_file",
        nargs="?",
        default="downlink.csv",
        type=Path,
        help="ngspice wrdata output (default: downlink.csv)",
    )
    p.add_argument(
        "-o",
        "--out",
        type=Path,
        default=None,
        help="output EPS path (default: <out_file stem>.eps)",
    )
    args = p.parse_args()

    out = args.out or args.out_file.with_suffix(".eps")
    data = load_wrdata(args.out_file)
    fig = make_figure(data)
    #fig.show()
    fig.savefig(out, format="eps", bbox_inches="tight")
    print(f"wrote {out}  ({len(data['time'])} samples)")


if __name__ == "__main__":
    main()
