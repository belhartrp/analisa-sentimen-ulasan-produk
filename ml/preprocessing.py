"""
ml/preprocessing.py  (VERSI PERBAIKAN — GANTI file preprocessing.py lamamu dengan ini)

Pipeline text preprocessing berurutan untuk ulasan Tokopedia:
1. Case folding
2. Cleaning (tanda baca, angka, simbol)
3. Normalisasi slang Tokopedia
4. Tokenization
5. Stopword removal (mempertahankan kata negasi) -> pakai ml/stopwords_custom.py
6. Stemming (Sastrawi)
"""

import re
from functools import lru_cache

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from ml.slang_dict import apply_slang_normalization
from ml.stopwords_custom import NEGATION_WORDS, is_stopword

_stemmer = StemmerFactory().create_stemmer()


def case_folding(text: str) -> str:
    """Ubah seluruh teks menjadi huruf kecil."""
    return text.lower()


def cleaning(text: str) -> str:
    """Hapus URL, mention, angka, tanda baca, dan simbol non-alfabet."""
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+|#\w+", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_slang(text: str) -> str:
    """Ganti istilah slang Tokopedia dengan padanan formalnya."""
    return apply_slang_normalization(text)


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
    """Jalankan seluruh pipeline preprocessing secara berurutan pada satu teks."""
    text = case_folding(raw_text)
    text = cleaning(text)
    text = normalize_slang(text)
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    tokens = stem_tokens(tokens)
    return " ".join(tokens)


def preprocess_batch(texts: list[str]) -> list[str]:
    """Preprocessing untuk banyak teks sekaligus (dipakai untuk upload CSV)."""
    return [preprocess_text(t) for t in texts]
