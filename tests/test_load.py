import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import psycopg2
from psycopg2 import OperationalError, errors as psycopg2_errors
from utils.load import (
    save_to_csv,
    save_to_google_sheets,
    create_database,
    save_to_postgres_append,
    save_to_postgres_overwrite
)

# Sample DataFrame for testing
TEST_DF = pd.DataFrame({
    'title': ['Product A', 'Product B'],
    'price': [100000, 200000],
    'rating': [4.5, 3.8],
    'colors': [2, 3],
    'size': ['M', 'L'],
    'gender': ['Male', 'Female'],
    'timestamp': ['2023-01-01', '2023-01-02']
})

# ------------------------ Test save_to_csv ------------------------ #
@patch('pandas.DataFrame.to_csv')
def test_save_to_csv_success(mock_to_csv):
    save_to_csv(TEST_DF, "test_output.csv")
    mock_to_csv.assert_called_once_with("test_output.csv", index=False)

@patch('pandas.DataFrame.to_csv', side_effect=Exception("Save error"))
def test_save_to_csv_failure(mock_to_csv):
    save_to_csv(TEST_DF, "test_output.csv")
    mock_to_csv.assert_called_once_with("test_output.csv", index=False)

# ------------------------ Test save_to_google_sheets ------------------------ #
@patch('utils.load.Credentials.from_service_account_file')
@patch('utils.load.build')
def test_save_to_google_sheets_success(mock_build, mock_creds):
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    save_to_google_sheets(
        TEST_DF,
        "credentials.json",
        "spreadsheet_id",
        "Test Sheet"
    )

    mock_creds.assert_called_once_with(
        "credentials.json",
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    mock_service.spreadsheets.return_value.values.return_value.update.assert_called_once()

@patch('utils.load.Credentials.from_service_account_file', side_effect=Exception("Auth error"))
def test_save_to_google_sheets_failure(mock_creds):
    save_to_google_sheets(TEST_DF, "credentials.json", "spreadsheet_id")
    mock_creds.assert_called_once()

# ------------------------ Test create_database ------------------------ #
@patch('psycopg2.connect')
def test_create_database_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    create_database('new_db', 'user', 'password')

    mock_connect.assert_called_once_with(
        dbname='postgres',
        user='user',
        password='password',
        host='localhost',
        port=5432
    )
    mock_cursor.execute.assert_any_call("CREATE DATABASE new_db;")
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('psycopg2.connect')
def test_create_database_duplicate(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = psycopg2_errors.DuplicateDatabase()

    create_database('existing_db', 'user', 'password')
    mock_cursor.execute.assert_called_once_with("CREATE DATABASE existing_db;")

@patch('psycopg2.connect', side_effect=OperationalError("Connection failed"))
def test_create_database_failure(mock_connect):
    create_database('new_db', 'user', 'password')
    mock_connect.assert_called_once()

# ------------------------ Test save_to_postgres_append ------------------------ #
@patch('psycopg2.connect')
def test_save_to_postgres_append_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    db_config = {
        'dbname': 'test_db',
        'user': 'test_user',
        'password': 'test_pass',
        'host': 'localhost',
        'port': '5432'
    }
    save_to_postgres_append(TEST_DF, db_config)

    mock_connect.assert_called_once_with(**db_config)
    assert mock_cursor.execute.call_count >= 2
    mock_conn.commit.assert_called()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('psycopg2.connect', side_effect=OperationalError("Connection failed"))
def test_save_to_postgres_append_failure(mock_connect):
    db_config = {
        'dbname': 'test_db',
        'user': 'test_user',
        'password': 'test_pass',
        'host': 'localhost',
        'port': '5432'
    }
    save_to_postgres_append(TEST_DF, db_config)
    mock_connect.assert_called_once_with(**db_config)

# ------------------------ Test save_to_postgres_overwrite ------------------------ #
@patch('utils.load.execute_values')
@patch('utils.load.psycopg2.connect')
def test_save_to_postgres_overwrite_success(mock_connect, mock_execute):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    db_config = {
        'dbname': 'test_db',
        'user': 'test_user',
        'password': 'test_pass',
        'host': 'localhost',
        'port': '5432'
    }
    save_to_postgres_overwrite(TEST_DF, db_config)

    mock_connect.assert_called_once_with(**db_config)
    mock_cursor.execute.assert_any_call("DROP TABLE IF EXISTS fashion_products;")
    mock_execute.assert_called_once()
    mock_conn.commit.assert_called()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('utils.load.execute_values', side_effect=Exception("Insert error"))
@patch('utils.load.psycopg2.connect')
def test_save_to_postgres_overwrite_failure(mock_connect, mock_execute):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    db_config = {
        'dbname': 'test_db',
        'user': 'test_user',
        'password': 'test_pass',
        'host': 'localhost',
        'port': '5432'
    }
    save_to_postgres_overwrite(TEST_DF, db_config)

    mock_connect.assert_called_once_with(**db_config)
    mock_execute.assert_called_once()
