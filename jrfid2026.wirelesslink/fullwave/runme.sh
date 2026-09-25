#!/usr/bin/env zsh

set -euo pipefail
cd "$(dirname "$0")"

HELP_URL="https://github.com/bpdegnan/macportseda"  #if things are missing to run.
missing=0
# I needed to test things as not all of my computers had the complete chain
function need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: '$1' not found in PATH." >&2
    missing=1
  fi
}

need nec2c
need ngspice
need python3
if [ "$missing" -eq 0 ] && ! python3 -c "import numpy, scipy, matplotlib" >/dev/null 2>&1; then
  echo "ERROR: python3 is missing one of numpy, scipy, matplotlib." >&2
  missing=1
fi
if [ "$missing" -ne 0 ]; then
  echo "Install the missing tools first.  see:" >&2
  echo "    $HELP_URL" >&2
  exit 1
fi

if [ "${1:-}" != "--plot" ]; then
  echo "== 1/3  NEC-2 (MoM) sweeps"
  for a in 0.03 0.1 1.0; do
    python3 nec_sweep.py --radius_mm "$a" --segs 81 --dmin 1 --dmax 200 --step 1
  done

  echo "== 2/3  SPICE two-port decks"
  echo "   a) induced-EMF Z21 (same deck as paper Fig. 1)  -> twoport.kron.raw"
  rm -f twoport.kron.raw
  ngspice -b twoport.kron.cir >/dev/null
  echo "   b) NEC-2 Z11,Z21 table (d >= 5 cm) -> twoport.nec.raw"
  python3 run_nec_deck.py nec_z.a0.1mm.csv 5
fi

echo "== fullwave.eps / fullwave.png"
python3 plot_fullwave.py twoport.kron.raw
echo "done."
