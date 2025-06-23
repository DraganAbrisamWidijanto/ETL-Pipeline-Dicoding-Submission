import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from utils.transform import transform_fashion_data

class TestTransformFashionData:
    def test_valid_data_transformation(self):
        """Test transform with clean valid data"""
        raw_data = pd.DataFrame([{
            "title": "Cool Shirt",
            "price": "Rp 100.000",
            "rating": "4.5/5",
            "colors": "Colors: 3",
            "size": " M ",
            "gender": "Male",
            "timestamp": "2025-06-22T10:00:00"
        }])
        
        expected = pd.DataFrame([{
            "title": "Cool Shirt",
            "price": 100.0 * 16000.0,  
            "rating": 4.5,
            "colors": 3.0,
            "size": "M",
            "gender": "male",
            "timestamp": "2025-06-22T10:00:00"
        }])


        result = transform_fashion_data(raw_data)
        assert_frame_equal(result, expected, check_dtype=False)

    def test_invalid_titles_and_prices_are_dropped(self):
        """Test removal of rows with invalid titles or prices"""
        raw_data = pd.DataFrame([
            {"title": "Unknown Product", "price": "Rp 120.000", "rating": "4.0/5", "colors": "Colors: 2", "size": "L", "gender": "female", "timestamp": "x"},
            {"title": "Nice Pants", "price": "Price Unavailable", "rating": "4.2/5", "colors": "Colors: 4", "size": "S", "gender": "male", "timestamp": "x"}
        ])
        result = transform_fashion_data(raw_data)
        assert result.empty

    def test_invalid_ratings_are_dropped(self):
        """Test filtering of rows with invalid ratings"""
        raw_data = pd.DataFrame([
            {"title": "Fancy Hat", "price": "Rp 90.000", "rating": "⭐ Invalid Rating / 5", "colors": "Colors: 2", "size": "S", "gender": "male", "timestamp": "x"}
        ])
        result = transform_fashion_data(raw_data)
        assert result.empty

    def test_partial_nan_removal(self):
        """Test removal of rows with NaNs after transformation"""
        raw_data = pd.DataFrame([
            {"title": "Shirt", "price": "Rp 120.000", "rating": "4.2/5", "colors": "Colors: 4", "size": None, "gender": "male", "timestamp": "x"}
        ])
        result = transform_fashion_data(raw_data)
        assert result.empty

    def test_non_numeric_price_rating_colors(self):
        """Test coercion of malformed numeric fields to NaN and dropping"""
        raw_data = pd.DataFrame([{
            "title": "Item A",
            "price": "invalid",
            "rating": "not rated",
            "colors": "Colors: many",
            "size": "XL",
            "gender": "Male",
            "timestamp": "x"
        }])
        result = transform_fashion_data(raw_data)
        assert result.empty

    def test_no_crash_on_empty_input(self):
        """Test no crash and empty result on empty input"""
        raw_data = pd.DataFrame()
        result = transform_fashion_data(raw_data)
        assert result.empty
