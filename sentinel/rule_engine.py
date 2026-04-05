import os
import json
import logging
from datetime import datetime, timedelta
from supabase import create_client, Client

class RuleEngine:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            logging.warning("SUPABASE_URL or SUPABASE_KEY not set. Rule Engine will run in dry-run mode if no DB connection available.")
            
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        except Exception as e:
            self.supabase = None
            logging.error(f"Failed to initialize Supabase client: {e}")

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - RuleEngine - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def fetch_active_rules(self):
        """Fetch all active rules from alert_rules table."""
        if not self.supabase: return []
        response = self.supabase.table('alert_rules').select('*').eq('is_active', True).execute()
        return response.data

    def fetch_todays_performance(self):
        """Fetch today's performance metrics for all ad accounts, joined with their client data."""
        if not self.supabase: return []
        # Get today's performance
        today = datetime.now().date().isoformat()
        
        # We need client targets as well, so we pull clients, ad_accounts, and performance
        # For simplicity in this engine, we'll do separate queries and join them in memory 
        # or use a view if one exists. Custom views are better, but we'll manually join here.
        
        clients_res = self.supabase.table('clients').select('id, client_name, business_type, target_roas, target_cpa').execute()
        accounts_res = self.supabase.table('ad_accounts').select('id, client_id, platform, account_name').execute()
        perf_res = self.supabase.table('performance_daily').select('*').eq('date', today).execute()
        
        if not clients_res.data or not accounts_res.data or not perf_res.data:
            return []
            
        clients_map = {c['id']: c for c in clients_res.data}
        accounts_map = {a['id']: a for a in accounts_res.data}
        
        enriched_data = []
        for p in perf_res.data:
            acc = accounts_map.get(p['ad_account_id'])
            if not acc: continue
            client = clients_map.get(acc['client_id'])
            if not client: continue
            
            enriched_data.append({
                'account_id': p['ad_account_id'],
                'account_name': acc['account_name'],
                'platform': acc['platform'],
                'client_name': client['client_name'],
                'business_type': client['business_type'],
                'target_roas': client.get('target_roas') or 0,
                'target_cpa': client.get('target_cpa') or 0,
                'spend': p.get('spend', 0),
                'conversions': p.get('conversions', 0),
                'roas': p.get('roas', 0),
                'cpa': p.get('cpa', 0),
                'clicks': p.get('clicks', 0),
                'impressions': p.get('impressions', 0)
            })
            
        return enriched_data

    def evaluate_rule(self, rule, data_row):
        """Evaluate a single rule against a single data row."""
        conditions = rule.get('conditions', {})
        
        # Check platform and business type match
        if rule['platform'] != 'all' and rule['platform'] != data_row['platform']:
            return False
            
        if rule['business_type'] != 'all' and rule['business_type'] != data_row['business_type']:
            return False

        # Parse conditions
        metric = conditions.get('metric')
        comparison = conditions.get('comparison') # can be a string (key in data_row) or hardcoded value
        operator = conditions.get('operator')
        value = conditions.get('value')
        min_spend = conditions.get('min_spend', 0)
        min_conversions = conditions.get('min_conversions', 0)
        
        # Check minimums
        if data_row.get('spend', 0) < min_spend:
            return False
            
        if data_row.get('conversions', 0) < min_conversions:
            return False

        actual_val = data_row.get(metric, 0)
        
        # Determine target threshold
        target_val = None
        if comparison and comparison in data_row:
            target_val = data_row[comparison]
        elif value is not None:
            target_val = value
            
        # Specific threshold ratio logic (like ROAS < 50% target)
        if 'threshold_ratio' in conditions and target_val is not None:
            target_val = float(target_val) * float(conditions['threshold_ratio'])

        if target_val is None:
            return False
            
        # Evaluate operator
        actual_val = float(actual_val)
        target_val = float(target_val)
        
        if operator == '>': return actual_val > target_val
        elif operator == '<': return actual_val < target_val
        elif operator == '=': return actual_val == target_val
        elif operator == '>=': return actual_val >= target_val
        elif operator == '<=': return actual_val <= target_val
        
        return False

    def check_cooldown(self, ad_account_id, alert_type, cooldown_hours):
        """Check if an alert of this type was recently sent."""
        if not self.supabase or not cooldown_hours: return True
        
        cutoff = datetime.now() - timedelta(hours=cooldown_hours)
        res = self.supabase.table('alerts') \
            .select('id') \
            .eq('ad_account_id', ad_account_id) \
            .eq('alert_type', alert_type) \
            .gte('created_at', cutoff.isoformat()) \
            .execute()
            
        return len(res.data) == 0

    def generate_alerts(self):
        """Main execution loop for the rule engine."""
        self.logger.info("Starting Rule Engine Evaluation...")
        
        rules = self.fetch_active_rules()
        if not rules:
            self.logger.info("No active rules found. Exiting.")
            return

        perf_data = self.fetch_todays_performance()
        if not perf_data:
            self.logger.info("No performance data found for today. Exiting.")
            return
            
        alerts_to_insert = []
        for data in perf_data:
            for rule in rules:
                if self.evaluate_rule(rule, data):
                    
                    # Rule Triggered! Check Cooldown.
                    cooldown = rule.get('conditions', {}).get('cooldown_hours', 0)
                    if self.check_cooldown(data['account_id'], rule['template_type'], cooldown):
                        
                        # Generate alert row
                        title = rule['name']
                        description = rule.get('action_suggested', '')
                        
                        self.logger.warning(f"ALERT TRIGGERED: {title} for account {data['account_name']}")
                        
                        alerts_to_insert.append({
                            'ad_account_id': data['account_id'],
                            'alert_type': rule['template_type'],
                            'severity': rule['severity'],
                            'title': title,
                            'description': description,
                            'metric_value': float(data.get(rule.get('conditions', {}).get('metric', 'spend'), 0)),
                            'status': 'open'
                        })
                        
        if alerts_to_insert and self.supabase:
            try:
                self.supabase.table('alerts').insert(alerts_to_insert).execute()
                self.logger.info(f"Successfully inserted {len(alerts_to_insert)} new alerts into database.")
            except Exception as e:
                self.logger.error(f"Failed to insert alerts to database: {e}")
                
        return alerts_to_insert

if __name__ == '__main__':
    engine = RuleEngine()
    engine.generate_alerts()
