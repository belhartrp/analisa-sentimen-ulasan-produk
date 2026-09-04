"""
ml/wknn.py
Implementasi Weighted K-Nearest Neighbor (WKNN) dengan Cosine Distance,
dibangun mengikuti kontrak estimator scikit-learn (fit/predict) agar mudah
di-pickle dan dipakai ulang di mode inferensi maupun training.

Jarak     : d(x, y) = 1 - cosine_similarity(x, y)
Bobot     : w_i = 1 / (d_i + epsilon)      -> tetangga lebih dekat = lebih berpengaruh
Epsilon   : 1e-5, untuk menghindari pembagian dengan nol saat d_i = 0
Prediksi  : kelas dengan total bobot tertinggi di antara K tetangga terdekat
"""

from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

EPSILON = 1e-5


class WeightedKNNCosine:
    """K-Nearest Neighbor dengan pembobotan inverse-distance berbasis Cosine Distance."""

    def __init__(self, k: int = 5):
        if k < 1:
            raise ValueError("Nilai k harus >= 1")
        self.k = k
        self.X_train_: csr_matrix | None = None
        self.y_train_: np.ndarray | None = None
        self.classes_: np.ndarray | None = None

    def fit(self, X_train, y_train) -> "WeightedKNNCosine":
        """Simpan data latih (TF-IDF matrix) dan label. WKNN adalah lazy learner."""
        self.X_train_ = csr_matrix(X_train)
        self.y_train_ = np.asarray(y_train)
        self.classes_ = np.unique(self.y_train_)
        return self

    def _cosine_distance(self, X_query) -> np.ndarray:
        """Hitung matriks jarak (1 - cosine similarity) antara query dan data latih."""
        similarity = cosine_similarity(X_query, self.X_train_)
        distance = 1.0 - similarity
        return np.clip(distance, 0.0, 2.0)

    def _predict_one(self, distances_row: np.ndarray) -> tuple[str, dict]:
        """Prediksi label untuk satu baris jarak, kembalikan juga rincian voting."""
        k = min(self.k, len(distances_row))
        neighbor_idx = np.argsort(distances_row)[:k]
        neighbor_dist = distances_row[neighbor_idx]
        neighbor_labels = self.y_train_[neighbor_idx]

        weights = 1.0 / (neighbor_dist + EPSILON)

        vote_scores: dict[str, float] = {c: 0.0 for c in self.classes_}
        for label, weight in zip(neighbor_labels, weights):
            vote_scores[label] += weight

        predicted_label = max(vote_scores, key=vote_scores.get)
        detail = {
            "neighbor_labels": neighbor_labels.tolist(),
            "neighbor_distances": neighbor_dist.tolist(),
            "weights": weights.tolist(),
            "vote_scores": vote_scores,
        }
        return predicted_label, detail

    def predict(self, X_query) -> np.ndarray:
        """Prediksi label untuk banyak sampel sekaligus."""
        if self.X_train_ is None:
            raise RuntimeError("Model belum di-fit. Panggil fit() terlebih dahulu.")
        distances = self._cosine_distance(csr_matrix(X_query))
        predictions = [self._predict_one(row)[0] for row in distances]
        return np.array(predictions)

    def predict_with_detail(self, X_query) -> list[dict]:
        """Prediksi sekaligus mengembalikan rincian tetangga & bobot (untuk transparansi UI)."""
        distances = self._cosine_distance(csr_matrix(X_query))
        results = []
        for row in distances:
            label, detail = self._predict_one(row)
            detail["prediction"] = label
            results.append(detail)
        return results

    def get_params(self, deep: bool = True) -> dict:
        return {"k": self.k}

    def set_params(self, **params) -> "WeightedKNNCosine":
        for key, value in params.items():
            setattr(self, key, value)
        return self
