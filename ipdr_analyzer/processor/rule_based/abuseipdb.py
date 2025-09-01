import requests
import os

ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")  # set this in your env

def abuseipdb_score(ip):
    """
    Returns AbuseIPDB confidence score (0-100) for a given IP.
    Returns None if IP not found or API fails.
    """
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90  # optional: look at last 90 days
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()["data"]
            return data.get("abuseConfidenceScore", 0)  # 0–100
        else:
            print(f"❌ AbuseIPDB API error for {ip}: {resp.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception calling AbuseIPDB for {ip}: {e}")
        return None
