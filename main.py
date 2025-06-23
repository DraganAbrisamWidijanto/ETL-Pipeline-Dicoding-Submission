from utils.extract import scrape_all_pages
from utils.transform import transform_fashion_data
from utils.load import (
    save_to_csv,
    save_to_google_sheets,
    create_database,
    save_to_postgres_append,
    save_to_postgres_overwrite
)
import pandas as pd

# 1. URL awal
BASE_URL = "https://fashion-studio.dicoding.dev/"

# 2. Ekstraksi
print("🚀 Memulai scraping data...")
data = scrape_all_pages(BASE_URL)

# 3. Konversi ke DataFrame
df = pd.DataFrame(data)

# 4. Cek data mentah
print("\n📌 5 Produk Teratas:")
print(df.head())
print("\n📌 5 Produk Terakhir:")
print(df.tail())

# 5. Transformasi
print("\n⚙️  Melakukan transformasi data...")
df_transformed = transform_fashion_data(df)

# 6. Cek hasil transformasi
print("\n✅ 5 Data Teratas Setelah Transformasi:")
print(df_transformed.head())
print("\n✅ 5 Data Terakhir Setelah Transformasi:")
print(df_transformed.tail())

# 7. Simpan ke CSV
save_to_csv(df_transformed, "products.csv")

# 8. Simpan ke Google Sheets
json_path = "google-sheets-api.json"
sheet_id = "18Z-Yj3nFozJ11KRQxl4kjBoWKVr6Qgub2sDWIUIEMkk" #Ganti dengan sheet id anda
save_to_google_sheets(df_transformed, json_path, sheet_id)

# 9. Simpan ke PostgreSQL
db_config = {
    "host": "localhost",
    "port": 5432,
    "database": "fashion_db",
    "user": "postgres",
    "password": "admin123" #ganti dengan password database anda
}

# Buat database jika belum ada
create_database("fashion_db", user="postgres", password="admin123") #sesuaikan dengan pw anda

# Simpan ke database PostgreSQL
# Pilih salah satu: append atau overwrite
save_to_postgres_overwrite(df_transformed, db_config)
# atau:
# save_to_postgres_append(df_transformed, db_config)