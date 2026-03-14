"""
Anomaly injection script
Enables anomaly flags for testing
"""
import os
import sys

def inject_anomaly(anomaly_type: str, value: str = None):
    """Inject anomaly by updating environment or config"""
    print(f"Injecting anomaly: {anomaly_type}")
    
    if anomaly_type == "delay":
        delay_seconds = float(value) if value else 2.0
        print(f"  - Setting artificial delay: {delay_seconds} seconds")
        print(f"  - Set environment: ENABLE_ANOMALY_DELAY=True, ANOMALY_DELAY_SECONDS={delay_seconds}")
        print(f"  - Or update docker-compose.yml backend environment section")
        
    elif anomaly_type == "errors":
        error_rate = float(value) if value else 0.1
        print(f"  - Setting random error rate: {error_rate * 100}%")
        print(f"  - Set environment: ENABLE_RANDOM_ERRORS=True, RANDOM_ERROR_RATE={error_rate}")
        print(f"  - Or update docker-compose.yml backend environment section")
        
    elif anomaly_type == "both":
        delay_seconds = float(value.split(",")[0]) if value and "," in value else 1.0
        error_rate = float(value.split(",")[1]) if value and "," in value else 0.05
        print(f"  - Setting delay: {delay_seconds}s and error rate: {error_rate * 100}%")
        print(f"  - Set environment variables accordingly")
        
    else:
        print(f"Unknown anomaly type: {anomaly_type}")
        print("Available types: delay, errors, both")
        sys.exit(1)
    
    print("\nTo apply changes:")
    print("1. Update docker-compose.yml backend environment section")
    print("2. Restart backend: docker-compose restart backend")
    print("3. Run load tests to see the impact")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inject_anomaly.py <anomaly_type> [value]")
        print("  anomaly_type: delay, errors, or both")
        print("  value: for delay (seconds), errors (rate 0-1), or both (delay,rate)")
        sys.exit(1)
    
    anomaly_type = sys.argv[1]
    value = sys.argv[2] if len(sys.argv) > 2 else None
    inject_anomaly(anomaly_type, value)


