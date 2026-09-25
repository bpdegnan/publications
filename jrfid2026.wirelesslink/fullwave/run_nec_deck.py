#!/usr/bin/env python3
"""Run the mutual-impedance two-port SPICE deck with Z11(d), Z21(d) taken from the
independent NEC-2 (Method-of-Moments) sweep instead of the induced-EMF closed form.
The deck topology is identical to twoport.kron.cir (paper Fig. 1); only the numbers
that populate Rself, Xself, R21, X21 change.  One ngspice run per separation.
Usage: python3 run_nec_deck.py nec_z.a0.1mm.csv [dmin_cm]   ->  twoport.nec.raw
Columns of twoport.nec.raw:  d_cm  i1  i2  Prx  Ptx  ratio
"""
import sys, subprocess, tempfile, os, numpy as np

DECK = """* twoport.nec.cir -- two-port deck of twoport.kron.cir, fed with NEC-2 impedances
* d = {d:.1f} cm   Z11 = {R11:.4f} + j{X11:.4f}   Z21 = {R21:.4f} + j{X21:.4f}
.param f     = 900e6
.param w     = {{2*3.141592653589793*f}}
.param Rself = {R11}
.param Xself = {X11}
.param R21   = {R21}
.param X21   = {X21}
.param Lant  = {{Xself/w}}
.param Cmat  = {{1/(w*Xself)}}
.param kc    = {{X21/Xself}}
.param Vsrc  = {{sqrt(8*Rself*1.0)}}
* transmit loop: source - match - antenna(R + L) - ammeter - mutual EMF
Vs   n1 0 DC 0 AC {{Vsrc}}
Rs   n1 n2 {{Rself}}
Cs   n2 tx {{Cmat}}
Ltx  tx ta {{Lant}}
Rtx  ta tb {{Rself}}
Vse1 tb tc DC 0
Hr1  tc 0  Vse2 {{R21}}
* receive loop: antenna(L + R) - ammeter - mutual EMF - load - match
Lrx  0  ra {{Lant}}
Rrx  ra rb {{Rself}}
Vse2 rb rc DC 0
Hr2  rc rd Vse1 {{R21}}
RL   rd re {{Rself}}
CL   re 0  {{Cmat}}
K12  Ltx Lrx {{kc}}
.ac lin 1 {{f}} {{f}}
.control
run
let i1 = abs(i(Vse1))
let i2 = abs(i(Vse2))
let Prx = 0.5*{R11}*i2*i2
let Ptx = 0.5*{R11}*i1*i1
let ratio = Prx/Ptx
echo RESULT $&i1 $&i2 $&Prx $&Ptx $&ratio
.endc
.end
"""
z = np.loadtxt(sys.argv[1])
dmin = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0   # |kc|>1 for NEC values below ~5 cm
rows = []
with tempfile.TemporaryDirectory() as td:
    for d, R11, X11, R21, X21 in z:
        if d < dmin or abs(X21) >= abs(X11):
            continue
        fn = os.path.join(td, "p.cir")
        open(fn, "w").write(DECK.format(d=d, R11=R11, X11=X11, R21=R21, X21=X21))
        out = subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True).stdout
        vals = [l for l in out.splitlines() if l.startswith("RESULT")][0].split()[1:]
        rows.append([d] + [float(v) for v in vals])
np.savetxt("twoport.nec.raw", np.array(rows), fmt="%.8e",
           header="d_cm i1 i2 Prx Ptx ratio  (twoport.kron.cir topology fed with %s)" % sys.argv[1])
print(f"wrote twoport.nec.raw with {len(rows)} points (d >= {dmin} cm)")
