"""
app.py
Backend Flask utama — dipakai untuk run lokal (`python app.py`) maupun
di-import oleh api/index.py sebagai WSGI handler di Vercel.

Endpoint:
  GET  /                     -> Halaman Upload (index.html)
  GET  /preprocessing        -> Halaman Preview Preprocessing
  GET  /dashboard            -> Halaman Evaluasi/Prediksi
  POST /api/predict          -> Mode 1: prediksi pakai model pre-trained (CSV atau teks manual)
  POST /api/train            -> Mode 2: custom training + evaluasi (CSV berlabel)
  POST /api/save-run         -> Simpan histori evaluasi ke Supabase (opsional)
  GET  /api/history          -> Ambil histori evaluasi dari Supabase (opsional)
"""

import io
import os

import pandas as pd
from flask import Flask, jsonify, render_template, request

from ml.inference import predict_batch, predict_single
from ml.training import train_and_evaluate

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # batas upload 10MB


# ---------------------------------------------------------------------------
# Halaman (Views)
# ---------------------------------------------------------------------------

# @app.route("/")
# def index():
#     return render_template("index.html")


# @app.route("/preprocessing")
# def preprocessing_page():
#     return render_template("preprocessing.html")


# @app.route("/dashboard")
# def dashboard_page():
#     return render_template("dashboard.html")


# GANTI route index() yang lama:
@app.route("/")
def index():
    return render_template("index.html", active_page="upload")


# GANTI route preprocessing_page() yang lama:
@app.route("/preprocessing")
def preprocessing_page():
    return render_template("preprocessing.html", active_page="preprocessing")


# GANTI route dashboard_page() yang lama:
@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html", active_page="dashboard")



# ---------------------------------------------------------------------------
# API — Mode 1: Prediksi Instan (pre-trained model)
# ---------------------------------------------------------------------------

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Terima CSV (kolom 'text'/'ulasan') ATAU teks manual dari textarea."""
    try:
        manual_text = request.form.get("manual_text", "").strip()
        if manual_text:
            result = predict_single(manual_text)
            return jsonify({"status": "ok", "mode": "manual", "result": result})

        file = request.files.get("file")
        if not file:
            return jsonify({"status": "error", "message": "File CSV atau teks manual wajib diisi."}), 400

        df = pd.read_csv(io.StringIO(file.stream.read().decode("utf-8", errors="ignore")))
        text_col = _detect_text_column(df)
        raw_texts = df[text_col].astype(str).tolist()

        result = predict_batch(raw_texts)
        return jsonify({"status": "ok", "mode": "batch", "result": result})

    except Exception as exc:  # noqa: BLE001
        return jsonify({"status": "error", "message": str(exc)}), 500


# ---------------------------------------------------------------------------
# API — Mode 2: Custom Training
# ---------------------------------------------------------------------------

@app.route("/api/train", methods=["POST"])
def api_train():
    """Terima CSV berlabel + nilai K dari slider, jalankan training & evaluasi."""
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"status": "error", "message": "File CSV berlabel wajib diunggah."}), 400

        k = int(request.form.get("k", 5))
        df = pd.read_csv(io.StringIO(file.stream.read().decode("utf-8", errors="ignore")))

        text_col = _detect_text_column(df)
        label_col = _detect_label_column(df)

        result = train_and_evaluate(df, text_col=text_col, label_col=label_col, k=k)

        # objek model/vectorizer tidak bisa di-JSON-kan langsung, buang sebelum response
        response_payload = {key: value for key, value in result.items() if key not in ("vectorizer", "model")}

        return jsonify({"status": "ok", "mode": "training", "result": response_payload})

    except Exception as exc:  # noqa: BLE001
        return jsonify({"status": "error", "message": str(exc)}), 500


# ---------------------------------------------------------------------------
# API — Supabase (opsional): histori evaluasi
# ---------------------------------------------------------------------------

@app.route("/api/save-run", methods=["POST"])
def api_save_run():
    """Simpan ringkasan metrik training ke tabel Supabase `training_runs`."""
    try:
        from supabase_client import get_supabase_client

        payload = request.get_json(force=True)
        client = get_supabase_client()
        client.table("training_runs").insert({
            "k_value": payload.get("k"),
            "accuracy": payload.get("accuracy"),
            "precision": payload.get("precision"),
            "recall": payload.get("recall"),
            "f1_score": payload.get("f1_score"),
        }).execute()

        return jsonify({"status": "ok"})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/history", methods=["GET"])
def api_history():
    """Ambil 20 histori evaluasi terakhir dari Supabase."""
    try:
        from supabase_client import get_supabase_client

        client = get_supabase_client()
        response = (
            client.table("training_runs")
            .select("*")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        return jsonify({"status": "ok", "data": response.data})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"status": "error", "message": str(exc)}), 500


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _detect_text_column(df: pd.DataFrame) -> str:
    candidates = ["text", "ulasan", "review", "review_text", "komentar"]
    for col in candidates:
        if col in df.columns:
            return col
    return df.columns[0]  # fallback: kolom pertama


def _detect_label_column(df: pd.DataFrame) -> str:
    candidates = ["label", "sentimen", "sentiment", "kelas"]
    for col in candidates:
        if col in df.columns:
            return col
    raise ValueError("Kolom label tidak ditemukan. Beri nama kolom 'label' atau 'sentimen'.")


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
