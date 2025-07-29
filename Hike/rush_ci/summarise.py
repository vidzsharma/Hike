"""
AI summarization module for Rush Gaming CI System

Uses OpenAI to generate weekly competitive intelligence briefs.
"""

import json
import openai
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .config import config
from .utils.logger import get_logger
from .utils.helpers import get_current_iso_week, format_currency

logger = get_logger(__name__)


class AISummarizer:
    """AI-powered summarization for competitive intelligence"""
    
    def __init__(self):
        if config.openai_api_key:
            openai.api_key = config.openai_api_key
        else:
            logger.warning("OpenAI API key not configured")
    
    def generate_weekly_brief(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive weekly competitive intelligence brief
        
        Args:
            parsed_data: Parsed data from parse module
            
        Returns:
            Weekly brief with insights and recommendations
        """
        logger.info("Generating weekly competitive intelligence brief")
        
        try:
            # Prepare data for AI analysis
            brief_data = self._prepare_brief_data(parsed_data)
            
            # Generate AI summaries
            company_summaries = self._generate_company_summaries(brief_data)
            cross_company_themes = self._generate_cross_company_themes(brief_data)
            recommendations = self._generate_recommendations(brief_data)
            
            # Compile final brief
            weekly_brief = {
                'week': get_current_iso_week(),
                'generated_at': datetime.now().isoformat(),
                'company_summaries': company_summaries,
                'cross_company_themes': cross_company_themes,
                'recommendations': recommendations,
                'market_overview': self._generate_market_overview(brief_data),
                'alert_summary': self._summarize_alerts(parsed_data.get('alerts', []))
            }
            
            # Save brief to file
            self._save_brief(weekly_brief)
            
            logger.info("Weekly brief generated successfully")
            return weekly_brief
            
        except Exception as e:
            logger.error(f"Error generating weekly brief: {e}")
            return {}
    
    def _prepare_brief_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for AI analysis"""
        brief_data = {
            'companies': {},
            'alerts': parsed_data.get('alerts', []),
            'trends': parsed_data.get('trends', {})
        }
        
        insights = parsed_data.get('insights', {})
        
        for company, company_insights in insights.items():
            company_data = {
                'name': company,
                'blogs': company_insights.get('blogs', []),
                'tweets': company_insights.get('tweets', []),
                'linkedin': company_insights.get('linkedin', []),
                'jobs': company_insights.get('jobs', []),
                'summary': parsed_data.get('summaries', {}).get(company, {})
            }
            brief_data['companies'][company] = company_data
        
        return brief_data
    
    def _generate_company_summaries(self, brief_data: Dict[str, Any]) -> Dict[str, Dict]:
        """Generate AI-powered company summaries"""
        company_summaries = {}
        
        for company, company_data in brief_data['companies'].items():
            try:
                summary = self._generate_single_company_summary(company, company_data)
                company_summaries[company] = summary
            except Exception as e:
                logger.error(f"Error generating summary for {company}: {e}")
                company_summaries[company] = self._generate_fallback_summary(company, company_data)
        
        return company_summaries
    
    def _generate_single_company_summary(self, company: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for a single company using AI"""
        
        # Prepare context for AI
        context = self._prepare_company_context(company, company_data)
        
        # AI prompt for company summary
        prompt = f"""
        You are a competitive intelligence analyst for Rush Gaming, analyzing {company}'s activities this week.
        
        Context about {company}:
        {context}
        
        Please provide a structured analysis in JSON format with the following fields:
        {{
            "what_they_shipped": ["List of product launches, updates, or new features"],
            "who_they_hired": ["List of key hiring activities, departments, seniority levels"],
            "signals_narrative": ["Strategic themes, market positioning, competitive moves"],
            "alert_level": "high/medium/low",
            "key_insights": ["3-5 key insights about this company's strategy"]
        }}
        
        Focus on actionable intelligence that would help Rush Gaming understand competitive threats and opportunities.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a competitive intelligence expert specializing in gaming and technology companies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse AI response
            ai_summary = json.loads(response.choices[0].message.content)
            
            return {
                'what_they_shipped': ai_summary.get('what_they_shipped', []),
                'who_they_hired': ai_summary.get('who_they_hired', []),
                'signals_narrative': ai_summary.get('signals_narrative', []),
                'alert_level': ai_summary.get('alert_level', 'low'),
                'key_insights': ai_summary.get('key_insights', []),
                'data_sources': self._summarize_data_sources(company_data)
            }
            
        except Exception as e:
            logger.error(f"AI summary generation failed for {company}: {e}")
            return self._generate_fallback_summary(company, company_data)
    
    def _prepare_company_context(self, company: str, company_data: Dict[str, Any]) -> str:
        """Prepare context about company for AI analysis"""
        context_parts = [f"Company: {company}"]
        
        # Blog posts
        blogs = company_data.get('blogs', [])
        if blogs:
            context_parts.append(f"Blog posts ({len(blogs)}):")
            for blog in blogs[:3]:  # Top 3 blogs
                context_parts.append(f"- {blog.get('title', '')}: {blog.get('content', '')[:200]}...")
        
        # Tweets
        tweets = company_data.get('tweets', [])
        if tweets:
            context_parts.append(f"Recent tweets ({len(tweets)}):")
            for tweet in tweets[:5]:  # Top 5 tweets
                context_parts.append(f"- {tweet.get('text', '')}")
        
        # Job postings
        jobs = company_data.get('jobs', [])
        if jobs:
            context_parts.append(f"Job postings ({len(jobs)}):")
            for job in jobs[:5]:  # Top 5 jobs
                context_parts.append(f"- {job.get('role', '')} ({job.get('department', '')}) - {job.get('location', '')}")
        
        # Hiring trends
        hiring_trends = company_data.get('summary', {}).get('hiring_trends', {})
        if hiring_trends:
            context_parts.append(f"Hiring trends: {hiring_trends}")
        
        return "\n".join(context_parts)
    
    def _generate_fallback_summary(self, company: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback summary without AI"""
        summary = {
            'what_they_shipped': [],
            'who_they_hired': [],
            'signals_narrative': [],
            'alert_level': 'low',
            'key_insights': [],
            'data_sources': self._summarize_data_sources(company_data)
        }
        
        # Extract product updates from blogs
        blogs = company_data.get('blogs', [])
        for blog in blogs:
            if any(keyword in blog.get('title', '').lower() for keyword in ['launch', 'update', 'new', 'feature']):
                summary['what_they_shipped'].append(blog.get('title', ''))
        
        # Extract hiring info from jobs
        jobs = company_data.get('jobs', [])
        if jobs:
            summary['who_they_hired'].append(f"Posted {len(jobs)} new job positions")
            
            # Analyze departments
            departments = {}
            for job in jobs:
                dept = job.get('department', 'other')
                departments[dept] = departments.get(dept, 0) + 1
            
            top_dept = max(departments.items(), key=lambda x: x[1]) if departments else None
            if top_dept:
                summary['who_they_hired'].append(f"Focus on {top_dept[0]} hiring ({top_dept[1]} positions)")
        
        # Extract themes from tweets
        tweets = company_data.get('tweets', [])
        themes = []
        for tweet in tweets:
            text = tweet.get('text', '').lower()
            if any(theme in text for theme in ['partnership', 'collaboration', 'expansion']):
                themes.append(tweet.get('text', ''))
        
        summary['signals_narrative'] = themes[:3]  # Top 3 themes
        
        return summary
    
    def _generate_cross_company_themes(self, brief_data: Dict[str, Any]) -> List[str]:
        """Generate cross-company themes using AI"""
        try:
            # Prepare context for cross-company analysis
            context = self._prepare_cross_company_context(brief_data)
            
            prompt = f"""
            You are analyzing competitive intelligence across multiple gaming companies.
            
            Context:
            {context}
            
            Identify 3-5 key cross-company themes or market movements that are relevant for Rush Gaming.
            Focus on strategic insights, market trends, and competitive dynamics.
            
            Provide your analysis as a JSON array of theme strings.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a competitive intelligence expert analyzing gaming industry trends."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            themes = json.loads(response.choices[0].message.content)
            return themes if isinstance(themes, list) else []
            
        except Exception as e:
            logger.error(f"Error generating cross-company themes: {e}")
            return self._generate_fallback_cross_company_themes(brief_data)
    
    def _prepare_cross_company_context(self, brief_data: Dict[str, Any]) -> str:
        """Prepare context for cross-company analysis"""
        context_parts = []
        
        # Company activity summary
        for company, company_data in brief_data['companies'].items():
            activity_summary = f"{company}: "
            
            blogs_count = len(company_data.get('blogs', []))
            tweets_count = len(company_data.get('tweets', []))
            jobs_count = len(company_data.get('jobs', []))
            
            activity_summary += f"{blogs_count} blogs, {tweets_count} tweets, {jobs_count} jobs"
            
            # Add key insights
            summary = company_data.get('summary', {})
            if summary.get('key_themes'):
                activity_summary += f" | Themes: {', '.join(summary['key_themes'][:3])}"
            
            context_parts.append(activity_summary)
        
        # Market trends
        trends = brief_data.get('trends', {})
        if trends:
            context_parts.append(f"Market trends: {trends}")
        
        return "\n".join(context_parts)
    
    def _generate_fallback_cross_company_themes(self, brief_data: Dict[str, Any]) -> List[str]:
        """Generate fallback cross-company themes"""
        themes = []
        
        # Analyze hiring patterns
        total_jobs = 0
        engineering_jobs = 0
        marketing_jobs = 0
        
        for company, company_data in brief_data['companies'].items():
            jobs = company_data.get('jobs', [])
            total_jobs += len(jobs)
            
            for job in jobs:
                dept = job.get('department', '')
                if 'engineering' in dept:
                    engineering_jobs += 1
                elif 'marketing' in dept:
                    marketing_jobs += 1
        
        if total_jobs > 20:
            themes.append(f"High hiring activity across companies ({total_jobs} total jobs)")
        
        if engineering_jobs > marketing_jobs:
            themes.append("Engineering-focused hiring trend")
        elif marketing_jobs > engineering_jobs:
            themes.append("Marketing-focused hiring trend")
        
        # Analyze product activity
        product_updates = 0
        for company, company_data in brief_data['companies'].items():
            blogs = company_data.get('blogs', [])
            for blog in blogs:
                if any(keyword in blog.get('title', '').lower() for keyword in ['launch', 'update', 'new']):
                    product_updates += 1
        
        if product_updates > 5:
            themes.append(f"Active product development cycle ({product_updates} updates)")
        
        return themes
    
    def _generate_recommendations(self, brief_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations for Rush Gaming"""
        try:
            context = self._prepare_recommendations_context(brief_data)
            
            prompt = f"""
            Based on the competitive intelligence data, provide 3-5 actionable recommendations for Rush Gaming.
            
            Context:
            {context}
            
            Provide recommendations in JSON format:
            {{
                "recommendations": [
                    {{
                        "category": "product/marketing/strategy/operations",
                        "title": "Brief title",
                        "description": "Detailed recommendation",
                        "priority": "high/medium/low",
                        "timeline": "immediate/short-term/long-term"
                    }}
                ]
            }}
            
            Focus on practical, actionable insights that Rush Gaming can implement.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a strategic advisor for Rush Gaming, providing actionable competitive intelligence recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('recommendations', [])
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self._generate_fallback_recommendations(brief_data)
    
    def _prepare_recommendations_context(self, brief_data: Dict[str, Any]) -> str:
        """Prepare context for recommendations"""
        context_parts = []
        
        # Key competitive moves
        for company, company_data in brief_data['companies'].items():
            summary = company_data.get('summary', {})
            if summary.get('product_updates'):
                context_parts.append(f"{company} product updates: {len(summary['product_updates'])}")
            
            hiring_trends = summary.get('hiring_trends', {})
            if hiring_trends.get('total_jobs', 0) > 5:
                context_parts.append(f"{company} aggressive hiring: {hiring_trends['total_jobs']} jobs")
        
        # Market trends
        trends = brief_data.get('trends', {})
        if trends:
            context_parts.append(f"Market trends: {trends}")
        
        return "\n".join(context_parts)
    
    def _generate_fallback_recommendations(self, brief_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate fallback recommendations"""
        recommendations = []
        
        # Analyze hiring patterns
        engineering_focus = []
        marketing_focus = []
        
        for company, company_data in brief_data['companies'].items():
            jobs = company_data.get('jobs', [])
            if len(jobs) > 5:
                dept_counts = {}
                for job in jobs:
                    dept = job.get('department', 'other')
                    dept_counts[dept] = dept_counts.get(dept, 0) + 1
                
                if dept_counts.get('engineering', 0) > 3:
                    engineering_focus.append(company)
                if dept_counts.get('marketing', 0) > 2:
                    marketing_focus.append(company)
        
        if engineering_focus:
            recommendations.append({
                'category': 'product',
                'title': 'Accelerate Engineering Hiring',
                'description': f"Competitors {', '.join(engineering_focus)} are aggressively hiring engineers. Consider ramping up engineering recruitment.",
                'priority': 'high',
                'timeline': 'short-term'
            })
        
        if marketing_focus:
            recommendations.append({
                'category': 'marketing',
                'title': 'Enhance Marketing Efforts',
                'description': f"Competitors {', '.join(marketing_focus)} are focusing on marketing. Review marketing strategy and budget allocation.",
                'priority': 'medium',
                'timeline': 'short-term'
            })
        
        return recommendations
    
    def _generate_market_overview(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market overview"""
        overview = {
            'total_activity': 0,
            'companies_active': 0,
            'key_highlights': [],
            'market_sentiment': 'neutral'
        }
        
        for company, company_data in brief_data['companies'].items():
            activity = (
                len(company_data.get('blogs', [])) +
                len(company_data.get('tweets', [])) +
                len(company_data.get('jobs', []))
            )
            
            if activity > 0:
                overview['companies_active'] += 1
                overview['total_activity'] += activity
        
        # Determine market sentiment
        if overview['total_activity'] > 50:
            overview['market_sentiment'] = 'high'
        elif overview['total_activity'] > 20:
            overview['market_sentiment'] = 'moderate'
        else:
            overview['market_sentiment'] = 'low'
        
        return overview
    
    def _summarize_alerts(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Summarize alerts"""
        alert_summary = {
            'total_alerts': len(alerts),
            'high_priority': len([a for a in alerts if a.get('level') == 'high']),
            'medium_priority': len([a for a in alerts if a.get('level') == 'medium']),
            'low_priority': len([a for a in alerts if a.get('level') == 'low']),
            'companies_with_alerts': list(set([a.get('company') for a in alerts]))
        }
        
        return alert_summary
    
    def _summarize_data_sources(self, company_data: Dict[str, Any]) -> Dict[str, int]:
        """Summarize data sources for company"""
        return {
            'blogs': len(company_data.get('blogs', [])),
            'tweets': len(company_data.get('tweets', [])),
            'linkedin': len(company_data.get('linkedin', [])),
            'jobs': len(company_data.get('jobs', []))
        }
    
    def _save_brief(self, weekly_brief: Dict[str, Any]) -> None:
        """Save weekly brief to file"""
        try:
            # Create briefs directory
            briefs_dir = Path(__file__).parent.parent / 'briefs'
            briefs_dir.mkdir(exist_ok=True)
            
            # Save JSON version
            json_path = briefs_dir / f"{weekly_brief['week']}.json"
            with open(json_path, 'w') as f:
                json.dump(weekly_brief, f, default=str, indent=2)
            
            # Generate markdown version
            markdown_path = briefs_dir / f"{weekly_brief['week']}.md"
            markdown_content = self._generate_markdown_brief(weekly_brief)
            with open(markdown_path, 'w') as f:
                f.write(markdown_content)
            
            logger.info(f"Weekly brief saved to {json_path} and {markdown_path}")
            
        except Exception as e:
            logger.error(f"Error saving brief: {e}")
    
    def _generate_markdown_brief(self, weekly_brief: Dict[str, Any]) -> str:
        """Generate markdown version of weekly brief"""
        week = weekly_brief['week']
        
        markdown = f"""# Week {week} – Competitive Intelligence Brief

## Executive Summary

**Week**: {week}  
**Generated**: {weekly_brief['generated_at']}  
**Market Sentiment**: {weekly_brief['market_overview']['market_sentiment'].title()}  
**Total Activity**: {weekly_brief['market_overview']['total_activity']} items across {weekly_brief['market_overview']['companies_active']} companies

## Company Snapshots

"""
        
        # Company summaries
        for company, summary in weekly_brief['company_summaries'].items():
            markdown += f"### {company}\n\n"
            
            # What they shipped
            if summary.get('what_they_shipped'):
                markdown += "**What They Shipped:**\n"
                for item in summary['what_they_shipped']:
                    markdown += f"- {item}\n"
                markdown += "\n"
            
            # Who they hired
            if summary.get('who_they_hired'):
                markdown += "**Who They Hired:**\n"
                for item in summary['who_they_hired']:
                    markdown += f"- {item}\n"
                markdown += "\n"
            
            # Signals & narrative
            if summary.get('signals_narrative'):
                markdown += "**Signals & Narrative:**\n"
                for item in summary['signals_narrative']:
                    markdown += f"- {item}\n"
                markdown += "\n"
            
            # Alert level
            markdown += f"**Alert Level**: {summary.get('alert_level', 'low').title()}\n\n"
        
        # Cross-company themes
        if weekly_brief.get('cross_company_themes'):
            markdown += "## Cross-Company Themes\n\n"
            for theme in weekly_brief['cross_company_themes']:
                markdown += f"- {theme}\n"
            markdown += "\n"
        
        # Recommendations
        if weekly_brief.get('recommendations'):
            markdown += "## Recommended Actions for Rush\n\n"
            for rec in weekly_brief['recommendations']:
                markdown += f"### {rec.get('title', '')}\n"
                markdown += f"**Category**: {rec.get('category', '').title()}\n"
                markdown += f"**Priority**: {rec.get('priority', '').title()}\n"
                markdown += f"**Timeline**: {rec.get('timeline', '').title()}\n\n"
                markdown += f"{rec.get('description', '')}\n\n"
        
        # Alert summary
        alert_summary = weekly_brief.get('alert_summary', {})
        if alert_summary.get('total_alerts', 0) > 0:
            markdown += "## Alert Summary\n\n"
            markdown += f"- **Total Alerts**: {alert_summary['total_alerts']}\n"
            markdown += f"- **High Priority**: {alert_summary['high_priority']}\n"
            markdown += f"- **Medium Priority**: {alert_summary['medium_priority']}\n"
            markdown += f"- **Low Priority**: {alert_summary['low_priority']}\n"
            markdown += f"- **Companies with Alerts**: {', '.join(alert_summary['companies_with_alerts'])}\n\n"
        
        return markdown


def main():
    """Main function to run AI summarization"""
    logger.info("Starting Rush Gaming CI AI summarization")
    
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
    
    summarizer = AISummarizer()
    weekly_brief = summarizer.generate_weekly_brief(parsed_data)
    
    if weekly_brief:
        logger.info("AI summarization completed successfully")
    else:
        logger.error("AI summarization failed")
    
    return weekly_brief


if __name__ == "__main__":
    main() 