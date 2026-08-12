"""scripts/figure1_R_vs_C.py — Figure 1 du papier : R(C) pour 4MZI et 3KMD
côte à côte, avec les courbes de Spearman.

Génère proofs/figure1_R_vs_C.png : deux sous-figures (4MZI, 3KMD) montrant
R=P_sig vs C, avec la corrélation de Spearman annotée. C'est la figure 1
du papier LCT.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from kernel.ttf.lct_law import scan_monotonicity, evaluate_monotonicity
from tests.test_ttf_5tests import load_pdb_atoms, normalize_coords

PDB_4MZI = _ROOT / "proofs" / "agent_run_v9.4" / "4MZI.pdb"
PDB_3KMD = _ROOT / "data" / "pdb" / "3KMD.pdb"


def main():
    print("=" * 72)
    print("FIGURE 1 : R(C) pour 4MZI et 3KMD, côte à côte + Spearman")
    print("=" * 72)

    systems = [
        ("4MZI", PDB_4MZI, "tab:blue"),
        ("3KMD", PDB_3KMD, "tab:red"),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=False)
    fig.suptitle("Figure 1 — Loi de Cohérence Topologique (LCT) : $R(C) = P_{sig}$\n"
                 "$R$ croît avec la cohérence $C$ du milieu génial (l'intrication nettoie la topologie)",
                 fontsize=13, fontweight="bold")

    summary = {}
    for ax, (name, pdb_path, color) in zip(axes, systems):
        print(f"\n[{name}] scan R(C)...")
        coords, _ = load_pdb_atoms(pdb_path)
        sub = normalize_coords(coords, 150)
        measurements = scan_monotonicity(sub, n_points=24, omega=math.pi / 2,
                                          max_edge=5.0, t=1.0, J=0.3, label=name)
        mono = evaluate_monotonicity(measurements)

        C = np.array([m.coherence_C for m in measurements])
        R = np.array([m.R for m in measurements])

        # tri par C pour la courbe continue
        order = np.argsort(C)
        C_s = C[order]
        R_s = R[order]

        # points + courbe
        ax.scatter(C, R, c=color, s=50, alpha=0.85, edgecolors="k", zorder=3,
                   label=f"{name} (mesures QPU-ready)")
        ax.plot(C_s, R_s, color=color, alpha=0.5, linewidth=1.5, zorder=2)

        # régression linéaire (visuel de la tendance)
        if C.std() > 1e-9:
            coeffs = np.polyfit(C, R, 1)
            C_line = np.linspace(C.min(), C.max(), 100)
            R_line = np.polyval(coeffs, C_line)
            ax.plot(C_line, R_line, color=color, linestyle="--", alpha=0.6,
                    linewidth=1.5, label=f"régression linéaire")

        # annotation Spearman
        ax.set_title(f"{name}  (p53 {'mutant' if name=='4MZI' else '+DNA'})\n"
                     f"Spearman = {mono['corr_spearman']:+.3f}  |  "
                     f"Pearson = {mono['corr_pearson']:+.3f}",
                     fontsize=11)
        ax.set_xlabel("Cohérence $C$ du milieu génial  ($|\\cos\\theta|$)", fontsize=11)
        if name == "4MZI":
            ax.set_ylabel("$R = P_{sig}$  (persistance topologique)", fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9, loc="lower right")

        # verdict monotonie
        verdict = "PASS" if mono["monotone"] else "FAIL"
        ax.text(0.05, 0.95, f"Monotonie : {verdict}",
                transform=ax.transAxes, fontsize=11, fontweight="bold",
                verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7))

        summary[name] = {
            "n_points": len(measurements),
            "spearman": mono["corr_spearman"],
            "pearson": mono["corr_pearson"],
            "monotone": mono["monotone"],
            "C_range": mono["C_range"],
            "R_range": mono["R_range"],
        }
        print(f"  Spearman = {mono['corr_spearman']:+.4f}  |  Pearson = {mono['corr_pearson']:+.4f}  |  {verdict}")

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out_path = _ROOT / "proofs" / "figure1_R_vs_C.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nFigure 1 sauvegardée : {out_path}")
    print(f"Résumé : {json.dumps(summary, indent=2, default=str)}")
    return summary


if __name__ == "__main__":
    main()
