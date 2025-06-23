import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from utils.extract import (
    fetching_content,
    extract_fashion_data,
    scrape_all_pages,
    extract_all_products_from_url,
    HEADERS
)

BASE_URL = "https://fashion-studio.dicoding.dev/"

class TestFetchingContent:
    @patch('requests.get')
    def test_successful_fetch(self, mock_get):
        """Test successful content fetching"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'<html>content</html>'
        mock_get.return_value = mock_response

        result = fetching_content(BASE_URL)
        assert result == b'<html>content</html>'
        mock_get.assert_called_once_with(BASE_URL, headers=HEADERS)

    @patch('requests.get')
    def test_failed_fetch(self, mock_get):
        """Test failed request handling"""
        mock_get.side_effect = requests.exceptions.RequestException("Error")

        result = fetching_content(BASE_URL)
        assert result is None

class TestExtractFashionData:
    def test_complete_product_data(self):
        """Test extraction with complete product data"""
        mock_div = MagicMock()
        mock_div.find.return_value = BeautifulSoup(f"""
            <div class="product-details">
                <h3 class="product-title">Premium Jacket</h3>
                <div class="price-container"><span class="price">Rp 499.000</span></div>
                <p>Rating: 4.8/5</p>
                <p>Colors: Black, Navy</p>
                <p>Size: XL</p>
                <p>Gender: Male</p>
            </div>
        """, 'html.parser')

        result = extract_fashion_data(mock_div)
        assert result['title'] == 'Premium Jacket'
        assert result['price'] == 'Rp 499.000'
        assert result['rating'] == '4.8/5'
        assert result['colors'] == 'Colors: Black, Navy'
        assert result['size'] == 'XL'
        assert result['gender'] == 'male'
        assert isinstance(result['timestamp'], str)

    def test_partial_product_data(self):
        """Test extraction with missing fields"""
        mock_div = MagicMock()
        mock_div.find.return_value = BeautifulSoup(f"""
            <div class="product-details">
                <h3 class="product-title">Basic T-Shirt</h3>
                <div class="price-container"><span class="price">Rp 149.000</span></div>
            </div>
        """, 'html.parser')

        result = extract_fashion_data(mock_div)
        assert result['title'] == 'Basic T-Shirt'
        assert result['price'] == 'Rp 149.000'
        assert result['rating'] is None
        assert result['colors'] is None
        assert result['size'] is None
        assert result['gender'] is None

class TestScrapeAllPages:
    @patch('utils.extract.fetching_content')
    @patch('utils.extract.time.sleep')
    def test_single_page_scraping(self, mock_sleep, mock_fetch):
        """Test scraping when there's only one page"""
        mock_fetch.return_value = b"""
            <html>
                <div class="collection-card">Product 1</div>
                <div class="collection-card">Product 2</div>
            </html>
        """

        results = scrape_all_pages(BASE_URL)
        assert len(results) == 2
        mock_fetch.assert_called_once_with(BASE_URL)
        mock_sleep.assert_not_called()

    @patch('utils.extract.fetching_content')
    @patch('utils.extract.time.sleep')
    def test_multi_page_scraping(self, mock_sleep, mock_fetch):
        """Test scraping across multiple pages"""
        mock_fetch.side_effect = [
            bytes(f"""
            <html>
                <div class="collection-card">Page 1 Product</div>
                <li class="next"><a href="{BASE_URL}page2"></a></li>
            </html>
            """, 'utf-8'),
            bytes(f"""
            <html>
                <div class="collection-card">Page 2 Product</div>
            </html>
            """, 'utf-8')
        ]

        results = scrape_all_pages(BASE_URL)
        assert len(results) == 2
        assert mock_fetch.call_count == 2
        mock_sleep.assert_called_once_with(1)
    
    @patch('utils.extract.fetching_content')
    def test_scrape_page_html_none(self, mock_fetch, capsys):
        """Test early stop when fetch fails (html is None)"""
        mock_fetch.return_value = None
        results = scrape_all_pages(BASE_URL)
        captured = capsys.readouterr()
        assert "Failed to fetch content. Stopping." in captured.out
        assert results == []
    @patch('utils.extract.fetching_content')
    @patch('utils.extract.time.sleep')
    def test_scrape_page_no_next(self, mock_sleep, mock_fetch):
        """Test stop condition when 'next' pagination is missing"""
        mock_fetch.return_value = b"""
            <html>
                <div class="collection-card">Only Page Product</div>
            </html>
        """
        results = scrape_all_pages(BASE_URL)
        assert len(results) == 1
        mock_sleep.assert_not_called()
    
    @patch('utils.extract.fetching_content')
    @patch('utils.extract.time.sleep')
    def test_scrape_page_no_products(self, mock_sleep, mock_fetch, capsys):
        """Test stopping when no products found on a page"""
        mock_fetch.return_value = b"""
            <html><body><p>No products here</p></body></html>
        """
        results = scrape_all_pages(BASE_URL)
        captured = capsys.readouterr()
        
        assert "No more products found. Done." in captured.out
        assert results == []
        mock_sleep.assert_not_called()

class TestExtractAllProductsFromUrl:
    @patch('utils.extract.fetching_content')
    def test_product_extraction(self, mock_fetch):
        """Test product extraction from single URL"""
        mock_fetch.return_value = b"""
            <html>
                <div class="collection-card">Summer Dress</div>
                <div class="collection-card">Winter Coat</div>
            </html>
        """

        results = extract_all_products_from_url(BASE_URL)
        assert len(results) == 2
        mock_fetch.assert_called_once_with(BASE_URL)
    
    @patch('utils.extract.fetching_content')
    def test_html_none_returns_empty_list(self, mock_fetch):
        """Test None response returns empty list"""
        mock_fetch.return_value = None

        results = extract_all_products_from_url(BASE_URL)
        assert results == []