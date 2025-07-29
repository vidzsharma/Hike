"""
Configuration management for Rush Gaming CI System
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class for the CI system"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        
        # API Keys
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Database & Storage
        self.airtable_api_key = os.getenv("AIRTABLE_API_KEY")
        self.airtable_base_id = os.getenv("AIRTABLE_BASE_ID")
        self.notion_api_key = os.getenv("NOTION_API_KEY")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID")
        
        # Notifications
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.aws_ses_access_key = os.getenv("AWS_SES_ACCESS_KEY")
        self.aws_ses_secret_key = os.getenv("AWS_SES_SECRET_KEY")
        
        # Redis
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # System Config
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.alert_email = os.getenv("ALERT_EMAIL", "ci-alerts@rushgaming.com")
        
        # Load competitor configuration
        self.competitors = self._load_competitors()
        self.alert_rules = self._load_alert_rules()
        
    def _load_competitors(self) -> Dict[str, Any]:
        """Load competitor configuration from JSON file"""
        config_path = self.base_path / "config" / "competitors.json"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default competitor configuration
            return {
                "mpl": {
                    "name": "Mobile Premier League",
                    "website": "https://mpl.live",
                    "blog_url": "https://mpl.live/blog",
                    "twitter_handle": "PlayMPL",
                    "linkedin_company": "mobile-premier-league",
                    "careers_url": "https://careers.mpl.live",
                    "keywords": ["fantasy sports", "cash games", "tournaments", "esports"]
                },
                "winzo": {
                    "name": "WinZO Games",
                    "website": "https://winzogames.com",
                    "blog_url": "https://winzogames.com/blog",
                    "twitter_handle": "WinZOgames",
                    "linkedin_company": "winzo-games",
                    "careers_url": "https://winzogames.com/careers",
                    "keywords": ["vernacular games", "micro-transactions", "developer fund"]
                },
                "zupee": {
                    "name": "Zupee",
                    "website": "https://zupee.com",
                    "blog_url": "https://zupee.com/blog",
                    "twitter_handle": "Zupee_official",
                    "linkedin_company": "zupee",
                    "careers_url": "https://zupee.com/careers",
                    "keywords": ["ludo", "skill-based", "responsible gaming"]
                },
                "gameskraft": {
                    "name": "Gameskraft",
                    "website": "https://gameskraft.com",
                    "blog_url": "https://gameskraft.com/blog",
                    "twitter_handle": "GameskraftTech",
                    "linkedin_company": "gameskraft",
                    "careers_url": "https://jobs.gameskraft.com",
                    "keywords": ["rummy", "GST", "profitability", "standalone apps"]
                },
                "dream_sports": {
                    "name": "Dream Sports",
                    "website": "https://dreamsports.group",
                    "blog_url": "https://dreamsports.group/blog",
                    "twitter_handle": "DreamSportsHQ",
                    "linkedin_company": "dream-sports",
                    "careers_url": "https://dreamsports.group/careers",
                    "keywords": ["fantasy sports", "Dream11", "casual gaming", "carrom"]
                }
            }
    
    def _load_alert_rules(self) -> Dict[str, Any]:
        """Load alert rules configuration"""
        config_path = self.base_path / "config" / "alerts.json"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default alert rules
            return {
                "high_priority": {
                    "keywords": [
                        r"(?i)(funding|series|seed|pre-seed|acqui-hire|acquired)",
                        r"(?i)(launch|token|NFT|web3|blockchain)",
                        r"(?i)(C-level|VP|Vice President|Chief|Head of)"
                    ],
                    "channels": ["slack", "email"],
                    "escalation": "immediate"
                },
                "medium_priority": {
                    "keywords": [
                        r"(?i)(hiring|job|career|recruitment)",
                        r"(?i)(partnership|collaboration|tie-up)",
                        r"(?i)(expansion|market|geography)"
                    ],
                    "channels": ["slack"],
                    "escalation": "daily"
                },
                "low_priority": {
                    "keywords": [
                        r"(?i)(update|improvement|enhancement)",
                        r"(?i)(blog|article|press release)"
                    ],
                    "channels": ["weekly_brief"],
                    "escalation": "weekly"
                }
            }
    
    def get_competitor_by_name(self, name: str) -> Dict[str, Any]:
        """Get competitor config by name"""
        for key, config in self.competitors.items():
            if config["name"].lower() == name.lower():
                return config
        return {}
    
    def get_all_competitors(self) -> List[str]:
        """Get list of all competitor names"""
        return [config["name"] for config in self.competitors.values()]
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present"""
        required_keys = [
            "twitter_bearer_token",
            "openai_api_key",
            "airtable_api_key",
            "airtable_base_id",
            "notion_api_key",
            "notion_database_id"
        ]
        
        missing_keys = [key for key in required_keys if not getattr(self, key)]
        
        if missing_keys:
            print(f"Missing required environment variables: {missing_keys}")
            return False
        
        return True


# Global config instance
config = Config() 