import requests

API_BASE_URL = "http://127.0.0.1:8001"

def api_get(endpoint: str, params: dict = None):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        resp = requests.get(url, params=params, timeout=5)
        return resp.json(), resp.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def api_post(endpoint: str, data: dict):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        resp = requests.post(url, json=data, timeout=5)
        return resp.json(), resp.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def api_put(endpoint: str, data: dict):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        resp = requests.put(url, json=data, timeout=5)
        return resp.json(), resp.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def api_delete(endpoint: str):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        resp = requests.delete(url, timeout=5)
        return resp.json(), resp.status_code
    except Exception as e:
        return {"error": str(e)}, 500
