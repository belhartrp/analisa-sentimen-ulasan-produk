"""
ml/inference.py  (VERSI UPDATE — GANTI file inference.py lamamu dengan ini)

TAMBAHAN: predict_single() sekarang mengembalikan `neighbors` (daftar lengkap
teks tetangga tidak tersedia karena Mode 1 tidak menyimpan teks asli data
latih, hanya TF-IDF-nya) beserta jarak, bobot, dan confidence_score --
untuk fitur Explainable AI di halaman uji kalimat manual.
"""

from ml.preprocessing import preprocess_batch, preprocess_text
from ml.utils import load_pretrained_artifacts, to_native

_vectorizer = None
_model = None


def _get_artifacts():
    global _vectorizer, _model
    if _vectorizer is None or _model is None:
        _vectorizer, _model = load_pretrained_artifacts()
    return _vectorizer, _model


def predict_single(raw_text: str) -> dict:
    """Prediksi sentimen untuk satu kalimat ulasan, lengkap dengan rincian
    Explainable AI (tetangga, jarak, bobot, confidence score)."""
    vectorizer, model = _get_artifacts()
    clean_text = preprocess_text(raw_text)
    X = vectorizer.transform([clean_text])
    detail = model.predict_with_detail(X)[0]

    neighbors = [
        {
            "label": label,
            "distance": round(dist, 4),
            "weight": round(weight, 4),
        }
        for label, dist, weight in zip(
            detail["neighbor_labels"], detail["neighbor_distances"], detail["weights"]
        )
    ]

    return {
        "raw_text": raw_text,
        "clean_text": clean_text,
        "prediction": detail["prediction"],
        "confidence_score": detail["confidence_score"],
        "neighbors": neighbors,
        "vote_scores": {k: round(to_native(v), 4) for k, v in detail["vote_scores"].items()},
    }


def predict_batch(raw_texts: list[str]) -> dict:
    """Prediksi sentimen untuk banyak ulasan sekaligus, dengan confidence score per baris."""
    vectorizer, model = _get_artifacts()
    clean_texts = preprocess_batch(raw_texts)
    X = vectorizer.transform(clean_texts)
    detail_list = model.predict_with_detail(X)

    rows = [
        {
            "raw_text": raw,
            "clean_text": clean,
            "prediction": detail["prediction"],
            "confidence_score": detail["confidence_score"],
        }
        for raw, clean, detail in zip(raw_texts, clean_texts, detail_list)
    ]
    return {"rows": rows, "total": len(rows)}
