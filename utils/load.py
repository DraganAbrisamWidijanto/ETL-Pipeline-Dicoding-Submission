from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd


def save_to_csv(df: pd.DataFrame, filename: str = "products.csv"):
    """Simpan DataFrame ke file CSV."""
    try:
        df.to_csv(filename, index=False)
        print(f"✅ Data berhasil disimpan ke {filename}")
    except Exception as e:
        print(f"❌ Gagal menyimpan ke CSV: {e}")


def save_to_google_sheets(df: pd.DataFrame, json_keyfile_path: str, spreadsheet_id: str, sheet_name: str = 'Sheet1'):
    """Simpan DataFrame ke Google Sheets."""
    try:
        print("📤 Menyimpan ke Google Sheets...")
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(json_keyfile_path, scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)

        values = [df.columns.tolist()] + df.astype(str).values.tolist()
        range_name = f'{sheet_name}!A1'
        body = {'values': values}

        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        print("✅ Data berhasil ditulis ke Google Sheets!")

    except Exception as e:
        print(f"❌ Gagal menyimpan ke Google Sheets: {e}")


def create_database(dbname: str, user: str, password: str, host: str = 'localhost', port: int = 5432):
    """Buat database PostgreSQL jika belum ada."""
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE {dbname};")
        print(f"✅ Database '{dbname}' berhasil dibuat!")
        cur.close()
        conn.close()
    except psycopg2.errors.DuplicateDatabase:
        print(f"ℹ️ Database '{dbname}' sudah ada. Lewatkan pembuatan.")
    except Exception as e:
        print(f"❌ Gagal membuat database: {e}")


def save_to_postgres_append(df: pd.DataFrame, db_config: dict, table_name: str = "products"):
    """Simpan data ke PostgreSQL (append jika tabel sudah ada)."""
    try:
        print("🛢️ Menyimpan ke PostgreSQL (append)...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            title TEXT,
            price FLOAT,
            rating FLOAT,
            colors INTEGER,
            size TEXT,
            gender TEXT,
            timestamp TEXT
        )
        """
        cursor.execute(create_table_query)
        conn.commit()

        for _, row in df.iterrows():
            cursor.execute(
                f"INSERT INTO {table_name} (title, price, rating, colors, size, gender, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                tuple(row)
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Data berhasil disimpan ke PostgreSQL (append)!")
        
    except Exception as e:
        print(f"❌ Gagal menyimpan ke PostgreSQL (append): {e}")


def save_to_postgres_overwrite(df: pd.DataFrame, db_config: dict, table_name: str = "fashion_products"):
    """Simpan data ke PostgreSQL dengan cara overwrite (drop table lalu buat ulang)."""
    try:
        print("🛢️ Menyimpan ke PostgreSQL (overwrite)...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        create_table_query = f"""
        CREATE TABLE {table_name} (
            title TEXT,
            price FLOAT,
            rating FLOAT,
            colors INT,
            size TEXT,
            gender TEXT,
            timestamp TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()

        insert_query = f"""
        INSERT INTO {table_name} (title, price, rating, colors, size, gender, timestamp)
        VALUES %s
        """
        data_tuples = [tuple(row) for row in df.itertuples(index=False)]
        execute_values(cursor, insert_query, data_tuples)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Data berhasil ditulis ulang ke PostgreSQL (overwrite)!")

    except Exception as e:
        print(f"❌ Gagal menyimpan ke PostgreSQL (overwrite): {e}")