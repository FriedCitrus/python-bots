from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

ZODIAC_SIGNS = {
    "aries": 1, "taurus": 2, "gemini": 3, "cancer": 4,
    "leo": 5, "virgo": 6, "libra": 7, "scorpio": 8,
    "sagittarius": 9, "capricorn": 10, "aquarius": 11, "pisces": 12
}

DAY_PATH = {
    "today": "horoscope-general-daily-today",
    "yesterday": "horoscope-general-daily-yesterday",
    "tomorrow": "horoscope-general-daily-tomorrow",
}

def build_url(sign: str, day: str) -> str:
    sign_id = ZODIAC_SIGNS.get(sign.lower())
    if sign_id is None:
        raise ValueError("Unknown sign")
    path = DAY_PATH.get(day.lower())
    if path is None:
        raise ValueError("Unknown day")
    return f"https://www.horoscope.com/us/horoscopes/general/{path}.aspx?sign={sign_id}"

def scrape_horoscope(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    # Основний текст зазвичай в цьому контейнері:
    block = soup.select_one(".main-horoscope > p")
    if not block:
        # запасний селектор
        block = soup.select_one(".horoscope-content > p")
    if not block:
        return ""
    return block.get_text(strip=True)

@app.route("/api/v1/horoscope", methods=["GET"])
def get_horoscope():
    sign = request.args.get("sign", "").lower().strip()
    day = request.args.get("day", "today").lower().strip()

    if sign not in ZODIAC_SIGNS:
        return jsonify({"ok": False, "error": "Invalid sign"}), 400
    if day not in DAY_PATH:
        return jsonify({"ok": False, "error": "Invalid day"}), 400

    try:
        url = build_url(sign, day)
        text = scrape_horoscope(url)
        if not text:
            return jsonify({"ok": False, "error": "Content not found"}), 502
        return jsonify({"ok": True, "sign": sign, "day": day, "horoscope": text})
    except requests.RequestException as e:
        return jsonify({"ok": False, "error": f"Network error: {e}"}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
