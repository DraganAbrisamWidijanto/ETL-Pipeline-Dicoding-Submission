import pandas as pd
import numpy as np

def transform_fashion_data(df):
    try:
        df_clean = df.copy()

        # 1. Hapus baris dengan title tidak valid
        df_clean = df_clean[~df_clean['title'].str.lower().isin(['unknown product', 'none'])]

        # 2. Hapus baris dengan price tidak valid
        df_clean = df_clean[~df_clean['price'].str.lower().isin(['price unavailable', 'none'])]

        # 3. Konversi price ke float lalu ke Rupiah
        df_clean['price'] = df_clean['price'].str.replace(r'[^\d.]', '', regex=True)
        df_clean['price'] = pd.to_numeric(df_clean['price'], errors='coerce') * 16000

        # 4. Filter rating valid lalu ubah ke float
        df_clean = df_clean[~df_clean['rating'].str.lower().isin(['not rated', '⭐ invalid rating / 5', 'none'])]
        df_clean['rating'] = df_clean['rating'].str.extract(r'([\d.]+)')
        df_clean['rating'] = pd.to_numeric(df_clean['rating'], errors='coerce')

        # 5. Ekstrak angka dari kolom colors
        df_clean['colors'] = df_clean['colors'].str.extract(r'(\d+)')
        df_clean['colors'] = pd.to_numeric(df_clean['colors'], errors='coerce')

        # 6. Bersihkan size dan gender
        df_clean['size'] = df_clean['size'].astype(str).str.strip().str.upper()
        df_clean['size'] = df_clean['size'].replace(['NONE', 'NONETYPE', 'NAN'], np.nan).infer_objects(copy=False)

        df_clean['gender'] = df_clean['gender'].astype(str).str.strip().str.lower()

        # 7. Drop rows yang masih ada NaN
        df_clean.dropna(inplace=True)

        return df_clean.reset_index(drop=True)

    except Exception as e:
        print(f"⚠️ Terjadi kesalahan saat transformasi data: {e}")
        return pd.DataFrame()
