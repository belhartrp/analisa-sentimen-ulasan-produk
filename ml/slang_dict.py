"""
ml/slang_dict.py
Kamus normalisasi istilah slang & singkatan khas ulasan e-commerce Tokopedia.
Diterapkan SEBELUM tokenization agar frasa multi-kata (mis. "bintang 1") ikut tertangkap.
"""

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
    "pengiriman": "pengiriman",
    "cod": "bayar di tempat",
    "resi": "nomor resi",
    "cepet": "cepat",
    "lambat": "lambat",
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
    "bgtu": "begitu",
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
    "mantap": "mantap",
    "recomend": "rekomendasi",
    "rekomen": "rekomendasi",
    "rekomended": "rekomendasi",
    "sesuai": "sesuai",
    "gasesuai": "tidak sesuai",
    "ngecewain": "mengecewakan",
    "kecewa": "kecewa",
    "puas": "puas",
    "worth it": "sepadan",
    "worthit": "sepadan",
}


def apply_slang_normalization(text: str) -> str:
    """Ganti setiap frasa/kata slang pada teks dengan padanan formalnya.

    Diurutkan berdasarkan panjang frasa (descending) agar frasa multi-kata
    (mis. "bintang 1") tersubstitusi lebih dulu sebelum kata tunggal.
    """
    result = text
    for phrase in sorted(TOKOPEDIA_SLANG_DICT.keys(), key=len, reverse=True):
        result = result.replace(phrase, TOKOPEDIA_SLANG_DICT[phrase])
    return result
