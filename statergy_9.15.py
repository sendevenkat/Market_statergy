## we should trigger this 9.30am

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# ==========================================
# TELEGRAM CONFIG
# ==========================================
BOT_TOKEN = "9294156141:AAE7KKd1oCKtEryJbFuXTsz848hxiTAMcrc"
CHAT_ID = "663250113"
TRADER_NAME = "Venkatesh_sende"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=10
        )

        print("Telegram:", response.text)

    except Exception as e:
        print("Telegram Error:", e)


# ==========================================
# STOCK LIST
# ==========================================
stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS"
]


# ==========================================
# VWAP
# ==========================================
def calculate_vwap(df):
    typical_price = (
        df["High"] +
        df["Low"] +
        df["Close"]
    ) / 3

    return (
        (typical_price * df["Volume"]).cumsum()
        /
        df["Volume"].cumsum()
    )


# ==========================================
# MAIN LOOP
# ==========================================
for stock in stocks:

    try:

        df = yf.download(
            stock,
            interval="5m",
            period="1d",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.index = df.index.tz_convert("Asia/Kolkata")

        df["VWAP"] = calculate_vwap(df)

        opening_range = df.between_time(
            "09:15",
            "09:30"
        )

        if opening_range.empty:
            continue

        or_high = opening_range["High"].max()
        or_low = opening_range["Low"].min()

        latest = df.iloc[-1]

        avg_volume = (
            df["Volume"]
            .tail(5)
            .mean()
        )

        signal = "NO TRADE"

        # ==========================
        # BUY SIGNAL
        # ==========================
        if (
            latest["Close"] > or_high
            and latest["Close"] > latest["VWAP"]
            and latest["Volume"] > avg_volume
        ):

            signal = "BUY"

        # ==========================
        # SELL SIGNAL
        # ==========================
        elif (
            latest["Close"] < or_low
            and latest["Close"] < latest["VWAP"]
            and latest["Volume"] > avg_volume
        ):

            signal = "SELL"

        print("\n" + "=" * 60)

        print(
            f"{stock:<15} | "
            f"Price={latest['Close']:.2f} | "
            f"VWAP={latest['VWAP']:.2f} | "
            f"Signal={signal}"
        )

        print("=" * 60)

        print(f"OR High     : {or_high:.2f}")
        print(f"OR Low      : {or_low:.2f}")
        print(f"Price       : {latest['Close']:.2f}")
        print(f"VWAP        : {latest['VWAP']:.2f}")
        print(f"Volume      : {int(latest['Volume'])}")
        print(f"Avg Volume  : {int(avg_volume)}")

        # =====================================
        # OLLAMA ANALYSIS
        # =====================================

        prompt = f"""
Stock: {stock}

Current Price: {latest['Close']:.2f}
VWAP: {latest['VWAP']:.2f}
Opening Range High: {or_high:.2f}
Opening Range Low: {or_low:.2f}
Volume: {int(latest['Volume'])}
Average Volume: {int(avg_volume)}

Signal: {signal}

Explain this signal in one short paragraph.
"""

        try:

            ollama_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:1.5b",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )

            analysis = ollama_response.json()["response"]

        except Exception as e:

            analysis = f"Ollama analysis failed: {e}"

        print("\nAI Analysis:")
        print(analysis)

        # =====================================
        # TELEGRAM ALERT
        # =====================================

        if signal in ["BUY", "SELL"]:

            emoji = "🟢" if signal == "BUY" else "🔴"

            telegram_message = f"""
{emoji} {signal} SIGNAL

Trader: {TRADER_NAME}
Stock: {stock}

Price: {latest['Close']:.2f}
VWAP: {latest['VWAP']:.2f}

OR High: {or_high:.2f}
OR Low: {or_low:.2f}

Volume: {int(latest['Volume'])}
Avg Volume: {int(avg_volume)}

AI Analysis:
{analysis[:500]}
"""

            send_telegram(telegram_message)

    except Exception as e:
        print(f"{stock} -> {e}")

print("\nScan completed:", datetime.now())