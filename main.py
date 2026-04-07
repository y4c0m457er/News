from tools import get_market_data, get_news_sentiment, get_macro_volatility
from agents import call_analyst, call_manager

def run_trading_session(asset_ticker, asset_name, event_name):
    print(f"\n--- 📡 ANALIZANDO: {asset_name} ---")
    
    # 1. Recolección de datos
    market = get_market_data(asset_ticker)
    news = get_news_sentiment(asset_name)
    macro = get_macro_volatility()
    
    vix = macro.get('VIX', {}).get('price', 'N/A')
    dxy = macro.get('DXY', {}).get('price', 'N/A')
    print(f"📊 MONITOR: VIX {vix} | DXY {dxy}")

    # 2. Análisis
    print("🧠 Consultando analistas y flujo macro...")
    tech_report = call_analyst("Analista Técnico de Futuros.", str(market))
    news_report = call_analyst("Analista Fundamental/Sentimiento.", news)

    # 3. Veredicto
    print("⚖️ El Juez está dictando sentencia...")
    debate = f"TECH: {tech_report}\nSENT: {news_report}"
    ticket = call_manager(debate, asset_name, event_name, macro)

    # 4. Resultado
    print("\n" + "🎯" * 15)
    print(ticket)
    print("🎯" * 15)

if __name__ == "__main__":
    while True:
        print("\n" + "="*45)
        print("🚀 TERMINAL DE MICRO FUTUROS PROFESIONAL")
        print("="*45)
        
        activos = {
            "1": {"ticker": "MCL=F", "name": "Micro Crude Oil"},
            "2": {"ticker": "MGC=F", "name": "Micro Gold"},
            "3": {"ticker": "MNQ=F", "name": "Micro Nasdaq 100"},
            "4": {"ticker": "MYM=F", "name": "Micro Dow Jones"}
        }
        
        print("Selecciona una opción:")
        for k, v in activos.items():
            print(f" [{k}] {v['name']}")
        print(" [Q] Salir")
        
        choice = input("\n🔢 Elige (1-4 o Q): ").upper()
        
        if choice == 'Q':
            print("\n👋 Cerrando... ¡Buenas operaciones!")
            break
            
        if choice in activos:
            noticia = input(f"👉 ¿Qué noticia evaluamos para {activos[choice]['name']}?: ")
            run_trading_session(activos[choice]["ticker"], activos[choice]["name"], noticia)
            input("\nPresiona ENTER para volver al menú...")
        else:
            print("\n❌ Opción no válida.")