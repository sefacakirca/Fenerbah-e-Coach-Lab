"""Etiketsiz, keşifsel profil analizi. Küme numarası kalite sırası değildir."""
from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from .data import CRITERIA
from .scoring import Candidate, feature_matrix


def profile_candidates(candidates: list[Candidate], seed: int = 42) -> dict:
    features = feature_matrix(candidates)
    # Z-skorları yalnızca benzerlik analizi için; karar puanı sabit ölçek kullanır.
    scaled = StandardScaler().fit_transform(features)
    trials = []
    best = None
    unique_rows = np.unique(scaled, axis=0).shape[0]
    with threadpool_limits(limits=1):
        for k in range(2, min(4, len(candidates) - 1, unique_rows) + 1):
            labels = KMeans(n_clusters=k, n_init=30, random_state=seed).fit_predict(scaled)
            counts = np.bincount(labels, minlength=k)
            # Sekiz adayda tek kişilik kümeye güçlü bir profil yorumu yüklemiyoruz.
            if counts.min() < 2:
                trials.append({"k": k, "accepted": False, "reason": "singleton cluster", "silhouette": None})
                continue
            score = float(silhouette_score(scaled, labels))
            trials.append({"k": k, "accepted": True, "silhouette": score})
            if best is None or score > best["silhouette"]:
                best = {"k": k, "silhouette": score, "labels": labels}
        if np.allclose(scaled, 0):
            coordinates = np.zeros((len(candidates), 2))
            variance = [0.0, 0.0]
        else:
            pca = PCA(n_components=2, svd_solver="full")
            coordinates = pca.fit_transform(scaled)
            variance = np.nan_to_num(pca.explained_variance_ratio_, nan=0.0).tolist()
    if best is None:
        best = {"k": 1, "silhouette": None, "labels": np.zeros(len(candidates), dtype=int)}
    labels = best.pop("labels")
    centroids = []
    for label in range(best["k"]):
        mean = features[labels == label].mean(axis=0)
        centroids.append({"cluster": label, "size": int((labels == label).sum()),
                          **{key: float(mean[j]) for j, key in enumerate(CRITERIA)}})
    return {
        **best, "seed": seed, "trials": trials, "centroids_unit_scale": centroids,
        "pca_explained_variance_ratio": variance,
        "note": "Sekiz aday ve editoryal girdiler; kümeler başarı etiketi değildir. PCA yalnızca görünüm/keşif içindir.",
        "profiles": [{"coach_id": c.coach_id, "name": c.name, "cluster": int(labels[i]),
                      "pca_1": float(coordinates[i, 0]), "pca_2": float(coordinates[i, 1])}
                     for i, c in enumerate(candidates)],
    }
