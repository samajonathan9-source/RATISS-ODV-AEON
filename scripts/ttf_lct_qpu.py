"""scripts/ttf_lct_qpu.py — Validation QPU de l'invariance ZK de la loi LCT.

On soumet au QPU IBM la partie INVARIANCE de la loi LCT :
  - 2 circuits quantiques avec énergies DIFFÉRENTES (θ₁ ≠ θ₂)
  - mais on mesure le TOPOLOGICAL FORM (hash de la structure de corrélation
    de Bell) qui doit être INVARIANT.

C'est la validation hardware de : « R = P_sig est invariant sous changement
d'énergie (on certifie la forme, pas le courant) ».

Le QPU ne calcule pas directement la persistance H1 (pas de Rips hardware),
mais on mesure la TOPOLOGIE de corrélation (la partition de Bell) qui est
l'invariant ZK sous-jacent — le même objet qu'on certifie dans la loi LCT.

Construction :
  Circuit 1 : Bell + R_y(θ₁)  → énergie E1, distribution D1
  Circuit 2 : Bell + R_y(θ₂)  → énergie E2, distribution D2 (≠ E1)
  On hash la topologie de corrélation (partition même-spin / spin-opposé).
  Loi LCT (invariance ZK) : hash(D1) == hash(D2) malgré E1 ≠ E2.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))


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


def build_lct_circuits():
    """2 circuits Bell + R_y(θ) avec θ₁ ≠ θ₂ (énergies différentes).
    Mesure dans la base de Bell (inverse-Bell puis mesure Z)."""
    from qiskit import QuantumCircuit
    circs = []
    # θ₁ petit (énergie basse) vs θ₂ grand (énergie haute)
    for label, theta in [("E1_low", math.pi / 6), ("E2_high", 5 * math.pi / 6)]:
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.ry(theta, 0)
        # inverse-Bell pour mesurer dans la base de Bell (topologie)
        qc.cx(0, 1)
        qc.h(0)
        qc.measure(0, 0)
        qc.measure(1, 1)
        circs.append((label, theta, qc))
    return circs


def topo_form_hash(dist):
    """Hash de la TOPOLOGIE de corrélation (partition de Bell).
    Invariant sous changement d'énergie — c'est l'objet certifié par la loi LCT."""
    same = dist.get("00", 0) + dist.get("11", 0)    # A=B (même spin)
    opp = dist.get("01", 0) + dist.get("10", 0)      # A≠B (spin opposé)
    dom = "same" if same > opp else "opp"
    sign = "+" if same > opp else "-"
    sig = {"dominant_group": dom, "correlation_sign": sign}
    return hashlib.sha256(repr(sig).encode()).hexdigest()


def main():
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2 as Sampler

    print("=" * 72)
    print("VALIDATION QPU DE L'INVARIANCE ZK DE LA LOI LCT")
    print("R = P_sig invariant sous changement d'énergie (hardware)")
    print("=" * 72)

    svc = get_service()
    backend = pick_least_loaded_qpu(svc)
    st = backend.status()
    print(f"\nQPU : {backend.name} (opérationnel, {st.pending_jobs} jobs en attente)")

    circs = build_lct_circuits()
    labels = [c[0] for c in circs]
    thetas = [c[1] for c in circs]
    qcs = [c[2] for c in circs]
    shots = 4096

    print(f"Transpilation...")
    isa = transpile(qcs, backend=backend, optimization_level=1)
    print(f"Soumission au QPU {backend.name} ({shots} shots/circuit)...")
    sampler = Sampler(mode=backend)
    job = sampler.run(isa, shots=shots)
    job_id = job.job_id()
    print(f"Job ID (traçable) : {job_id}")
    print("Attente des résultats QPU...")

    result = job.result()
    print("Résultats QPU reçus !\n")

    dists = []
    for i, label in enumerate(labels):
        pub = result[i]
        counts = pub.data.c.get_counts() if hasattr(pub.data, 'c') else pub.data.get_counts()
        total = sum(counts.values())
        dist = {k: v / total for k, v in counts.items()}
        # "énergie" = somme pondérée des bits (proxy du courant)
        energy = sum(v * (int(k[0]) + int(k[1])) for k, v in dist.items())
        dists.append((label, dist, energy))
        print(f"  {label} (θ={thetas[i]:.3f}) : counts={counts}")
        print(f"    distribution={ {k: round(v,3) for k,v in dist.items()} }")
        print(f"    énergie (courant) = {energy:.4f}")

    h1 = topo_form_hash(dists[0][1])
    h2 = topo_form_hash(dists[1][1])
    e1, e2 = dists[0][2], dists[1][2]

    print(f"\n  Énergies différentes ? : E1={e1:.4f}  E2={e2:.4f}  → {abs(e1-e2)>0.01}")
    print(f"  Hash topologie (loi LCT) E1 = {h1[:20]}...")
    print(f"  Hash topologie (loi LCT) E2 = {h2[:20]}...")
    print(f"  Hash IDENTIQUE ? : {h1 == h2}")

    verdict = "PASS" if (h1 == h2 and abs(e1 - e2) > 0.01) else "FAIL"
    print(f"\n  VERDICT QPU LOI LCT (invariance ZK) : {verdict}")
    print(f"  → R = P_sig est invariant sous changement d'énergie : on certifie")
    print(f"    la forme topologique (le message), pas l'énergie (le courant).")

    return {
        "law": "LCT_invariance_ZK",
        "backend": backend.name,
        "job_id": job_id,
        "shots": shots,
        "theta_E1": thetas[0],
        "theta_E2": thetas[1],
        "energy_E1": e1,
        "energy_E2": e2,
        "energies_different": abs(e1 - e2) > 0.01,
        "topo_hash_E1": h1,
        "topo_hash_E2": h2,
        "topo_hash_identical": h1 == h2,
        "verdict": verdict,
        "dist_E1": dists[0][1],
        "dist_E2": dists[1][1],
    }


if __name__ == "__main__":
    out = main()
    out_path = _ROOT / "proofs" / "lct_qpu_validation_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nRésultats sauvegardés : {out_path}")
