"""scripts/generate_fig67_financial.py — Figures NN (limite) + finance (PASS)."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
FIG_DIR = _ROOT / "docs" / "figures"

def fig_nn_limit():
    """LCT sur NN (limite d'universalité)."""
    r = json.load(open(_ROOT / "proofs" / "lct_neural_network_results.json"))
    Cs, Ps, sp, pe = r["C_values"], r["P_sig_values"], r["corr_spearman"], r["corr_pearson"]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.scatter(Cs, Ps, c="#7c3aed", s=50, alpha=0.8, edgecolors="k")
    o = np.argsort(Cs); ax.plot(np.array(Cs)[o], np.array(Ps)[o], color="#7c3aed", alpha=0.4, lw=1.5)
    ax.set_xlabel("Cohérence $C$ (compression des poids)"); ax.set_ylabel("$R = P_{sig}$")
    ax.set_title(f"LCT sur réseau de neurones (MLP)\nSpearman = {sp:+.3f} | Pearson = {pe:+.3f} — PARTIAL (limite)",
                 fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.3); ax.text(0.05, 0.95, "Limite d'universalité", transform=ax.transAxes,
        fontsize=11, fontweight="bold", va="top", bbox=dict(boxstyle="round", facecolor="#fee2e2", alpha=0.7))
    fig.tight_layout(); fig.savefig(FIG_DIR / "fig6_lct_neural_network.png", dpi=150, bbox_inches="tight"); plt.close()
    print("  fig6 updated")

def fig8_financial():
    """LCT sur flux financier (PASS)."""
    r = json.load(open(_ROOT / "proofs" / "lct_financial_results.json"))
    Cs, Ps, sp, pe = r["C_values"], r["P_sig_values"], r["corr_spearman"], r["corr_pearson"]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(Cs, Ps, c="#059669", s=60, alpha=0.85, edgecolors="k", zorder=3)
    o = np.argsort(Cs); ax.plot(np.array(Cs)[o], np.array(Ps)[o], color="#059669", alpha=0.5, lw=1.5)
    c = np.polyfit(Cs, Ps, 1); ax.plot(np.linspace(min(Cs),max(Cs),100), np.polyval(c, np.linspace(min(Cs),max(Cs),100)),
            color="#059669", ls="--", alpha=0.6, label="régression")
    ax.set_xlabel("Cohérence $C$ (autocorrélation du marché)", fontsize=12)
    ax.set_ylabel("$R = P_{sig}$ (topologie des cycles de prix)", fontsize=12)
    ax.set_title(f"Figure 8 — LCT sur flux financier (5e système)\n"
                 f"Spearman = {sp:+.3f} | Pearson = {pe:+.3f} — PASS",
                 fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3); ax.legend(fontsize=10)
    ax.text(0.05, 0.95, "PASS — transdisciplinaire", transform=ax.transAxes, fontsize=11,
            fontweight="bold", va="top", bbox=dict(boxstyle="round", facecolor="#dcfce7", alpha=0.7))
    fig.tight_layout(); fig.savefig(FIG_DIR / "fig8_lct_financial.png", dpi=150, bbox_inches="tight"); plt.close()
    print("  fig8_lct_financial.png")

if __name__ == "__main__":
    print("Génération figures NN (limite) + finance (PASS) :")
    fig_nn_limit(); fig8_financial()
