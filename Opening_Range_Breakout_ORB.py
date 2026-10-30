## Enter immediately after Telegram alert.
##Run every 15 minutes: from 09:31 AM
import yfinance as yf
import pandas as pd
import requests

# =====================================
# TELEGRAM CONFIG
# =====================================
BOT_TOKEN = "9294156141:AAE7KKd1oCKtEryJbFuXTsz848hxiTAMcrc"
CHAT_ID = "663250113"

TRADER_NAME = "Venkatesh_sende"
# =====================================
# NIFTY 50 STOCKS
# =====================================
stocks = [
    "ADANIENT.NS",
    "ADANIPORTS.NS",
    "APOLLOHOSP.NS",
    "ASIANPAINT.NS",
    "AXISBANK.NS",
    "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS",
    "BAJAJFINSV.NS",
    "BEL.NS",
    "BHARTIARTL.NS",
    "BPCL.NS",
    "BRITANNIA.NS",
    "CIPLA.NS",
    "COALINDIA.NS",
    "DRREDDY.NS",
    "EICHERMOT.NS",
    "ETERNAL.NS",
    "GRASIM.NS",
    "HCLTECH.NS",
    "HDFCBANK.NS",
    "HDFCLIFE.NS",
    "HEROMOTOCO.NS",
    "HINDALCO.NS",
    "HINDUNILVR.NS",
    "ICICIBANK.NS",
    "INDUSINDBK.NS",
    "INFY.NS",
    "ITC.NS",
    "JIOFIN.NS",
    "JSWSTEEL.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "M&M.NS",
    "MARUTI.NS",
    "NESTLEIND.NS",
    "NTPC.NS",
    "ONGC.NS",
    "POWERGRID.NS",
    "RELIANCE.NS",
    "SBILIFE.NS",
    "SBIN.NS",
    "SHRIRAMFIN.NS",
    "SUNPHARMA.NS",
    "TATASTEEL.NS",
    "TCS.NS",
    "TECHM.NS",
    "TRENT.NS",
    "ULTRACEMCO.NS",
    "WIPRO.NS"
]


# =====================================
# VWAP FUNCTION
# =====================================
def calculate_vwap(df):
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    return (tp * df["Volume"]).cumsum() / df["Volume"].cumsum()


# =====================================
# TELEGRAM FUNCTION
# =====================================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        print("Telegram Response:", response.text)
    except Exception as e:
        print("Telegram Error:", e)


# =====================================
# STOCK SCANNER
# =====================================
for stock in stocks:

    try:

        df = yf.download(
            stock,
            interval="15m",
            period="5d",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df["VWAP"] = calculate_vwap(df)

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        signal = "NO TRADE"

        # BUY SIGNAL
        if (
            latest["Close"] > previous["High"]
            and latest["Close"] > latest["VWAP"]
            and latest["Volume"] > previous["Volume"]
        ):

            signal = "BUY"

            msg = f"""
🟢 BUY SIGNAL

Trader: {TRADER_NAME}

Stock: {stock}

Price: {latest['Close']:.2f}
VWAP : {latest['VWAP']:.2f}

Prev High: {previous['High']:.2f}
Volume   : {int(latest['Volume'])}
"""

            send_telegram(msg)

        # SELL SIGNAL
        elif (
            latest["Close"] < previous["Low"]
            and latest["Close"] < latest["VWAP"]
            and latest["Volume"] > previous["Volume"]
        ):

            signal = "SELL"

            msg = f"""
🔴 SELL SIGNAL

Trader: {TRADER_NAME}

Stock: {stock}

Price: {latest['Close']:.2f}
VWAP : {latest['VWAP']:.2f}

Prev Low: {previous['Low']:.2f}
Volume  : {int(latest['Volume'])}
"""

            send_telegram(msg)

        print(
            f"{stock:15} "
            f"Price={latest['Close']:.2f} "
            f"VWAP={latest['VWAP']:.2f} "
            f"Signal={signal}"
        )

    except Exception as e:
        print(f"{stock} -> {e}")
