"""
Data storage module for Rush Gaming CI System

Saves parsed data to Airtable and Notion databases.
"""

import json
import redis
from datetime import datetime
from typing import Dict, List, Any, Optional
from airtable import Airtable
from notion_client import Client

from .config import config
from .utils.logger import get_logger
from .utils.helpers import generate_content_hash

logger = get_logger(__name__)


class DataStore:
    """Main data storage class for competitor intelligence"""
    
    def __init__(self):
        self.redis_client = self._init_redis()
        self.airtable_client = self._init_airtable()
        self.notion_client = self._init_notion()
        
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis client for deduplication"""
        try:
            if config.redis_url:
                return redis.from_url(config.redis_url)
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
        return None
    
    def _init_airtable(self) -> Optional[Airtable]:
        """Initialize Airtable client"""
        try:
            if config.airtable_api_key and config.airtable_base_id:
                return Airtable(config.airtable_base_id, config.airtable_api_key)
        except Exception as e:
            logger.error(f"Airtable initialization failed: {e}")
        return None
    
    def _init_notion(self) -> Optional[Client]:
        """Initialize Notion client"""
        try:
            if config.notion_api_key:
                return Client(auth=config.notion_api_key)
        except Exception as e:
            logger.error(f"Notion initialization failed: {e}")
        return None
    
    def store_all_data(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Store all parsed data to databases
        
        Args:
            parsed_data: Parsed data from parse module
            
        Returns:
            Success status
        """
        logger.info("Starting data storage")
        
        success = True
        
        try:
            # Store raw data to Airtable
            if self.airtable_client:
                success &= self._store_to_airtable(parsed_data)
            
            # Store summaries to Notion
            if self.notion_client:
                success &= self._store_to_notion(parsed_data)
            
            # Store deduplication hashes to Redis
            if self.redis_client:
                success &= self._store_deduplication_hashes(parsed_data)
            
        except Exception as e:
            logger.error(f"Error in data storage: {e}")
            success = False
        
        logger.info("Data storage completed")
        return success
    
    def _store_to_airtable(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Store data to Airtable base
        
        Args:
            parsed_data: Parsed data
            
        Returns:
            Success status
        """
        try:
            insights = parsed_data.get('insights', {})
            
            # Store blogs
            if 'blogs' in insights:
                self._store_blogs_to_airtable(insights['blogs'])
            
            # Store tweets
            if 'tweets' in insights:
                self._store_tweets_to_airtable(insights['tweets'])
            
            # Store LinkedIn posts
            if 'linkedin' in insights:
                self._store_linkedin_to_airtable(insights['linkedin'])
            
            # Store jobs
            if 'jobs' in insights:
                self._store_jobs_to_airtable(insights['jobs'])
            
            logger.info("Data stored to Airtable successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error storing to Airtable: {e}")
            return False
    
    def _store_blogs_to_airtable(self, blogs_data: Dict[str, List[Dict]]) -> None:
        """Store blog data to Airtable"""
        for company, blogs in blogs_data.items():
            for blog in blogs:
                # Check for duplicates
                if self._is_duplicate('blogs', blog.get('content_hash', '')):
                    continue
                
                record = {
                    'title': blog.get('title', ''),
                    'url': blog.get('url', ''),
                    'content': blog.get('content', ''),
                    'company': company,
                    'published_at': blog.get('published_at', datetime.now()).isoformat(),
                    'source': blog.get('source', ''),
                    'keywords': ', '.join(blog.get('keywords', [])),
                    'sentiment': blog.get('sentiment', 'neutral'),
                    'alert_level': blog.get('alert_level', 'low')
                }
                
                try:
                    self.airtable_client.insert('Blogs', record)
                except Exception as e:
                    logger.error(f"Error inserting blog record: {e}")
    
    def _store_tweets_to_airtable(self, tweets_data: Dict[str, List[Dict]]) -> None:
        """Store tweet data to Airtable"""
        for company, tweets in tweets_data.items():
            for tweet in tweets:
                # Check for duplicates
                if self._is_duplicate('tweets', tweet.get('content_hash', '')):
                    continue
                
                record = {
                    'tweet_id': tweet.get('tweet_id', ''),
                    'text': tweet.get('text', ''),
                    'company': company,
                    'created_at': tweet.get('created_at', datetime.now()).isoformat(),
                    'metrics': json.dumps(tweet.get('metrics', {})),
                    'keywords': ', '.join(tweet.get('keywords', [])),
                    'sentiment': tweet.get('sentiment', 'neutral'),
                    'alert_level': tweet.get('alert_level', 'low'),
                    'engagement_score': tweet.get('engagement_score', 0)
                }
                
                try:
                    self.airtable_client.insert('Tweets', record)
                except Exception as e:
                    logger.error(f"Error inserting tweet record: {e}")
    
    def _store_linkedin_to_airtable(self, linkedin_data: Dict[str, List[Dict]]) -> None:
        """Store LinkedIn data to Airtable"""
        for company, posts in linkedin_data.items():
            for post in posts:
                # Check for duplicates
                if self._is_duplicate('linkedin', post.get('content_hash', '')):
                    continue
                
                record = {
                    'post_id': post.get('post_id', ''),
                    'text': post.get('text', ''),
                    'company': company,
                    'created_at': post.get('created_at', datetime.now()).isoformat(),
                    'reactions': json.dumps(post.get('reactions', {})),
                    'keywords': ', '.join(post.get('keywords', [])),
                    'sentiment': post.get('sentiment', 'neutral'),
                    'alert_level': post.get('alert_level', 'low'),
                    'engagement_score': post.get('engagement_score', 0)
                }
                
                try:
                    self.airtable_client.insert('LinkedIn', record)
                except Exception as e:
                    logger.error(f"Error inserting LinkedIn record: {e}")
    
    def _store_jobs_to_airtable(self, jobs_data: Dict[str, List[Dict]]) -> None:
        """Store job data to Airtable"""
        for company, jobs in jobs_data.items():
            for job in jobs:
                # Check for duplicates
                if self._is_duplicate('jobs', job.get('content_hash', '')):
                    continue
                
                record = {
                    'role': job.get('role', ''),
                    'company': company,
                    'location': job.get('location', ''),
                    'posted_at': job.get('posted_at', datetime.now()).isoformat(),
                    'url': job.get('url', ''),
                    'department': job.get('department', ''),
                    'seniority': job.get('seniority', ''),
                    'keywords': ', '.join(job.get('keywords', [])),
                    'alert_level': job.get('alert_level', 'low'),
                    'is_remote': job.get('is_remote', False),
                    'is_international': job.get('is_international', False)
                }
                
                try:
                    self.airtable_client.insert('Jobs', record)
                except Exception as e:
                    logger.error(f"Error inserting job record: {e}")
    
    def _store_to_notion(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Store summaries to Notion database
        
        Args:
            parsed_data: Parsed data
            
        Returns:
            Success status
        """
        try:
            summaries = parsed_data.get('summaries', {})
            alerts = parsed_data.get('alerts', [])
            
            # Store company summaries
            for company, summary in summaries.items():
                self._store_company_summary_to_notion(company, summary)
            
            # Store high-priority alerts
            high_priority_alerts = [alert for alert in alerts if alert.get('level') == 'high']
            for alert in high_priority_alerts:
                self._store_alert_to_notion(alert)
            
            logger.info("Data stored to Notion successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error storing to Notion: {e}")
            return False
    
    def _store_company_summary_to_notion(self, company: str, summary: Dict[str, Any]) -> None:
        """Store company summary to Notion"""
        try:
            # Get current week
            from .utils.helpers import get_current_iso_week
            current_week = get_current_iso_week()
            
            # Check if summary already exists for this week
            existing_pages = self.notion_client.databases.query(
                database_id=config.notion_database_id,
                filter={
                    "and": [
                        {
                            "property": "Company",
                            "select": {
                                "equals": company
                            }
                        },
                        {
                            "property": "Week",
                            "date": {
                                "equals": current_week
                            }
                        }
                    ]
                }
            )
            
            if existing_pages.get('results'):
                # Update existing page
                page_id = existing_pages['results'][0]['id']
                self.notion_client.pages.update(
                    page_id=page_id,
                    properties={
                        "What They Shipped": {
                            "rich_text": [{
                                "text": {
                                    "content": self._format_product_updates(summary.get('product_updates', []))
                                }
                            }]
                        },
                        "Who They Hired": {
                            "rich_text": [{
                                "text": {
                                    "content": self._format_hiring_trends(summary.get('hiring_trends', {}))
                                }
                            }]
                        },
                        "Signals & Narrative": {
                            "rich_text": [{
                                "text": {
                                    "content": self._format_key_themes(summary.get('key_themes', []))
                                }
                            }]
                        },
                        "Alert Level": {
                            "select": {
                                "name": self._determine_overall_alert_level(summary)
                            }
                        }
                    }
                )
            else:
                # Create new page
                self.notion_client.pages.create(
                    parent={"database_id": config.notion_database_id},
                    properties={
                        "Company": {
                            "select": {
                                "name": company
                            }
                        },
                        "Week": {
                            "date": {
                                "start": current_week
                            }
                        },
                        "What They Shipped": {
                            "rich_text": [{
                                "text": {
                                    "content": self._format_product_updates(summary.get('product_updates', []))
                                }
                            }]
                        },
                        "Who They Hired": {
                            "rich_text": [{
                                "text": {
                                    "content": self._format_hiring_trends(summary.get('hiring_trends', {}))
                                }
                            }]
                        },
                        "Signals & Narrative": {
                            "rich_text": [{
                                "text": {
                                    "content": self._format_key_themes(summary.get('key_themes', []))
                                }
                            }]
                        },
                        "Alert Level": {
                            "select": {
                                "name": self._determine_overall_alert_level(summary)
                            }
                        }
                    }
                )
                
        except Exception as e:
            logger.error(f"Error storing company summary to Notion: {e}")
    
    def _store_alert_to_notion(self, alert: Dict[str, Any]) -> None:
        """Store high-priority alert to Notion"""
        try:
            self.notion_client.pages.create(
                parent={"database_id": config.notion_database_id},
                properties={
                    "Company": {
                        "select": {
                            "name": alert.get('company', 'Unknown')
                        }
                    },
                    "Week": {
                        "date": {
                            "start": datetime.now().isoformat()
                        }
                    },
                    "What They Shipped": {
                        "rich_text": [{
                            "text": {
                                "content": f"🚨 ALERT: {alert.get('text', '')}"
                            }
                        }]
                    },
                    "Who They Hired": {
                        "rich_text": [{
                            "text": {
                                "content": f"Source: {alert.get('source_type', '')}"
                            }
                        }]
                    },
                    "Signals & Narrative": {
                        "rich_text": [{
                            "text": {
                                "content": f"Keywords: {', '.join(alert.get('keywords', []))}"
                            }
                        }]
                    },
                    "Alert Level": {
                        "select": {
                            "name": alert.get('level', 'medium').title()
                        }
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing alert to Notion: {e}")
    
    def _store_deduplication_hashes(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Store content hashes to Redis for deduplication
        
        Args:
            parsed_data: Parsed data
            
        Returns:
            Success status
        """
        try:
            insights = parsed_data.get('insights', {})
            
            for source_type, data in insights.items():
                for company, items in data.items():
                    for item in items:
                        content_hash = item.get('content_hash', '')
                        if content_hash:
                            # Store hash with 7-day expiration
                            key = f"{source_type}:{content_hash}"
                            self.redis_client.setex(key, 7 * 24 * 60 * 60, '1')
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing deduplication hashes: {e}")
            return False
    
    def _is_duplicate(self, source_type: str, content_hash: str) -> bool:
        """
        Check if content is duplicate using Redis
        
        Args:
            source_type: Type of content (blogs, tweets, etc.)
            content_hash: Content hash
            
        Returns:
            True if duplicate
        """
        if not self.redis_client or not content_hash:
            return False
        
        try:
            key = f"{source_type}:{content_hash}"
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking duplicate: {e}")
            return False
    
    def _format_product_updates(self, updates: List[Dict]) -> str:
        """Format product updates for Notion"""
        if not updates:
            return "No product updates detected this week."
        
        formatted = []
        for update in updates[:5]:  # Top 5 updates
            formatted.append(f"• {update.get('title', '')}: {update.get('text', '')}")
        
        return "\n".join(formatted)
    
    def _format_hiring_trends(self, trends: Dict) -> str:
        """Format hiring trends for Notion"""
        if not trends:
            return "No hiring activity detected this week."
        
        total_jobs = trends.get('total_jobs', 0)
        if total_jobs == 0:
            return "No hiring activity detected this week."
        
        formatted = [f"Total jobs posted: {total_jobs}"]
        
        # Top departments
        departments = trends.get('departments', {})
        if departments:
            top_depts = sorted(departments.items(), key=lambda x: x[1], reverse=True)[:3]
            formatted.append("Top departments:")
            for dept, count in top_depts:
                formatted.append(f"• {dept}: {count}")
        
        # Seniority levels
        seniority = trends.get('seniority_levels', {})
        if seniority:
            formatted.append("Seniority breakdown:")
            for level, count in seniority.items():
                formatted.append(f"• {level}: {count}")
        
        return "\n".join(formatted)
    
    def _format_key_themes(self, themes: List[str]) -> str:
        """Format key themes for Notion"""
        if not themes:
            return "No key themes identified this week."
        
        return "Key themes: " + ", ".join(themes[:5])
    
    def _determine_overall_alert_level(self, summary: Dict) -> str:
        """Determine overall alert level for company"""
        alert_summary = summary.get('alert_summary', {})
        
        if alert_summary.get('high', 0) > 0:
            return 'High'
        elif alert_summary.get('medium', 0) > 2:
            return 'Medium'
        else:
            return 'Low'
    
    def get_stored_data(self, source_type: str, company: str = None, limit: int = 50) -> List[Dict]:
        """
        Retrieve stored data from Airtable
        
        Args:
            source_type: Type of data (blogs, tweets, linkedin, jobs)
            company: Optional company filter
            limit: Maximum number of records
            
        Returns:
            List of stored records
        """
        if not self.airtable_client:
            return []
        
        try:
            table_name = source_type.title()
            records = self.airtable_client.get(table_name, max_records=limit)
            
            if company:
                records = [r for r in records if r.get('fields', {}).get('company') == company]
            
            return records
            
        except Exception as e:
            logger.error(f"Error retrieving data from Airtable: {e}")
            return []
    
    def export_data(self, format: str = 'json') -> str:
        """
        Export all stored data
        
        Args:
            format: Export format (json, csv)
            
        Returns:
            Export file path
        """
        try:
            all_data = {}
            
            for source_type in ['blogs', 'tweets', 'linkedin', 'jobs']:
                all_data[source_type] = self.get_stored_data(source_type)
            
            if format == 'json':
                file_path = f'data/export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                with open(file_path, 'w') as f:
                    json.dump(all_data, f, default=str, indent=2)
            
            logger.info(f"Data exported to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return ""


def main():
    """Main function to run data storage"""
    logger.info("Starting Rush Gaming CI data storage")
    
    # Load parsed data (this would come from parse module)
    try:
        with open('data/parsed_data.json', 'r') as f:
            parsed_data = json.load(f)
    except FileNotFoundError:
        logger.warning("No parsed data found. Creating sample data for testing.")
        parsed_data = {
            'insights': {},
            'alerts': [],
            'summaries': {},
            'trends': {}
        }
    
    store = DataStore()
    success = store.store_all_data(parsed_data)
    
    if success:
        logger.info("Data storage completed successfully")
    else:
        logger.error("Data storage failed")
    
    return success


if __name__ == "__main__":
    main() 