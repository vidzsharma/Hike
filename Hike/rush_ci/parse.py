"""
Data parsing module for Rush Gaming CI System

Processes raw fetched data and extracts key insights using NLP and keyword analysis.
"""

import re
import spacy
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

from .config import config
from .utils.logger import get_logger
from .utils.helpers import clean_text, extract_keywords, is_recent_content

logger = get_logger(__name__)

# Load spaCy model for NLP processing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None


class DataParser:
    """Main data parsing class for competitor intelligence"""
    
    def __init__(self):
        self.alert_keywords = self._extract_alert_keywords()
        self.product_keywords = self._extract_product_keywords()
        
    def parse_all_data(self, raw_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Parse all raw data and extract insights
        
        Args:
            raw_data: Raw data from fetch module
            
        Returns:
            Parsed data with insights and alerts
        """
        logger.info("Starting data parsing")
        
        parsed_data = {
            'insights': {},
            'alerts': [],
            'summaries': {},
            'trends': {}
        }
        
        # Parse each data type
        if raw_data.get('blogs'):
            parsed_data['insights']['blogs'] = self.parse_blogs(raw_data['blogs'])
        
        if raw_data.get('tweets'):
            parsed_data['insights']['tweets'] = self.parse_tweets(raw_data['tweets'])
        
        if raw_data.get('linkedin'):
            parsed_data['insights']['linkedin'] = self.parse_linkedin_posts(raw_data['linkedin'])
        
        if raw_data.get('jobs'):
            parsed_data['insights']['jobs'] = self.parse_jobs(raw_data['jobs'])
        
        # Generate alerts
        parsed_data['alerts'] = self.generate_alerts(raw_data)
        
        # Generate company summaries
        parsed_data['summaries'] = self.generate_company_summaries(parsed_data['insights'])
        
        # Analyze trends
        parsed_data['trends'] = self.analyze_trends(parsed_data['insights'])
        
        logger.info("Data parsing completed")
        return parsed_data
    
    def parse_blogs(self, blogs: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Parse blog posts and extract insights
        
        Args:
            blogs: List of blog post data
            
        Returns:
            Parsed blog insights by company
        """
        parsed_blogs = defaultdict(list)
        
        for blog in blogs:
            company = blog.get('company', 'Unknown')
            
            # Extract key information
            parsed_blog = {
                'title': blog.get('title', ''),
                'url': blog.get('url', ''),
                'content': blog.get('content', ''),
                'published_at': blog.get('published_at'),
                'source': blog.get('source', ''),
                'keywords': self._extract_keywords_from_text(blog.get('title', '') + ' ' + blog.get('content', '')),
                'entities': self._extract_entities(blog.get('title', '') + ' ' + blog.get('content', '')),
                'sentiment': self._analyze_sentiment(blog.get('title', '') + ' ' + blog.get('content', '')),
                'alert_level': self._determine_alert_level(blog.get('title', '') + ' ' + blog.get('content', '')),
                'product_mentions': self._extract_product_mentions(blog.get('title', '') + ' ' + blog.get('content', '')),
                'funding_mentions': self._extract_funding_mentions(blog.get('title', '') + ' ' + blog.get('content', '')),
                'partnership_mentions': self._extract_partnership_mentions(blog.get('title', '') + ' ' + blog.get('content', ''))
            }
            
            parsed_blogs[company].append(parsed_blog)
        
        return dict(parsed_blogs)
    
    def parse_tweets(self, tweets: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Parse tweets and extract insights
        
        Args:
            tweets: List of tweet data
            
        Returns:
            Parsed tweet insights by company
        """
        parsed_tweets = defaultdict(list)
        
        for tweet in tweets:
            company = tweet.get('company', 'Unknown')
            
            # Extract key information
            parsed_tweet = {
                'tweet_id': tweet.get('tweet_id', ''),
                'text': tweet.get('text', ''),
                'created_at': tweet.get('created_at'),
                'metrics': tweet.get('metrics', {}),
                'keywords': self._extract_keywords_from_text(tweet.get('text', '')),
                'entities': self._extract_entities(tweet.get('text', '')),
                'sentiment': self._analyze_sentiment(tweet.get('text', '')),
                'alert_level': self._determine_alert_level(tweet.get('text', '')),
                'engagement_score': self._calculate_engagement_score(tweet.get('metrics', {})),
                'hashtags': self._extract_hashtags(tweet.get('text', '')),
                'mentions': self._extract_mentions(tweet.get('text', ''))
            }
            
            parsed_tweets[company].append(parsed_tweet)
        
        return dict(parsed_tweets)
    
    def parse_linkedin_posts(self, linkedin_posts: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Parse LinkedIn posts and extract insights
        
        Args:
            linkedin_posts: List of LinkedIn post data
            
        Returns:
            Parsed LinkedIn insights by company
        """
        parsed_linkedin = defaultdict(list)
        
        for post in linkedin_posts:
            company = post.get('company', 'Unknown')
            
            # Extract key information
            parsed_post = {
                'post_id': post.get('post_id', ''),
                'text': post.get('text', ''),
                'created_at': post.get('created_at'),
                'reactions': post.get('reactions', {}),
                'keywords': self._extract_keywords_from_text(post.get('text', '')),
                'entities': self._extract_entities(post.get('text', '')),
                'sentiment': self._analyze_sentiment(post.get('text', '')),
                'alert_level': self._determine_alert_level(post.get('text', '')),
                'engagement_score': self._calculate_linkedin_engagement(post.get('reactions', {}))
            }
            
            parsed_linkedin[company].append(parsed_post)
        
        return dict(parsed_linkedin)
    
    def parse_jobs(self, jobs: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Parse job postings and extract insights
        
        Args:
            jobs: List of job data
            
        Returns:
            Parsed job insights by company
        """
        parsed_jobs = defaultdict(list)
        
        for job in jobs:
            company = job.get('company', 'Unknown')
            
            # Extract key information
            parsed_job = {
                'role': job.get('role', ''),
                'location': job.get('location', ''),
                'posted_at': job.get('posted_at'),
                'url': job.get('url', ''),
                'department': self._extract_department(job.get('role', '')),
                'seniority': self._determine_seniority(job.get('role', '')),
                'keywords': self._extract_keywords_from_text(job.get('role', '')),
                'alert_level': self._determine_job_alert_level(job.get('role', '')),
                'is_remote': self._check_remote_work(job.get('location', '')),
                'is_international': self._check_international_expansion(job.get('location', ''))
            }
            
            parsed_jobs[company].append(parsed_job)
        
        return dict(parsed_jobs)
    
    def generate_alerts(self, raw_data: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """
        Generate alerts based on raw data
        
        Args:
            raw_data: Raw data from fetch module
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Check all data sources for alert conditions
        for source_type, items in raw_data.items():
            for item in items:
                alert = self._check_alert_conditions(item, source_type)
                if alert:
                    alerts.append(alert)
        
        # Sort alerts by priority
        alerts.sort(key=lambda x: self._get_alert_priority(x['level']), reverse=True)
        
        return alerts
    
    def generate_company_summaries(self, insights: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Generate company-specific summaries
        
        Args:
            insights: Parsed insights by company
            
        Returns:
            Company summaries
        """
        summaries = {}
        
        for company, company_insights in insights.items():
            summary = {
                'company': company,
                'total_mentions': sum(len(items) for items in company_insights.values()),
                'key_themes': self._extract_key_themes(company_insights),
                'product_updates': self._extract_product_updates(company_insights),
                'hiring_trends': self._analyze_hiring_trends(company_insights.get('jobs', [])),
                'engagement_metrics': self._calculate_overall_engagement(company_insights),
                'alert_summary': self._summarize_alerts(company_insights)
            }
            summaries[company] = summary
        
        return summaries
    
    def analyze_trends(self, insights: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Analyze cross-company trends
        
        Args:
            insights: Parsed insights by company
            
        Returns:
            Trend analysis
        """
        trends = {
            'common_themes': self._find_common_themes(insights),
            'market_movements': self._identify_market_movements(insights),
            'competitive_gaps': self._identify_competitive_gaps(insights),
            'opportunity_areas': self._identify_opportunities(insights)
        }
        
        return trends
    
    def _extract_alert_keywords(self) -> Dict[str, List[str]]:
        """Extract alert keywords from configuration"""
        keywords = {}
        for priority, rules in config.alert_rules.items():
            keywords[priority] = []
            for pattern in rules.get('keywords', []):
                # Extract keywords from regex patterns
                keyword = pattern.replace(r'(?i)', '').replace(r'\(', '').replace(r'\)', '').replace(r'\|', ' ').replace(r'\?', '')
                keywords[priority].extend(keyword.split())
        return keywords
    
    def _extract_product_keywords(self) -> List[str]:
        """Extract product-related keywords"""
        return [
            'launch', 'update', 'feature', 'release', 'beta', 'new', 'improved',
            'enhanced', 'upgraded', 'version', 'app', 'game', 'platform'
        ]
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        if not text:
            return []
        
        # Use spaCy for keyword extraction if available
        if nlp:
            doc = nlp(text.lower())
            keywords = []
            
            # Extract nouns, verbs, and adjectives
            for token in doc:
                if token.pos_ in ['NOUN', 'VERB', 'ADJ'] and not token.is_stop and len(token.text) > 3:
                    keywords.append(token.text)
            
            return list(set(keywords))[:10]  # Top 10 keywords
        
        # Fallback to simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if len(word) > 3][:10]
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        if not text or not nlp:
            return {}
        
        doc = nlp(text)
        entities = defaultdict(list)
        
        for ent in doc.ents:
            entities[ent.label_].append(ent.text)
        
        return dict(entities)
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        if not text:
            return 'neutral'
        
        # Simple sentiment analysis based on keywords
        positive_words = ['launch', 'success', 'growth', 'partnership', 'innovation', 'win']
        negative_words = ['down', 'loss', 'failure', 'problem', 'issue', 'challenge']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _determine_alert_level(self, text: str) -> str:
        """Determine alert level based on text content"""
        if not text:
            return 'low'
        
        text_lower = text.lower()
        
        # High priority keywords
        high_priority = ['funding', 'series', 'acquired', 'launch', 'token', 'nft', 'c-level', 'vp', 'chief']
        if any(keyword in text_lower for keyword in high_priority):
            return 'high'
        
        # Medium priority keywords
        medium_priority = ['hiring', 'partnership', 'expansion', 'collaboration']
        if any(keyword in text_lower for keyword in medium_priority):
            return 'medium'
        
        return 'low'
    
    def _extract_product_mentions(self, text: str) -> List[str]:
        """Extract product mentions from text"""
        return extract_keywords(text, self.product_keywords)
    
    def _extract_funding_mentions(self, text: str) -> List[str]:
        """Extract funding-related mentions"""
        funding_keywords = ['funding', 'series', 'seed', 'investment', 'raise', 'backed']
        return extract_keywords(text, funding_keywords)
    
    def _extract_partnership_mentions(self, text: str) -> List[str]:
        """Extract partnership mentions"""
        partnership_keywords = ['partnership', 'collaboration', 'tie-up', 'alliance', 'joint']
        return extract_keywords(text, partnership_keywords)
    
    def _calculate_engagement_score(self, metrics: Dict) -> float:
        """Calculate engagement score for tweets"""
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        return (likes + retweets * 2 + replies * 3) / 100  # Normalized score
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        return re.findall(r'#\w+', text)
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        return re.findall(r'@\w+', text)
    
    def _calculate_linkedin_engagement(self, reactions: Dict) -> float:
        """Calculate LinkedIn engagement score"""
        total_reactions = sum(reactions.values())
        return total_reactions / 100  # Normalized score
    
    def _extract_department(self, role: str) -> str:
        """Extract department from job role"""
        role_lower = role.lower()
        
        departments = {
            'engineering': ['engineer', 'developer', 'programmer', 'tech'],
            'marketing': ['marketing', 'growth', 'brand', 'pr'],
            'sales': ['sales', 'business development', 'bd'],
            'product': ['product', 'pm', 'product manager'],
            'design': ['design', 'ux', 'ui', 'creative'],
            'operations': ['operations', 'ops', 'strategy'],
            'finance': ['finance', 'accounting', 'cfo'],
            'hr': ['hr', 'recruitment', 'talent', 'people']
        }
        
        for dept, keywords in departments.items():
            if any(keyword in role_lower for keyword in keywords):
                return dept
        
        return 'other'
    
    def _determine_seniority(self, role: str) -> str:
        """Determine job seniority level"""
        role_lower = role.lower()
        
        if any(word in role_lower for word in ['intern', 'internship']):
            return 'intern'
        elif any(word in role_lower for word in ['junior', 'entry', 'associate']):
            return 'junior'
        elif any(word in role_lower for word in ['senior', 'lead', 'principal']):
            return 'senior'
        elif any(word in role_lower for word in ['manager', 'director', 'head']):
            return 'manager'
        elif any(word in role_lower for word in ['vp', 'vice president', 'chief', 'c-level']):
            return 'executive'
        else:
            return 'mid'
    
    def _determine_job_alert_level(self, role: str) -> str:
        """Determine alert level for job postings"""
        role_lower = role.lower()
        
        if any(word in role_lower for word in ['vp', 'vice president', 'chief', 'c-level', 'head']):
            return 'high'
        elif any(word in role_lower for word in ['director', 'manager', 'lead']):
            return 'medium'
        else:
            return 'low'
    
    def _check_remote_work(self, location: str) -> bool:
        """Check if job is remote"""
        location_lower = location.lower()
        return any(word in location_lower for word in ['remote', 'work from home', 'wfh'])
    
    def _check_international_expansion(self, location: str) -> bool:
        """Check if job indicates international expansion"""
        international_keywords = ['us', 'usa', 'united states', 'uk', 'europe', 'singapore', 'dubai']
        location_lower = location.lower()
        return any(keyword in location_lower for keyword in international_keywords)
    
    def _check_alert_conditions(self, item: Dict, source_type: str) -> Optional[Dict]:
        """Check if item meets alert conditions"""
        text = ''
        
        if source_type == 'blogs':
            text = item.get('title', '') + ' ' + item.get('content', '')
        elif source_type == 'tweets':
            text = item.get('text', '')
        elif source_type == 'linkedin':
            text = item.get('text', '')
        elif source_type == 'jobs':
            text = item.get('role', '')
        
        alert_level = self._determine_alert_level(text)
        
        if alert_level != 'low':
            return {
                'level': alert_level,
                'company': item.get('company', 'Unknown'),
                'source_type': source_type,
                'text': text[:200] + '...' if len(text) > 200 else text,
                'timestamp': datetime.now(),
                'url': item.get('url', ''),
                'keywords': self._extract_keywords_from_text(text)
            }
        
        return None
    
    def _get_alert_priority(self, level: str) -> int:
        """Get numeric priority for alert level"""
        priorities = {'high': 3, 'medium': 2, 'low': 1}
        return priorities.get(level, 0)
    
    def _extract_key_themes(self, company_insights: Dict) -> List[str]:
        """Extract key themes from company insights"""
        all_text = ''
        
        for source_type, items in company_insights.items():
            for item in items:
                if source_type == 'blogs':
                    all_text += ' ' + item.get('title', '') + ' ' + item.get('content', '')
                elif source_type == 'tweets':
                    all_text += ' ' + item.get('text', '')
                elif source_type == 'linkedin':
                    all_text += ' ' + item.get('text', '')
        
        return self._extract_keywords_from_text(all_text)[:5]
    
    def _extract_product_updates(self, company_insights: Dict) -> List[Dict]:
        """Extract product updates from company insights"""
        updates = []
        
        for source_type, items in company_insights.items():
            for item in items:
                if source_type == 'blogs':
                    text = item.get('title', '') + ' ' + item.get('content', '')
                elif source_type == 'tweets':
                    text = item.get('text', '')
                elif source_type == 'linkedin':
                    text = item.get('text', '')
                else:
                    continue
                
                if any(keyword in text.lower() for keyword in self.product_keywords):
                    updates.append({
                        'title': item.get('title', ''),
                        'text': text[:100] + '...' if len(text) > 100 else text,
                        'source_type': source_type,
                        'timestamp': item.get('published_at') or item.get('created_at')
                    })
        
        return updates
    
    def _analyze_hiring_trends(self, jobs: List[Dict]) -> Dict:
        """Analyze hiring trends from job postings"""
        if not jobs:
            return {}
        
        departments = defaultdict(int)
        seniority_levels = defaultdict(int)
        remote_count = 0
        international_count = 0
        
        for job in jobs:
            departments[job.get('department', 'other')] += 1
            seniority_levels[job.get('seniority', 'mid')] += 1
            
            if job.get('is_remote'):
                remote_count += 1
            
            if job.get('is_international'):
                international_count += 1
        
        return {
            'total_jobs': len(jobs),
            'departments': dict(departments),
            'seniority_levels': dict(seniority_levels),
            'remote_percentage': (remote_count / len(jobs)) * 100 if jobs else 0,
            'international_percentage': (international_count / len(jobs)) * 100 if jobs else 0
        }
    
    def _calculate_overall_engagement(self, company_insights: Dict) -> Dict:
        """Calculate overall engagement metrics"""
        total_engagement = 0
        total_posts = 0
        
        for source_type, items in company_insights.items():
            for item in items:
                if source_type == 'tweets':
                    total_engagement += item.get('engagement_score', 0)
                    total_posts += 1
                elif source_type == 'linkedin':
                    total_engagement += item.get('engagement_score', 0)
                    total_posts += 1
        
        return {
            'total_engagement': total_engagement,
            'total_posts': total_posts,
            'avg_engagement': total_engagement / total_posts if total_posts > 0 else 0
        }
    
    def _summarize_alerts(self, company_insights: Dict) -> Dict:
        """Summarize alerts for company"""
        alert_counts = defaultdict(int)
        
        for source_type, items in company_insights.items():
            for item in items:
                alert_level = item.get('alert_level', 'low')
                alert_counts[alert_level] += 1
        
        return dict(alert_counts)
    
    def _find_common_themes(self, insights: Dict) -> List[str]:
        """Find common themes across all companies"""
        all_text = ''
        
        for company, company_insights in insights.items():
            for source_type, items in company_insights.items():
                for item in items:
                    if source_type == 'blogs':
                        all_text += ' ' + item.get('title', '') + ' ' + item.get('content', '')
                    elif source_type == 'tweets':
                        all_text += ' ' + item.get('text', '')
                    elif source_type == 'linkedin':
                        all_text += ' ' + item.get('text', '')
        
        return self._extract_keywords_from_text(all_text)[:10]
    
    def _identify_market_movements(self, insights: Dict) -> List[str]:
        """Identify market movements from insights"""
        movements = []
        
        # Check for funding announcements
        funding_companies = []
        for company, company_insights in insights.items():
            for source_type, items in company_insights.items():
                for item in items:
                    if source_type == 'blogs':
                        text = item.get('title', '') + ' ' + item.get('content', '')
                    elif source_type == 'tweets':
                        text = item.get('text', '')
                    else:
                        continue
                    
                    if any(keyword in text.lower() for keyword in ['funding', 'series', 'raise']):
                        funding_companies.append(company)
        
        if funding_companies:
            movements.append(f"Funding activity: {', '.join(set(funding_companies))}")
        
        # Check for product launches
        launch_companies = []
        for company, company_insights in insights.items():
            for source_type, items in company_insights.items():
                for item in items:
                    if source_type == 'blogs':
                        text = item.get('title', '') + ' ' + item.get('content', '')
                    elif source_type == 'tweets':
                        text = item.get('text', '')
                    else:
                        continue
                    
                    if any(keyword in text.lower() for keyword in ['launch', 'new feature', 'release']):
                        launch_companies.append(company)
        
        if launch_companies:
            movements.append(f"Product launches: {', '.join(set(launch_companies))}")
        
        return movements
    
    def _identify_competitive_gaps(self, insights: Dict) -> List[str]:
        """Identify competitive gaps and opportunities"""
        gaps = []
        
        # Analyze hiring patterns
        engineering_focus = []
        marketing_focus = []
        
        for company, company_insights in insights.items():
            jobs = company_insights.get('jobs', [])
            if jobs:
                hiring_trends = self._analyze_hiring_trends(jobs)
                if hiring_trends.get('departments', {}).get('engineering', 0) > 5:
                    engineering_focus.append(company)
                if hiring_trends.get('departments', {}).get('marketing', 0) > 3:
                    marketing_focus.append(company)
        
        if engineering_focus:
            gaps.append(f"Engineering focus: {', '.join(engineering_focus)}")
        if marketing_focus:
            gaps.append(f"Marketing focus: {', '.join(marketing_focus)}")
        
        return gaps
    
    def _identify_opportunities(self, insights: Dict) -> List[str]:
        """Identify opportunity areas for Rush"""
        opportunities = []
        
        # Check for market gaps
        all_products = set()
        for company, company_insights in insights.items():
            for source_type, items in company_insights.items():
                for item in items:
                    if source_type == 'blogs':
                        text = item.get('title', '') + ' ' + item.get('content', '')
                    elif source_type == 'tweets':
                        text = item.get('text', '')
                    else:
                        continue
                    
                    products = self._extract_product_mentions(text)
                    all_products.update(products)
        
        # Identify underserved areas
        rush_products = ['ludo', 'rummy', 'carrom']  # Rush's current products
        competitor_products = list(all_products)
        
        opportunities.append(f"Competitor products: {', '.join(competitor_products[:5])}")
        
        return opportunities


def main():
    """Main function to run data parsing"""
    logger.info("Starting Rush Gaming CI data parsing")
    
    # Load raw data (this would come from fetch module)
    try:
        with open('data/raw_fetch_data.json', 'r') as f:
            import json
            raw_data = json.load(f)
    except FileNotFoundError:
        logger.warning("No raw data found. Creating sample data for testing.")
        raw_data = {
            'blogs': [],
            'tweets': [],
            'linkedin': [],
            'jobs': []
        }
    
    parser = DataParser()
    parsed_data = parser.parse_all_data(raw_data)
    
    # Save parsed data
    with open('data/parsed_data.json', 'w') as f:
        json.dump(parsed_data, f, default=str, indent=2)
    
    logger.info("Data parsing completed")
    return parsed_data


if __name__ == "__main__":
    main() 