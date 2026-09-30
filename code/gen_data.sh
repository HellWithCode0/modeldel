#!/bin/sh
# Build the cycle tool and generate the prime cycle data used by the experiments.
#   data/primes_c{c}.txt : 14 probes c = -6..7, odd primes < 1e5   (~20 s on 4 cores)
#   data/full_c{c}.txt   : the proposal's probes c = -3..3, odd primes < 1e6
#                          (~30 CPU-minutes; needed only by exp_paperC.py and exp_depth.py b)
# Output goes to $ADT_SCRATCH (default: <repo>/build).
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
B=${ADT_SCRATCH:-$ROOT/build}
J=${JOBS:-4}
mkdir -p "$B/data"
gcc -O3 -o "$B/cycles" "$ROOT/code/cycles.c"
for c in -6 -5 -4 -3 -2 -1 0 1 2 3 4 5 6 7; do echo "$c"; done |
  xargs -P "$J" -I{} sh -c "'$B/cycles' primes 3 100000 {} > '$B/data/primes_c{}.txt'"
[ "$1" = "--small" ] && exit 0
for c in -3 -2 -1 0 1 2 3; do echo "$c"; done |
  xargs -P "$J" -I{} sh -c "'$B/cycles' primes 3 1000000 {} > '$B/data/full_c{}.txt'"
