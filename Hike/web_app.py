#!/usr/bin/env python3
"""
Rush Gaming CI System - Web Interface
Fast Flask-based dashboard for competitor intelligence
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import threading
import queue

# Import our CI system
from rush_ci.config import config
from rush_ci.utils.logger import get_logger
from main import RushCISystem

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rush-ci-secret-key-2024'

logger = get_logger(__name__)

# Global variables
ci_system = None
task_queue = queue.Queue()
task_results = {}

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    try:
        # Check if we have any recent data
        data_dir = Path('data')
        has_data = data_dir.exists() and any(data_dir.iterdir())
        
        # Check if we have any briefs
        briefs_dir = Path('briefs')
        has_briefs = briefs_dir.exists() and any(briefs_dir.glob('*.md'))
        
        # Get latest brief if available
        latest_brief = None
        if has_briefs:
            brief_files = list(briefs_dir.glob('*.md'))
            if brief_files:
                latest_brief_file = max(brief_files, key=lambda x: x.stat().st_mtime)
                with open(latest_brief_file, 'r', encoding='utf-8') as f:
                    latest_brief = f.read()
        
        return jsonify({
            'status': 'running',
            'has_data': has_data,
            'has_briefs': has_briefs,
            'latest_brief': latest_brief,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/run-pipeline', methods=['POST'])
def api_run_pipeline():
    """API endpoint to run the CI pipeline"""
    try:
        # Start pipeline in background
        def run_pipeline():
            try:
                global ci_system
                if ci_system is None:
                    ci_system = RushCISystem()
                
                # Run the pipeline
                success = ci_system.run_full_pipeline()
                
                # Log result
                logger.info(f"Pipeline completed with success: {success}")
                
            except Exception as e:
                logger.error(f"Pipeline error: {e}")
        
        # Start pipeline in background thread
        thread = threading.Thread(target=run_pipeline)
        thread.daemon = True
        thread.start()
        
        return jsonify({'status': 'started', 'message': 'Pipeline started successfully'})
        
    except Exception as e:
        logger.error(f"Error starting pipeline: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/competitors')
def api_competitors():
    """API endpoint to get competitor data"""
    try:
        competitors = config.competitors
        return jsonify(competitors)
    except Exception as e:
        logger.error(f"Error getting competitors: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/alerts')
def api_alerts():
    """API endpoint to get recent alerts"""
    try:
        # This would normally come from the database
        # For now, return sample data
        sample_alerts = [
            {
                'id': 1,
                'company': 'Mobile Premier League',
                'type': 'funding',
                'message': 'MPL raises $150M Series D funding',
                'priority': 'high',
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': 2,
                'company': 'WinZO Games',
                'type': 'launch',
                'message': 'WinZO launches new fantasy cricket game',
                'priority': 'medium',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat()
            }
        ]
        return jsonify(sample_alerts)
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/data')
def api_data():
    """API endpoint to get recent data"""
    try:
        # Check for recent data files
        data_dir = Path('data')
        if not data_dir.exists():
            return jsonify({'data': [], 'message': 'No data available'})
        
        # Get most recent data file
        data_files = list(data_dir.glob('*.json'))
        if not data_files:
            return jsonify({'data': [], 'message': 'No data files found'})
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error getting data: {e}")
        return jsonify({'error': str(e)})

@app.route('/briefs')
def briefs():
    """Page to view weekly briefs"""
    try:
        briefs_dir = Path('briefs')
        if not briefs_dir.exists():
            return render_template('briefs.html', briefs=[])
        
        brief_files = list(briefs_dir.glob('*.md'))
        briefs_data = []
        
        for brief_file in sorted(brief_files, key=lambda x: x.stat().st_mtime, reverse=True):
            with open(brief_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            briefs_data.append({
                'filename': brief_file.name,
                'content': content,
                'date': datetime.fromtimestamp(brief_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            })
        
        return render_template('briefs.html', briefs=briefs_data)
        
    except Exception as e:
        logger.error(f"Error loading briefs: {e}")
        return render_template('briefs.html', briefs=[], error=str(e))

@app.route('/config')
def config_page():
    """Page to view and edit configuration"""
    try:
        competitors = config.competitors
        alert_rules = config.alert_rules
        return render_template('config.html', competitors=competitors, alert_rules=alert_rules)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return render_template('config.html', competitors={}, alert_rules={}, error=str(e))

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    # Create static directory if it doesn't exist
    static_dir = Path('static')
    static_dir.mkdir(exist_ok=True)
    
    print("🚀 Starting Rush Gaming CI Web Interface...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("📋 Briefs available at: http://localhost:5000/briefs")
    print("⚙️  Config available at: http://localhost:5000/config")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 