import os
import yfinance as yf
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def clean_value(value):
    """
    Fuerza a los datos de yfinance a ser un float simple.
    Evita el error 'only 0-dimensional arrays can be converted to Python scalars'.
    """
    try:
        # Si el valor tiene el atributo iloc, es una Serie de Pandas (lo más común en yfinance)
        if hasattr(value, 'iloc'):
            if value.empty:
                return 0.0
            return float(value.iloc[-1])
        # Si es un valor escalar o un array de un elemento
        return float(value)
    except Exception:
        return 0.0

def get_market_data(ticker: str):
    """Obtiene precio actual, ATR y extremos de los últimos 5 días."""
    try:
        # Descargamos datos (progress=False para evitar ruido en logs)
        df = yf.download(ticker, period="5d", interval="15m", progress=False)
        if df.empty: 
            return "No data"
        
        # Cálculo de volatilidad ATR (14 periodos)
        high_low = df['High'] - df['Low']
        atr_series = high_low.rolling(14).mean()
        
        # Extraemos y limpiamos cada valor individualmente
        actual_price = clean_value(df['Close'])
        actual_atr = clean_value(atr_series)
        high_5d = clean_value(df['High'].max())
        low_5d = clean_value(df['Low'].min())
        
        return {
            "price": round(actual_price, 2),
            "atr": round(actual_atr, 2),
            "high_5d": round(high_5d, 2),
            "low_5d": round(low_5d, 2)
        }
    except Exception as e:
        return f"Error en Market Data: {e}"

def get_news_sentiment(asset_name: str):
    """Obtiene noticias financieras recientes mediante NewsAPI."""
    # Prioriza la clave de Streamlit Secrets sobre el .env local
    api_key = st.secrets["NEWS_API_KEY"] if "NEWS_API_KEY" in st.secrets else os.getenv("NEWS_API_KEY")
    
    url = f"https://newsapi.org/v2/everything?q={asset_name}+trading+finance&sortBy=publishedAt&apiKey={api_key}"
    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])[:5]
        if not articles: 
            return "No se encontraron noticias recientes relevantes."
        
        resumen = "\n".join([f"- {a['title']}" for a in articles])
        return resumen
    except Exception:
        return "Error al conectar con el servicio de noticias."

def get_macro_volatility():
    """Obtiene el valor actual del VIX y el DXY."""
    tickers = {"DXY": "DX-Y.NYB", "VIX": "^VIX"}
    data = {}
    
    for name, ticker in tickers.items():
        try:
            # Pedimos 2 días para tener margen de datos
            df = yf.download(ticker, period="2d", interval="1h", progress=False)
            if not df.empty:
                # Limpiamos el valor para asegurar que sea un número escalar
                current_val = clean_value(df['Close'])
                data[name] = {"price": round(current_val, 2)}
            else:
                data[name] = {"price": 0.0}
        except Exception:
            data[name] = {"price": 0.0}
            
    return data