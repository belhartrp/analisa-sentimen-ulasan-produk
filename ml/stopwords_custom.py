"""
ml/stopwords_custom.py
Daftar stopword bahasa Indonesia yang dipakai untuk membersihkan ulasan,
TAPI kata negasi (tidak, bukan, dst) SENGAJA tidak dibuang karena bisa
membalik arti kalimat (mis. "tidak bagus" beda arti dengan "bagus").

Modul ini dipisah dari preprocessing.py supaya lebih mudah di-edit sendiri
kalau nanti kamu mau menambah/mengurangi kata yang dianggap "stopword".
"""

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# Kata negasi yang WAJIB dipertahankan (jangan dibuang saat stopword removal)
NEGATION_WORDS = {"tidak", "bukan", "tak", "jangan", "belum", "kurang"}

# Ambil daftar stopword bawaan Sastrawi, lalu keluarkan kata negasi dari daftar itu
_default_stopwords = set(StopWordRemoverFactory().get_stop_words())
CUSTOM_STOPWORDS = _default_stopwords - NEGATION_WORDS


def is_stopword(word: str) -> bool:
    """Cek apakah sebuah kata termasuk stopword (dan bukan kata negasi)."""
    if word in NEGATION_WORDS:
        return False
    return word in CUSTOM_STOPWORDS
