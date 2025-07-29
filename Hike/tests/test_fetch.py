"""
Unit tests for data fetching module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from rush_ci import DataFetcher


class TestDataFetcher:
    """Test cases for DataFetcher class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.fetcher = DataFetcher()
        
    def test_fetch_all_sources_empty_config(self):
        """Test fetching with empty competitor config"""
        with patch('rush_ci.config.config') as mock_config:
            mock_config.competitors = {}
            
            result = self.fetcher.fetch_all_sources()
            
            assert result == {
                'blogs': [],
                'tweets': [],
                'linkedin': [],
                'jobs': []
            }
    
    def test_fetch_blogs_rss_success(self):
        """Test successful RSS blog fetching"""
        competitor_config = {
            'name': 'Test Company',
            'blog_url': 'https://test.com/blog'
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '''
        <rss>
            <channel>
                <item>
                    <title>Test Blog Post</title>
                    <link>https://test.com/blog/1</link>
                    <description>Test content</description>
                    <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>
        '''
        
        with patch('rush_ci.utils.helpers.safe_request', return_value=mock_response):
            blogs = self.fetcher.fetch_blogs(competitor_config)
            
            assert len(blogs) == 1
            assert blogs[0]['title'] == 'Test Blog Post'
            assert blogs[0]['company'] == 'Test Company'
    
    def test_fetch_blogs_no_rss_fallback_html(self):
        """Test HTML fallback when RSS fails"""
        competitor_config = {
            'name': 'Test Company',
            'blog_url': 'https://test.com/blog'
        }
        
        # Mock failed RSS requests
        with patch('rush_ci.utils.helpers.safe_request', return_value=None):
            blogs = self.fetcher.fetch_blogs(competitor_config)
            
            assert blogs == []
    
    def test_fetch_tweets_no_token(self):
        """Test tweet fetching without Twitter token"""
        competitor_config = {
            'name': 'Test Company',
            'twitter_handle': 'testcompany'
        }
        
        with patch('rush_ci.config.config') as mock_config:
            mock_config.twitter_bearer_token = None
            
            tweets = self.fetcher.fetch_tweets(competitor_config)
            
            assert tweets == []
    
    def test_fetch_jobs_json_api(self):
        """Test job fetching from JSON API"""
        competitor_config = {
            'name': 'Test Company',
            'careers_url': 'https://test.com/careers'
        }
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'jobs': [
                {
                    'title': 'Software Engineer',
                    'location': {'name': 'Bangalore'},
                    'absolute_url': 'https://test.com/job/1',
                    'updated_at': '2024-01-01T12:00:00Z'
                }
            ]
        }
        
        with patch('rush_ci.utils.helpers.safe_request', return_value=mock_response):
            jobs = self.fetcher.fetch_jobs(competitor_config)
            
            assert len(jobs) == 1
            assert jobs[0]['role'] == 'Software Engineer'
            assert jobs[0]['company'] == 'Test Company'
    
    def test_parse_date_valid_formats(self):
        """Test date parsing with valid formats"""
        test_cases = [
            ('2024-01-01T12:00:00Z', datetime),
            ('2024-01-01 12:00:00', datetime),
            ('01/01/2024', datetime),
            ('', datetime),  # Should return current time
        ]
        
        for date_string, expected_type in test_cases:
            result = self.fetcher._parse_date(date_string)
            assert isinstance(result, expected_type)
    
    def test_fetch_all_sources_with_mock_data(self):
        """Test complete fetch pipeline with mock data"""
        mock_competitors = {
            'test1': {
                'name': 'Test Company 1',
                'blog_url': 'https://test1.com/blog',
                'twitter_handle': 'test1',
                'linkedin_company': 'test1',
                'careers_url': 'https://test1.com/careers'
            }
        }
        
        with patch('rush_ci.config.config') as mock_config:
            mock_config.competitors = mock_competitors
            mock_config.twitter_bearer_token = 'test_token'
            
            # Mock all fetch methods to return sample data
            with patch.object(self.fetcher, 'fetch_blogs', return_value=[{'title': 'Test'}]), \
                 patch.object(self.fetcher, 'fetch_tweets', return_value=[{'text': 'Test'}]), \
                 patch.object(self.fetcher, 'fetch_linkedin_posts', return_value=[]), \
                 patch.object(self.fetcher, 'fetch_jobs', return_value=[{'role': 'Test'}]):
                
                result = self.fetcher.fetch_all_sources()
                
                assert 'blogs' in result
                assert 'tweets' in result
                assert 'linkedin' in result
                assert 'jobs' in result
                assert len(result['blogs']) > 0
                assert len(result['tweets']) > 0
                assert len(result['jobs']) > 0


if __name__ == '__main__':
    pytest.main([__file__]) 