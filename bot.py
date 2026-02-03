import requests
import time
import os
from datetime import datetime

# ───────── CONFIGURACIÓN ─────────
P2P_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
SPOT_URL = "https://api.binance.com/api/v3/ticker/bookTicker"
HEADERS = {"Content-Type": "application/json"}

MXN_INICIAL = 10_000
EXCLUDED_PAYMENTS = ["cashapp"]

# ───────── TELEGRAM DESDE ENV ─────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ALERT_SPREAD = float(os.getenv("ALERT_SPREAD", 0.5))

# ───────── SESIÓN ─────────
session = requests.Session()
session.headers.update(HEADERS)

# ───────── ACTIVOS ─────────
P2P_DIRECT = [
    "USDT","USDC","FDUSD","BTC","BNB","ETH","DOGE","WLD",
    "ADA","XRP","TRUMP","1000CHEEMS","TST","SOL"
]

ROUTES = [
("USDT","USDC"),("USDT","FDUSD"),("USDT","BTC"),("USDT","BNB"),
("USDT","ETH"),("USDT","DOGE"),("USDT","WLD"),("USDT","ADA"),
("USDT","XRP"),("USDT","TRUMP"),("USDT","1000CHEEMS"),
("USDT","TST"),("USDT","SOL"),

("USDC","USDT"),("USDC","FDUSD"),("USDC","BTC"),("USDC","BNB"),
("USDC","ETH"),("USDC","DOGE"),("USDC","WLD"),("USDC","ADA"),
("USDC","XRP"),("USDC","TRUMP"),("USDC","1000CHEEMS"),
("USDC","TST"),("USDC","SOL"),

("FDUSD","USDT"),("FDUSD","USDC"),("FDUSD","BTC"),("FDUSD","BNB"),
("FDUSD","ETH"),("FDUSD","DOGE"),("FDUSD","WLD"),("FDUSD","ADA"),
("FDUSD","XRP"),("FDUSD","TRUMP"),("FDUSD","1000CHEEMS"),
("FDUSD","TST"),("FDUSD","SOL"),

("BTC","USDT"),("BTC","USDC"),("BTC","FDUSD"),("BTC","BNB"),
("BTC","ETH"),("BTC","DOGE"),("BTC","WLD"),("BTC","ADA"),
("BTC","XRP"),("BTC","TRUMP"),("BTC","1000CHEEMS"),
("BTC","TST"),("BTC","SOL"),

("BNB","USDT"),("BNB","USDC"),("BNB","FDUSD"),("BNB","BTC"),
("BNB","ETH"),("BNB","DOGE"),("BNB","WLD"),("BNB","ADA"),
("BNB","XRP"),("BNB","TRUMP"),("BNB","1000CHEEMS"),
("BNB","TST"),("BNB","SOL"),

("ETH","USDT"),("ETH","USDC"),("ETH","FDUSD"),("ETH","BTC"),
("ETH","BNB"),("ETH","DOGE"),("ETH","WLD"),("ETH","ADA"),
("ETH","XRP"),("ETH","TRUMP"),("ETH","1000CHEEMS"),
("ETH","TST"),("ETH","SOL"),

("DOGE","USDT"),("DOGE","USDC"),("DOGE","FDUSD"),("DOGE","BTC"),
("DOGE","BNB"),("DOGE","ETH"),("DOGE","WLD"),("DOGE","ADA"),
("DOGE","XRP"),("DOGE","TRUMP"),("DOGE","1000CHEEMS"),
("DOGE","TST"),("DOGE","SOL"),

("WLD","USDT"),("WLD","USDC"),("WLD","FDUSD"),("WLD","BTC"),
("WLD","BNB"),("WLD","ETH"),("WLD","DOGE"),("WLD","ADA"),
("WLD","XRP"),("WLD","TRUMP"),("WLD","1000CHEEMS"),
("WLD","TST"),("WLD","SOL"),

("ADA","USDT"),("ADA","USDC"),("ADA","FDUSD"),("ADA","BTC"),
("ADA","BNB"),("ADA","ETH"),("ADA","DOGE"),("ADA","WLD"),
("ADA","XRP"),("ADA","TRUMP"),("ADA","1000CHEEMS"),
("ADA","TST"),("ADA","SOL"),

("XRP","USDT"),("XRP","USDC"),("XRP","FDUSD"),("XRP","BTC"),
("XRP","BNB"),("XRP","ETH"),("XRP","DOGE"),("XRP","WLD"),
("XRP","ADA"),("XRP","TRUMP"),("XRP","1000CHEEMS"),
("XRP","TST"),("XRP","SOL"),

("TRUMP","USDT"),("TRUMP","USDC"),("TRUMP","FDUSD"),("TRUMP","BTC"),
("TRUMP","BNB"),("TRUMP","ETH"),("TRUMP","DOGE"),("TRUMP","WLD"),
("TRUMP","ADA"),("TRUMP","XRP"),("TRUMP","1000CHEEMS"),
("TRUMP","TST"),("TRUMP","SOL"),

("1000CHEEMS","USDT"),("1000CHEEMS","USDC"),("1000CHEEMS","FDUSD"),
("1000CHEEMS","BTC"),("1000CHEEMS","BNB"),("1000CHEEMS","ETH"),
("1000CHEEMS","DOGE"),("1000CHEEMS","WLD"),("1000CHEEMS","ADA"),
("1000CHEEMS","XRP"),("1000CHEEMS","TRUMP"),("1000CHEEMS","TST"),
("1000CHEEMS","SOL"),

("TST","USDT"),("TST","USDC"),("TST","FDUSD"),("TST","BTC"),
("TST","BNB"),("TST","ETH"),("TST","DOGE"),("TST","WLD"),
("TST","ADA"),("TST","XRP"),("TST","TRUMP"),
("TST","1000CHEEMS"),("TST","SOL"),

("SOL","USDT"),("SOL","USDC"),("SOL","FDUSD"),("SOL","BTC"),
("SOL","BNB"),("SOL","ETH"),("SOL","DOGE"),("SOL","WLD"),
("SOL","ADA"),("SOL","XRP"),("SOL","TRUMP"),
("SOL","1000CHEEMS"),("SOL","TST")
]

# ───────── FUNCIONES ─────────
def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        session.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
            timeout=10
        )
    except:
        pass

def valid_adv(adv):
    for m in adv.get("tradeMethods", []):
        if any(x in m.get("identifier","").lower() for x in EXCLUDED_PAYMENTS):
            return False
    return True

def p2p_price(asset, side):
    payload = {
        "asset": asset,
        "fiat": "MXN",
        "tradeType": side,
        "page": 1,
        "rows": 10
    }
    r = session.post(P2P_URL, json=payload, timeout=10).json()
    for d in r.get("data", []):
        if valid_adv(d["adv"]):
            return float(d["adv"]["price"])
    return None

def spot_price(a, b):
    for s in session.get(SPOT_URL, timeout=10).json():
        if s["symbol"] == a+b:
            return float(s["bidPrice"]), False
        if s["symbol"] == b+a:
            return float(s["askPrice"]), True
    return None, None

def calc_spread(final):
    return ((final - MXN_INICIAL) / MXN_INICIAL) * 100

# ───────── MAIN ─────────
def main():
    send_telegram("🤖 Bot de arbitraje iniciado en Render")

    while True:
        try:
            print("\n" + "═"*150)
            print("RUTAS MXN → MXN")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            assets = set(P2P_DIRECT + list(sum(ROUTES, ())))
            p2p_buy = {a: p2p_price(a,"BUY") for a in assets}
            p2p_sell = {a: p2p_price(a,"SELL") for a in assets}

            for a in P2P_DIRECT:
                if not p2p_buy[a] or not p2p_sell[a]:
                    continue
                final = (MXN_INICIAL / p2p_buy[a]) * p2p_sell[a]
                s = calc_spread(final)

                if s >= ALERT_SPREAD:
                    send_telegram(f"🚨 P2P\nMXN > {a} > MXN\nSpread: {s:.2f}%")

            for a, b in ROUTES:
                if not p2p_buy[a] or not p2p_sell[b]:
                    continue
                rate, invert = spot_price(a,b)
                if not rate:
                    continue

                qty_a = MXN_INICIAL / p2p_buy[a]
                qty_b = qty_a / rate if invert else qty_a * rate
                final = qty_b * p2p_sell[b]
                s = calc_spread(final)

                if s >= ALERT_SPREAD:
                    send_telegram(f"🚨 P2P-SPOT\nMXN > {a} > {b} > MXN\nSpread: {s:.2f}%")

            time.sleep(60)

        except Exception as e:
            print("ERROR:", e)
            send_telegram(f"⚠️ Error crítico: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
