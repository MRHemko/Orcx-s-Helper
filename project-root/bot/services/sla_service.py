from datetime import datetime

def start_sla():
    return datetime.utcnow()

def end_sla_seconds(start):
    return int((datetime.utcnow() - start).total_seconds())

def format_duration(seconds: int):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}h {m}m"
