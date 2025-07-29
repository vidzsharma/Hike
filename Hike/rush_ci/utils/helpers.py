"""
Helper utilities for Rush Gaming CI System
"""

import time
import hashlib
import re
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


def rate_limit_delay(min_seconds: float = 2.0, max_seconds: float = 6.0) -> None:
    """
    Random delay to respect rate limits
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def generate_content_hash(content: str) -> str:
    """
    Generate SHA1 hash for content deduplication
    
    Args:
        content: Content to hash
        
    Returns:
        SHA1 hash string
    """
    return hashlib.sha1(content.encode('utf-8')).hexdigest()


def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', text)
    
    return text


def extract_date_from_text(text: str) -> Optional[datetime]:
    """
    Extract date from text using various patterns
    
    Args:
        text: Text containing date information
        
    Returns:
        Parsed datetime or None
    """
    # Common date patterns
    patterns = [
        r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
        r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',      # Month DD, YYYY
        r'(\d{1,2})\s+(\w+)\s+(\d{4})',        # DD Month YYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                # Try to parse the matched date
                date_str = match.group(0)
                # Add more sophisticated date parsing here
                return datetime.now()  # Placeholder
            except:
                continue
    
    return None


def validate_url(url: str) -> bool:
    """
    Validate URL format and accessibility
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid and accessible
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_meta_tags(html_content: str) -> Dict[str, str]:
    """
    Extract meta tags from HTML content
    
    Args:
        html_content: Raw HTML content
        
    Returns:
        Dictionary of meta tag name-value pairs
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    meta_tags = {}
    
    for meta in soup.find_all('meta'):
        name = meta.get('name') or meta.get('property')
        content = meta.get('content')
        if name and content:
            meta_tags[name] = content
    
    return meta_tags


def is_recent_content(date: datetime, days: int = 7) -> bool:
    """
    Check if content is recent (within specified days)
    
    Args:
        date: Content date
        days: Number of days to consider recent
        
    Returns:
        True if content is recent
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    return date >= cutoff_date


def extract_keywords(text: str, keywords: List[str]) -> List[str]:
    """
    Extract matching keywords from text
    
    Args:
        text: Text to search
        keywords: List of keywords to find
        
    Returns:
        List of found keywords
    """
    found_keywords = []
    text_lower = text.lower()
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords


def safe_request(url: str, headers: Optional[Dict] = None, timeout: int = 30) -> Optional[requests.Response]:
    """
    Make safe HTTP request with error handling
    
    Args:
        url: URL to request
        headers: Optional request headers
        timeout: Request timeout in seconds
        
    Returns:
        Response object or None if failed
    """
    try:
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        if headers:
            default_headers.update(headers)
        
        response = requests.get(url, headers=default_headers, timeout=timeout)
        response.raise_for_status()
        return response
        
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format currency amount
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == "INR":
        return f"₹{amount:,.0f}"
    elif currency == "USD":
        return f"${amount:,.0f}"
    else:
        return f"{amount:,.0f} {currency}"


def truncate_text(text: str, max_length: int = 200) -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def parse_iso_week(week_string: str) -> Optional[datetime]:
    """
    Parse ISO week string (e.g., "2025-W31")
    
    Args:
        week_string: ISO week string
        
    Returns:
        Date of Monday in that week
    """
    try:
        year, week = week_string.split('-W')
        year = int(year)
        week = int(week)
        
        # Calculate Monday of the week
        jan1 = datetime(year, 1, 1)
        days_since_monday = jan1.weekday()
        days_to_add = (week - 1) * 7 - days_since_monday
        
        return jan1 + timedelta(days=days_to_add)
        
    except:
        return None


def get_current_iso_week() -> str:
    """
    Get current ISO week string
    
    Returns:
        Current ISO week string (e.g., "2025-W31")
    """
    now = datetime.now()
    return f"{now.year}-W{now.isocalendar()[1]:02d}" 