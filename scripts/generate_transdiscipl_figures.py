"""scripts/generate_transdiscipl_figures.py — Figures transdisciplinaires LCT.

Génère les figures pour les nouveaux systèmes testés :
  fig6_lct_neural_network.png   LCT sur réseau de neurones (3e système)
  fig7_protein_stability.png    Application : stabilité protéine mutante
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
FIG_DIR = _ROOT / "docs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def fig6_neural_network():
    """Figure 6 : LCT sur réseau de neurones."""
    path = _ROOT / "proofs" / "lct_neural_network_results.json"
    r = json.load(open(path))
    Cs = r["C_values"]
    Ps = r["P_sig_values"]
    sp = r["corr_spearman"]
    pe = r["corr_pearson"]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(Cs, Ps, c="#7c3aed", s=60, alpha=0.85, edgecolors="k", zorder=3)
    order = np.argsort(Cs)
    ax.plot(np.array(Cs)[order], np.array(Ps)[order], color="#7c3aed", alpha=0.5, lw=1.5)
    coeffs = np.polyfit(Cs, Ps, 1)
    ax.plot(np.linspace(min(Cs), max(Cs), 100), np.polyval(coeffs, np.linspace(min(Cs), max(Cs), 100)),
            color="#7c3aed", ls="--", alpha=0.6, label="régression")
    ax.set_xlabel("Cohérence $C$ (compression des poids)", fontsize=12)
    ax.set_ylabel("$R = P_{sig}$ (persistance topologique)", fontsize=12)
    ax.set_title(f"Figure 6 — LCT sur réseau de neurones (3e système)\n"
                 f"MLP 6→12→4 + bruit | Spearman = {sp:+.3f} | Pearson = {pe:+.3f}",
                 fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    verdict = "PASS" if sp > 0.6 else "PARTIAL"
    ax.text(0.05, 0.95, f"Monotonie : {verdict}", transform=ax.transAxes,
            fontsize=11, fontweight="bold", verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7))
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig6_lct_neural_network.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  fig6_lct_neural_network.png")


def fig7_protein_stability():
    """Figure 7 : Application — stabilité protéine mutante."""
    path = _ROOT / "proofs" / "lct_protein_stability_results.json"
    r = json.load(open(path))
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    # (a) P_sig par fragment
    ax = axes[0]
    p_mut = r["4MZI"]["p_sigs"]
    p_wt = r["3KMD"]["p_sigs"]
    x = np.arange(len(p_mut))
    w = 0.35
    ax.bar(x - w/2, p_mut, w, color="#dc2626", alpha=0.8, label="4MZI (p53 MUTANT)")
    ax.bar(x + w/2, p_wt, w, color="#2563eb", alpha=0.8, label="3KMD (p53 WILD-TYPE)")
    ax.set_xlabel("Fragment protéique", fontsize=11)
    ax.set_ylabel("$P_{sig}$ (persistance topologique)", fontsize=11)
    ax.set_title("(a) $P_{sig}$ par fragment", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    # (b) comparaison moyenne
    ax = axes[1]
    names = ["4MZI\n(p53 MUTANT)", "3KMD\n(p53 WILD-TYPE)"]
    means = [r["4MZI"]["P_sig_mean"], r["3KMD"]["P_sig_mean"]]
    stds = [r["4MZI"]["P_sig_std"], r["3KMD"]["P_sig_std"]]
    colors = ["#dc2626", "#2563eb"]
    bars = ax.bar(names, means, yerr=stds, capsize=8, color=colors, alpha=0.8, edgecolor="k")
    ax.set_ylabel("$P_{sig}$ moyen (stabilité topologique)", fontsize=11)
    ax.set_title("(b) Stabilité topologique comparée", fontsize=11)
    ax.grid(True, alpha=0.3, axis="y")
    # annotation
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.05, f"{val:.3f}",
                ha="center", fontsize=11, fontweight="bold")
    comp = r["comparison"]
    ax.text(0.5, 0.05, f"Ratio = {comp['ratio']:.3f}\n{comp['verdict']}",
            ha="center", transform=ax.transAxes, fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7))

    fig.suptitle("Figure 7 — Application LCT : prédiction de stabilité de protéine mutante\n"
                 "p53 mutant (4MZI) vs p53 wild-type (3KMD) — LCT prédit l'instabilité du mutant",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(FIG_DIR / "fig7_protein_stability.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  fig7_protein_stability.png")


def main():
    print("Génération des figures transdisciplinaires :")
    fig6_neural_network()
    fig7_protein_stability()
    print(f"\nFigures dans : {FIG_DIR}")


if __name__ == "__main__":
    main()
