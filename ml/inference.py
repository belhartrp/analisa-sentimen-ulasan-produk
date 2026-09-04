"""
ml/inference.py
Mode 1: Prediksi Instan menggunakan model pre-trained (offline).
Hanya melakukan transform() TF-IDF (bukan fit_transform), lalu predict().
"""

from ml.preprocessing import preprocess_batch, preprocess_text
from ml.utils import load_pretrained_artifacts, to_native

_vectorizer = None
_model = None


def _get_artifacts():
    """Lazy-load model sekali per cold start (di-cache di level modul)."""
    global _vectorizer, _model
    if _vectorizer is None or _model is None:
        _vectorizer, _model = load_pretrained_artifacts()
    return _vectorizer, _model


def predict_single(raw_text: str) -> dict:
    """Prediksi sentimen untuk satu kalimat ulasan (dipakai textarea manual)."""
    vectorizer, model = _get_artifacts()
    clean_text = preprocess_text(raw_text)
    X = vectorizer.transform([clean_text])
    detail = model.predict_with_detail(X)[0]
    return {
        "raw_text": raw_text,
        "clean_text": clean_text,
        "prediction": detail["prediction"],
        "confidence_detail": {
            "neighbor_labels": detail["neighbor_labels"],
            "neighbor_distances": [round(d, 4) for d in detail["neighbor_distances"]],
            "vote_scores": {k: round(to_native(v), 4) for k, v in detail["vote_scores"].items()},
        },
    }


def predict_batch(raw_texts: list[str]) -> dict:
    """Prediksi sentimen untuk banyak ulasan sekaligus (dipakai untuk upload CSV Mode 1)."""
    vectorizer, model = _get_artifacts()
    clean_texts = preprocess_batch(raw_texts)
    X = vectorizer.transform(clean_texts)
    predictions = model.predict(X)

    rows = [
        {
            "raw_text": raw,
            "clean_text": clean,
            "prediction": str(pred),
        }
        for raw, clean, pred in zip(raw_texts, clean_texts, predictions)
    ]
    return {"rows": rows, "total": len(rows)}
