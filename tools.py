import os
import yfinance as yf
import requests
from dotenv import load_dotenv

load_dotenv()

def get_market_data(ticker: str):
    """Obtiene precio actual y volatilidad (ATR) del Micro Futuro."""
    try:
        # Descargamos datos con progress=False para que no ensucie la terminal
        df = yf.download(ticker, period="5d", interval="15m", progress=False)
        if df.empty: return "No data"
        
        # Calculamos el ATR
        high_low = df['High'] - df['Low']
        atr_series = high_low.rolling(14).mean()
        
        # .iloc[-1:].values[0] es la forma más segura de extraer el escalar puro
        return {
            "price": round(float(df['Close'].iloc[-1:].values[0]), 2),
            "atr": round(float(atr_series.iloc[-1:].values[0]), 2),
            "high_5d": round(float(df['High'].max()), 2),
            "low_5d": round(float(df['Low'].min()), 2)
        }
    except Exception as e:
        return f"Error en Market Data: {e}"

def get_news_sentiment(asset_name: str):
    """Busca noticias financieras para el sentimiento."""
    api_key = os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q={asset_name}+trading+finance&sortBy=publishedAt&apiKey={api_key}"
    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])[:5]
        return "\n".join([f"- {a['title']}" for a in articles])
    except:
        return "No se pudieron obtener noticias."

def get_macro_volatility():
    """Obtiene DXY y VIX sin generar avisos de Pandas."""
    tickers = {"DXY": "DX-Y.NYB", "VIX": "^VIX"}
    data = {}
    
    for name, ticker in tickers.items():
        try:
            df = yf.download(ticker, period="2d", interval="1h", progress=False)
            if not df.empty:
                # Extraemos los valores como escalares puros usando .values[0]
                current_val = float(df['Close'].iloc[-1:].values[0])
                prev_val = float(df['Close'].iloc[0:1].values[0])
                
                change = ((current_val - prev_val) / prev_val) * 100
                
                data[name] = {
                    "price": round(current_val, 2), 
                    "change_pct": round(float(change), 2)
                }
            else:
                data[name] = {"price": 0.0, "change_pct": 0.0}
        except:
            data[name] = {"price": 0.0, "change_pct": 0.0}
            
    return data