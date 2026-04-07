import streamlit as st
from tools import get_market_data, get_news_sentiment, get_macro_volatility
from agents import call_analyst, call_manager

# Configuración de la página
st.set_page_config(page_title="IA Trading Terminal", layout="wide")

st.title("🚀 IA Micro Futuros Dashboard")
st.markdown("---")

# --- BARRA LATERAL (Configuración) ---
with st.sidebar:
    st.header("Configuración")
    # El usuario puede elegir el activo
    activos = {
        "Micro Crude Oil": "MCL=F",
        "Micro Gold": "MGC=F",
        "Micro Nasdaq 100": "MNQ=F",
        "Micro Dow Jones": "MYM=F"
    }
    asset_name = st.selectbox("Selecciona Activo", list(activos.keys()))
    asset_ticker = activos[asset_name]
    
    event_name = st.text_input("Evento Económico (ej: CPI, ISM)", "Inventarios")
    
    btn_analizar = st.button("Lanzar Análisis", type="primary")

# --- CUERPO PRINCIPAL ---
if btn_analizar:
    with st.spinner("Extrayendo datos y consultando analistas..."):
        # 1. Obtener Datos
        market = get_market_data(asset_ticker)
        news = get_news_sentiment(asset_name)
        macro = get_macro_volatility()
        
        vix = macro.get('VIX', {}).get('price', 0)
        dxy = macro.get('DXY', {}).get('price', 0)

        # --- FILA 1: Indicadores Macro ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("VIX (Miedo)", f"{vix}", delta="ALTO" if vix > 22 else "Normal", delta_color="inverse")
        with col2:
            st.metric("DXY (Dólar)", f"{dxy}")
        with col3:
            st.metric(f"Precio {asset_name}", f"${market['price']}")

        # --- FILA 2: Análisis de Agentes ---
        st.subheader("🧠 Debate de la Mesa de Trading")
        c1, c2 = st.columns(2)
        
        with c1:
            with st.expander("Analista Técnico", expanded=True):
                tech_report = call_analyst("Analista Técnico de Futuros.", str(market))
                st.write(tech_report)
        
        with c2:
            with st.expander("Analista de Sentimiento", expanded=True):
                news_report = call_analyst("Analista de Noticias y Sentimiento.", news)
                st.write(news_report)

        # --- FILA 3: Veredicto Final ---
        st.markdown("---")
        st.subheader("⚖️ Decisión del Juez")
        debate = f"TECH: {tech_report}\nSENT: {news_report}"
        ticket = call_manager(debate, asset_name, event_name, macro)
        
        # Estilo para el ticket final
        st.info(ticket)

else:
    st.info("👈 Selecciona un activo y haz clic en 'Lanzar Análisis' para empezar.")