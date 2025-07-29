"""
Alerting module for Rush Gaming CI System

Sends real-time notifications via Slack and email for high-priority events.
"""

import json
import boto3
from datetime import datetime
from typing import Dict, List, Any, Optional
from slack_sdk import WebhookClient
from slack_sdk.errors import SlackApiError

from .config import config
from .utils.logger import get_logger

logger = get_logger(__name__)


class AlertManager:
    """Alert management for competitive intelligence"""
    
    def __init__(self):
        self.slack_client = self._init_slack()
        self.ses_client = self._init_ses()
        
    def _init_slack(self) -> Optional[WebhookClient]:
        """Initialize Slack webhook client"""
        try:
            if config.slack_webhook_url:
                return WebhookClient(config.slack_webhook_url)
        except Exception as e:
            logger.error(f"Slack initialization failed: {e}")
        return None
    
    def _init_ses(self) -> Optional[boto3.client]:
        """Initialize AWS SES client"""
        try:
            if config.aws_ses_access_key and config.aws_ses_secret_key:
                return boto3.client(
                    'ses',
                    aws_access_key_id=config.aws_ses_access_key,
                    aws_secret_access_key=config.aws_ses_secret_key,
                    region_name='us-east-1'
                )
        except Exception as e:
            logger.error(f"AWS SES initialization failed: {e}")
        return None
    
    def process_alerts(self, alerts: List[Dict[str, Any]]) -> bool:
        """
        Process and send alerts
        
        Args:
            alerts: List of alerts from parse module
            
        Returns:
            Success status
        """
        logger.info(f"Processing {len(alerts)} alerts")
        
        success = True
        
        for alert in alerts:
            try:
                self._process_single_alert(alert)
            except Exception as e:
                logger.error(f"Error processing alert: {e}")
                success = False
        
        return success
    
    def _process_single_alert(self, alert: Dict[str, Any]) -> None:
        """Process a single alert"""
        alert_level = alert.get('level', 'low')
        company = alert.get('company', 'Unknown')
        text = alert.get('text', '')
        source_type = alert.get('source_type', '')
        
        # Determine notification channels based on alert level
        if alert_level == 'high':
            self._send_high_priority_alert(alert)
        elif alert_level == 'medium':
            self._send_medium_priority_alert(alert)
        else:
            # Low priority alerts are logged but not sent
            logger.info(f"Low priority alert for {company}: {text[:100]}...")
    
    def _send_high_priority_alert(self, alert: Dict[str, Any]) -> None:
        """Send high priority alert via multiple channels"""
        company = alert.get('company', 'Unknown')
        text = alert.get('text', '')
        source_type = alert.get('source_type', '')
        keywords = alert.get('keywords', [])
        
        # Slack notification
        if self.slack_client:
            self._send_slack_alert(alert, priority='high')
        
        # Email notification
        if self.ses_client:
            self._send_email_alert(alert, priority='high')
        
        logger.info(f"High priority alert sent for {company}")
    
    def _send_medium_priority_alert(self, alert: Dict[str, Any]) -> None:
        """Send medium priority alert via Slack only"""
        company = alert.get('company', 'Unknown')
        
        # Slack notification only
        if self.slack_client:
            self._send_slack_alert(alert, priority='medium')
        
        logger.info(f"Medium priority alert sent for {company}")
    
    def _send_slack_alert(self, alert: Dict[str, Any], priority: str = 'medium') -> None:
        """Send alert to Slack"""
        try:
            company = alert.get('company', 'Unknown')
            text = alert.get('text', '')
            source_type = alert.get('source_type', '')
            keywords = alert.get('keywords', [])
            url = alert.get('url', '')
            
            # Determine emoji and color based on priority
            if priority == 'high':
                emoji = "🚨"
                color = "#FF0000"  # Red
            else:
                emoji = "⚠️"
                color = "#FFA500"  # Orange
            
            # Create Slack message
            message = {
                "text": f"{emoji} Competitive Intelligence Alert",
                "attachments": [
                    {
                        "color": color,
                        "title": f"{company} - {priority.upper()} Priority Alert",
                        "text": text[:500] + "..." if len(text) > 500 else text,
                        "fields": [
                            {
                                "title": "Source",
                                "value": source_type.title(),
                                "short": True
                            },
                            {
                                "title": "Keywords",
                                "value": ", ".join(keywords[:5]),
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True
                            }
                        ],
                        "footer": "Rush Gaming CI System",
                        "footer_icon": "https://getrushapp.com/favicon.ico"
                    }
                ]
            }
            
            # Add URL if available
            if url:
                message["attachments"][0]["title_link"] = url
            
            # Send to Slack
            response = self.slack_client.send(text=message["text"], attachments=message["attachments"])
            
            if not response["ok"]:
                logger.error(f"Slack API error: {response.get('error', 'Unknown error')}")
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
    
    def _send_email_alert(self, alert: Dict[str, Any], priority: str = 'high') -> None:
        """Send alert via email"""
        try:
            company = alert.get('company', 'Unknown')
            text = alert.get('text', '')
            source_type = alert.get('source_type', '')
            keywords = alert.get('keywords', [])
            url = alert.get('url', '')
            
            # Email subject
            subject = f"[RUSH CI] {priority.upper()} Priority Alert - {company}"
            
            # Email body
            body = f"""
🚨 Competitive Intelligence Alert

Company: {company}
Priority: {priority.upper()}
Source: {source_type.title()}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Content:
{text}

Keywords: {', '.join(keywords)}

Source URL: {url if url else 'N/A'}

---
This alert was generated by the Rush Gaming Competitive Intelligence System.
For questions or to modify alert settings, contact the CI team.
            """
            
            # Send email
            response = self.ses_client.send_email(
                Source=config.alert_email,
                Destination={
                    'ToAddresses': [config.alert_email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            logger.info(f"Email alert sent: {response['MessageId']}")
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
    
    def send_weekly_summary(self, weekly_brief: Dict[str, Any]) -> bool:
        """
        Send weekly summary to stakeholders
        
        Args:
            weekly_brief: Weekly brief from summarization module
            
        Returns:
            Success status
        """
        logger.info("Sending weekly summary")
        
        try:
            # Create weekly summary message
            summary_message = self._create_weekly_summary_message(weekly_brief)
            
            # Send to Slack
            if self.slack_client:
                self._send_weekly_slack_summary(weekly_brief)
            
            # Send email summary
            if self.ses_client:
                self._send_weekly_email_summary(weekly_brief)
            
            logger.info("Weekly summary sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending weekly summary: {e}")
            return False
    
    def _create_weekly_summary_message(self, weekly_brief: Dict[str, Any]) -> str:
        """Create weekly summary message"""
        week = weekly_brief.get('week', 'Unknown')
        market_sentiment = weekly_brief.get('market_overview', {}).get('market_sentiment', 'neutral')
        total_activity = weekly_brief.get('market_overview', {}).get('total_activity', 0)
        companies_active = weekly_brief.get('market_overview', {}).get('companies_active', 0)
        
        message = f"""
📊 Weekly Competitive Intelligence Summary - Week {week}

Market Overview:
• Sentiment: {market_sentiment.title()}
• Total Activity: {total_activity} items
• Active Companies: {companies_active}

Key Highlights:
"""
        
        # Add company highlights
        company_summaries = weekly_brief.get('company_summaries', {})
        for company, summary in company_summaries.items():
            alert_level = summary.get('alert_level', 'low')
            if alert_level == 'high':
                message += f"• {company}: {alert_level.upper()} priority activity\n"
        
        # Add cross-company themes
        themes = weekly_brief.get('cross_company_themes', [])
        if themes:
            message += "\nCross-Company Themes:\n"
            for theme in themes[:3]:
                message += f"• {theme}\n"
        
        return message
    
    def _send_weekly_slack_summary(self, weekly_brief: Dict[str, Any]) -> None:
        """Send weekly summary to Slack"""
        try:
            week = weekly_brief.get('week', 'Unknown')
            company_summaries = weekly_brief.get('company_summaries', {})
            
            # Create summary attachment
            fields = []
            for company, summary in company_summaries.items():
                alert_level = summary.get('alert_level', 'low')
                activity_count = sum(summary.get('data_sources', {}).values())
                
                fields.append({
                    "title": company,
                    "value": f"Alert: {alert_level.upper()} | Activity: {activity_count} items",
                    "short": True
                })
            
            message = {
                "text": f"📊 Weekly CI Summary - Week {week}",
                "attachments": [
                    {
                        "color": "#36A64F",
                        "title": f"Week {week} Competitive Intelligence Summary",
                        "text": self._create_weekly_summary_message(weekly_brief),
                        "fields": fields,
                        "footer": "Rush Gaming CI System",
                        "footer_icon": "https://getrushapp.com/favicon.ico"
                    }
                ]
            }
            
            response = self.slack_client.send(text=message["text"], attachments=message["attachments"])
            
            if not response["ok"]:
                logger.error(f"Slack API error: {response.get('error', 'Unknown error')}")
            
        except Exception as e:
            logger.error(f"Error sending weekly Slack summary: {e}")
    
    def _send_weekly_email_summary(self, weekly_brief: Dict[str, Any]) -> None:
        """Send weekly summary via email"""
        try:
            week = weekly_brief.get('week', 'Unknown')
            
            subject = f"[RUSH CI] Weekly Competitive Intelligence Summary - Week {week}"
            
            body = self._create_weekly_summary_message(weekly_brief)
            
            # Add recommendations
            recommendations = weekly_brief.get('recommendations', [])
            if recommendations:
                body += "\n\nRecommended Actions for Rush:\n"
                for i, rec in enumerate(recommendations[:5], 1):
                    body += f"{i}. {rec.get('title', '')} ({rec.get('priority', '').title()} priority)\n"
                    body += f"   {rec.get('description', '')}\n\n"
            
            body += "\n---\nThis summary was generated by the Rush Gaming Competitive Intelligence System."
            
            response = self.ses_client.send_email(
                Source=config.alert_email,
                Destination={
                    'ToAddresses': [config.alert_email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            logger.info(f"Weekly email summary sent: {response['MessageId']}")
            
        except Exception as e:
            logger.error(f"Error sending weekly email summary: {e}")
    
    def send_test_alert(self) -> bool:
        """Send test alert to verify configuration"""
        logger.info("Sending test alert")
        
        test_alert = {
            'level': 'medium',
            'company': 'Test Company',
            'text': 'This is a test alert from the Rush Gaming CI System to verify configuration.',
            'source_type': 'test',
            'keywords': ['test', 'verification'],
            'url': 'https://getrushapp.com'
        }
        
        try:
            # Send test Slack alert
            if self.slack_client:
                self._send_slack_alert(test_alert, priority='medium')
                logger.info("Test Slack alert sent successfully")
            
            # Send test email alert
            if self.ses_client:
                self._send_email_alert(test_alert, priority='medium')
                logger.info("Test email alert sent successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Test alert failed: {e}")
            return False
    
    def get_alert_stats(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get alert statistics"""
        stats = {
            'total_alerts': len(alerts),
            'high_priority': len([a for a in alerts if a.get('level') == 'high']),
            'medium_priority': len([a for a in alerts if a.get('level') == 'medium']),
            'low_priority': len([a for a in alerts if a.get('level') == 'low']),
            'by_company': {},
            'by_source': {}
        }
        
        for alert in alerts:
            company = alert.get('company', 'Unknown')
            source = alert.get('source_type', 'Unknown')
            
            stats['by_company'][company] = stats['by_company'].get(company, 0) + 1
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
        
        return stats


def main():
    """Main function to run alerting"""
    logger.info("Starting Rush Gaming CI alerting")
    
    # Load alerts (this would come from parse module)
    try:
        with open('data/parsed_data.json', 'r') as f:
            import json
            parsed_data = json.load(f)
            alerts = parsed_data.get('alerts', [])
    except FileNotFoundError:
        logger.warning("No parsed data found. Creating sample alerts for testing.")
        alerts = [
            {
                'level': 'high',
                'company': 'MPL',
                'text': 'MPL announces new funding round of $50M',
                'source_type': 'blogs',
                'keywords': ['funding', 'series', 'investment'],
                'url': 'https://example.com'
            },
            {
                'level': 'medium',
                'company': 'WinZO',
                'text': 'WinZO launches new game feature',
                'source_type': 'tweets',
                'keywords': ['launch', 'feature', 'game'],
                'url': 'https://example.com'
            }
        ]
    
    alert_manager = AlertManager()
    
    # Process alerts
    success = alert_manager.process_alerts(alerts)
    
    # Send test alert if no real alerts
    if not alerts:
        alert_manager.send_test_alert()
    
    if success:
        logger.info("Alerting completed successfully")
    else:
        logger.error("Alerting failed")
    
    return success


if __name__ == "__main__":
    main() 