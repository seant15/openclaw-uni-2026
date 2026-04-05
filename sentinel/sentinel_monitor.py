import os
import time
import requests
import logging
from supabase import create_client, Client
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from sentinel.rule_engine import RuleEngine

class SentinelPerformanceMonitor:
    def __init__(self):
        # Supabase Configuration
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Slack Configuration
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.slack_channel = os.getenv('SLACK_ALERT_CHANNEL', '#marketing-alerts')
        self.slack_client = WebClient(token=self.slack_token)

        # Logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - Sentinel - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Initialize the new Rule Engine
        self.rule_engine = RuleEngine()

    def fetch_ad_performance_metrics(self):
        """
        Fetch performance metrics from Ad APIs
        Placeholder for actual API integration
        """
        try:
            # Replace with actual Ad API endpoint
            response = requests.get('https://ads-api.example.com/performance', 
                                    headers={'Authorization': f'Bearer {os.getenv("AD_API_TOKEN")}'})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch Ad API metrics: {e}")
            return None

    def check_integration_health(self):
        """
        Check health of marketing integrations via Supabase
        """
        try:
            # Example: Check recent integration logs
            result = self.supabase.table('integration_logs').select('*').filter('status', 'eq', 'error').execute()
            return result.data
        except Exception as e:
            self.logger.error(f"Supabase integration health check failed: {e}")
            return None

    def send_slack_alert(self, title, message, severity='warning'):
        """
        Send alerts to Slack with color coding based on severity
        """
        color_map = {
            'critical': 'danger',
            'high': 'danger',
            'warning': 'warning',
            'info': 'good'
        }
        
        try:
            self.slack_client.chat_postMessage(
                channel=self.slack_channel,
                attachments=[{
                    'color': color_map.get(severity.lower(), 'warning'),
                    'title': title,
                    'text': message
                }]
            )
        except SlackApiError as e:
            self.logger.error(f"Slack alert failed: {e}")

    def run_monitoring_cycle(self):
        """
        Primary monitoring cycle
        """
        self.logger.info("Sentinel Performance Monitor - Starting monitoring cycle")

        # Check Ad Performance
        ad_metrics = self.fetch_ad_performance_metrics()
        if ad_metrics:
            # Example performance anomaly detection
            if ad_metrics.get('error_rate', 0) > 10:
                self.send_slack_alert(
                    'AD API Performance Anomaly', 
                    f"High error rate detected: {ad_metrics['error_rate']}%", 
                    severity='critical'
                )

        # Check Integration Health
        integration_errors = self.check_integration_health()
        if integration_errors:
            self.send_slack_alert(
                'Marketing Integration Errors', 
                f"{len(integration_errors)} recent integration failures detected", 
                severity='high'
            )

        # Run the dynamically configured DB Alerts (Rule Engine)
        try:
            new_alerts = self.rule_engine.generate_alerts()
            if new_alerts:
                for alert in new_alerts:
                    # Push local DB alerts to slack
                    self.send_slack_alert(
                        title=f"🚨 {alert['title']}",
                        message=f"{alert['description']} (Metric: {alert.get('metric_value', 'N/A')})",
                        severity=alert['severity']
                    )
        except Exception as e:
            self.logger.error(f"Rule Engine failed: {e}")

def main():
    monitor = SentinelPerformanceMonitor()
    
    while True:
        monitor.run_monitoring_cycle()
        time.sleep(300)  # Run every 5 minutes

if __name__ == '__main__':
    main()