import streamlit as st
from tools import get_market_data, get_news_sentiment, get_macro_volatility
from agents import call_analyst, call_manager

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="IA Trading Terminal", layout="wide", page_icon="📈")

# 2. SISTEMA DE SEGURIDAD (PASSWORD)
def check_password():
    """Retorna True si el usuario introdujo la contraseña correcta."""
    def password_entered():
        if st.session_state["password"] == st.secrets["CLAVE_ACCESO"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso Restringido")
        st.text_input("Introduce la clave de acceso para operar:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 Acceso Restringido")
        st.text_input("Introduce la clave de acceso para operar:", type="password", on_change=password_entered, key="password")
        st.error("😕 Clave incorrecta. Contacta con el administrador.")
        return False
    else:
        return True

# 3. LÓGICA PRINCIPAL
if check_password():
    st.title("🚀 IA Micro Futuros Dashboard")
    st.markdown("---")

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.header("⚙️ Configuración")
        activos = {
            "Micro Nasdaq 100": "MNQ=F",
            "Micro Gold": "MGC=F",
            "Micro Crude Oil": "MCL=F",
            "Micro Dow Jones": "MYM=F"
        }
        asset_name = st.selectbox("Selecciona Activo", list(activos.keys()))
        asset_ticker = activos[asset_name]
        
        event_name = st.text_input("Evento Económico", "Análisis de Rutina")
        
        st.divider()
        st.warning("⚠️ Cada análisis consume créditos de API.")
        btn_analizar = st.button("🔥 Lanzar Análisis Profesional", type="primary")

    # --- EJECUCIÓN ---
    if btn_analizar:
        with st.spinner(f"Analizando {asset_name}..."):
            # A. Obtención de datos
            market = get_market_data(asset_ticker)
            news = get_news_sentiment(asset_name)
            macro = get_macro_volatility()
            
            vix = macro.get('VIX', {}).get('price', 0)
            dxy = macro.get('DXY', {}).get('price', 0)

            # B. Panel de Métricas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("VIX (Volatilidad)", f"{vix}", delta="RIESGO" if vix > 22 else "Estable", delta_color="inverse")
            with col2:
                st.metric("DXY (Índice Dólar)", f"{dxy}")
            with col3:
                # Verificación de seguridad para evitar fallos de renderizado
                if isinstance(market, dict) and 'price' in market:
                    st.metric(f"Precio {asset_name}", f"${market['price']}")
                else:
                    st.metric(f"Precio {asset_name}", "N/A")
                    st.error("Error al conectar con Yahoo Finance.")

            # C. Informes de Agentes
            st.subheader("🧠 Debate de Expertos")
            c1, c2 = st.columns(2)
            
            with c1:
                with st.expander("📊 Informe Técnico", expanded=True):
                    tech_report = call_analyst("Analista Técnico de Futuros.", str(market))
                    st.write(tech_report)
            
            with c2:
                with st.expander("🗞️ Informe Fundamental", expanded=True):
                    news_report = call_analyst("Analista de Noticias.", news)
                    st.write(news_report)

            # D. Veredicto Final
            st.markdown("---")
            st.subheader("⚖️ Decisión del Gestor de Riesgos")
            debate_context = f"TECH: {tech_report}\nSENT: {news_report}"
            ticket = call_manager(debate_context, asset_name, event_name, macro)
            
            st.markdown(f"""
            <div style="background-color: #0E1117; padding: 25px; border-radius: 15px; border: 2px solid #ff4b4b;">
                <h4 style="color: #ff4b4b; margin-top: 0;">ORDEN DE TRADING GENERADA:</h4>
                <pre style="color: #e0e0e0; font-family: 'Courier New', monospace; white-space: pre-wrap;">{ticket}</pre>
            </div>
            """, unsafe_allow_html=True)

    else:
        # BANNER VISUAL (Sustituye a la imagen que no cargaba)
        st.markdown("""
            <div style="background-color: #262730; padding: 60px; border-radius: 20px; text-align: center; border: 1px dashed #464b5d; margin-top: 20px;">
                <h1 style="font-size: 80px; margin-bottom: 10px;">📉🤖</h1>
                <h2 style="color: white; margin-bottom: 10px;">Terminal de Inteligencia Artificial</h2>
                <p style="color: #a3a8b4; font-size: 18px;">VIX, DXY y Noticias en tiempo real para Micro Futuros.</p>
                <p style="color: #ff4b4b; font-weight: bold;">Listo para iniciar el próximo escaneo.</p>
            </div>
        """, unsafe_allow_html=True)