# RATISS-ODV-AEON — Moteur algorithmique

Dépôt du **cerveau / moteur algorithmique** extrait de `ratiss-aeon-agent`.

Ce dépôt ne contient **que la logique moteur** (pas d'interface, pas d'écran, pas d'assets visuels).

## Structure du moteur

- `kernel/` — noyau RATISS V9 Aeon Prime
  - `core/` — raffinerie topologique + structural vault
  - `solvers/` — solveurs quantique, topologique, tryperposition
  - `redteam/` — circuit LB, solveur d'impossibilité, preuves naturelles, attaques TSP
  - `system/` — Memory Guard + mémoire souveraine persistante
  - `zk/` — pont de preuve ZK-STARK (RISC Zero, Rust + Python bridge)
  - `connectors/` — clients IBM Quantum, Quandela, intégrations, registre
  - `bridge.py` — pont unifié orchestrateur ↔ noyau
  - `main.py` — orchestrateur séquentiel du pipeline
- `orchestrator/` — agent scientifique autonome (Plan → Execute → Certify → Artifacts)
  - cascade, auto-improve, harness manager, LLM router, Nemotron client,
    skill manager, extracteur de skills, planificateur topologique
- `security/` — coffre API, durcisseur de sandbox, gestionnaire de session,
  hasher de tokens, sécurité transdisc, vuln auth/scanner, isolateur de workspace
- `tools/` — outils exécutables du moteur (terminal, python, browser, web, fichiers…)
- `proofs/` — preuves et scripts de test agentique / émergence FRL + runs
- `config/` — identité souveraine + imports autorisés
- `scripts/` — alignement agent, initialisation coffre, import de skills
- `tests/` — tests du moteur
- `audits/generate_report_pdf.py` — générateur de rapports d'audit

## Exclusion

Tout ce qui est interface/écran a été retiré : `app/frontend`, `app/static`,
`assets/`, `screenshots/`, serveur FastAPI de présentation.

---

Extraction du moteur effectuée depuis `evinajonathan13-max/ratiss-aeon-agent`.
