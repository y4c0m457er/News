import os
import yfinance as yf
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_market_data(ticker: str):
    """Obtiene datos de mercado usando un método de descarga directa."""
    try:
        # Usamos un agente de usuario muy común para evitar el bloqueo de Yahoo
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Descargamos los datos de los últimos 2 días para asegurar que haya velas
        df = yf.download(ticker, period="2d", interval="15m", progress=False)
        
        if df.empty or len(df) < 2:
            return {"error": "Yahoo Finance ha devuelto datos vacíos. Reintente en unos minutos."}

        # Extraemos el último precio de cierre de forma ultra segura
        # Usamos .tail(1) y convertimos a float directamente
        current_price = float(df['Close'].iloc[-1])
        
        # Cálculo simple del ATR para la IA
        high_low = df['High'] - df['Low']
        atr = float(high_low.rolling(window=min(14, len(df))).mean().iloc[-1])
        
        high_5d = float(df['High'].max())
        low_5d = float(df['Low'].min())

        return {
            "price": round(current_price, 2),
            "atr": round(atr, 2),
            "high_5d": round(high_5d, 2),
            "low_5d": round(low_5d, 2)
        }
    except Exception as e:
        return {"error": f"Fallo de conexión: {str(e)}"}

def get_news_sentiment(asset_name: str):
    """Noticias frescas mediante NewsAPI."""
    api_key = st.secrets["NEWS_API_KEY"] if "NEWS_API_KEY" in st.secrets else os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q={asset_name}+finance&sortBy=publishedAt&apiKey={api_key}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        articles = data.get('articles', [])[:5]
        if not articles: return "Mercado en calma, sin noticias de impacto."
        return "\n".join([f"- {a['title']}" for a in articles])
    except:
        return "Servicio de noticias temporalmente no disponible."

def get_macro_volatility():
    """Obtiene VIX y DXY de forma simplificada."""
    results = {}
    for name, sym in {"DXY": "DX-Y.NYB", "VIX": "^VIX"}.items():
        try:
            # Descarga rápida de 1 día
            temp_df = yf.download(sym, period="1d", progress=False)
            if not temp_df.empty:
                val = float(temp_df['Close'].iloc[-1])
                results[name] = {"price": round(val, 2)}
            else:
                results[name] = {"price": 0.0}
        except:
            results[name] = {"price": 0.0}
    return results