#!/usr/bin/env python3
"""Tests for wallpaper providers."""

from unittest.mock import patch
from muralis.providers.bing import BingProvider
from muralis.providers.nasa import NasaProvider
from muralis.providers.pexels import PexelsProvider
from muralis.providers.wikimedia import WikimediaProvider
from muralis.providers.artinstitute import ArtInstituteProvider

class TestProviders:
    """Test all wallpaper providers."""

    @patch('requests.Session.get')
    def test_bing_provider(self, mock_get):
        """Test Bing provider."""
        # Mock the API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'images': [{'url': 'image.jpg'}]}
        
        provider = BingProvider()
        url = provider.get_daily_url()
        assert url is not None
        assert 'http'  in url
        
        # Test metadata
        meta = provider.get_metadata()
        assert 'title' in meta

    @patch('requests.Session.get')
    def test_nasa_provider(self, mock_get):
        """Test NASA provider."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'media_type': 'image', 'url': 'image.jpg'}
        
        provider = NasaProvider()
        url = provider.get_daily_url()
        assert url is not None

    @patch('requests.Session.get')
    def test_pexels_provider(self, mock_get):
        """Test Pexels provider."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'photos': [{'src': {'original': 'url.jpg'}}]}
        
        provider = PexelsProvider()
        url = provider.get_daily_url()
        assert url is not None
        assert url == 'url.jpg'

    @patch('requests.Session.get')
    def test_wikimedia_provider(self, mock_get):
        """Test Wikimedia provider."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'query': {'pages': {'1': {'imageinfo': [{'url': 'image.jpg'}]}}}
        }
        
        provider = WikimediaProvider()
        url = provider.get_daily_url()
        assert url is not None

    @patch('requests.Session.get')
    def test_artinstitute_provider(self, mock_get):
        """Test Art Institute provider."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': [{'image_id': '123', 'title': 'Test'}]}
        
        provider = ArtInstituteProvider()
        url = provider.get_daily_url()
        assert url is not None