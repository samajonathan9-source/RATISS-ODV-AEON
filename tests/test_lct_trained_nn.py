"""tests/test_lct_trained_nn.py — LCT sur un réseau de neurones ENTRAÎNÉ.

La version précédente (poids aléatoires) donnait Spearman +0.588 (partial).
Ici on entraîne réellement un MLP sur un dataset (classification binaire
synthétique) par backpropagation numpy pur. Les poids entraînés ont une
STRUCTURE (certains deviennent forts, d'autres faibles) → la compression TTF
est plus efficace → la monotonie LCT devrait passer au-dessus de 0.6.

C'est la connexion vers l'AGI : LCT sur un réseau qui a APPRIS, pas juste
aléatoire. Le cerveau LCT pilote l'apprentissage et le certifie.
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


def make_dataset(n=200, seed=42):
    """Dataset binaire synthétique (2 classes, 4 features)."""
    rng = np.random.default_rng(seed)
    # classe 0 : gaussienne centrée
    X0 = rng.normal(-1, 0.8, (n // 2, 4))
    # classe 1 : gaussienne décalée
    X1 = rng.normal(1, 0.8, (n // 2, 4))
    X = np.vstack([X0, X1])
    y = np.array([0] * (n // 2) + [1] * (n // 2))
    # shuffle
    idx = rng.permutation(n)
    return X[idx], y[idx]


def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -50, 50)))


def train_mlp(X, y, n_in=4, n_hidden=10, n_out=1, epochs=500, lr=0.5, seed=42):
    """Entraîne un MLP par backpropagation (numpy pur). Retourne les poids."""
    rng = np.random.default_rng(seed)
    W1 = rng.normal(0, 0.5, (n_in, n_hidden))
    b1 = np.zeros(n_hidden)
    W2 = rng.normal(0, 0.5, (n_hidden, n_out))
    b2 = np.zeros(n_out)
    y_col = y.reshape(-1, 1).astype(float)
    for ep in range(epochs):
        # forward
        z1 = X @ W1 + b1
        a1 = sigmoid(z1)
        z2 = a1 @ W2 + b2
        a2 = sigmoid(z2)
        # loss = BCE
        # backward
        dz2 = a2 - y_col
        dW2 = a1.T @ dz2 / len(X)
        db2 = dz2.mean(axis=0)
        da1 = dz2 @ W2.T
        dz1 = da1 * a1 * (1 - a1)
        dW1 = X.T @ dz1 / len(X)
        db1 = dz1.mean(axis=0)
        W1 -= lr * dW1
        b1 -= lr * db1
        W2 -= lr * dW2
        b2 -= lr * db2
    # accuracy
    pred = (sigmoid(sigmoid(X @ W1 + b1) @ W2 + b2) > 0.5).flatten()
    acc = float(np.mean(pred == y))
    return W1, W2, b1, b2, acc


def weights_to_point_cloud(W1, W2, n_noise=25, seed=7):
    """Transforme les poids entraînés en nuage de points + bruit.

    Chaque neurone = un point (son vecteur de poids). Les neurones de bruit
    (poids faibles aléatoires) simulent le 'solvant' — la compression TTF
    doit les éliminer."""
    n_in, n_hid = W1.shape
    n_hid2, n_out = W2.shape
    coords = []
    # couche entrée : poids vers cachée (n_in vecteurs de dim n_hid)
    for i in range(n_in):
        coords.append(np.asarray(W1[i], dtype=float))
    # couche cachée : poids vers sortie (n_hid vecteurs de dim n_out)
    for j in range(n_hid):
        coords.append(np.asarray(W2[j], dtype=float))
    # couche sortie : poids entrants (n_out vecteurs de dim n_hid)
    for k in range(n_out):
        coords.append(np.asarray(W2[:, k], dtype=float))
    # pad à même dimension (max des dims)
    max_dim = max(c.shape[0] for c in coords)
    coords = np.array([np.pad(c.astype(float), (0, max_dim - len(c))) for c in coords])
    # ajouter bruit
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 0.05, (n_noise, max_dim))
    return np.vstack([coords, noise])


def measure_P_sig(coords, max_edge=2.0):
    diagrams, _ = _persistence_diagrams(coords, max_edge)
    h1 = [d - b for b, d in diagrams.get(1, []) if d != float("inf") and d > b]
    return max(h1) if h1 else 0.0


def compress_by_weights(coords, C, max_q=0.75):
    """Compression TTF : C élevé → garde les neurones aux poids forts."""
    mags = np.linalg.norm(coords, axis=1)
    q = min(max_q, C * max_q)
    threshold = float(np.quantile(mags, q))
    mask = mags >= threshold
    if mask.sum() < 4:
        mask = np.ones(len(coords), dtype=bool)
    return coords[mask], mask


def main():
    print("=" * 72)
    print("LCT SUR RÉSEAU DE NEURONES ENTRAÎNÉ (poids réels, backprop)")
    print("Objectif : pousser Spearman au-dessus de 0.6 (universalité complète)")
    print("=" * 72)

    X, y = make_dataset(n=200, seed=42)
    print(f"Dataset : {len(X)} samples, {X.shape[1]} features, 2 classes")

    W1, W2, b1, b2, acc = train_mlp(X, y, n_in=4, n_hidden=10, n_out=1,
                                     epochs=500, lr=0.5, seed=42)
    print(f"MLP entraîné : 4→10→1, accuracy = {acc:.3f}")

    coords = weights_to_point_cloud(W1, W2, n_noise=25)
    print(f"Nuage : {len(coords)} points (neurones entraînés + bruit)")
    print(f"Magnitude des poids : min={np.linalg.norm(coords,axis=1).min():.3f} "
          f"max={np.linalg.norm(coords,axis=1).max():.3f} "
          f"(structure entraînée → magnitudes variées)")

    # scan R(C)
    print(f"\nScan R(C) :")
    Cs, Ps = [], []
    for i in range(16):
        C = 1.0 - i * 0.95 / 15
        sub, mask = compress_by_weights(coords, C)
        ps = measure_P_sig(sub, max_edge=2.0)
        Cs.append(C)
        Ps.append(ps)
        print(f"  C={C:.3f}  n_kept={int(mask.sum())}  P_sig={ps:.4f}")

    Cs = np.array(Cs)
    Ps = np.array(Ps)
    ra = np.argsort(np.argsort(Cs))
    rb = np.argsort(np.argsort(Ps))
    spearman = float(np.corrcoef(ra, rb)[0, 1])
    pearson = float(np.corrcoef(Cs, Ps)[0, 1]) if Cs.std() > 1e-9 else 0.0

    print(f"\n  Pearson(C, P_sig)  = {pearson:+.4f}")
    print(f"  Spearman(C, P_sig) = {spearman:+.4f}")
    verdict = "PASS" if spearman > 0.6 else "PARTIAL"
    print(f"  VERDICT : {verdict}")
    if verdict == "PASS":
        print("  → LCT sur NN entraîné : UNIVERSALITÉ COMPLÈTE (5 systèmes).")

    return {
        "system": "trained_neural_network",
        "accuracy": acc,
        "n_points": len(coords),
        "C_values": [round(float(c), 4) for c in Cs],
        "P_sig_values": [round(float(p), 4) for p in Ps],
        "corr_pearson": pearson,
        "corr_spearman": spearman,
        "verdict": verdict,
    }


if __name__ == "__main__":
    out = main()
    out_path = _ROOT / "proofs" / "lct_trained_nn_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nRésultats sauvegardés : {out_path}")
