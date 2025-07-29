# Rush Gaming CI System - Deployment Guide

## Quick Start (5 Minutes)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd rush_ci
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Test Configuration
```bash
python main.py --config-check
```

### 4. Run Test Mode
```bash
python main.py --mode test
```

## Detailed Setup

### Prerequisites

- Python 3.12+
- Redis (optional, for deduplication)
- GitHub account (for Actions)
- API keys for services

### Required API Keys

#### 1. Twitter API
- Go to [Twitter Developer Portal](https://developer.twitter.com/)
- Create app and get Bearer Token
- Add to `.env`: `TWITTER_BEARER_TOKEN=your_token`

#### 2. OpenAI API
- Go to [OpenAI Platform](https://platform.openai.com/)
- Create API key
- Add to `.env`: `OPENAI_API_KEY=your_key`

#### 3. Airtable
- Go to [Airtable](https://airtable.com/)
- Create base "Rush CI Raw"
- Create tables: Blogs, Tweets, LinkedIn, Jobs
- Get API key and Base ID
- Add to `.env`: `AIRTABLE_API_KEY=your_key` and `AIRTABLE_BASE_ID=your_base_id`

#### 4. Notion
- Go to [Notion Developers](https://developers.notion.com/)
- Create integration
- Create database "Rush Competitive Intelligence"
- Share database with integration
- Add to `.env`: `NOTION_API_KEY=your_key` and `NOTION_DATABASE_ID=your_database_id`

#### 5. Slack
- Go to [Slack Apps](https://api.slack.com/apps)
- Create app with webhook
- Add to `.env`: `SLACK_WEBHOOK_URL=your_webhook`

#### 6. AWS SES (Optional)
- Configure AWS SES for email alerts
- Add to `.env`: `AWS_SES_ACCESS_KEY=your_key` and `AWS_SES_SECRET_KEY=your_secret`

### Database Setup

#### Airtable Base Structure

Create base "Rush CI Raw" with these tables:

**Blogs Table:**
- title (Single line text)
- url (URL)
- content (Long text)
- company (Single select)
- published_at (Date)
- source (Single line text)
- keywords (Long text)
- sentiment (Single select: positive/negative/neutral)
- alert_level (Single select: high/medium/low)

**Tweets Table:**
- tweet_id (Single line text)
- text (Long text)
- company (Single select)
- created_at (Date)
- metrics (Long text)
- keywords (Long text)
- sentiment (Single select)
- alert_level (Single select)
- engagement_score (Number)

**LinkedIn Table:**
- post_id (Single line text)
- text (Long text)
- company (Single select)
- created_at (Date)
- reactions (Long text)
- keywords (Long text)
- sentiment (Single select)
- alert_level (Single select)
- engagement_score (Number)

**Jobs Table:**
- role (Single line text)
- company (Single select)
- location (Single line text)
- posted_at (Date)
- url (URL)
- department (Single line text)
- seniority (Single select: intern/junior/mid/senior/manager/executive)
- keywords (Long text)
- alert_level (Single select)
- is_remote (Checkbox)
- is_international (Checkbox)

#### Notion Database Structure

Create database "Rush Competitive Intelligence" with properties:

- **Company** (Select): MPL, WinZO, Zupee, Gameskraft, Dream Sports
- **Week** (Date): ISO week format
- **What They Shipped** (Rich Text): Product updates and launches
- **Who They Hired** (Rich Text): Hiring activities and trends
- **Signals & Narrative** (Rich Text): Strategic insights
- **Alert Level** (Select): High/Medium/Low

### GitHub Actions Setup

#### 1. Repository Secrets

Add these secrets to your GitHub repository:

```
TWITTER_BEARER_TOKEN
OPENAI_API_KEY
AIRTABLE_API_KEY
AIRTABLE_BASE_ID
NOTION_API_KEY
NOTION_DATABASE_ID
SLACK_WEBHOOK_URL
AWS_SES_ACCESS_KEY
AWS_SES_SECRET_KEY
REDIS_URL
ALERT_EMAIL
```

#### 2. Enable Actions

- Go to repository Settings > Actions > General
- Enable "Allow all actions and reusable workflows"
- The workflow will run automatically every 6 hours

### Local Development

#### 1. Install Development Dependencies
```bash
pip install -r requirements.txt
pip install -e .[dev]
```

#### 2. Run Tests
```bash
pytest tests/ -v
pytest tests/ --cov=rush_ci --cov-report=html
```

#### 3. Code Quality
```bash
black rush_ci/
flake8 rush_ci/
mypy rush_ci/
```

#### 4. Manual Runs
```bash
# Full pipeline
python main.py --mode full

# Weekly brief only
python main.py --mode weekly

# Alert check only
python main.py --mode alerts

# Data fetch only
python main.py --mode fetch

# Test mode
python main.py --mode test

# Scheduler mode (continuous)
python main.py --mode scheduler
```

### Production Deployment

#### Option 1: GitHub Actions (Recommended)

1. Push code to main branch
2. Actions will run automatically
3. Monitor in Actions tab

#### Option 2: AWS Lambda

1. Create Lambda function
2. Upload code as ZIP
3. Set environment variables
4. Configure EventBridge triggers

#### Option 3: Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py", "--mode", "scheduler"]
```

```bash
docker build -t rush-ci .
docker run -d --env-file .env rush-ci
```

#### Option 4: VPS/Server

1. Set up Python 3.12 environment
2. Install dependencies
3. Configure systemd service
4. Set up cron jobs

### Monitoring and Maintenance

#### 1. Log Monitoring
- Check `logs/` directory for application logs
- Monitor GitHub Actions logs
- Set up log aggregation (optional)

#### 2. Data Quality Checks
- Monitor Airtable record counts
- Check for duplicate entries
- Verify alert accuracy

#### 3. API Rate Limits
- Monitor Twitter API usage
- Check OpenAI API quotas
- Track Airtable API limits

#### 4. Performance Optimization
- Adjust scraping intervals
- Optimize database queries
- Monitor memory usage

### Troubleshooting

#### Common Issues

1. **API Rate Limits**
   - Check API quotas in respective dashboards
   - Implement exponential backoff
   - Reduce scraping frequency

2. **Authentication Errors**
   - Verify API keys are correct
   - Check token expiration
   - Ensure proper permissions

3. **Data Duplication**
   - Clear Redis cache if needed
   - Check deduplication logic
   - Verify content hashing

4. **Missing Data**
   - Check source availability
   - Verify HTML structure changes
   - Test individual scrapers

#### Debug Mode

```bash
LOG_LEVEL=DEBUG python main.py --mode full
```

#### Manual Data Export

```python
from rush_ci.03_store import DataStore
store = DataStore()
export_path = store.export_data('json')
print(f"Data exported to: {export_path}")
```

### Security Considerations

1. **API Key Management**
   - Use environment variables
   - Rotate keys regularly
   - Use AWS Secrets Manager (production)

2. **Data Privacy**
   - Only collect public information
   - No personal data beyond job titles
   - Comply with GDPR/privacy laws

3. **Access Control**
   - Limit database access
   - Use read-only API keys where possible
   - Monitor access logs

### Scaling Considerations

1. **High Volume**
   - Implement queuing system
   - Use distributed processing
   - Optimize database queries

2. **Multiple Competitors**
   - Parallel processing
   - Separate data stores
   - Load balancing

3. **Real-time Requirements**
   - WebSocket connections
   - Event-driven architecture
   - Stream processing

### Support and Maintenance

#### Regular Tasks
- Weekly: Review alert accuracy
- Monthly: Update competitor configurations
- Quarterly: Review and optimize performance
- Annually: Security audit and key rotation

#### Contact Information
- Technical issues: Create GitHub issue
- Configuration changes: Update config files
- Emergency: Contact CI team directly

---

*This deployment guide covers the essential setup and maintenance tasks for the Rush Gaming CI System. For additional support, refer to the main README or contact the development team.* 