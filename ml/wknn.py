"""
ml/wknn.py  (VERSI UPDATE — GANTI file wknn.py lamamu dengan ini)

TAMBAHAN: parameter `weighted` (default True). Kalau `weighted=False`, semua
tetangga dianggap punya bobot sama (w=1) sehingga model berperilaku seperti
KNN standar (voting mayoritas biasa) -- dipakai khusus untuk perbandingan
KNN vs WKNN di dashboard evaluasi. Konsep dasarnya tetap sama: cosine
distance, cuma bobotnya yang dibedakan.
"""

from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

EPSILON = 1e-5


class WeightedKNNCosine:
    """K-Nearest Neighbor berbasis Cosine Distance.

    weighted=True  -> WKNN (inverse distance weighting, w = 1/(d+eps))
    weighted=False -> KNN standar (semua tetangga berbobot sama, w = 1)
    """

    def __init__(self, k: int = 5, weighted: bool = True):
        if k < 1:
            raise ValueError("Nilai k harus >= 1")
        self.k = k
        self.weighted = weighted
        self.X_train_: csr_matrix | None = None
        self.y_train_: np.ndarray | None = None
        self.classes_: np.ndarray | None = None

    def fit(self, X_train, y_train) -> "WeightedKNNCosine":
        self.X_train_ = csr_matrix(X_train)
        self.y_train_ = np.asarray(y_train)
        self.classes_ = np.unique(self.y_train_)
        return self

    def _cosine_distance(self, X_query) -> np.ndarray:
        similarity = cosine_similarity(X_query, self.X_train_)
        distance = 1.0 - similarity
        return np.clip(distance, 0.0, 2.0)

    def _predict_one(self, distances_row: np.ndarray) -> tuple[str, dict]:
        k = min(self.k, len(distances_row))
        neighbor_idx = np.argsort(distances_row)[:k]
        neighbor_dist = distances_row[neighbor_idx]
        neighbor_labels = self.y_train_[neighbor_idx]

        if self.weighted:
            weights = 1.0 / (neighbor_dist + EPSILON)
        else:
            weights = np.ones_like(neighbor_dist)  # KNN standar: bobot sama rata

        vote_scores: dict[str, float] = {c: 0.0 for c in self.classes_}
        for label, weight in zip(neighbor_labels, weights):
            vote_scores[label] += weight

        predicted_label = max(vote_scores, key=vote_scores.get)
        total_weight = sum(vote_scores.values())
        confidence = (vote_scores[predicted_label] / total_weight * 100) if total_weight > 0 else 0.0

        detail = {
            "neighbor_labels": neighbor_labels.tolist(),
            "neighbor_distances": neighbor_dist.tolist(),
            "weights": weights.tolist(),
            "vote_scores": vote_scores,
            "confidence_score": round(float(confidence), 2),
        }
        return predicted_label, detail

    def predict(self, X_query) -> np.ndarray:
        if self.X_train_ is None:
            raise RuntimeError("Model belum di-fit. Panggil fit() terlebih dahulu.")
        distances = self._cosine_distance(csr_matrix(X_query))
        predictions = [self._predict_one(row)[0] for row in distances]
        return np.array(predictions)

    def predict_with_detail(self, X_query) -> list[dict]:
        """Prediksi + rincian tetangga, bobot, dan confidence score (untuk Explainable AI)."""
        distances = self._cosine_distance(csr_matrix(X_query))
        results = []
        for row in distances:
            label, detail = self._predict_one(row)
            detail["prediction"] = label
            results.append(detail)
        return results

    def get_params(self, deep: bool = True) -> dict:
        return {"k": self.k, "weighted": self.weighted}

    def set_params(self, **params) -> "WeightedKNNCosine":
        for key, value in params.items():
            setattr(self, key, value)
        return self
