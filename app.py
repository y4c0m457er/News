import streamlit as st
from tools import get_market_data, get_news_sentiment, get_macro_volatility
from agents import call_analyst, call_manager

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="IA Trading Terminal", layout="wide", page_icon="🚀")

# 2. SISTEMA DE SEGURIDAD (PASSWORD)
def check_password():
    """Retorna True si el usuario introdujo la contraseña correcta."""
    def password_entered():
        if st.session_state["password"] == st.secrets["CLAVE_ACCESO"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Eliminar de session_state por seguridad
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Primera vez que entra
        st.title("🔐 Acceso Restringido")
        st.text_input("Introduce la clave de acceso para operar:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Contraseña incorrecta
        st.title("🔐 Acceso Restringido")
        st.text_input("Introduce la clave de acceso para operar:", type="password", on_change=password_entered, key="password")
        st.error("😕 Clave incorrecta. Contacta con el administrador.")
        return False
    else:
        # Contraseña correcta
        return True

# 3. LÓGICA PRINCIPAL DE LA APLICACIÓN
if check_password():
    st.title("🚀 IA Micro Futuros Dashboard")
    st.markdown("---")

    # --- BARRA LATERAL (Configuración) ---
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
        
        event_name = st.text_input("Evento Económico (ej: CPI, Inventarios)", "Análisis de Rutina")
        
        st.info("⚠️ Cada análisis consume créditos de API. Úsalo con criterio.")
        btn_analizar = st.button("🔥 Lanzar Análisis Profesional", type="primary")

    # --- EJECUCIÓN DEL ANÁLISIS ---
    if btn_analizar:
        with st.spinner(f"Extrayendo datos de {asset_name} y consultando agentes..."):
            # A. Obtención de datos con manejo de errores
            market = get_market_data(asset_ticker)
            news = get_news_sentiment(asset_name)
            macro = get_macro_volatility()
            
            # Extraer valores macro de forma segura
            vix = macro.get('VIX', {}).get('price', 0)
            dxy = macro.get('DXY', {}).get('price', 0)

            # B. Fila de Métricas (Dashboard)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("VIX (Miedo)", f"{vix}", delta="ALTO" if vix > 22 else "Normal", delta_color="inverse")
            with col2:
                st.metric("DXY (Dólar)", f"{dxy}")
            with col3:
                # Validación crítica para evitar el TypeError de la línea 46
                if isinstance(market, dict) and 'price' in market:
                    st.metric(f"Precio {asset_name}", f"${market['price']}")
                else:
                    st.metric(f"Precio {asset_name}", "Error N/A")
                    st.warning("No se pudo obtener el precio actual. Verifique el ticker.")

            # C. Debate de Agentes
            st.subheader("🧠 Debate de la Mesa de Trading")
            c1, c2 = st.columns(2)
            
            with c1:
                with st.expander("📊 Analista Técnico", expanded=True):
                    tech_report = call_analyst("Analista Técnico de Futuros.", str(market))
                    st.write(tech_report)
            
            with c2:
                with st.expander("🗞️ Analista de Sentimiento", expanded=True):
                    news_report = call_analyst("Analista de Noticias y Sentimiento.", news)
                    st.write(news_report)

            # D. Veredicto Final del Juez
            st.markdown("---")
            st.subheader("⚖️ Decisión Final del Juez")
            debate_context = f"TECH: {tech_report}\nSENT: {news_report}"
            
            # El manager toma la decisión final
            ticket = call_manager(debate_context, asset_name, event_name, macro)
            
            # Mostramos el resultado en una caja resaltada
            st.success("Análisis Completado")
            st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b;">
                <pre style="color: white; white-space: pre-wrap;">{ticket}</pre>
            </div>
            """, unsafe_allow_html=True)

    else:
        # Pantalla de espera
        st.image("https://images.unsplash.com/photo-1611974717482-98aa007ae39d?q=80&w=1000&auto=format&fit=crop", caption="IA Trading Terminal lista para operar.")
        st.info("👈 Configure el activo y pulse el botón para iniciar el escaneo macro y técnico.")