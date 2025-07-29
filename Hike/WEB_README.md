# Rush Gaming CI - Web Interface

A modern, real-time web dashboard for the Rush Gaming Competitive Intelligence system.

## 🚀 Quick Start

### Option 1: Direct Start
```bash
python web_app.py
```

### Option 2: Using Startup Script
```bash
python start_web.py
```

## 📊 Features

### Dashboard (`/`)
- **Real-time System Status**: Live monitoring of CI system health
- **Competitor Overview**: Visual cards showing all monitored competitors
- **Recent Alerts**: Real-time alert feed with priority indicators
- **Data Metrics**: Key performance indicators and data statistics
- **Pipeline Control**: One-click pipeline execution with live status updates

### Briefs (`/briefs`)
- **Weekly Intelligence Briefs**: View generated competitive intelligence reports
- **Markdown Rendering**: Beautifully formatted briefs with syntax highlighting
- **Download & Share**: Export briefs as PDF or share via email/Slack
- **Historical View**: Access to all past weekly briefs

### Configuration (`/config`)
- **Competitor Management**: View and edit competitor settings
- **Alert Rules**: Configure notification triggers and priorities
- **System Settings**: Monitor data sources and automation schedules

## 🎨 UI Features

- **Modern Design**: Gradient backgrounds, glassmorphism effects, smooth animations
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **Real-time Updates**: WebSocket-powered live updates without page refresh
- **Interactive Elements**: Hover effects, loading states, toast notifications
- **Dark Mode Ready**: Clean, professional interface design

## 🔧 Technical Stack

- **Backend**: Flask + Flask-SocketIO
- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **Real-time**: WebSocket connections for live updates
- **Styling**: Custom CSS with modern design patterns
- **Icons**: Font Awesome 6

## 📱 API Endpoints

- `GET /api/status` - System status and health check
- `POST /api/run-pipeline` - Execute CI pipeline
- `GET /api/competitors` - List all competitors
- `GET /api/alerts` - Recent alerts
- `GET /api/data` - Recent data samples

## 🎯 Usage

1. **Start the web interface** using one of the methods above
2. **Open your browser** and navigate to `http://localhost:5000`
3. **Explore the dashboard** to see system status and competitor overview
4. **Run the pipeline** by clicking the "Run Pipeline" button
5. **View briefs** by clicking the "Briefs" link in the navigation
6. **Check configuration** by clicking the "Config" link

## 🔄 Real-time Features

- **Live Status Updates**: System status refreshes every 30 seconds
- **Pipeline Progress**: Real-time pipeline execution status
- **Alert Notifications**: Instant alert delivery via WebSocket
- **Data Refresh**: Automatic data updates without page reload

## 🛠️ Development

### File Structure
```
templates/
├── dashboard.html    # Main dashboard page
├── briefs.html       # Weekly briefs viewer
└── config.html       # Configuration management

web_app.py            # Main Flask application
start_web.py          # Startup script with error handling
```

### Customization
- Modify `templates/dashboard.html` for dashboard changes
- Update `templates/briefs.html` for brief display customization
- Edit `templates/config.html` for configuration interface
- Add new API endpoints in `web_app.py`

## 🚨 Troubleshooting

### Common Issues

1. **Port 5000 in use**: Change the port in `web_app.py` or `start_web.py`
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Template errors**: Ensure `templates/` directory exists with all HTML files
4. **Import errors**: Check that all CI system modules are properly installed

### Debug Mode
The web interface runs in debug mode by default. Check the console for detailed error messages and stack traces.

## 📈 Performance

- **Lightweight**: Minimal JavaScript, optimized CSS
- **Fast Loading**: CDN resources, efficient rendering
- **Scalable**: Modular design, easy to extend
- **Responsive**: Mobile-first design approach

---

**Ready to monitor your competitors? Start the web interface and dive into real-time competitive intelligence! 🎯** 