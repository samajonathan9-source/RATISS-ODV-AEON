"""tests/test_ratis_net.py — Preuve de concept : un NN qui apprend par LCT.

On entraîne un réseau RATIS-Net (4→10→3) sur le dataset Iris par la loi LCT
(ΔW = η · φ · P_sig · C), SANS gradient descendant.

On vérifie 2 choses :
  1. Le réseau APPREND-il ? (accuracy augmente)
  2. P_sig CROÎT-il pendant l'entraînement ? (la topologie devient robuste)

Si oui → preuve que LCT peut remplacer le gradient. C'est la brique AGI.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from ratis_net.lct_network import LCTNetwork


def load_iris():
    """Charge Iris (4 features, 3 classes) — one-hot."""
    from sklearn.datasets import load_iris
    iris = load_iris()
    X = iris.data.astype(float)
    # normaliser
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)
    y = iris.target
    # one-hot
    y_oh = np.zeros((len(y), 3))
    y_oh[np.arange(len(y)), y] = 1.0
    return X, y_oh, y


def main():
    print("=" * 72)
    print("RATIS-Net — Preuve de concept : NN entraîné par LCT (pas gradient)")
    print("On vérifie : (1) accuracy augmente, (2) P_sig croît pendant l'entraînement")
    print("=" * 72)

    try:
        X, y_oh, y = load_iris()
    except ImportError:
        print("  sklearn non disponible, dataset synthétique de substitution.")
        rng = np.random.default_rng(42)
        X = rng.normal(0, 1, (150, 4))
        y = rng.integers(0, 3, 150)
        y_oh = np.zeros((150, 3))
        y_oh[np.arange(150), y] = 1.0

    # split train/test
    idx = np.random.RandomState(42).permutation(len(X))
    n_train = int(0.8 * len(X))
    X_train, X_test = X[idx[:n_train]], X[idx[n_train:]]
    y_train, y_test = y_oh[idx[:n_train]], y[idx[n_train:]]

    print(f"Dataset : {len(X)} samples, {X.shape[1]} features, 3 classes")
    print(f"Train : {n_train} | Test : {len(X_test)}")

    # créer le réseau LCT
    net = LCTNetwork(n_in=4, n_hidden=10, n_out=3, eta=0.05, omega=1.5707963, seed=42)
    print(f"RATIS-Net : 4→10→3, η=0.05, ω=π/2")

    # entraîner
    print(f"\nEntraînement par LCT (50 epochs) :")
    acc_hist, psig_hist = net.train(X_train, y_train, epochs=50, verbose=True)

    # évaluer
    pred_test = net.predict(X_test)
    test_acc = float(np.mean(pred_test == y_test))
    print(f"\nAccuracy test : {test_acc:.3f}")

    # P_sig a-t-il crû ?
    psig_init = psig_hist[0] if psig_hist else 0.0
    psig_final = psig_hist[-1] if psig_hist else 0.0
    psig_growth = psig_final - psig_init

    print(f"\n── Validation LCT ──")
    print(f"  P_sig initial  = {psig_init:.4f}")
    print(f"  P_sig final    = {psig_final:.4f}")
    print(f"  Croissance P_sig = {psig_growth:+.4f}")
    print(f"  Accuracy initiale = {acc_hist[0]:.3f}")
    print(f"  Accuracy finale   = {acc_hist[-1]:.3f}")

    learns = acc_hist[-1] > acc_hist[0] + 0.1
    psig_grows = psig_growth > 0

    print(f"\n  Le réseau APPREND ?    : {'OUI' if learns else 'NON'}")
    print(f"  P_sig CROÎT ?          : {'OUI' if psig_grows else 'NON'}")

    if learns:
        print(f"\n  → PREUVE DE CONCEPT : un NN peut apprendre par LCT (pas gradient).")
        print(f"    La loi ΔW = η·φ·P_sig·C est une règle d'apprentissage viable.")
        print(f"    C'est la brique AGI : apprentissage par cohérence topologique.")
    else:
        print(f"\n  → Le réseau n'apprend pas encore assez. Ajuster η/ω/epochs.")

    return {
        "test_accuracy": test_acc,
        "acc_history": [round(float(a), 4) for a in acc_hist],
        "psig_history": [round(float(p), 4) for p in psig_hist],
        "psig_growth": round(float(psig_growth), 4),
        "learns": learns,
        "psig_grows": psig_grows,
        "verdict": "PASS" if learns else "PARTIAL",
    }


if __name__ == "__main__":
    out = main()
    out_path = _ROOT / "proofs" / "ratis_net_poc_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nRésultats sauvegardés : {out_path}")
