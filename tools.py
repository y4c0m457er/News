import os
import yfinance as yf
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def clean_value(value):
    """Extrae el valor numérico de forma segura."""
    try:
        if hasattr(value, 'iloc'):
            return float(value.iloc[-1]) if not value.empty else 0.0
        return float(value)
    except:
        return 0.0

def get_market_data(ticker: str):
    """Obtiene datos de mercado con cabeceras de seguridad."""
    try:
        # Creamos una sesión para evitar bloqueos del servidor
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        
        # Descarga de datos usando la sesión
        dat = yf.Ticker(ticker, session=session)
        df = dat.history(period="5d", interval="15m")
        
        if df.empty: return "No data"
        
        high_low = df['High'] - df['Low']
        atr_series = high_low.rolling(14).mean()
        
        return {
            "price": round(clean_value(df['Close']), 2),
            "atr": round(clean_value(atr_series), 2),
            "high_5d": round(clean_value(df['High'].max()), 2),
            "low_5d": round(clean_value(df['Low'].min()), 2)
        }
    except Exception as e:
        return f"Error: {e}"

def get_news_sentiment(asset_name: str):
    """Busca noticias usando la clave de Secrets."""
    api_key = st.secrets["NEWS_API_KEY"] if "NEWS_API_KEY" in st.secrets else os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q={asset_name}+trading+finance&sortBy=publishedAt&apiKey={api_key}"
    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])[:5]
        return "\n".join([f"- {a['title']}" for a in articles]) if articles else "Sin noticias."
    except:
        return "Error de conexión a noticias."

def get_macro_volatility():
    """Obtiene VIX y DXY con sesión segura."""
    tickers = {"DXY": "DX-Y.NYB", "VIX": "^VIX"}
    data = {}
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker, session=session)
            df = t.history(period="2d", interval="1h")
            val = clean_value(df['Close']) if not df.empty else 0.0
            data[name] = {"price": round(val, 2)}
        except:
            data[name] = {"price": 0.0}
    return data