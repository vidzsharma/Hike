#!/usr/bin/env python3
"""
Main orchestration module for Rush Gaming Competitive Intelligence System

Coordinates all components and provides the main entry point.
"""

import sys
import time
import schedule
from datetime import datetime
from pathlib import Path

# Add the rush_ci package to the path
sys.path.append(str(Path(__file__).parent))

from rush_ci.config import config
from rush_ci.utils.logger import get_logger
from rush_ci.utils.helpers import get_current_iso_week

# Import all modules
from rush_ci.fetch import DataFetcher
from rush_ci.parse import DataParser
from rush_ci.store import DataStore
from rush_ci.summarise import AISummarizer
from rush_ci.alert import AlertManager

logger = get_logger(__name__)


class RushCISystem:
    """Main orchestration class for the Rush Gaming CI System"""
    
    def __init__(self):
        self.fetcher = DataFetcher()
        self.parser = DataParser()
        self.store = DataStore()
        self.summarizer = AISummarizer()
        self.alert_manager = AlertManager()
        
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories for the system"""
        directories = ['data', 'logs', 'briefs', 'config']
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def run_full_pipeline(self) -> bool:
        """
        Run the complete CI pipeline
        
        Returns:
            Success status
        """
        logger.info("Starting Rush Gaming CI pipeline")
        start_time = time.time()
        
        try:
            # Step 1: Fetch data from all sources
            logger.info("Step 1: Fetching data from all sources")
            raw_data = self.fetcher.fetch_all_sources()
            
            if not raw_data or not any(raw_data.values()):
                logger.warning("No data fetched from any source")
                return False
            
            # Save raw data for debugging
            self._save_raw_data(raw_data)
            
            # Step 2: Parse and analyze data
            logger.info("Step 2: Parsing and analyzing data")
            parsed_data = self.parser.parse_all_data(raw_data)
            
            # Save parsed data
            self._save_parsed_data(parsed_data)
            
            # Step 3: Store data to databases
            logger.info("Step 3: Storing data to databases")
            storage_success = self.store.store_all_data(parsed_data)
            
            if not storage_success:
                logger.error("Data storage failed")
                return False
            
            # Step 4: Generate AI summaries
            logger.info("Step 4: Generating AI summaries")
            weekly_brief = self.summarizer.generate_weekly_brief(parsed_data)
            
            # Step 5: Send alerts
            logger.info("Step 5: Processing alerts")
            alerts = parsed_data.get('alerts', [])
            alert_success = self.alert_manager.process_alerts(alerts)
            
            # Step 6: Send weekly summary (if it's the right time)
            if self._should_send_weekly_summary():
                logger.info("Step 6: Sending weekly summary")
                self.alert_manager.send_weekly_summary(weekly_brief)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            logger.info(f"Pipeline completed successfully in {execution_time:.2f} seconds")
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return False
    
    def run_weekly_brief(self) -> bool:
        """
        Run weekly brief generation (typically on Sundays)
        
        Returns:
            Success status
        """
        logger.info("Generating weekly competitive intelligence brief")
        
        try:
            # Load latest parsed data
            parsed_data = self._load_latest_parsed_data()
            
            if not parsed_data:
                logger.error("No parsed data available for weekly brief")
                return False
            
            # Generate weekly brief
            weekly_brief = self.summarizer.generate_weekly_brief(parsed_data)
            
            if weekly_brief:
                # Send weekly summary
                self.alert_manager.send_weekly_summary(weekly_brief)
                logger.info("Weekly brief generated and sent successfully")
                return True
            else:
                logger.error("Failed to generate weekly brief")
                return False
                
        except Exception as e:
            logger.error(f"Weekly brief generation failed: {e}")
            return False
    
    def run_alert_check(self) -> bool:
        """
        Run alert check (typically every 6 hours)
        
        Returns:
            Success status
        """
        logger.info("Running alert check")
        
        try:
            # Load latest parsed data
            parsed_data = self._load_latest_parsed_data()
            
            if not parsed_data:
                logger.warning("No parsed data available for alert check")
                return False
            
            # Process alerts
            alerts = parsed_data.get('alerts', [])
            success = self.alert_manager.process_alerts(alerts)
            
            if success:
                logger.info(f"Alert check completed. Processed {len(alerts)} alerts")
            else:
                logger.error("Alert check failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Alert check failed: {e}")
            return False
    
    def run_data_fetch_only(self) -> bool:
        """
        Run only data fetching (for testing or manual runs)
        
        Returns:
            Success status
        """
        logger.info("Running data fetch only")
        
        try:
            raw_data = self.fetcher.fetch_all_sources()
            self._save_raw_data(raw_data)
            
            logger.info("Data fetch completed")
            return True
            
        except Exception as e:
            logger.error(f"Data fetch failed: {e}")
            return False
    
    def run_test_mode(self) -> bool:
        """
        Run system in test mode
        
        Returns:
            Success status
        """
        logger.info("Running Rush Gaming CI System in test mode")
        
        try:
            # Test configuration
            if not config.validate_config():
                logger.error("Configuration validation failed")
                return False
            
            # Test alert system
            alert_success = self.alert_manager.send_test_alert()
            
            if alert_success:
                logger.info("Test mode completed successfully")
                return True
            else:
                logger.error("Test mode failed")
                return False
                
        except Exception as e:
            logger.error(f"Test mode failed: {e}")
            return False
    
    def _save_raw_data(self, raw_data: dict) -> None:
        """Save raw data to file"""
        try:
            import json
            file_path = f'data/raw_fetch_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(file_path, 'w') as f:
                json.dump(raw_data, f, default=str, indent=2)
            logger.debug(f"Raw data saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving raw data: {e}")
    
    def _save_parsed_data(self, parsed_data: dict) -> None:
        """Save parsed data to file"""
        try:
            import json
            file_path = f'data/parsed_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(file_path, 'w') as f:
                json.dump(parsed_data, f, default=str, indent=2)
            logger.debug(f"Parsed data saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving parsed data: {e}")
    
    def _load_latest_parsed_data(self) -> dict:
        """Load the latest parsed data file"""
        try:
            import json
            import glob
            
            # Find the latest parsed data file
            data_files = glob.glob('data/parsed_data_*.json')
            if not data_files:
                return {}
            
            latest_file = max(data_files, key=lambda x: Path(x).stat().st_mtime)
            
            with open(latest_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading parsed data: {e}")
            return {}
    
    def _should_send_weekly_summary(self) -> bool:
        """Check if weekly summary should be sent (Sundays)"""
        return datetime.now().weekday() == 6  # Sunday
    
    def setup_scheduling(self):
        """Setup automated scheduling"""
        logger.info("Setting up automated scheduling")
        
        # Run full pipeline every 6 hours
        schedule.every(6).hours.do(self.run_full_pipeline)
        
        # Run alert check every 2 hours
        schedule.every(2).hours.do(self.run_alert_check)
        
        # Run weekly brief every Sunday at 23:55 IST
        schedule.every().sunday.at("23:55").do(self.run_weekly_brief)
        
        logger.info("Scheduling setup completed")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        logger.info("Starting scheduler loop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rush Gaming Competitive Intelligence System')
    parser.add_argument('--mode', choices=['full', 'weekly', 'alerts', 'fetch', 'test', 'scheduler'], 
                       default='full', help='Run mode')
    parser.add_argument('--config-check', action='store_true', help='Check configuration only')
    
    args = parser.parse_args()
    
    # Check configuration first
    if not config.validate_config():
        logger.error("Configuration validation failed. Please check your .env file.")
        sys.exit(1)
    
    if args.config_check:
        logger.info("Configuration check passed")
        sys.exit(0)
    
    # Initialize system
    ci_system = RushCISystem()
    
    # Run based on mode
    if args.mode == 'full':
        success = ci_system.run_full_pipeline()
    elif args.mode == 'weekly':
        success = ci_system.run_weekly_brief()
    elif args.mode == 'alerts':
        success = ci_system.run_alert_check()
    elif args.mode == 'fetch':
        success = ci_system.run_data_fetch_only()
    elif args.mode == 'test':
        success = ci_system.run_test_mode()
    elif args.mode == 'scheduler':
        ci_system.setup_scheduling()
        ci_system.run_scheduler()
        success = True
    else:
        logger.error(f"Unknown mode: {args.mode}")
        success = False
    
    if success:
        logger.info("Operation completed successfully")
        sys.exit(0)
    else:
        logger.error("Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 