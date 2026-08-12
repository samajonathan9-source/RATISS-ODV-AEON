"""tests/test_lct_protein_stability.py — Application concrète de LCT :
prédire la stabilité d'une protéine mutante.

4MZI = p53 MUTANT (structure cristallographique d'un mutant de p53).
3KMD = p53 WILD-TYPE (p53 core domain lié à l'ADN, tétramère).

Hypothèse LCT : la persistance topologique P_sig (à C=1, compression max)
distingue le mutant du wild-type. Si P_sig(mutant) < P_sig(wild-type), le
mutant est topologiquement MOINS stable (sa structure est moins robuste
topologiquement). C'est une prédiction de stabilité par LCT.
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
from tests.test_ttf_5tests import load_pdb_atoms, normalize_coords
from scipy.spatial.distance import cdist

PDB_4MZI = _ROOT / "proofs" / "agent_run_v9.4" / "4MZI.pdb"  # p53 MUTANT
PDB_3KMD = _ROOT / "data" / "pdb" / "3KMD.pdb"              # p53 WILD-TYPE + DNA


def measure_stability_signature(coords, n_fragments=5, fragment_size=100, max_edge=5.0):
    """Mesure la signature de stabilité LCT d'une protéine : P_sig moyen sur
    plusieurs fragments contigus, à C=1 (compression max = structure pure).

    P_sig élevé = topologie robuste = protéine stable.
    P_sig faible = topologie fragile = protéine instable (mutant).
    """
    rng = np.random.RandomState(42)
    p_sigs = []
    for i in range(n_fragments):
        start = i * fragment_size
        end = start + fragment_size
        if end > len(coords):
            end = len(coords)
        frag = coords[start:end]
        if len(frag) < 10:
            continue
        # compression C=1 : ne garder que les nœuds les plus denses (quantile 0.5)
        Dfull = cdist(frag, frag)
        np.fill_diagonal(Dfull, np.inf)
        nn_dist = Dfull.min(axis=1)
        local_coh = 1.0 / (nn_dist + 0.1)
        threshold = float(np.quantile(local_coh, 0.5))
        mask = local_coh >= threshold
        if mask.sum() < 4:
            mask = np.ones(len(frag), dtype=bool)
        landmarks = frag[mask]
        diagrams, _ = _persistence_diagrams(landmarks, max_edge)
        h1 = [d - b for b, d in diagrams.get(1, []) if d != float("inf") and d > b]
        p_sigs.append(max(h1) if h1 else 0.0)
    return {
        "p_sigs": p_sigs,
        "P_sig_mean": float(np.mean(p_sigs)),
        "P_sig_max": float(np.max(p_sigs)),
        "P_sig_std": float(np.std(p_sigs)),
        "n_fragments": len(p_sigs),
    }


def main():
    print("=" * 72)
    print("APPLICATION CONCRÈTE LCT : STABILITÉ DE PROTÉINE MUTANTE")
    print("4MZI = p53 MUTANT  vs  3KMD = p53 WILD-TYPE (+ DNA)")
    print("Hypothèse : P_sig(mutant) < P_sig(wild-type) → mutant moins stable")
    print("=" * 72)

    results = {}
    for name, pdb_path, status in [("4MZI", PDB_4MZI, "p53 MUTANT"),
                                    ("3KMD", PDB_3KMD, "p53 WILD-TYPE")]:
        print(f"\n── {name} ({status}) ──")
        coords, elems = load_pdb_atoms(pdb_path)
        print(f"  {len(coords)} atomes, éléments : {sorted(set(elems))}")
        sig = measure_stability_signature(coords, n_fragments=8, fragment_size=150)
        print(f"  P_sig par fragment : {[round(p, 3) for p in sig['p_sigs']]}")
        print(f"  P_sig moyen = {sig['P_sig_mean']:.4f}")
        print(f"  P_sig max   = {sig['P_sig_max']:.4f}")
        print(f"  P_sig std   = {sig['P_sig_std']:.4f}  (uniformité topologique)")
        results[name] = {"status": status, **sig}

    # comparaison
    p_mutant = results["4MZI"]["P_sig_mean"]
    p_wt = results["3KMD"]["P_sig_mean"]
    ratio = p_wt / p_mutant if p_mutant > 1e-9 else float("inf")

    print(f"\n{'='*72}")
    print(f"COMPARAISON LCT")
    print(f"{'='*72}")
    print(f"  P_sig(mutant 4MZI)   = {p_mutant:.4f}")
    print(f"  P_sig(wild-type 3KMD) = {p_wt:.4f}")
    print(f"  Ratio wild-type/mutant = {ratio:.3f}")

    if p_wt > p_mutant:
        verdict = "MUTANT MOINS STABLE"
        print(f"\n  VERDICT LCT : {verdict}")
        print(f"  → Le mutant p53 (4MZI) a une topologie MOINS robuste que le wild-type (3KMD).")
        print(f"    P_sig(mutant) < P_sig(wild-type) : la mutation a fragilisé la structure topologique.")
        print(f"    LCT prédit correctement l'instabilité du mutant (connue biologiquement).")
    else:
        verdict = "MUTANT PLUS STABLE (inattendu)"
        print(f"\n  VERDICT LCT : {verdict}")
        print(f"  → Le mutant est topologiquement PLUS robuste — à investiguer.")

    results["comparison"] = {
        "P_sig_mutant": p_mutant,
        "P_sig_wild_type": p_wt,
        "ratio": ratio,
        "verdict": verdict,
        "biological_context": "p53 mutants are known to be destabilized (4MZI is a mutant crystal structure).",
    }
    return results


if __name__ == "__main__":
    out = main()
    out_path = _ROOT / "proofs" / "lct_protein_stability_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nRésultats sauvegardés : {out_path}")
