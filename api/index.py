"""
api/index.py
Entry point khusus Vercel. Vercel Python runtime mencari variabel `app`
(WSGI callable) di file dalam folder `api/`. File ini hanya meng-import
ulang instance Flask dari app.py di root proyek.
"""

import sys
from pathlib import Path

# Tambahkan root proyek ke sys.path agar `import app`, `import ml.*` berhasil
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app import app  # noqa: E402  (Flask WSGI app yang dipakai Vercel)

# Vercel akan otomatis mendeteksi variabel `app` ini sebagai handler.
