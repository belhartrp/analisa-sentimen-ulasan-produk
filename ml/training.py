"""
ml/training.py  (VERSI UPDATE — GANTI file training.py lamamu dengan ini)

TAMBAHAN dari versi sebelumnya:
1. compare_knn_vs_wknn()   -> latih KNN standar & WKNN di data yang sama, untuk grafik komparasi.
2. compute_k_curve()       -> latih WKNN dengan beberapa nilai K (3,5,7,9,11), untuk grafik kurva K.
3. extract_top_keywords()  -> ambil 10 kata dengan skor TF-IDF tertinggi per kelas sentimen.
4. train_and_evaluate() sekarang juga mengembalikan confidence_score per prediksi,
   comparison_chart, k_curve_chart, dan top_keywords.
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

from ml.preprocessing import preprocess_batch
from ml.wknn import WeightedKNNCosine

DEFAULT_K_RANGE = [3, 5, 7, 9, 11]


def random_undersample(df: pd.DataFrame, label_col: str, random_state: int = 42) -> pd.DataFrame:
    """Seimbangkan jumlah data tiap kelas dengan mengambil sampel acak
    sebanyak jumlah kelas minoritas (Random Undersampling)."""
    class_counts = df[label_col].value_counts()
    minority_count = class_counts.min()

    balanced_parts = [
        df[df[label_col] == label].sample(n=minority_count, random_state=random_state)
        for label in class_counts.index
    ]
    balanced_df = pd.concat(balanced_parts, axis=0)
    return shuffle(balanced_df, random_state=random_state).reset_index(drop=True)


def build_confusion_matrix_payload(y_true, y_pred, labels: list[str]) -> dict:
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    return {"labels": labels, "matrix": cm.tolist()}


def _split_with_raw_text(X, y, raw_texts, test_size, random_state):
    indices = np.arange(len(y))
    idx_train, idx_test = train_test_split(
        indices, test_size=test_size, random_state=random_state, stratify=y
    )
    X_train, X_test = X[idx_train], X[idx_test]
    y_train, y_test = y[idx_train], y[idx_test]
    raw_train = [raw_texts[i] for i in idx_train]
    raw_test = [raw_texts[i] for i in idx_test]
    return X_train, X_test, y_train, y_test, raw_train, raw_test


def _compute_metrics(y_test, y_pred) -> dict:
    return {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
    }


def compare_knn_vs_wknn(X_train, y_train, X_test, y_test, k: int) -> dict:
    """Latih KNN standar (weighted=False) dan WKNN (weighted=True) pada data
    yang sama, kembalikan metrik keduanya untuk grafik perbandingan."""
    knn = WeightedKNNCosine(k=k, weighted=False)
    knn.fit(X_train, y_train)
    knn_pred = knn.predict(X_test)
    knn_metrics = _compute_metrics(y_test, knn_pred)

    wknn = WeightedKNNCosine(k=k, weighted=True)
    wknn.fit(X_train, y_train)
    wknn_pred = wknn.predict(X_test)
    wknn_metrics = _compute_metrics(y_test, wknn_pred)

    return {
        "labels": ["Akurasi", "Presisi", "Recall", "F1-Score"],
        "knn": [knn_metrics["accuracy"], knn_metrics["precision"], knn_metrics["recall"], knn_metrics["f1_score"]],
        "wknn": [wknn_metrics["accuracy"], wknn_metrics["precision"], wknn_metrics["recall"], wknn_metrics["f1_score"]],
    }


def compute_k_curve(X_train, y_train, X_test, y_test, k_range: list[int] = None) -> dict:
    """Latih WKNN dengan beberapa nilai K berbeda, kembalikan akurasi masing-masing
    untuk grafik kurva performa K (line chart)."""
    k_range = k_range or DEFAULT_K_RANGE
    accuracies = []
    for k in k_range:
        model = WeightedKNNCosine(k=k, weighted=True)
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        accuracies.append(round(float(accuracy_score(y_test, pred)), 4))
    return {"k_values": k_range, "accuracies": accuracies}


def extract_top_keywords(clean_texts: list[str], labels: list[str], top_n: int = 10) -> dict:
    """Ambil top-N kata dengan skor TF-IDF rata-rata tertinggi untuk masing-masing
    kelas sentimen. Berguna untuk insight bisnis (pain points / keunggulan produk)."""
    result = {}
    for label in sorted(set(labels)):
        texts_for_label = [t for t, l in zip(clean_texts, labels) if l == label]
        if not texts_for_label:
            result[label] = []
            continue

        vectorizer = TfidfVectorizer(max_features=2000)
        try:
            tfidf_matrix = vectorizer.fit_transform(texts_for_label)
        except ValueError:
            result[label] = []
            continue

        mean_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
        feature_names = vectorizer.get_feature_names_out()
        top_indices = mean_scores.argsort()[::-1][:top_n]

        result[label] = [
            {"word": feature_names[i], "score": round(float(mean_scores[i]), 4)}
            for i in top_indices
        ]
    return result


def train_and_evaluate(
    df: pd.DataFrame,
    text_col: str,
    label_col: str,
    k: int = 5,
    test_size: float = 0.2,
    max_features: int = 5000,
    random_state: int = 42,
    include_comparison: bool = True,
    include_k_curve: bool = True,
) -> dict:
    """Jalankan pipeline lengkap Mode 2: preprocessing, undersampling, TF-IDF,
    training WKNN, evaluasi, plus fitur pembuktian (komparasi KNN vs WKNN,
    kurva K) dan insight bisnis (top keywords, confidence score)."""
    df = df[[text_col, label_col]].dropna().reset_index(drop=True)
    df.columns = ["text", "label"]

    class_balance_before = df["label"].value_counts().to_dict()

    balanced_df = random_undersample(df, label_col="label", random_state=random_state)
    class_balance_after = balanced_df["label"].value_counts().to_dict()

    raw_texts = balanced_df["text"].astype(str).tolist()
    clean_texts = preprocess_batch(raw_texts)
    labels = balanced_df["label"].astype(str).tolist()

    preview_rows = [
        {"raw_text": r, "clean_text": c, "label": l}
        for r, c, l in zip(raw_texts[:50], clean_texts[:50], labels[:50])
    ]

    vectorizer = TfidfVectorizer(max_features=max_features)
    X = vectorizer.fit_transform(clean_texts)
    y = np.array(labels)

    X_train, X_test, y_train, y_test, raw_train, raw_test = _split_with_raw_text(
        X, y, raw_texts, test_size, random_state
    )

    model = WeightedKNNCosine(k=k, weighted=True)
    model.fit(X_train, y_train)

    detail_list = model.predict_with_detail(X_test)
    y_pred = np.array([d["prediction"] for d in detail_list])
    confidence_scores = [d["confidence_score"] for d in detail_list]

    unique_labels = sorted(np.unique(y).tolist())
    metrics = _compute_metrics(y_test, y_pred)
    metrics["k"] = k

    cm_payload = build_confusion_matrix_payload(y_test.tolist(), y_pred.tolist(), unique_labels)

    prediction_table = [
        {"raw_text": raw, "actual": actual, "predicted": pred, "confidence": conf}
        for raw, actual, pred, conf in zip(raw_test, y_test.tolist(), y_pred.tolist(), confidence_scores)
    ]

    result = {
        "class_balance_before": class_balance_before,
        "class_balance_after": class_balance_after,
        "preview_rows": preview_rows,
        "metrics": metrics,
        "confusion_matrix": cm_payload,
        "prediction_table": prediction_table,
        "top_keywords": extract_top_keywords(clean_texts, labels, top_n=10),
        "vectorizer": vectorizer,
        "model": model,
    }

    if include_comparison:
        result["comparison_chart"] = compare_knn_vs_wknn(X_train, y_train, X_test, y_test, k=k)

    if include_k_curve:
        result["k_curve_chart"] = compute_k_curve(X_train, y_train, X_test, y_test)

    return result
