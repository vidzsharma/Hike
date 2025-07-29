"""
Data fetching module for Rush Gaming CI System

Scrapes blogs, social media, and job boards for competitor intelligence.
"""

import time
import feedparser
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import json

from .config import config
from .utils.logger import get_logger
from .utils.helpers import rate_limit_delay, safe_request, clean_text, generate_content_hash

logger = get_logger(__name__)


class DataFetcher:
    """Main data fetching class for competitor intelligence"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def fetch_all_sources(self) -> Dict[str, List[Dict]]:
        """
        Fetch data from all sources for all competitors
        
        Returns:
            Dictionary with data by source type
        """
        logger.info("Starting data fetch for all competitors")
        
        all_data = {
            'blogs': [],
            'tweets': [],
            'linkedin': [],
            'jobs': []
        }
        
        for competitor_key, competitor_config in config.competitors.items():
            logger.info(f"Fetching data for {competitor_config['name']}")
            
            # Fetch blogs
            try:
                blogs = self.fetch_blogs(competitor_config)
                all_data['blogs'].extend(blogs)
                logger.info(f"Fetched {len(blogs)} blog posts for {competitor_config['name']}")
            except Exception as e:
                logger.error(f"Error fetching blogs for {competitor_config['name']}: {e}")
            
            rate_limit_delay()
            
            # Fetch tweets
            try:
                tweets = self.fetch_tweets(competitor_config)
                all_data['tweets'].extend(tweets)
                logger.info(f"Fetched {len(tweets)} tweets for {competitor_config['name']}")
            except Exception as e:
                logger.error(f"Error fetching tweets for {competitor_config['name']}: {e}")
            
            rate_limit_delay()
            
            # Fetch LinkedIn posts
            try:
                linkedin_posts = self.fetch_linkedin_posts(competitor_config)
                all_data['linkedin'].extend(linkedin_posts)
                logger.info(f"Fetched {len(linkedin_posts)} LinkedIn posts for {competitor_config['name']}")
            except Exception as e:
                logger.error(f"Error fetching LinkedIn posts for {competitor_config['name']}: {e}")
            
            rate_limit_delay()
            
            # Fetch jobs
            try:
                jobs = self.fetch_jobs(competitor_config)
                all_data['jobs'].extend(jobs)
                logger.info(f"Fetched {len(jobs)} job postings for {competitor_config['name']}")
            except Exception as e:
                logger.error(f"Error fetching jobs for {competitor_config['name']}: {e}")
            
            rate_limit_delay()
        
        logger.info(f"Completed data fetch. Total: {sum(len(data) for data in all_data.values())} items")
        return all_data
    
    def fetch_blogs(self, competitor_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch blog posts from competitor website
        
        Args:
            competitor_config: Competitor configuration
            
        Returns:
            List of blog post data
        """
        blogs = []
        blog_url = competitor_config.get('blog_url')
        
        if not blog_url:
            return blogs
        
        try:
            # Try RSS feed first
            rss_urls = [
                f"{blog_url}/feed",
                f"{blog_url}/rss",
                f"{blog_url}/feed.xml",
                f"{blog_url}/rss.xml"
            ]
            
            for rss_url in rss_urls:
                try:
                    response = safe_request(rss_url)
                    if response and response.status_code == 200:
                        feed = feedparser.parse(response.content)
                        
                        for entry in feed.entries[:10]:  # Last 10 posts
                            blog_data = {
                                'title': clean_text(entry.get('title', '')),
                                'url': entry.get('link', ''),
                                'content': clean_text(entry.get('summary', '')),
                                'company': competitor_config['name'],
                                'published_at': self._parse_date(entry.get('published', '')),
                                'source': 'rss',
                                'content_hash': generate_content_hash(entry.get('title', '') + entry.get('summary', ''))
                            }
                            blogs.append(blog_data)
                        break
                        
                except Exception as e:
                    logger.debug(f"RSS feed failed for {rss_url}: {e}")
                    continue
            
            # Fallback to HTML scraping if RSS fails
            if not blogs:
                blogs = self._scrape_blog_html(blog_url, competitor_config['name'])
                
        except Exception as e:
            logger.error(f"Error fetching blogs from {blog_url}: {e}")
        
        return blogs
    
    def _scrape_blog_html(self, blog_url: str, company_name: str) -> List[Dict[str, Any]]:
        """
        Scrape blog posts from HTML when RSS is not available
        
        Args:
            blog_url: Blog URL
            company_name: Company name
            
        Returns:
            List of blog post data
        """
        blogs = []
        
        try:
            response = safe_request(blog_url)
            if not response:
                return blogs
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common blog post selectors
            selectors = [
                'article',
                '.post',
                '.blog-post',
                '.entry',
                '[class*="post"]',
                '[class*="blog"]'
            ]
            
            for selector in selectors:
                articles = soup.select(selector)
                if articles:
                    for article in articles[:10]:  # Last 10 posts
                        try:
                            title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                            title = clean_text(title_elem.get_text()) if title_elem else ''
                            
                            link_elem = article.find('a')
                            url = link_elem.get('href') if link_elem else ''
                            if url and not url.startswith('http'):
                                url = blog_url.rstrip('/') + '/' + url.lstrip('/')
                            
                            content_elem = article.find(['p', 'div'])
                            content = clean_text(content_elem.get_text()) if content_elem else ''
                            
                            if title and url:
                                blog_data = {
                                    'title': title,
                                    'url': url,
                                    'content': content,
                                    'company': company_name,
                                    'published_at': datetime.now(),  # Fallback
                                    'source': 'html',
                                    'content_hash': generate_content_hash(title + content)
                                }
                                blogs.append(blog_data)
                                
                        except Exception as e:
                            logger.debug(f"Error parsing article: {e}")
                            continue
                    
                    break  # Use first working selector
                    
        except Exception as e:
            logger.error(f"Error scraping HTML from {blog_url}: {e}")
        
        return blogs
    
    def fetch_tweets(self, competitor_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch recent tweets from competitor Twitter handle
        
        Args:
            competitor_config: Competitor configuration
            
        Returns:
            List of tweet data
        """
        tweets = []
        twitter_handle = competitor_config.get('twitter_handle')
        
        if not twitter_handle or not config.twitter_bearer_token:
            return tweets
        
        try:
            # Using Twitter API v2
            from twitter.twitter_client import TwitterClient
            
            client = TwitterClient(config.twitter_bearer_token)
            
            # Get user ID first
            user = client.get_user_by_username(twitter_handle)
            if not user:
                return tweets
            
            user_id = user['data']['id']
            
            # Get recent tweets
            tweet_data = client.get_users_tweets(
                user_id,
                max_results=20,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            if tweet_data and 'data' in tweet_data:
                for tweet in tweet_data['data']:
                    tweet_info = {
                        'tweet_id': tweet['id'],
                        'text': clean_text(tweet['text']),
                        'company': competitor_config['name'],
                        'created_at': self._parse_date(tweet['created_at']),
                        'metrics': tweet.get('public_metrics', {}),
                        'source': 'twitter_api',
                        'content_hash': generate_content_hash(tweet['text'])
                    }
                    tweets.append(tweet_info)
                    
        except Exception as e:
            logger.error(f"Error fetching tweets for {twitter_handle}: {e}")
        
        return tweets
    
    def fetch_linkedin_posts(self, competitor_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch recent LinkedIn posts from competitor company page
        
        Args:
            competitor_config: Competitor configuration
            
        Returns:
            List of LinkedIn post data
        """
        posts = []
        linkedin_company = competitor_config.get('linkedin_company')
        
        if not linkedin_company:
            return posts
        
        try:
            # LinkedIn API requires authentication
            # For now, we'll use a simplified approach
            linkedin_url = f"https://www.linkedin.com/company/{linkedin_company}"
            
            # Note: LinkedIn scraping requires proper authentication
            # This is a placeholder for the actual implementation
            logger.info(f"LinkedIn scraping for {linkedin_company} - requires proper auth setup")
            
        except Exception as e:
            logger.error(f"Error fetching LinkedIn posts for {linkedin_company}: {e}")
        
        return posts
    
    def fetch_jobs(self, competitor_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch job postings from competitor careers page
        
        Args:
            competitor_config: Competitor configuration
            
        Returns:
            List of job posting data
        """
        jobs = []
        careers_url = competitor_config.get('careers_url')
        
        if not careers_url:
            return jobs
        
        try:
            # Try different job board formats
            job_sources = [
                f"{careers_url}/jobs.json",  # Greenhouse format
                f"{careers_url}/api/jobs",   # Lever format
                careers_url  # HTML fallback
            ]
            
            for job_source in job_sources:
                try:
                    if job_source.endswith('.json'):
                        jobs.extend(self._fetch_json_jobs(job_source, competitor_config['name']))
                    else:
                        jobs.extend(self._scrape_jobs_html(job_source, competitor_config['name']))
                    
                    if jobs:
                        break
                        
                except Exception as e:
                    logger.debug(f"Job source failed {job_source}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching jobs from {careers_url}: {e}")
        
        return jobs
    
    def _fetch_json_jobs(self, json_url: str, company_name: str) -> List[Dict[str, Any]]:
        """
        Fetch jobs from JSON API (Greenhouse, Lever, etc.)
        
        Args:
            json_url: JSON API URL
            company_name: Company name
            
        Returns:
            List of job data
        """
        jobs = []
        
        try:
            response = safe_request(json_url)
            if not response:
                return jobs
            
            data = response.json()
            
            # Handle different JSON formats
            job_list = data.get('jobs', data.get('positions', data.get('openings', [])))
            
            for job in job_list[:20]:  # Last 20 jobs
                job_data = {
                    'role': clean_text(job.get('title', job.get('name', ''))),
                    'company': company_name,
                    'location': clean_text(job.get('location', {}).get('name', job.get('location', ''))),
                    'posted_at': self._parse_date(job.get('updated_at', job.get('created_at', ''))),
                    'url': job.get('absolute_url', job.get('url', '')),
                    'source': 'json_api',
                    'content_hash': generate_content_hash(job.get('title', '') + job.get('content', ''))
                }
                jobs.append(job_data)
                
        except Exception as e:
            logger.error(f"Error parsing JSON jobs from {json_url}: {e}")
        
        return jobs
    
    def _scrape_jobs_html(self, careers_url: str, company_name: str) -> List[Dict[str, Any]]:
        """
        Scrape job postings from HTML careers page
        
        Args:
            careers_url: Careers page URL
            company_name: Company name
            
        Returns:
            List of job data
        """
        jobs = []
        
        try:
            response = safe_request(careers_url)
            if not response:
                return jobs
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common job posting selectors
            selectors = [
                '.job',
                '.position',
                '.opening',
                '[class*="job"]',
                '[class*="position"]'
            ]
            
            for selector in selectors:
                job_elements = soup.select(selector)
                if job_elements:
                    for job_elem in job_elements[:20]:  # Last 20 jobs
                        try:
                            title_elem = job_elem.find(['h1', 'h2', 'h3', 'h4'])
                            title = clean_text(title_elem.get_text()) if title_elem else ''
                            
                            location_elem = job_elem.find(['span', 'div'], class_=lambda x: x and 'location' in x.lower())
                            location = clean_text(location_elem.get_text()) if location_elem else ''
                            
                            link_elem = job_elem.find('a')
                            url = link_elem.get('href') if link_elem else ''
                            if url and not url.startswith('http'):
                                url = careers_url.rstrip('/') + '/' + url.lstrip('/')
                            
                            if title:
                                job_data = {
                                    'role': title,
                                    'company': company_name,
                                    'location': location,
                                    'posted_at': datetime.now(),  # Fallback
                                    'url': url,
                                    'source': 'html',
                                    'content_hash': generate_content_hash(title + location)
                                }
                                jobs.append(job_data)
                                
                        except Exception as e:
                            logger.debug(f"Error parsing job element: {e}")
                            continue
                    
                    break  # Use first working selector
                    
        except Exception as e:
            logger.error(f"Error scraping HTML jobs from {careers_url}: {e}")
        
        return jobs
    
    def _parse_date(self, date_string: str) -> datetime:
        """
        Parse date string to datetime object
        
        Args:
            date_string: Date string to parse
            
        Returns:
            Parsed datetime or current time as fallback
        """
        if not date_string:
            return datetime.now()
        
        try:
            # Try common date formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            
            # Fallback to current time
            return datetime.now()
            
        except Exception:
            return datetime.now()


def main():
    """Main function to run data fetching"""
    logger.info("Starting Rush Gaming CI data fetch")
    
    fetcher = DataFetcher()
    data = fetcher.fetch_all_sources()
    
    # Save raw data to file for debugging
    with open('data/raw_fetch_data.json', 'w') as f:
        json.dump(data, f, default=str, indent=2)
    
    logger.info("Data fetch completed")
    return data


if __name__ == "__main__":
    main() 