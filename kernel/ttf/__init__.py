"""kernel.ttf — Tryperposition Topologique Fine (TTF) Compute engine.

Cerveau unifié implémentant la théorie TTF du chercheur Jonathan Evina :
  - H_TTF = H_tJ ⊗ I_Geni + I_Q ⊗ H_Geni + λ(t)·Φ
  - Milieu « géni » informationnel = oscillateur harmonique de phase θ(t)=cos(ωt)
  - Compression topologique Φ = ∇S·∇T·θ(t), coupleur oscillant λ(t)=±cos(ωt)
  - Puits d'effondrement relativiste V_puits = -k/(1+d_topo²) + TSP minimal
  - Mémoire Corrélation Bit (MCB) : triplets (source, cible, φ) — pensée sans mots

Réutilise les briques existantes du noyau RATISS :
  kernel.solvers.quantum_solver (t-J Lanczos), kernel.solvers.topo_solver (Betti),
  kernel.core.structural_vault (mémoire structurelle graphique), kernel.zk.prover_bridge (ZK).
"""
from kernel.ttf.ttf_compute import (
    TTFBrain,
    IntricatedGraph,
    TJTransmitter,
    RipsTranslator,
    MatrixRLM,
    CorrelationBitMemory,
    CollapseWell,
)

__all__ = [
    "TTFBrain",
    "IntricatedGraph",
    "TJTransmitter",
    "RipsTranslator",
    "MatrixRLM",
    "CorrelationBitMemory",
    "CollapseWell",
]
