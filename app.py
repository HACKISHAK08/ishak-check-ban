from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

VALID_API_KEYS = {
    "YOUR-API-KEY": "active"
}

def validate_api_key(api_key):
    if not api_key:
        return {"error": "API key is missing", "status_code": 401}
    if api_key not in VALID_API_KEYS:
        return {"error": "Invalid API key", "status_code": 401}
    
    status = VALID_API_KEYS[api_key]
    if status == "inactive":
        return {"error": "API key is changed", "status_code": 403}
    if status == "banned":
        return {"error": "API key is banned", "status_code": 403}
    
    return {"valid": True}

def get_player_info(uid):
    try:
        headers = {
            "Host": "shop2game.com",
            "Connection": "keep-alive",
            "Content-Length": "58",
            "accept": "application/json",
            "x-datadome-clientid": "GvEFJuBKzy0EHFZKO2XE67DE09lMAaipIuIwicrcRoEn4nBgZe-p6Ki3ifFTbozSNqu-Q4hUhY3AJbnBHOB8HS052OPgZcB1FJ431NuEO7ls1lam84GqpEYS_jUbqht",
            "content-type": "application/json",
            "sec-ch-ua-mobile": "?1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; Plume L2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
            "sec-ch-ua-platform": "\"Android\"",
            "Origin": "https://shop2game.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://shop2game.com/app/100067/idlogin",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,ar-DZ;q=0.8,ar;q=0.7"
        }
        data = {"app_id": 100067, "login_id": uid, "app_server_id": 0}
        res = requests.post('https://shop2game.com/api/auth/player_id_login', json=data, headers=headers, timeout=10)
        if res.status_code == 200:
            j = res.json()
            return {
                "player_name": j.get("nickname", "Unknown"),
                "region": j.get("region", "Unknown"),
                "openid": j.get("open_id", "")
            }
    except Exception:
        pass
    return {"player_name": "Unknown", "region": "Unknown", "openid": ""}

def check_banned(player_id):
    url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "referer": "https://ff.garena.com/en/support/",
        "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json().get("data", {})
            is_banned = data.get("is_banned", 0)
            period = data.get("period", 0)

            player_info = get_player_info(player_id)

            result = {
                "credits": "@ishakspeed",
                "channel": "https://t.me/ishakspeed",
                "player_name": player_info["player_name"] 
                "status": "BANNED" if is_banned else "NOT BANNED",
                "ban_period": period if is_banned else 0,
                "uid": player_id,
                "region": player_info["region"],
                "openid": player_info["openid"],
                "is_banned": bool(is_banned)
            }

            return Response(json.dumps(result, ensure_ascii=False), mimetype="application/json")
        else:
            return Response(json.dumps({"error": "Failed to fetch data from Garena", "status_code": 500}), mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e), "status_code": 500}), mimetype="application/json")

@app.route("/bancheck", methods=["GET"])
def bancheck():
    api_key = request.args.get("key", "")
    player_id = request.args.get("uid", "")

    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")

    if not player_id:
        return Response(json.dumps({"error": "Player ID is required", "status_code": 400}), mimetype="application/json")

    return check_banned(player_id)

@app.route("/check_key", methods=["GET"])
def check_key():
    api_key = request.args.get("key", "")

    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")

    return Response(json.dumps({"status": "valid", "key_status": VALID_API_KEYS.get(api_key, "unknown")}), mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)