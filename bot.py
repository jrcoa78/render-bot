import requests
import time
import os
from datetime import datetime

# ───────── CONFIGURACIÓN GENERAL ─────────
P2P_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
HEADERS = {"Content-Type": "application/json"}

MXN_INICIAL = 10_000
EXCLUDED_PAYMENTS = ["cashapp"]

# ───────── TELEGRAM ─────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8492035261:AAFXoAgOQIqZKY8tHLz1mb1tTkMWD56isKc")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8383860413")
ALERT_SPREAD = float(os.getenv("ALERT_SPREAD", 0.5))

# ───────── SESSION ─────────
session = requests.Session()
session.headers.update(HEADERS)

# ───────── ACTIVOS P2P DIRECTOS ─────────
P2P_DIRECT = [
    "USDT","USDC","FDUSD","BTC","BNB","ETH","DOGE","WLD",
    "ADA","XRP","TRUMP","1000CHEEMS","TST","SOL"
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

def calc_spread(final):
    return ((final - MXN_INICIAL) / MXN_INICIAL) * 100

# ───────── MAIN ─────────
def main():
    send_telegram("🤖 Bot P2P MXN > ACTIVO > MXN iniciado en Render")

    while True:
        try:
            print("\n" + "═"*120)
            print("ARBITRAJE P2P MXN → ACTIVO → MXN")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            p2p_buy = {a: p2p_price(a,"BUY") for a in P2P_DIRECT}
            p2p_sell = {a: p2p_price(a,"SELL") for a in P2P_DIRECT}

            for a in P2P_DIRECT:
                if not p2p_buy[a] or not p2p_sell[a]:
                    continue

                final = (MXN_INICIAL / p2p_buy[a]) * p2p_sell[a]
                spread = calc_spread(final)

                if spread > 0:
                    print(f"MXN > {a} > MXN | Spread: {spread:.2f}%")

                if spread >= ALERT_SPREAD:
                    send_telegram(
                        f"🚨 ARBITRAJE P2P\n"
                        f"MXN > {a} > MXN\n"
                        f"Spread: {spread:.2f}%"
                    )

            print(" FIN CICLO ")
            time.sleep(60)

        except Exception as e:
            print("ERROR:", e)
            send_telegram(f"⚠️ ERROR BOT: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
