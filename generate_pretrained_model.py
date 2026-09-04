"""
generate_pretrained_model.py
Jalankan file ini SEKALI di laptop (bukan di server/Vercel) untuk membuat
2 file model yang dibutuhkan Mode 1 (Prediksi Instan):
  - models/tfidf_vectorizer.pkl
  - models/wknn_model.pkl

CARA PAKAI:
1. Siapkan file CSV bernama "dataset_awal.csv" di folder utama proyek ini,
   isinya minimal 2 kolom: "text" (teks ulasan) dan "label" (Positif/Negatif).
2. Jalankan di terminal (pastikan venv sudah aktif & requirements sudah diinstall):
       python generate_pretrained_model.py
3. Tunggu sampai muncul tulisan "Model berhasil disimpan!"
4. Cek folder models/ — akan muncul 2 file .pkl baru.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from ml.preprocessing import preprocess_batch
from ml.training import random_undersample
from ml.utils import save_pickle, MODEL_PATH, VECTORIZER_PATH
from ml.wknn import WeightedKNNCosine

DATASET_PATH = r"C:\me\github\analisa-sentimen-ulasan-produk\PRDECT-ID Dataset.csv"
TEXT_COLUMN = "Customer Review"
LABEL_COLUMN = "Sentiment"
K_DEFAULT = 5
MAX_FEATURES = 5000


def main():
    print(f"Membaca dataset dari {DATASET_PATH} ...")
    df = pd.read_csv(DATASET_PATH)
    df = df[[TEXT_COLUMN, LABEL_COLUMN]].dropna()
    df.columns = ["text", "label"]

    print("Menyeimbangkan data (random undersampling) ...")
    balanced_df = random_undersample(df, label_col="label")

    print(f"Total data setelah undersampling: {len(balanced_df)} baris")
    print("Melakukan preprocessing teks (ini bisa makan waktu beberapa menit) ...")
    raw_texts = balanced_df["text"].astype(str).tolist()
    clean_texts = preprocess_batch(raw_texts)
    labels = balanced_df["label"].astype(str).tolist()

    print("Melatih TF-IDF Vectorizer ...")
    vectorizer = TfidfVectorizer(max_features=MAX_FEATURES)
    X = vectorizer.fit_transform(clean_texts)

    print(f"Melatih model WKNN dengan K={K_DEFAULT} ...")
    model = WeightedKNNCosine(k=K_DEFAULT)
    model.fit(X, labels)

    print("Menyimpan model ke folder models/ ...")
    save_pickle(vectorizer, VECTORIZER_PATH)
    save_pickle(model, MODEL_PATH)

    print("\n✅ Model berhasil disimpan!")
    print(f"   - {VECTORIZER_PATH}")
    print(f"   - {MODEL_PATH}")
    print("\nSekarang kamu bisa jalankan 'python app.py' dan coba Mode 1 (Prediksi Instan).")


if __name__ == "__main__":
    main()
