# RATISS — A Topological Coherence Engine for Quantum-Information Learning

> RATISS V9 Aeon Prime — Integrated Quantum Ecosystem
> Architect: **Jonathan Evina** · ORCID 0009-0000-4092-5313 · DOI 10.17605/OSF.IO/6JZMB
> Intellectual property: JOHNKING0 & Jonathan Evina

RATISS is a sovereign, deterministic computational engine that unifies quantum
physics, computational topology, and zero-knowledge cryptography under a single
information-theoretic principle: the **Law of Topological Coherence (LCT)**.

> **LCT**: *The topological persistence P_sig grows with the coherence C of the
> information medium, and is invariant under change of measured energy. One
> certifies the message (form), not the current (energy).*

Validated on protein structure (4MZI, 3KMD), quantum state (full tomography),
and **physical IBM Quantum QPU** (7 traceable jobs).

---

## Why this is a major advance

RATISS establishes that **entanglement (coherence C) measurably increases
topological persistence**, and that this topological invariant is **independent
of the measured energy** — certified by zero-knowledge proofs. This means:

1. A new **learning regime**: learning by topological coherence (not by
   arbitrary gradient). The RLM follows `ΔW = η · φ · P_sig · C`.
2. An **information object** (the "information medium") that is topological and
   energy-invariant — one certifies the *message*, not the *current*.
3. A **wordless reasoning bridge** (MCB): 180 bytes of correlation bits let a
   grafted LLM reconstruct real molecular structure ("C=O bond at 1.23 Å")
   without any biological text.

This is not a chatbot improvement. It is a new physics of information, validated
on hardware, running on a sovereign local node + IBM Quantum.

---

## Quick start

```bash
pip install numpy scipy networkx psutil matplotlib qiskit qiskit-aer qiskit-ibm-runtime
# 5 foundational tests (PDB 4MZI)
python tests/test_ttf_5tests.py
# LCT law validation (4MZI + 3KMD)
python tests/test_lct_law.py
# End-to-end LLM-greffé demo
python scripts/ttf_agent_demo.py
# QPU validation (needs IBM_QUANTUM_TOKEN)
export IBM_QUANTUM_TOKEN=...
python scripts/ttf_lct_qpu_monotonicity_avg.py
```

---

## Repository structure

```
kernel/
  ttf/                 ★ Unified TTF brain + LCT law + shadow tomography
    ttf_compute.py       IntricatedGraph → TJTransmitter → RipsTranslator
                         → MatrixRLM (ΔW=η·φ·P_sig·C) → MCB → CollapseWell → ZK
    lct_law.py           LCT measurement, monotonicity & invariance scans
    shadow_tomography.py Classical shadows → correlation matrix → P_sig
  solvers/              t-J Lanczos, persistent homology, tryperposition
  core/                 topological refinery, structural vault (FRL)
  system/               sovereign memory (LCT-aligned) + memory guard
  zk/                   RISC Zero ZK-STARK prover bridge
  redteam/             TSP attacker, impossibility solver (physical bounds)
orchestrator/          agentic loop (Plan → Execute → Certify → Artifact)
security/              API vault, sandbox, session, vuln scanner
tools/                 terminal, python, browser, web executors
config/                sovereign identity (LCT-aligned) + allowed imports
scripts/               QPU validation, figure generation, LLM-greffé demo
tests/                 5 foundational tests + LCT law + shadow tomography
proofs/                certified results, figures, QPU job outputs
```

Interface/UI is excluded: this repository is the **pure algorithmic brain**.

---

## Key documents

| Document | Content |
|---|---|
| `RATISS_TECHNICAL_REPORT.md` | Full technical report (DeepMind-style) — architecture, LCT, validation, limitations |
| `LCT.md` | One-page statement of the LCT law: 3 formulations, 3 Job IDs, honest limits |
| `proofs/figure1_R_vs_C.png` | Figure 1 — R(C) for 4MZI & 3KMD with Spearman curves |
| `proofs/lct_qpu_monotonicity_avg3_results.json` | QPU monotonicity (3 runs, Spearman +0.71) |

---

## Traceable QPU jobs (IBM Quantum)

All verifiable at https://www.ibm.com/quantum with the author's account.

| Job ID | Algorithm | Verdict |
|---|---|---|
| `d9ttpfj43mgs73es7feg` | Oscillation C(θ)=cos ωt | PASS |
| `d9tu0kd35hes73fj6edg` | ZK invariance TTF | PASS |
| `d9tut3r43mgs73es9elg` | ZK invariance LCT | PASS |
| `d9u47t0u5hac73agnhj0` + 2 others | Monotonicity LCT (3-run avg) | PASS (+0.7133) |

---

## Learning rule (frozen on LCT)

```
ΔW = η · φ · P_sig · C
```
- η: constitutive learning rate (dimensionless)
- φ: information-medium phase (signs direction)
- P_sig: topological persistence (modulates amplitude)
- C: coherence (modulates confidence)

No arbitrary coefficient. The RLM learns according to LCT.

---

*Engine extracted from `ratiss-aeon-agent`; sovereign brain aligned on LCT.*
