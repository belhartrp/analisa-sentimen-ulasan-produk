"""
ml/utils.py
Helper untuk load/save pickle model dan konversi hasil ke format JSON-friendly.
"""

import pickle
from pathlib import Path

import numpy as np

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"
MODEL_PATH = MODELS_DIR / "wknn_model.pkl"


def load_pickle(path: Path):
    """Muat objek pickle dari path. Raise error jelas jika file belum ada."""
    if not path.exists():
        raise FileNotFoundError(
            f"File model '{path.name}' tidak ditemukan di {path}. "
            "Pastikan sudah menjalankan training offline dan menaruh file .pkl di folder models/."
        )
    with open(path, "rb") as f:
        return pickle.load(f)


def save_pickle(obj, path: Path) -> None:
    """Simpan objek Python ke file pickle."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def load_pretrained_artifacts():
    """Muat TF-IDF vectorizer dan model WKNN pre-trained untuk Mode 1."""
    vectorizer = load_pickle(VECTORIZER_PATH)
    model = load_pickle(MODEL_PATH)
    return vectorizer, model


def to_native(value):
    """Konversi tipe numpy ke tipe Python native agar bisa di-JSON-kan."""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value
