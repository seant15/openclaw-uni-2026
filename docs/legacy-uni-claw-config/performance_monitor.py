import os
import sys
import json
import logging
from datetime import datetime, timedelta

class PerformanceMonitor:
    def __init__(self, platforms=['meta', 'google_ads']):
        self.platforms = platforms
        self.log_dir = '/data/workspace/logs'
        self.setup_logging()
    
    def setup_logging(self):
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configure logging
        log_file = os.path.join(self.log_dir, f'performance_monitor_{datetime.now().strftime("%Y%m%d")}.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def fetch_platform_data(self, platform):
        """
        Simulate fetching performance data for a platform.
        In a real implementation, this would connect to platform APIs.
        """
        # Mock data generation
        return {
            'total_spend': round(100 * random.random(), 2),
            'impressions': int(1000 * random.random()),
            'clicks': int(100 * random.random()),
            'roas': round(random.uniform(0.5, 3.0), 2)
        }
    
    def check_performance(self):
        """
        Check performance across all configured platforms
        """
        alerts = []
        
        for platform in self.platforms:
            try:
                data = self.fetch_platform_data(platform)
                
                # Anomaly detection rules
                if data['total_spend'] == 0:
                    alert = f"CRITICAL ALERT: Zero spend detected on {platform}"
                    alerts.append(alert)
                    self.logger.critical(alert)
                
                if data['roas'] < 1.0:
                    alert = f"WARNING: Low ROAS ({data['roas']}) on {platform}"
                    alerts.append(alert)
                    self.logger.warning(alert)
                
                # Log performance details
                self.logger.info(f"{platform.upper()} Performance: {json.dumps(data)}")
            
            except Exception as e:
                error = f"Error monitoring {platform}: {str(e)}"
                self.logger.error(error)
                alerts.append(error)
        
        return alerts
    
    def sync_to_database(self, data):
        """
        Simulate syncing performance data to a database
        """
        try:
            # In a real scenario, this would connect to an actual database
            db_file = os.path.join(self.log_dir, 'performance_database.json')
            with open(db_file, 'a') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }, f)
                f.write('\n')
            self.logger.info("Performance data synced to database")
        except Exception as e:
            self.logger.error(f"Database sync failed: {str(e)}")

def main():
    monitor = PerformanceMonitor()
    alerts = monitor.check_performance()
    
    if alerts:
        # In a real implementation, this could trigger email/SMS alerts
        print("Performance Alerts:", alerts)

if __name__ == '__main__':
    main()