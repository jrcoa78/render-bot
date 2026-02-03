import requests
import time
import os
from datetime import datetime

# ───────── CONFIGURACIÓN GENERAL ─────────
P2P_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
SPOT_URL = "https://api.binance.com/api/v3/ticker/bookTicker"
HEADERS = {"Content-Type": "application/json"}

MXN_INICIAL = 10_000
EXCLUDED_PAYMENTS = ["cashapp"]

# ───────── TELEGRAM ─────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8492035261:AAFXoAgOQIqZKY8tHLz1mb1tTkMWD56isKc")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8383860413")
ALERT_SPREAD = float(os.getenv("ALERT_SPREAD", 0.5))

# ───────── SESSION (RENDER) ─────────
session = requests.Session()
session.headers.update(HEADERS)

# ───────── RUTAS P2P DIRECTAS ─────────
P2P_DIRECT = [
    "USDT","USDC","FDUSD","BTC","BNB","ETH","DOGE","WLD",
    "ADA","XRP","TRUMP","1000CHEEMS","TST","SOL"
]

# ───────── RUTAS MXN > A > B > MXN ─────────
ROUTES = [  


]

# ───────── FUNCIONES ─────────
def send_telegram(msg):
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
            print("\n" + "═"*170)
            print("RUTAS MXN → MXN | SPREAD > 0%")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            assets = set(P2P_DIRECT + list(sum(ROUTES, ())))
            p2p_buy = {a: p2p_price(a,"BUY") for a in assets}
            p2p_sell = {a: p2p_price(a,"SELL") for a in assets}

            for a in P2P_DIRECT:
                if not p2p_buy[a] or not p2p_sell[a]:
                    continue
                final = (MXN_INICIAL / p2p_buy[a]) * p2p_sell[a]
                s = calc_spread(final)

                if s > 0:
                    print(f"MXN > {a} > MXN | Spread: {s:.2f}%")
                if s >= ALERT_SPREAD:
                    send_telegram(f"🚨 ARBITRAJE P2P\nMXN > {a} > MXN\nSpread: {s:.2f}%")

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

                if s > 0:
                    print(f"MXN > {a} > {b} > MXN | Spread: {s:.2f}%")
                if s >= ALERT_SPREAD:
                    send_telegram(f"🚨 ARBITRAJE P2P-SPOT\nMXN > {a} > {b} > MXN\nSpread: {s:.2f}%")

            print(" FIN CICLO ")
            time.sleep(60)

        except Exception as e:
            print("ERROR:", e)
            #send_telegram(f"⚠️ ERROR BOT: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
