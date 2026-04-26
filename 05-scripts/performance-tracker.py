#!/usr/bin/env python3
"""
Performance Tracker - Daily system performance metrics collection
Runs at 22:00 daily to record response times, error rates, and resource usage
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration
DATA_DIR = Path("/home/admin/.openclaw/workspace/06-data/performance")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_timestamp():
    """Get current ISO timestamp"""
    return datetime.now().isoformat()

def get_date_str():
    """Get current date string for filename"""
    return datetime.now().strftime("%Y-%m-%d")

def collect_system_metrics():
    """Collect system resource usage metrics"""
    metrics = {}
    
    # CPU usage
    try:
        result = subprocess.run(
            ["top", "-bn1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=10
        )
        for line in result.stdout.split("\n"):
            if "Cpu(s)" in line:
                parts = line.split(",")
                for part in parts:
                    if "us" in part:
                        metrics["cpu_user"] = float(part.split()[0].replace("%", ""))
                    elif "sy" in part:
                        metrics["cpu_system"] = float(part.split()[0].replace("%", ""))
                break
    except Exception as e:
        metrics["cpu_error"] = str(e)
    
    # Memory usage
    try:
        result = subprocess.run(
            ["free", "-m"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=10
        )
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if line.startswith("Mem:"):
                parts = line.split()
                total = float(parts[1])
                used = float(parts[2])
                metrics["memory_total_mb"] = total
                metrics["memory_used_mb"] = used
                metrics["memory_usage_percent"] = round((used / total) * 100, 2)
                break
    except Exception as e:
        metrics["memory_error"] = str(e)
    
    # Disk usage
    try:
        result = subprocess.run(
            ["df", "-h", "/"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=10
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            metrics["disk_usage_percent"] = float(parts[4].replace("%", ""))
            metrics["disk_used"] = parts[2]
            metrics["disk_available"] = parts[3]
    except Exception as e:
        metrics["disk_error"] = str(e)
    
    # Load average
    try:
        with open("/proc/loadavg", "r") as f:
            load = f.read().strip().split()
            metrics["load_1min"] = float(load[0])
            metrics["load_5min"] = float(load[1])
            metrics["load_15min"] = float(load[2])
    except Exception as e:
        metrics["load_error"] = str(e)
    
    return metrics

def collect_openclaw_metrics():
    """Collect OpenClaw-specific metrics"""
    metrics = {}
    
    try:
        # Check Gateway status
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=30
        )
        metrics["gateway_status"] = "running" if result.returncode == 0 else "error"
        metrics["gateway_output"] = result.stdout[:500] if result.stdout else ""
    except Exception as e:
        metrics["gateway_status"] = "error"
        metrics["gateway_error"] = str(e)
    
    try:
        # Check session status
        result = subprocess.run(
            ["openclaw", "sessions", "list", "--limit", "1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=30
        )
        metrics["sessions_available"] = result.returncode == 0
    except Exception as e:
        metrics["sessions_error"] = str(e)
    
    return metrics

def collect_cron_metrics():
    """Collect cron job execution metrics"""
    metrics = {}
    
    try:
        jobs_file = Path("/home/admin/.openclaw/cron/jobs.json")
        if jobs_file.exists():
            with open(jobs_file, "r") as f:
                data = json.load(f)
            
            jobs = data.get("jobs", [])
            metrics["total_jobs"] = len(jobs)
            metrics["enabled_jobs"] = sum(1 for j in jobs if j.get("enabled", False))
            
            # Count by status
            ok_count = sum(1 for j in jobs if j.get("state", {}).get("lastStatus") == "ok")
            error_count = sum(1 for j in jobs if j.get("state", {}).get("lastStatus") == "error")
            
            metrics["jobs_ok"] = ok_count
            metrics["jobs_error"] = error_count
            metrics["jobs_success_rate"] = round((ok_count / len(jobs)) * 100, 2) if jobs else 0
    except Exception as e:
        metrics["cron_error"] = str(e)
    
    return metrics

def analyze_trends():
    """Analyze performance trends from historical data"""
    trends = {
        "summary": "No historical data available",
        "alerts": []
    }
    
    # Get last 7 days of data
    historical_files = sorted(DATA_DIR.glob("metrics-*.json"))[-7:]
    
    if len(historical_files) >= 2:
        try:
            old_data = None
            new_data = None
            
            with open(historical_files[0], "r") as f:
                old_data = json.load(f)
            with open(historical_files[-1], "r") as f:
                new_data = json.load(f)
            
            # Compare key metrics
            old_mem = old_data.get("system", {}).get("memory_usage_percent", 0)
            new_mem = new_data.get("system", {}).get("memory_usage_percent", 0)
            
            old_disk = old_data.get("system", {}).get("disk_usage_percent", 0)
            new_disk = new_data.get("system", {}).get("disk_usage_percent", 0)
            
            trends["summary"] = f"Comparing {len(historical_files)} days of data"
            
            if new_mem > old_mem + 10:
                trends["alerts"].append(f"⚠️ Memory usage increased: {old_mem}% → {new_mem}%")
            
            if new_disk > old_disk + 5:
                trends["alerts"].append(f"⚠️ Disk usage increased: {old_disk}% → {new_disk}%")
            
            if new_disk > 85:
                trends["alerts"].append(f"🔴 High disk usage: {new_disk}%")
            
            if new_mem > 85:
                trends["alerts"].append(f"🔴 High memory usage: {new_mem}%")
                
        except Exception as e:
            trends["error"] = str(e)
    
    return trends

def save_metrics(data):
    """Save metrics to file"""
    date_str = get_date_str()
    filename = DATA_DIR / f"metrics-{date_str}.json"
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Also update latest.json for easy access
    latest_file = DATA_DIR / "latest.json"
    with open(latest_file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename

def main():
    """Main execution"""
    print(f"📊 Performance Tracker - {get_timestamp()}")
    print("=" * 50)
    
    # Collect all metrics
    print("🔍 Collecting system metrics...")
    system_metrics = collect_system_metrics()
    
    print("🔍 Collecting OpenClaw metrics...")
    openclaw_metrics = collect_openclaw_metrics()
    
    print("🔍 Collecting cron metrics...")
    cron_metrics = collect_cron_metrics()
    
    print("📈 Analyzing trends...")
    trends = analyze_trends()
    
    # Compile full report
    report = {
        "timestamp": get_timestamp(),
        "date": get_date_str(),
        "system": system_metrics,
        "openclaw": openclaw_metrics,
        "cron": cron_metrics,
        "trends": trends
    }
    
    # Save to file
    filename = save_metrics(report)
    print(f"💾 Metrics saved to: {filename}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 Performance Summary:")
    print(f"  CPU: {system_metrics.get('cpu_user', 'N/A')}% user, {system_metrics.get('cpu_system', 'N/A')}% system")
    print(f"  Memory: {system_metrics.get('memory_usage_percent', 'N/A')}% ({system_metrics.get('memory_used_mb', 'N/A')}MB / {system_metrics.get('memory_total_mb', 'N/A')}MB)")
    print(f"  Disk: {system_metrics.get('disk_usage_percent', 'N/A')}% used")
    print(f"  Load: {system_metrics.get('load_1min', 'N/A')} (1m), {system_metrics.get('load_5min', 'N/A')} (5m)")
    print(f"  Gateway: {openclaw_metrics.get('gateway_status', 'N/A')}")
    print(f"  Cron Jobs: {cron_metrics.get('enabled_jobs', 0)} enabled, {cron_metrics.get('jobs_success_rate', 'N/A')}% success rate")
    
    if trends.get("alerts"):
        print("\n⚠️ Alerts:")
        for alert in trends["alerts"]:
            print(f"  {alert}")
    
    print("\n✅ Performance tracking complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
