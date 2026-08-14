# jrfid2026.wirelesslink

ngspice decks reproducing the figures in "The Wireless Link as One Circuit: Mutual-Impedance Coupling for End-to-End SPICE Simulation of a Passive UHF RFID Tag" (IEEE J. Radio Freq. Identif., 2026).

Models a reader-tag antenna pair as a mutual-impedance two-port and embeds it in a passive UHF RFID SPICE deck (SkyWater SKY130): rectification, ASK downlink, backscatter, carrier cancellation, and polarization.

Regarding Skywater's 130 PDK, I use the [https://github.com/bpdegnan/spicesupport](https://github.com/bpdegnan/spicesupport) repo and the [installskywater.sh](https://raw.githubusercontent.com/bpdegnan/spicesupport/refs/heads/main/installskywater.sh) script to set it up.  

## Setup
```sh
./venv.setup.sh && source .venv/bin/activate   # ngspice output -> plots
./installspiceinit.sh                          # drops .spiceinit into each figN/
```
Edit `setupspice.source` to point `SPICE_LIB` at your local [SKY130 PDK](https://github.com/google/skywater-pdk) models, then `source` it before running ngspice.

## Layout
Each `figN/` is self-contained: one `.cir` deck, one plotting script, one `makefigN.sh` that runs both.
```
fig1/   power-transfer ratio, Maxwell vs. SPICE
fig3/   downlink ASK/PIE demodulation
fig4/   backscatter link
fig5/   polarization pattern
fig6/   polarization vs. harvested supply / backscatter depth
fig7/   full transistor-level reader-tag exchange
```

## Run
```sh
cd fig1 && ./makefig1.sh   # ... etc. for fig3-fig7
```


