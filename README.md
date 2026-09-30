# Arithmetic Dynamical Tomography: theory and experiments

This repository develops the mathematics behind the research proposal *“Arithmetic Dynamical Tomography: Reconstructing Integers from Polynomial Orbit Data”*. The proposal asks whether the prime factorisation of $n$ can be recovered from periodic-point counts of a few quadratic maps $x\mapsto x^2+c$ on $\mathbb Z/n\mathbb Z$.

**Main document: [`paper/ADT_foundations.md`](paper/ADT_foundations.md).** It contains full statements and proofs, heuristics, conjectures and tables. Every statement is labelled Theorem, Heuristic, Observation or Conjecture.

## Headline results

| Proposal item | What we found |
|---|---|
| **Reconstruction Conjecture** (“finite set of collisions”) | One collision $n\sim m$ forces $nr\sim mr$ for every coprime $r$, so the exceptional set must be **empty**. The fingerprint depends only on the per-probe **marginals** of the multiset of prime “types”, which makes the inverse problem literally discrete tomography. Its failure mode is the classical switching component. Example: $65=5\cdot13$ and $119=7\cdot17$ are indistinguishable for $x^2$ and $x^2-2$. For the proposal’s probe set $C=\{-3,\dots,3\}$ there is **no collision** among all 405,285 odd squarefree $n\le10^6$, nor among the 3.2 million $n\le10^7$ with prime factors below $10^6$. |
| **Finite-Depth Conjecture** (polylog depth) | Bounded depth is impossible: at fixed depth the fingerprint sees only Frobenius classes in one finite Galois group. Depth $\gg\sqrt{\log X}$ is needed unconditionally. For $x^2$ even depth $X^{1/8-\varepsilon}$ fails. A Poisson–Chebotarev model, verified against the wreath-product Galois groups of dynatomic polynomials, predicts $\lvert C\rvert\log K\approx\log X$, i.e. depth $\approx X^{1/\lvert C\rvert}$. This is confirmed numerically. |
| **Prime-Power Rigidity** | False as stated: $\mathrm{ADF}_{C,K}(p^e)=\mathrm{ADF}_{C,K}(p)$ for all but finitely many $p$. $p^2$ becomes visible exactly at depth $T_c(p)=\min\ell\cdot\mathrm{ord}_p(\lambda)$ over cycles, typically about $p^{0.9}$. Primes whose only cycle is critical are invisible at *every* depth: $41^e$ looks like $41$ to the probes $\{1,2\}$. |
| **Efficient Oracle** | Depth-1 entries are a quadratic-residuosity oracle. The number of periodic points of $x^2$ factors semiprimes in deterministic polynomial time. The only efficiently computable multiplicative shadows known are Jacobi symbols of dynamical discriminants. |
| **Graph reconstruction** (Target D) | The unlabeled graph of $x^2+c$ mod $n$ always determines $n$, via indegree counts $\sum_jI_jt^j=\prod_{p\mid n}(1+\tfrac{p-1}2t)$. |
| **Exactly solvable probes** $c=0,-2$ | Explicit through multiplicative orders. Together they separate all primes (a theorem). Among all 1.56 million odd semiprimes below $10^7$ the only collision is $65\sim119$. |
| **Consecutive vs. random constants** | $\Phi_2(x,c)=\Phi_1(-x,c+1)$, and minus every 3-cycle sum of $f_c$ is a fixed point of $f_{c+2}$. The proposal’s seven consecutive probes carry only 5 independent quadratic characters at depth $\le2$. Predicted depth-2 collision rate $2^{-5}$; measured $3.1\cdot10^{-2}$. |

## Layout

```
paper/ADT_foundations.md   the theory paper
figures/                   figures used in the paper (made by code/make_figures.py)
results/                   saved outputs of every experiment
code/cycles.c              C tool: cycle structure of x^2+c on Z/n (linear time per modulus)
code/adt.py                Z-sets, Burnside products, marks, fingerprints, CRT synthesis
code/gen_data.sh           builds the tool and generates the prime cycle data
code/validate.py           CRT synthesis and exact-formula checks
code/symbolic_identities.py  sympy verification of the dynatomic identities (Prop. 3.3)
code/exp_*.py              one script per experiment (see the table below)
```

## Reproducing

Requirements: `gcc`, Python 3 with `numpy`, `matplotlib` and `sympy`.

```sh
sh code/gen_data.sh --small      # tool + cycle data for 14 probes, primes < 1e5 (about 20 s)
sh code/gen_data.sh              # additionally the proposal's 7 probes to 1e6 (about 30 CPU-min)
cd code
python3 validate.py              # CRT and formula checks
python3 symbolic_identities.py   # Proposition 3.3 (a few minutes)
```

Data goes to `build/` by default; set `ADT_SCRATCH` to use another directory.

| script | paper | output in `results/` |
|---|---|---|
| `exp_local.py` | Obs. 3.2′, 3.5, 3.7, §3.5 | `local_statistics.txt` |
| `exp_solvable.py 300000` | §4, Example 5.5 | `solvable_0_m2_3e5.txt` |
| `exp_blum.py 10000000` | Obs. 5.6 | `solvable_semiprimes_1e7.txt` |
| `exp_paperC.py 1000000` / `10000000` | Obs. 5.7 | `paperC_1e6.txt`, `paperC_1e7.txt` |
| `exp_primes.py` | Obs. 5.8, 5.9 | `primes_collisions.txt` |
| `exp_collprob.py` | Heur. 8.1, Fig. 2 | `collision_vs_depth.txt` |
| `exp_depth.py ab` | Heur. 8.3, Fig. 3, Target B | `least_depth.txt` |
| `exp_primepower.py` | Obs. 7.3, 7.4 | `prime_powers.txt` |
| `exp_consecutive.py` | Obs. 10.2 | `consecutive_vs_spread.txt` |
| `make_figures.py` | Figs. 1–3 | `figures/*.png` |

## Status and caveats

The theorems are proved in the paper, some using standard cited inputs: Chebotarev, the Bousch–Morton Galois groups, the linear sieve with Bombieri–Vinogradov, and Stickelberger’s theorem.

The claims about generic probes at large depth are **heuristic**. They are stated as such, and their predictions are tested numerically.

Several ingredients are classical: CRT products of functional graphs, the squaring and Chebyshev graphs over $\mathbb F_p$, dynatomic Galois groups, Burnside/Witt rings, and discrete tomography. A literature search (MathSciNet/zbMATH) should precede any novelty claim.
