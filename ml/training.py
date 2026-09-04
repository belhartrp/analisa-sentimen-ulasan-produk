"""
ml/training.py
Mode 2: Custom Training — pengguna mengunggah CSV berlabel sendiri.
Alur: preprocessing -> random undersampling -> fit_transform TF-IDF ->
      train_test_split -> train WKNN(k) -> evaluate.

Catatan arsitektur (Vercel serverless):
Training dan evaluasi dilakukan dalam SATU request/response yang sama karena
instance function tidak persisten antar request. Model hasil training tidak
disimpan di memori server; jika ingin dipakai lagi, hasilnya (vectorizer +
model) dikembalikan ke client sebagai referensi atau disimpan ke Supabase
Storage lewat endpoint terpisah (lihat app.py -> /api/save-model).
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
    """Ubah confusion matrix menjadi struktur JSON siap dipakai Chart.js."""
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    return {"labels": labels, "matrix": cm.tolist()}


def train_and_evaluate(
    df: pd.DataFrame,
    text_col: str,
    label_col: str,
    k: int = 5,
    test_size: float = 0.2,
    max_features: int = 5000,
    random_state: int = 42,
) -> dict:
    """Jalankan pipeline lengkap Mode 2 dan kembalikan metrik + hasil prediksi.

    Return dict berisi: metrics, confusion_matrix, class_balance_before/after,
    preview_rows (raw vs clean text), dan prediction_table.
    """
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
    ]  # dibatasi 50 baris untuk payload halaman preprocessing

    vectorizer = TfidfVectorizer(max_features=max_features)
    X = vectorizer.fit_transform(clean_texts)
    y = np.array(labels)

    X_train, X_test, y_train, y_test, raw_train, raw_test = train_test_split(
        X, y, raw_texts_paired(clean_texts, raw_texts),
        test_size=test_size, random_state=random_state, stratify=y
    ) if False else _manual_split(X, y, raw_texts, clean_texts, test_size, random_state)

    model = WeightedKNNCosine(k=k)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    unique_labels = sorted(np.unique(y).tolist())
    pos_label = unique_labels[-1]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "k": k,
    }

    cm_payload = build_confusion_matrix_payload(y_test.tolist(), y_pred.tolist(), unique_labels)

    prediction_table = [
        {"raw_text": raw, "actual": actual, "predicted": pred}
        for raw, actual, pred in zip(raw_test, y_test.tolist(), y_pred.tolist())
    ]

    return {
        "class_balance_before": class_balance_before,
        "class_balance_after": class_balance_after,
        "preview_rows": preview_rows,
        "metrics": metrics,
        "confusion_matrix": cm_payload,
        "prediction_table": prediction_table,
        "vectorizer": vectorizer,
        "model": model,
    }


def raw_texts_paired(clean_texts, raw_texts):
    return list(zip(raw_texts, clean_texts))


def _manual_split(X, y, raw_texts, clean_texts, test_size, random_state):
    """Split X, y, dan raw_texts secara konsisten berdasarkan index yang sama."""
    indices = np.arange(len(y))
    idx_train, idx_test = train_test_split(
        indices, test_size=test_size, random_state=random_state, stratify=y
    )
    X_train, X_test = X[idx_train], X[idx_test]
    y_train, y_test = y[idx_train], y[idx_test]
    raw_train = [raw_texts[i] for i in idx_train]
    raw_test = [raw_texts[i] for i in idx_test]
    return X_train, X_test, y_train, y_test, raw_train, raw_test
