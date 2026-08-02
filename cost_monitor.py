import boto3

class CostMonitor:
    def __init__(self):
        self.cw = boto3.client('cloudwatch')
    
    def calc_glue(self, dpu_hours: float):
        return dpu_hours * 0.44
    
    def calc_s3(self, gb_stored: float, requests: int):
        return (gb_stored * 0.023) + (requests / 1000 * 0.0004)
    
    def calc_redshift(self, nodes: int, hours: float):
        return nodes * hours * 1.086
    
    def monitor_job(self, job_name: str, config: dict):
        cost = self.calc_glue(config['dpu'] * config['duration'] / 60)
        self.cw.put_metric_data(
            Namespace='CostMonitor',
            MetricData=[{'MetricName': 'JobCost', 'Value': cost, 'Unit': 'None'}]
        )
        return {'cost': cost, 'job': job_name}
