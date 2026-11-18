import yfinance as yf
import pandas as pd
import numpy as np
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS",
    "BAJFINANCE.NS", "MARUTI.NS", "SUNPHARMA.NS", "M&M.NS", "TITAN.NS",
    "TATAMOTORS.NS", "AXISBANK.NS", "ULTRACEMCO.NS", "NTPC.NS", "ADANIENT.NS",
    "ADANIPORTS.NS", "ASIANPAINT.NS", "COALINDIA.NS", "WIPRO.NS", "ONGC.NS",
    "BAJAJFINSV.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "POWERGRID.NS", "HEROMOTOCO.NS"
]

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = -delta.clip(upper=0).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=period).mean().fillna(high_low)

def get_strike_price(price, signal):
    if price < 500:
        step = 5
    elif price < 1000:
        step = 10
    elif price < 2500:
        step = 20
    elif price < 5000:
        step = 50
    else:
        step = 100
    atm_strike = round(price / step) * step
    opt_type = "PE" if signal == "SELL" else "CE"
    return f"{int(atm_strike)} {opt_type}"

def get_market_news():
    feeds = [
        ("GLOBAL NEWS", "https://google.com"),
        ("NATIONAL NEWS", "https://google.com"),
        ("INTERNATIONAL NEWS", "https://google.com"),
        ("IMPORTANT NEWS", "https://google.com")
    ]
    news_list = []
    for category, url in feeds:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            xml_data = urllib.request.urlopen(req, timeout=5).read()
            root = ET.fromstring(xml_data)
            for item in root.findall('./channel/item')[:2]:
                title_el = item.find('title')
                if title_el is not None and title_el.text:
                    clean_title = title_el.text.split(' - ')[0]
                    news_list.append({"category": category, "headline": clean_title})
        except Exception:
            continue
    if not news_list:
        news_list = [
            {"category": "NATIONAL NEWS", "headline": "Nifty 50 and Sensex live algorithmic market scan active."},
            {"category": "GLOBAL NEWS", "headline": "Global indices tracking US Treasury yields and crude oil prices."}
        ]
    return news_list

def fetch_index_data(symbol, fallback_price):
    try:
        df = yf.Ticker(symbol).history(period="5d")
        if len(df) >= 2:
            curr = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            chg = ((curr - prev) / prev) * 100
            return round(curr, 0), round(chg, 2)
    except Exception:
        pass
    return fallback_price, 0.0

def analyze_stocks():
    results = []
    advancers = 0

    for ticker in STOCKS:
        try:
            df = yf.Ticker(ticker).history(period="1y")
            if df is None or len(df) < 200:
                continue

            close = df['Close']
            volume = df['Volume']

            curr_price = float(close.iloc[-1])
            prev_price = float(close.iloc[-2])
            day_change_pct = ((curr_price - prev_price) / prev_price) * 100
            if day_change_pct > 0:
                advancers += 1

            dma_50 = float(close.rolling(50).mean().iloc[-1])
            dma_200 = float(close.rolling(200).mean().iloc[-1])
            rsi = float(calculate_rsi(close, 14).iloc[-1])
            atr = float(calculate_atr(df, 14).iloc[-1])

            vol_avg_20 = float(volume.rolling(20).mean().iloc[-1])
            curr_vol = float(volume.iloc[-1])
            vol_ratio = curr_vol / vol_avg_20 if vol_avg_20 > 0 else 1.0

            score = 0
            score += 1 if curr_price > dma_50 else -1
            score += 1 if dma_50 > dma_200 else -1
            if 45 <= rsi <= 68:
                score += 1
            elif rsi > 75:
                score -= 1
            if vol_ratio >= 1.5:
                score += 1 if day_change_pct >= 0 else -1

            signal = "BUY" if score >= 3 else ("SELL" if score <= -2 else "HOLD")

            entry = round(curr_price, 2)
            raw_sl = entry - (1.5 * atr)
            min_sl = 0.97 * dma_50
            max_sl = entry - (0.75 * atr)
            stoploss = round(min(max(raw_sl, min_sl), max_sl), 2)
            if stoploss >= entry:
                stoploss = round(entry * 0.97, 2)

            risk = max(entry - stoploss, 0.5)
            target_1 = round(entry + (2 * risk), 2)
            target_2 = round(entry + (3 * risk), 2)
            risk_pct = round((risk / entry) * 100, 2)

            ret_5d = ((curr_price - float(close.iloc[-6])) / float(close.iloc[-6])) * 100
            ret_1m = ((curr_price - float(close.iloc[-22])) / float(close.iloc[-22])) * 100
            high_20d = float(df['High'].rolling(20).max().iloc[-1])
            high_52w = float(df['High'].max())
            low_52w = float(df['Low'].min())

            early_points = 0
            if ret_5d < 5 and ret_1m < 10 and day_change_pct < 4:
                if curr_price > dma_200 and curr_price >= (0.97 * dma_50) and (38 <= rsi <= 65):
                    bb_width = (4 * close.rolling(20).std()) / close.rolling(20).mean()
                    curr_bb = float(bb_width.iloc[-1])
                    bb_pct = (bb_width.tail(126) < curr_bb).mean() * 100
                    if bb_pct <= 20:
                        early_points += 2
                    elif bb_pct <= 35:
                        early_points += 1
                    if curr_price >= 0.97 * high_20d:
                        early_points += 1
                    if curr_price >= 0.95 * high_52w:
                        early_points += 1
                    if vol_ratio >= 1.2 and day_change_pct >= 0:
                        early_points += 1

            is_early = early_points >= 3
            buy_now_pts = score + early_points
            if signal == "BUY" and is_early:
                buy_now_pts += 2
            if rsi > 68:
                buy_now_pts -= 1
            if ret_5d >= 8:
                buy_now_pts -= 1
            if risk_pct > 6:
                buy_now_pts -= 1

            results.append({
                "symbol": ticker.replace(".NS", ""),
                "price": entry,
                "change_pct": round(day_change_pct, 2),
                "rsi": round(rsi, 1),
                "vol_ratio": round(vol_ratio, 2),
                "score": score,
                "signal": signal,
                "strike": get_strike_price(entry, signal),
                "stoploss": stoploss,
                "risk_pct": risk_pct,
                "target_1": target_1,
                "target_2": target_2,
                "is_early_setup": is_early,
                "buy_now_points": buy_now_pts,
                "near_52w_low": curr_price <= (low_52w * 1.10)
            })
        except Exception as e:
            print(f"Skipping {ticker}: {e}")

    nifty_price, nifty_chg = fetch_index_data("^NSEI", 24000)
    sensex_price, sensex_chg = fetch_index_data("^BSESN", 79000)

    adv_ratio = (advancers / len(results)) * 100 if results else 50
    sentiment = "BULLISH" if adv_ratio >= 58 else ("BEARISH" if adv_ratio <= 42 else "NEUTRAL")

    sorted_picks = sorted(results, key=lambda x: (x['buy_now_points'], -x['risk_pct']), reverse=True)
    buy_now_pick = sorted_picks[0] if sorted_picks else None

    output = {
        "last_updated": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "nifty": {"price": nifty_price, "change_pct": nifty_chg},
        "sensex": {"price": sensex_price, "change_pct": sensex_chg},
        "sentiment": sentiment,
        "stats": {
            "total_stocks": len(results),
            "advancers": advancers,
            "buy_count": sum(1 for x in results if x['signal'] == 'BUY'),
            "sell_count": sum(1 for x in results if x['signal'] == 'SELL')
        },
        "buy_now": buy_now_pick,
        "news": get_market_news(),
        "stocks": results
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Successfully generated data.json")

if __name__ == "__main__":
    analyze_stocks()
