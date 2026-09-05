"""
ml/slang_dict.py  (VERSI PERBAIKAN — GANTI file slang_dict.py lamamu dengan ini)

PERBAIKAN: sebelumnya pakai text.replace() biasa, yang mengganti "ga" di
MANA SAJA termasuk di tengah kata lain (mis. "harga" -> "hartidak", "juga" ->
"jutidak"). Sekarang pakai regex dengan \\b (word boundary) supaya HANYA kata
yang berdiri sendiri persis yang diganti, bukan potongan dari kata lain.
"""

import re

TOKOPEDIA_SLANG_DICT: dict[str, str] = {
    # Sapaan / penjual
    "min": "admin",
    "kak min": "admin",
    "gan": "juragan",
    "sis": "saudari",
    "bro": "saudara",
    "kk": "kakak",

    # Frasa rating -> sentimen kata
    "bintang 1": "buruk",
    "bintang 2": "buruk",
    "bintang 3": "biasa",
    "bintang 4": "baik",
    "bintang 5": "sangat baik",
    "bintang satu": "buruk",
    "bintang lima": "sangat baik",

    # Istilah transaksi & pengiriman
    "paking": "kemasan",
    "packing": "kemasan",
    "po": "preorder",
    "kirim": "pengiriman",
    "cod": "bayar di tempat",
    "resi": "nomor resi",
    "cepet": "cepat",
    "lama bgt": "lama sekali",

    # Singkatan umum chat
    "gak": "tidak",
    "ga": "tidak",
    "ngga": "tidak",
    "nggak": "tidak",
    "tdk": "tidak",
    "bgt": "sekali",
    "banget": "sekali",
    "yg": "yang",
    "dgn": "dengan",
    "utk": "untuk",
    "sdh": "sudah",
    "udh": "sudah",
    "udah": "sudah",
    "blm": "belum",
    "blum": "belum",
    "tp": "tapi",
    "krn": "karena",
    "karna": "karena",
    "gmn": "bagaimana",
    "gimana": "bagaimana",
    "dr": "dari",
    "jd": "jadi",
    "jgn": "jangan",
    "org": "orang",
    "sy": "saya",
    "gw": "saya",
    "gue": "saya",
    "aq": "aku",

    # Kualitas produk
    "ori": "asli",
    "kw": "tiruan",
    "oke": "baik",
    "ok": "baik",
    "mantul": "mantap sekali",
    "recomend": "rekomendasi",
    "rekomen": "rekomendasi",
    "rekomended": "rekomendasi",
    "ngecewain": "mengecewakan",
    "worth it": "sepadan",
    "worthit": "sepadan",
}

# Urutkan frasa dari yang PALING PANJANG dulu, supaya "bintang 1" dicek
# lebih dulu daripada kata tunggal yang mungkin ada di dalamnya.
_SORTED_PHRASES = sorted(TOKOPEDIA_SLANG_DICT.keys(), key=len, reverse=True)


def apply_slang_normalization(text: str) -> str:
    """Ganti kata/frasa slang dengan padanan formalnya.

    Memakai regex dengan \\b (word boundary) supaya HANYA kata yang berdiri
    sendiri yang diganti — bukan potongan huruf yang kebetulan sama dengan
    kata lain (mis. "ga" di dalam "harga" TIDAK akan ikut diganti).
    """
    result = text
    for phrase in _SORTED_PHRASES:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        result = re.sub(pattern, TOKOPEDIA_SLANG_DICT[phrase], result)
    return result
