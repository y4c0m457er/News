from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Usamos modelos eficientes para respuestas rápidas
llm = ChatOpenAI(model="gpt-4o-mini") 

def call_analyst(role_prompt, context_data):
    messages = [
        SystemMessage(content=role_prompt),
        HumanMessage(content=f"Datos: {context_data}")
    ]
    return llm.invoke(messages).content

def call_manager(debate_history, asset, event, macro_data):
    vix = macro_data.get('VIX', {}).get('price', 20)
    dxy = macro_data.get('DXY', {})

    prompt = f"""Actúa como Director de Riesgos. Evalúa {asset} para {event}.
    
    MACRO DATA:
    - VIX: {vix} (Si >22, sé conservador con el SL).
    - DXY: {dxy} (Si sube, presiona a la baja Oro e Índices).
    
    RESPONDE EN ESPAÑOL:
    VERDICTO: [BUY / SELL / NO TRADE] | CERTEZA: [1-5]
    NIVELES: SL: [Precio] | TP: [Precio] | RR: [Ratio]
    ---------------------------------------------
    VIX & SL: [Cómo influye la volatilidad en el riesgo]
    DXY & BIAS: [Cómo influye el dólar en la dirección]
    RAZÓN: [Explicación breve]
    """
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Debate: {debate_history}")
    ]
    return llm.invoke(messages).content