<<<<<<< HEAD
# Rush Gaming Competitive Intelligence System
=======
# Hike
Rush Gaming Competitive Intelligence System
>>>>>>> a747da4eae6a4843f2209caf272ba943d6db9697

An automated competitive intelligence pipeline that monitors key competitors in India's real-money gaming market and delivers actionable insights.

## 🎯 Overview

This system automatically tracks 5 key competitors:
1. **Mobile Premier League (MPL)** - mpl.live
2. **WinZO Games** - winzogames.com  
3. **Zupee** - zupee.com
4. **Gameskraft** - gameskraft.com, gamezy.com, rummyculture.com
5. **Dream Sports** - dreamsports.group

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone and setup
git clone <repository-url>
cd rush_ci
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` file:

```env
# API Keys
TWITTER_BEARER_TOKEN=your_twitter_token
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
OPENAI_API_KEY=your_openai_key

# Database & Storage
AIRTABLE_API_KEY=your_airtable_key
AIRTABLE_BASE_ID=your_base_id
NOTION_API_KEY=your_notion_key
NOTION_DATABASE_ID=your_database_id

# Notifications
SLACK_WEBHOOK_URL=your_slack_webhook
AWS_SES_ACCESS_KEY=your_ses_key
AWS_SES_SECRET_KEY=your_ses_secret

# Redis (Optional - for deduplication)
REDIS_URL=redis://localhost:6379

# System Config
LOG_LEVEL=INFO
ALERT_EMAIL=ci-alerts@rushgaming.com
```

### 3. Database Setup

#### Airtable Base Structure
Create base "Rush CI Raw" with tables:
- `Blogs` (title, url, content, company, published_at, source)
- `Tweets` (tweet_id, text, company, created_at, metrics)
- `LinkedIn` (post_id, text, company, created_at, reactions)
- `Jobs` (role, company, location, posted_at, url)

#### Notion Database Structure
Create database "Rush Competitive Intelligence" with properties:
- `Company` (Select)
- `Week` (Date)
- `What They Shipped` (Rich Text)
- `Who They Hired` (Rich Text) 
- `Signals & Narrative` (Rich Text)
- `Alert Level` (Select: Low/Medium/High)

### 4. Run the System

```bash
# Manual run
python main.py

# Or run individual modules
python rush_ci/01_fetch.py
python rush_ci/02_parse.py
python rush_ci/03_store.py
python rush_ci/04_summarise.py
python rush_ci/05_alert.py
```

## 📅 Automated Scheduling

### GitHub Actions (Recommended)

Create `.github/workflows/ci_pipeline.yml`:

```yaml
name: Competitive Intelligence Pipeline
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          TWITTER_BEARER_TOKEN: ${{ secrets.TWITTER_BEARER_TOKEN }}
          # ... other env vars
```

### AWS Lambda (For Real-time Alerts)

Deploy `lambda_function.py` to AWS Lambda with EventBridge triggers.

## 📊 Dashboard Access

- **Live Dashboard**: Notion database shared with stakeholders
- **Raw Data**: Airtable base for detailed analysis
- **Alerts**: Slack channel `#market-intel`
- **Weekly Briefs**: Auto-generated every Monday 9 AM IST

## 🔧 Configuration

### Competitor Sources

Edit `config/competitors.json` to modify:
- Company URLs and social handles
- Alert keywords and regex patterns
- Custom scraping rules

### Alert Rules

Modify `config/alerts.json` to customize:
- Trigger conditions
- Notification channels
- Escalation rules

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=rush_ci --cov-report=html

# Test specific module
pytest tests/test_fetch.py -v
```

## 📈 Monitoring

- **Success Rate**: Check GitHub Actions logs
- **Data Quality**: Monitor Airtable record counts
- **Alert Performance**: Review Slack notification history
- **API Usage**: Track rate limit consumption

## 🔒 Security & Compliance

- All API keys stored in environment variables
- No personal data beyond public job titles
- Rate limiting respects robots.txt
- 90-day token rotation recommended

## 🆘 Troubleshooting

### Common Issues

1. **Rate Limiting**: Check API quotas in respective dashboards
2. **Authentication**: Verify token validity and permissions
3. **Data Duplication**: Clear Redis cache if needed
4. **Missing Data**: Check source availability and HTML structure changes

### Logs

```bash
# View recent logs
tail -f logs/rush_ci.log

# Debug mode
LOG_LEVEL=DEBUG python main.py
```

## 📞 Support

For technical issues or feature requests:
- Create GitHub issue
- Contact: ci-team@rushgaming.com
- Documentation: [Internal Wiki Link]

## 📄 License

<<<<<<< HEAD
Internal use only - Rush Gaming proprietary system. 
=======
Internal use only - Rush Gaming proprietary system. 
>>>>>>> a747da4eae6a4843f2209caf272ba943d6db9697
