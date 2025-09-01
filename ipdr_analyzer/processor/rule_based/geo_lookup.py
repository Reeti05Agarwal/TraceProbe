import requests

def get_geo(ip):
    try:
        url = f"http://api.hostip.info/get_json.php?ip={ip}&position=true"
        res = requests.get(url).json()
        return res.get("country_name"), res.get("lat"), res.get("lng")
    except:
        return None, None, None
