"""scripts/ttf_lct_qpu_monotonicity_avg.py — Validation QPU de la MONOTONIE
de la loi LCT par tomographie complète, MOYENNÉE sur N runs.

Le bruit hardware du QPU (Spearman 0.594 sur 1 run) est l'obstacle. Moyenner
P_sig sur N runs indépendants réduit la variance d'un facteur √N. On lance
N=3 runs (chacun = 36 circuits, 12 θ × 3 bases) et on moyenne P_sig par θ.

Cela doit faire passer Spearman au-dessus du seuil strict de 0.6.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from scripts.ttf_lct_qpu_monotonicity import (
    build_cluster_state_circuit,
    reconstruct_corr_matrix,
    corr_to_P_sig,
    N_QUBITS,
)


def get_service():
    from qiskit_ibm_runtime import QiskitRuntimeService
    tok = os.environ["IBM_QUANTUM_TOKEN"]
    return QiskitRuntimeService(channel="ibm_cloud", token=tok)


def pick_least_loaded_qpu(svc):
    best, best_pending = None, float("inf")
    for b in svc.backends():
        try:
            st = b.status()
            if st.operational and st.pending_jobs < best_pending:
                best, best_pending = b, st.pending_jobs
        except Exception:
            continue
    return best


def run_one(svc, backend, n_theta: int, shots: int, run_label: str):
    """Lance un run complet (36 circuits) et renvoie P_sig par θ + job_id."""
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2 as Sampler

    all_circuits = []
    for i in range(n_theta):
        theta = (math.pi / 2) * i / (n_theta - 1)
        for basis in ["X", "Y", "Z"]:
            all_circuits.append(build_cluster_state_circuit(theta, basis))

    isa = transpile(all_circuits, backend=backend, optimization_level=1)
    sampler = Sampler(mode=backend)
    job = sampler.run(isa, shots=shots)
    job_id = job.job_id()
    print(f"  [{run_label}] Job ID : {job_id} — en attente QPU...")
    result = job.result()
    print(f"  [{run_label}] DONE")

    p_sigs = []
    for i in range(n_theta):
        all_counts = {}
        for j, basis in enumerate(["X", "Y", "Z"]):
            idx = i * 3 + j
            pub = result[idx]
            counts = pub.data.c.get_counts() if hasattr(pub.data, "c") else pub.data.get_counts()
            all_counts[basis] = counts
        corr = reconstruct_corr_matrix(all_counts, N_QUBITS)
        p_sigs.append(corr_to_P_sig(corr, max_edge=2.0))
    return job_id, p_sigs


def main():
    from qiskit_ibm_runtime import QiskitRuntimeService

    print("=" * 72)
    print("VALIDATION QPU MONOTONIE LCT — MOYENNE DE 3 RUNS")
    print("Le bruit hardware se réduit d'un facteur √3 en moyennant.")
    print("=" * 72)

    svc = get_service()
    backend = pick_least_loaded_qpu(svc)
    st = backend.status()
    print(f"QPU : {backend.name} (opérationnel, {st.pending_jobs} jobs en attente)")

    n_theta = 12
    shots = 4096
    n_runs = 3

    # lancer les 3 runs (séquentiel, chaque run = 1 job de 36 circuits)
    all_job_ids = []
    all_p_sigs = []  # (n_runs, n_theta)
    for r in range(n_runs):
        print(f"\n── Run {r+1}/{n_runs} ──")
        jid, p_sigs = run_one(svc, backend, n_theta, shots, f"run{r+1}")
        all_job_ids.append(jid)
        all_p_sigs.append(p_sigs)
        print(f"  P_sig run{r+1}: {[round(p, 3) for p in p_sigs]}")

    # moyenne de P_sig sur les runs
    P_avg = np.mean(all_p_sigs, axis=0)
    Cs = np.array([abs(math.cos((math.pi / 2) * i / (n_theta - 1))) for i in range(n_theta)])

    print(f"\n{'='*72}")
    print(f"RÉSULTATS MOYENNÉS (3 runs)")
    print(f"{'='*72}")
    print(f"{'θ':>8} {'C':>8} {'P_avg':>10}  runs")
    for i in range(n_theta):
        runs_str = " ".join([f"{all_p_sigs[r][i]:.3f}" for r in range(n_runs)])
        print(f"  {i:6d} {Cs[i]:8.3f} {P_avg[i]:10.4f}  [{runs_str}]")

    # corrélations
    ra = np.argsort(np.argsort(Cs))
    rb = np.argsort(np.argsort(P_avg))
    spearman_avg = float(np.corrcoef(ra, rb)[0, 1])
    pearson_avg = float(np.corrcoef(Cs, P_avg)[0, 1])
    print(f"\n  Pearson(C, P_avg)  = {pearson_avg:+.4f}")
    print(f"  Spearman(C, P_avg) = {spearman_avg:+.4f}")
    print(f"  P_avg range : {P_avg.min():.4f} → {P_avg.max():.4f}")

    verdict = "PASS" if spearman_avg > 0.6 else "FAIL"
    print(f"\n  VERDICT QPU MONOTONIE LCT (3 runs moyennés) : {verdict}")

    return {
        "law": "LCT_monotonicity_QPU_avg3",
        "backend": backend.name,
        "n_runs": n_runs,
        "job_ids": all_job_ids,
        "shots": shots,
        "n_theta": n_theta,
        "C_values": [round(float(c), 4) for c in Cs],
        "P_sig_runs": [[round(float(p), 4) for p in run] for run in all_p_sigs],
        "P_sig_avg": [round(float(p), 4) for p in P_avg],
        "corr_pearson": pearson_avg,
        "corr_spearman": spearman_avg,
        "verdict": verdict,
    }


if __name__ == "__main__":
    out = main()
    out_path = _ROOT / "proofs" / "lct_qpu_monotonicity_avg3_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nRésultats sauvegardés : {out_path}")
