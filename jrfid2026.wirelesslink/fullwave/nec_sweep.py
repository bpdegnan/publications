#!/usr/bin/env python3
"""Independent full-wave (Method-of-Moments, NEC-2) check of the dipole two-port.

Two parallel, centre-fed, half-wave dipoles at 900 MHz.  For each separation d the
NEC-2 code (nec2c) solves the electric-field integral equation for the currents.
Dipole 1 is driven with 1 V at its centre segment; dipole 2 is left as a passive,
short-circuited wire.  With V1 = Z11 I1 + Z21 I2 and 0 = Z21 I1 + Z11 I2 (identical
dipoles), the two-port follows from the two centre-segment currents:

    Z11 = V1 I1 / (I1^2 - I2^2),      Z21 = -Z11 I2 / I1 .

Output: nec_z.<radius>.csv  with columns  d_cm R11 X11 R21 X21
Usage:  python3 nec_sweep.py [--radius_mm 0.1] [--segs 41] [--dmin 1] [--dmax 200] [--step 1]
"""
import argparse, subprocess, tempfile, os, re
import numpy as np

C0, F0 = 2.99792458e8, 900e6
LAM = C0 / F0
L = LAM / 2

def nec_deck(d_m, a_m, nseg, two=True):
    h = L / 2
    lines = ["CM parallel half-wave dipoles, 900 MHz", "CE",
             f"GW 1 {nseg} 0 0 {-h:.6f} 0 0 {h:.6f} {a_m:.6e}"]
    if two:
        lines.append(f"GW 2 {nseg} {d_m:.6f} 0 {-h:.6f} {d_m:.6f} 0 {h:.6f} {a_m:.6e}")
    lines += ["GE 0", "EK", f"FR 0 1 0 0 {F0/1e6:.3f} 0",
              f"EX 0 1 {(nseg+1)//2} 0 1 0", "XQ", "EN"]
    return "\n".join(lines) + "\n"

CUR = re.compile(r"^\s+(\d+)\s+(\d+)\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+[\d.]+\s+([-\dE.+]+)\s+([-\dE.+]+)")

def run_nec(deck):
    with tempfile.TemporaryDirectory() as td:
        inp, out = os.path.join(td, "a.nec"), os.path.join(td, "a.out")
        open(inp, "w").write(deck)
        subprocess.run(["nec2c", f"-i{inp}", f"-o{out}"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        txt = open(out).read()
    cur = {}
    block = txt.split("CURRENTS AND LOCATION")[1].split("POWER BUDGET")[0]
    for ln in block.splitlines():
        m = CUR.match(ln)
        if m:
            cur[int(m.group(1))] = complex(float(m.group(3)), float(m.group(4)))
    return cur

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--radius_mm", type=float, default=0.1)
    ap.add_argument("--segs", type=int, default=41)
    ap.add_argument("--dmin", type=float, default=1)
    ap.add_argument("--dmax", type=float, default=200)
    ap.add_argument("--step", type=float, default=1)
    args = ap.parse_args()
    a = args.radius_mm * 1e-3
    n = args.segs
    c = (n + 1) // 2

    # isolated dipole for reference
    cur = run_nec(nec_deck(0, a, n, two=False))
    Ziso = 1.0 / cur[c]
    print(f"isolated dipole a={args.radius_mm} mm, {n} segs: Z11 = {Ziso.real:.2f} {Ziso.imag:+.2f}j ohm")

    rows = []
    for dcm in np.arange(args.dmin, args.dmax + 1e-9, args.step):
        cur = run_nec(nec_deck(dcm / 100, a, n))
        I1, I2 = cur[c], cur[n + c]
        Z11 = I1 / (I1 * I1 - I2 * I2)          # V1 = 1 V
        Z21 = -Z11 * I2 / I1
        rows.append((dcm, Z11.real, Z11.imag, Z21.real, Z21.imag))
    rows = np.array(rows)
    fn = f"nec_z.a{args.radius_mm:g}mm.csv"
    np.savetxt(fn, rows, header="d_cm R11 X11 R21 X21  (NEC-2 MoM, a=%g mm, %d segs, Ziso=%.3f%+.3fj)"
               % (args.radius_mm, n, Ziso.real, Ziso.imag), fmt="%.6e")
    i = np.argmin(abs(rows[:, 0] - LAM / 2 * 100))
    print(f"wrote {fn};  at d={rows[i,0]:.0f} cm (~lambda/2): Z21 = {rows[i,3]:.2f} {rows[i,4]:+.2f}j ohm  "
          f"(Carter thin-wire: -12.52 -29.91j)")

if __name__ == "__main__":
    main()
