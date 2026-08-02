"""Cost Monitor - Complete Production Implementation"""
import logging
from typing import Dict, List
from datetime import datetime
import boto3

logger = logging.getLogger(__name__)

class CostMonitor:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.cost_history = []
        
        # Pricing
        self.GLUE_DPU_HOUR = 0.44
        self.S3_STORAGE_GB = 0.023
        self.S3_REQUEST_1K = 0.0004
        self.REDSHIFT_NODE_HOUR = 1.086
        self.LAMBDA_INVOCATION = 0.0000002
    
    def calc_glue_cost(self, dpu: int, hours: float) -> float:
        return dpu * hours * self.GLUE_DPU_HOUR
    
    def calc_s3_cost(self, gb_stored: float, requests: int = 0) -> float:
        storage = gb_stored * self.S3_STORAGE_GB
        req_cost = (requests / 1000) * self.S3_REQUEST_1K if requests else 0
        return storage + req_cost
    
    def calc_redshift_cost(self, nodes: int, hours: float) -> float:
        return nodes * hours * self.REDSHIFT_NODE_HOUR
    
    def calc_lambda_cost(self, invocations: int, gb_seconds: float) -> float:
        return (invocations * self.LAMBDA_INVOCATION) + (gb_seconds * 0.0000166667)
    
    def estimate_daily_cost(self, config: Dict) -> float:
        total = 0
        
        if 'glue_dpu_hours' in config:
            total += self.calc_glue_cost(config['glue_dpu'], config['glue_dpu_hours'])
        
        if 's3_gb' in config:
            total += self.calc_s3_cost(config['s3_gb'], config.get('s3_requests', 0))
        
        if 'redshift' in config:
            total += self.calc_redshift_cost(config['redshift']['nodes'], 24)
        
        return total
    
    def publish_metrics(self, namespace: str, metrics: List[Dict]):
        try:
            metric_data = []
            for m in metrics:
                metric_data.append({
                    'MetricName': m['name'],
                    'Value': m['value'],
                    'Unit': m.get('unit', 'None'),
                    'Timestamp': datetime.utcnow()
                })
            
            self.cloudwatch.put_metric_data(Namespace=namespace, MetricData=metric_data)
            logger.info(f"Published {len(metric_data)} metrics")
        except Exception as e:
            logger.error(f"Metric publication failed: {e}")
    
    def get_cost_report(self) -> Dict:
        return {
            'total_tracked': len(self.cost_history),
            'total_cost': sum(h['cost'] for h in self.cost_history),
            'history': self.cost_history
        }
