#!/usr/bin/env python3

import numpy as np, sys
from scipy.special import sici
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

c, f = 2.99792458e8, 900e6
lam = c / f; k = 2*np.pi/lam; L = lam/2; eta = 376.730313
R11c, X11c = 73.079010, 42.5

def Z21c(d):
    r = np.sqrt(d*d + L*L)
    S0, C0 = sici(k*d); S1, C1 = sici(k*(r+L)); S2, C2 = sici(k*(r-L))
    return eta/(4*np.pi)*(2*C0-C1-C2) - 1j*eta/(4*np.pi)*(2*S0-S1-S2)

def friis(d): return 1.643**2*(lam/(4*np.pi*d))**2

kron = np.loadtxt(sys.argv[1] if len(sys.argv) > 1 else "twoport.kron.raw")
d_k, rat_k = kron[:, 3]/100, kron[:, 15]

nec = {a: np.loadtxt(f"nec_z.a{a}mm.csv") for a in ("0.03", "0.1", "1")}
def nec_ratio(z): return (z[:, 3]**2 + z[:, 4]**2) / (2*z[:, 1])**2

sn = np.loadtxt("twoport.nec.raw")
d_sn, rat_sn = sn[:, 0]/100, sn[:, 5]
ok = np.ones(len(d_sn), bool)          # deck was run only for d >= 5 cm (|k12| < 1)

z = nec["0.1"]; d_n = z[:, 0]/100
Zc = Z21c(d_n); Zn = z[:, 3] + 1j*z[:, 4]

C1, C2, C3, C4, C5 = "#1f4e8c", "#e07b39", "#5a5a5a", "#7a3b8f", "#2a9d8f"
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 9.2), sharex=True,
                                    gridspec_kw={"height_ratios": [2.2, 3, 1.6]})
dcm = d_n*100
ax1.semilogx(dcm, Zc.real, "-",  color=C1, lw=2.0, label=r"$R_{21}$ induced-EMF (Carter)")
ax1.semilogx(dcm, Zc.imag, "-",  color=C4, lw=2.0, label=r"$X_{21}$ induced-EMF (Carter)")
ax1.semilogx(dcm[::4], Zn.real[::4], "o", color=C2, ms=4, mfc="none", label=r"$R_{21}$ NEC-2 MoM, $a$ = 0.1 mm")
ax1.semilogx(dcm[::4], Zn.imag[::4], "s", color=C5, ms=4, mfc="none", label=r"$X_{21}$ NEC-2 MoM, $a$ = 0.1 mm")
ax1.axhline(0, color="0.8", lw=0.8)
ax1.set_ylabel(r"mutual impedance $Z_{21}$ [$\Omega$]")
ax1.set_title("Induced-EMF SPICE vs. full-wave (NEC-2) solution @ 900 MHz")
ax1.legend(frameon=False, fontsize=8, ncol=2)
ax1.grid(True, which="both", alpha=0.25)

#ax2.loglog(d_k*100, rat_k, "-", color=C1, lw=2.0, label="SPICE deck, Carter $Z_{21}$ (paper Fig. 1)")
ax2.loglog(d_k*100, rat_k, "-", color=C1, lw=2.0, label="SPICE deck, induced-EMF $Z_{21}$ ")
ax2.loglog(dcm[::4], nec_ratio(z)[::4], "o", color=C2, ms=4.5, mfc="none", label="NEC-2 MoM, $a$ = 0.1 mm")
ax2.loglog(d_sn[ok]*100, rat_sn[ok], "x", color=C5, ms=3.5, label="SPICE deck fed with NEC-2 $Z_{11},Z_{21}$")
ax2.loglog(dcm, friis(d_n), "--", color=C3, lw=1.3, label="Friis far-field ($G$ = 1.64)")
ymin, ymax = ax2.get_ylim()
for x, t in [(lam/(2*np.pi)*100, r"$\lambda/2\pi$"), (lam/2*100, r"$\lambda/2$"), (100, "1 m link")]:
    ax2.axvline(x, color="0.8", ls=":", lw=1); ax2.text(x, ymax, t, rotation=90, va="top", ha="right", fontsize=7, color="0.5")
ax2.set_ylabel(r"power transfer $P_{rx}/P_{tx}$")
ax2.legend(frameon=False, fontsize=8)
ax2.grid(True, which="both", alpha=0.25)

for a, col, lab in (("0.03", C4, "0.03"), ("0.1", C2, "0.1"), ("1", C3, "1")):
    zz = nec[a]; dd = zz[:, 0]/100
    ax3.semilogx(dd*100, 100*(nec_ratio(zz)/(abs(Z21c(dd))**2/(2*R11c)**2) - 1), "-", color=col, lw=1.3,
                 label=f"NEC-2 ($a$ = {lab} mm) vs. induced-EMF")
# SPICE(NEC-fed) vs NEC itself: implementation check
zi = np.interp(d_sn[ok], d_n, nec_ratio(z))
ax3.semilogx(d_sn[ok]*100, 100*(rat_sn[ok]/zi - 1), "x", color=C5, ms=3, label="SPICE (NEC-fed) vs. NEC-2")
ax3.axhline(0, color="0.8", lw=0.8)
ax3.set_ylabel(r"$P_{rx}/P_{tx}$ difference [%]"); ax3.set_xlabel("dipole separation distance [cm]")
ax3.set_ylim(-12, 12); ax3.legend(frameon=False, fontsize=8, ncol=2); ax3.grid(True, which="both", alpha=0.25)
fig.tight_layout()
fig.savefig("fullwave.eps", format="eps"); fig.savefig("fullwave.png", dpi=130)

# ---- summary numbers ----
print("wire radius | NEC Z11 (isolated)      | |Z21| NEC/induced-EMF @1m | Prx/Ptx NEC/induced-EMF @1m | far-field (>=50cm) max |diff| | near (1-10cm) max |diff|")
for a in ("0.03", "0.1", "1"):
    zz = nec[a]; dd = zz[:, 0]/100
    hdr = open(f"nec_z.a{a}mm.csv").readline()
    ziso = hdr.split("Ziso=")[1].rstrip(")\n")
    rn = nec_ratio(zz); rc = abs(Z21c(dd))**2/(2*R11c)**2
    i1 = np.argmin(abs(dd-1.0))
    far = dd >= 0.5; near = dd <= 0.10
    print(f"{a:>5} mm     | {ziso:>22} | {abs(zz[i1,3]+1j*zz[i1,4])/abs(Z21c(1.0)):.3f}                | {rn[i1]/rc[i1]:.4f}                 | {100*np.max(abs(rn[far]/rc[far]-1)):.2f} %                      | {100*np.max(abs(rn[near]/rc[near]-1)):.1f} %")
print(f"SPICE(NEC-fed) vs NEC-2 (d>=5cm): max |diff| = {100*np.max(abs(rat_sn[ok]/zi-1)):.2e} %")
i1 = np.argmin(abs(d_n-1.0)); print(f"at 1 m: induced-EMF Z21 = {Z21c(1.0):.3f};  NEC(0.1mm) Z21 = {Zn[i1]:.3f};  NEC R11 = {z[i1,1]:.2f} X11 = {z[i1,2]:.2f}")
ff = d_n >= 0.5
print(f"Friis: induced-EMF/Friis median (d>=50cm) = {np.median((abs(Zc[ff])**2/(2*R11c)**2)/friis(d_n[ff])):.4f}; NEC(0.1mm)/Friis = {np.median(nec_ratio(z)[ff]/friis(d_n[ff])):.4f}")
