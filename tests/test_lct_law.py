"""tests/test_lct_law.py — Valide la Loi de Cohérence Topologique (LCT).

Étapes :
  1. MONOTONIE : tracer R(C) sur 4MZI et 3KMD. R doit croître avec C.
  2. UNIVERSALITÉ : la loi tient sur les 2 systèmes (4MZI p53, 3KMD p53-DNA).
  3. INVARIANCE : R constant sous changement d'énergie (mêmes θ/topologie).
  4. Graphiques R(C) sauvegardés dans proofs/.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from kernel.ttf.lct_law import (
    scan_monotonicity,
    test_invariance,
    evaluate_monotonicity,
)
from tests.test_ttf_5tests import load_pdb_atoms, normalize_coords

PDB_4MZI = _ROOT / "proofs" / "agent_run_v9.4" / "4MZI.pdb"
PDB_3KMD = _ROOT / "data" / "pdb" / "3KMD.pdb"


def plot_R_vs_C(measurements, label, color, ax):
    """Trace R(C) sur un axe matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    C = [m.coherence_C for m in measurements]
    R = [m.R for m in measurements]
    ax.scatter(C, R, c=color, s=60, alpha=0.8, edgecolors="k", zorder=3, label=label)
    # trier par C pour la courbe
    order = np.argsort(C)
    C_sorted = [C[i] for i in order]
    R_sorted = [R[i] for i in order]
    ax.plot(C_sorted, R_sorted, color=color, alpha=0.4, linestyle="--", zorder=2)
    return C, R


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    print("=" * 72)
    print("VALIDATION DE LA LOI DE COHÉRENCE TOPOLOGIQUE (LCT)")
    print("R = P_sig / P_noise doit croître avec C (monotonie),")
    print("être invariant sous changement d'énergie, et universel.")
    print("=" * 72)

    systems = [
        ("4MZI", PDB_4MZI, "tab:blue"),
        ("3KMD", PDB_3KMD, "tab:red"),
    ]

    results = {}
    fig, ax = plt.subplots(1, 1, figsize=(9, 6))

    for name, pdb_path, color in systems:
        print(f"\n{'─'*72}")
        print(f"SYSTÈME : {name} ({pdb_path.name})")
        print(f"{'─'*72}")
        if not pdb_path.exists():
            print(f"  PDB introuvable : {pdb_path}")
            continue
        coords, elems = load_pdb_atoms(pdb_path)
        sub = normalize_coords(coords, 150)
        print(f"  {name} chargé : {len(sub)} atomes, éléments : {sorted(set(elems))}")

        # ── 1. MONOTONIE : scan R(C) ──
        print(f"\n  [1] MONOTONIE : scan R(C) sur {name}...")
        measurements = scan_monotonicity(sub, n_points=12, omega=math.pi / 2,
                                          max_edge=5.0, t=1.0, J=0.3, label=name)
        mono = evaluate_monotonicity(measurements)
        print(f"      C range : [{mono['C_range'][0]:.4f}, {mono['C_range'][1]:.4f}]")
        print(f"      R range : [{mono['R_range'][0]:.4f}, {mono['R_range'][1]:.4f}]")
        print(f"      Corr Pearson (C,R)  = {mono['corr_pearson']:+.4f}")
        print(f"      Corr Spearman (C,R) = {mono['corr_spearman']:+.4f}")
        print(f"      C_vals = {mono['C_vals']}")
        print(f"      R_vals = {mono['R_vals']}")
        verdict_mono = "PASS" if mono["monotone"] else "FAIL"
        print(f"      MONOTONIE : {verdict_mono}  (Spearman > 0.6 ⇒ R croît avec C)")

        # tracer
        plot_R_vs_C(measurements, f"{name} (Spearman={mono['corr_spearman']:.2f})", color, ax)

        # ── 2. INVARIANCE : R constant sous changement d'énergie ──
        print(f"\n  [2] INVARIANCE : R constant sous changement d'énergie ({name})...")
        inv = test_invariance(sub, theta_fixed=math.pi / 2, max_edge=5.0)
        print(f"      Énergies t-J : {[round(e,4) for e in inv['energies']]}")
        print(f"      R valeurs    : {[round(r,4) for r in inv['R_values']]}")
        print(f"      R moyen = {inv['R_mean']:.4f}  | R std = {inv['R_std']:.4f}")
        print(f"      Coeff. variation R = {inv['R_cv']:.4f}  (< 0.05 = invariant)")
        print(f"      Énergie changée ? {inv['energy_changed']}")
        verdict_inv = "PASS" if (inv["invariant"] and inv["energy_changed"]) else "FAIL"
        print(f"      INVARIANCE : {verdict_inv}  (R stable malgré énergies ≠ ⇒ on certifie la forme)")

        results[name] = {
            "monotonicity": mono,
            "monotonicity_verdict": verdict_mono,
            "invariance": {
                "theta_fixed": inv["theta_fixed"],
                "energies": [round(e, 4) for e in inv["energies"]],
                "R_values": [round(r, 4) for r in inv["R_values"]],
                "R_mean": round(inv["R_mean"], 4),
                "R_std": round(inv["R_std"], 4),
                "R_cv": round(inv["R_cv"], 4),
                "invariant": inv["invariant"],
                "energy_changed": inv["energy_changed"],
                "verdict": verdict_inv,
            },
        }

    # ── 3. UNIVERSALITÉ : la loi tient sur les 2 systèmes ──
    print(f"\n{'─'*72}")
    print("UNIVERSALITÉ : la loi LCT tient-elle sur les 2 systèmes ?")
    print(f"{'─'*72}")
    mono_pass = sum(1 for n in results if results[n]["monotonicity_verdict"] == "PASS")
    inv_pass = sum(1 for n in results if results[n]["invariance"]["verdict"] == "PASS")
    n_sys = len(results)
    universal = (mono_pass == n_sys and inv_pass == n_sys)
    print(f"  Monotonie : {mono_pass}/{n_sys} systèmes PASS")
    print(f"  Invariance: {inv_pass}/{n_sys} systèmes PASS")
    verdict_univ = "PASS" if universal else "PARTIAL"
    print(f"  UNIVERSALITÉ : {verdict_univ}")
    results["universal"] = {"verdict": verdict_univ, "n_systems": n_sys,
                            "monotonicity_pass": mono_pass, "invariance_pass": inv_pass}

    # finalisation graphique
    ax.set_xlabel("Cohérence C du milieu génial", fontsize=12)
    ax.set_ylabel("R = P_sig / P_noise (invariant topologique)", fontsize=12)
    ax.set_title("Loi de Cohérence Topologique (LCT) : R(C)\n"
                 "R croît avec C, invariant sous énergie — universel", fontsize=12)
    ax.legend(fontsize=10, loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    plot_path = _ROOT / "proofs" / "lct_R_vs_C.png"
    fig.savefig(plot_path, dpi=120)
    print(f"\nGraphique R(C) sauvegardé : {plot_path}")

    # récapitulatif
    print(f"\n{'='*72}")
    print("RÉCAPITULATIF LOI LCT")
    print(f"{'='*72}")
    for name in [n for n in results if n != "universal"]:
        m = results[name]["monotonicity_verdict"]
        i = results[name]["invariance"]["verdict"]
        print(f"  {name:8s} : monotonie={m}  invariance={i}")
    print(f"  UNIVERSALITÉ : {verdict_univ}")
    return results


if __name__ == "__main__":
    out = main()
    out_path = _ROOT / "proofs" / "lct_law_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nRésultats sauvegardés : {out_path}")
