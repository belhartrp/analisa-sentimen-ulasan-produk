"""
ml/preprocessing.py  (VERSI PERBAIKAN KE-2 — GANTI file preprocessing.py lamamu dengan ini)

PERBAIKAN: urutan cleaning dan normalisasi slang ditukar. Sebelumnya cleaning
(hapus angka & tanda baca) dijalankan SEBELUM normalisasi slang, sehingga
frasa seperti "bintang 1" tidak pernah bisa terdeteksi (angkanya keburu
hilang). Sekarang urutannya: case folding -> normalisasi slang (saat tanda
baca/angka masih ada) -> cleaning -> tokenization -> stopword removal -> stemming.
"""

import re
from functools import lru_cache

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from ml.slang_dict import apply_slang_normalization
from ml.stopwords_custom import is_stopword

_stemmer = StemmerFactory().create_stemmer()


def case_folding(text: str) -> str:
    """Ubah seluruh teks menjadi huruf kecil."""
    return text.lower()


def normalize_slang(text: str) -> str:
    """Ganti istilah slang Tokopedia dengan padanan formalnya.
    Dilakukan SEBELUM cleaning supaya frasa yang mengandung angka
    (mis. "bintang 1") masih bisa terdeteksi."""
    return apply_slang_normalization(text)


def cleaning(text: str) -> str:
    """Hapus URL, mention, angka, tanda baca, dan simbol non-alfabet."""
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+|#\w+", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    """Pecah teks menjadi daftar token/kata."""
    return text.split()


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Buang stopword umum, TAPI pertahankan kata negasi."""
    return [token for token in tokens if not is_stopword(token)]


@lru_cache(maxsize=20000)
def _stem_word(word: str) -> str:
    return _stemmer.stem(word)


def stem_tokens(tokens: list[str]) -> list[str]:
    """Lakukan stemming bahasa Indonesia menggunakan Sastrawi (dengan cache)."""
    return [_stem_word(token) for token in tokens]


def preprocess_text(raw_text: str) -> str:
    """Jalankan seluruh pipeline preprocessing secara berurutan pada satu teks.

    Urutan BENAR: case folding -> normalisasi slang -> cleaning ->
    tokenization -> stopword removal -> stemming.
    """
    text = case_folding(raw_text)
    text = normalize_slang(text)
    text = cleaning(text)
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    tokens = stem_tokens(tokens)
    return " ".join(tokens)


def preprocess_batch(texts: list[str]) -> list[str]:
    """Preprocessing untuk banyak teks sekaligus (dipakai untuk upload CSV)."""
    return [preprocess_text(t) for t in texts]
