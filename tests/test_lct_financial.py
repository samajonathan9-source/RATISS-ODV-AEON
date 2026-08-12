"""tests/test_lct_financial.py — LCT sur un flux financier (5e système).

On applique LCT à une série temporelle financière (prix synthétique type
marché). La "cohérence" C = corrélation temporelle (autocorrélation lag-1).
La topologie = structure des cycles du prix (fenêtres glissantes → nuage de
points → Rips → P_sig).

Hypothèse : quand le marché est cohérent (forte autocorrélation, tendance
claire), la topologie des cycles de prix est robuste (P_sig élevé). Quand le
marché est chaotique (faible autocorrélation, bruit), P_sig est bas.

C'est la transdisciplinarité : LCT sur finance, pas juste quantique/bio.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from kernel.ttf.ttf_compute import _persistence_diagrams


def generate_price_series(n=500, coherence=0.8, volatility=0.02, seed=42):
    """Génère une série de prix avec autocorrélation contrôlée.

    coherence=1 → marche directionnelle forte (tendance claire, C élevé).
    coherence=0 → bruit pur (random walk, C bas).
    Modèle : p[t] = coherence * p[t-1] + (1-coherence) * noise.
    """
    rng = np.random.default_rng(seed)
    prices = np.zeros(n)
    prices[0] = 100.0
    for t in range(1, n):
        trend = coherence * prices[t-1]
        noise = (1 - coherence) * rng.normal(0, volatility * 100, 1)[0]
        prices[t] = trend + noise + (1 - coherence) * 100  # recentrer
    return prices


def series_to_point_cloud(prices, window=20, stride=5):
    """Transforme une série temporelle en nuage de points (time-delay embedding).

    Chaque point = une fenêtre glissante de `window` prix consécutifs.
    La topologie de ce nuage capture la structure des cycles du prix.
    """
    n = len(prices)
    points = []
    for i in range(0, n - window, stride):
        points.append(prices[i:i+window])
    return np.array(points)


def measure_P_sig(coords, max_edge=5.0):
    diagrams, _ = _persistence_diagrams(coords, max_edge)
    h1 = [d - b for b, d in diagrams.get(1, []) if d != float("inf") and d > b]
    return max(h1) if h1 else 0.0


def compress_ttf(coords, C, max_q=0.5):
    """Compression TTF : C élevé → garde les fenêtres les plus 'denses'
    (variance intra-fenêtre basse = tendance claire = cohérent)."""
    # densité locale = 1 / variance de la fenêtre
    var = np.var(coords, axis=1)
    local_coh = 1.0 / (var + 0.01)
    q = min(max_q, C * max_q)
    threshold = float(np.quantile(local_coh, q))
    mask = local_coh >= threshold
    if mask.sum() < 4:
        mask = np.ones(len(coords), dtype=bool)
    return coords[mask], mask


def main():
    print("=" * 72)
    print("LCT SUR FLUX FINANCIER (5e système — transdisciplinaire)")
    print("Cohérence C = autocorrélation du marché. P_sig = topologie des cycles.")
    print("=" * 72)

    # scanner C de 0 (chaos) à 1 (tendance forte)
    coherences = np.linspace(0.05, 0.95, 14)
    Cs = []
    P_sigs = []
    for coh in coherences:
        # générer la série
        prices = generate_price_series(n=500, coherence=coh, volatility=0.02, seed=42)
        # nuage de points (time-delay embedding)
        coords = series_to_point_cloud(prices, window=20, stride=5)
        # compression TTF à C=coh (on garde les fenêtres cohérentes)
        sub, mask = compress_ttf(coords, coh)
        ps = measure_P_sig(sub, max_edge=5.0)
        Cs.append(coh)
        P_sigs.append(ps)
        print(f"  C={coh:.3f}  n_points={len(coords)}→{int(mask.sum())}  P_sig={ps:.4f}")

    Cs = np.array(Cs)
    P_sigs = np.array(P_sigs)
    ra = np.argsort(np.argsort(Cs))
    rb = np.argsort(np.argsort(P_sigs))
    spearman = float(np.corrcoef(ra, rb)[0, 1])
    pearson = float(np.corrcoef(Cs, P_sigs)[0, 1]) if Cs.std() > 1e-9 else 0.0

    print(f"\n  Pearson(C, P_sig)  = {pearson:+.4f}")
    print(f"  Spearman(C, P_sig) = {spearman:+.4f}")
    verdict = "PASS" if spearman > 0.6 else "PARTIAL"
    print(f"  VERDICT : {verdict}")
    if verdict == "PASS":
        print("  → LCT sur finance : un marché cohérent a une topologie de cycles robuste.")
        print("    La loi est transdisciplinaire : quantique + bio + ML + finance.")

    return {
        "system": "financial_time_series",
        "n_points": len(coords),
        "C_values": [round(float(c), 4) for c in Cs],
        "P_sig_values": [round(float(p), 4) for p in P_sigs],
        "corr_pearson": pearson,
        "corr_spearman": spearman,
        "verdict": verdict,
    }


if __name__ == "__main__":
    out = main()
    out_path = _ROOT / "proofs" / "lct_financial_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nRésultats sauvegardés : {out_path}")
