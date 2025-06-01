# frontend/frontend_interface.py
import sys
import os
import sqlite3
import streamlit as st
import pandas as pd

# --- Early Page Config ---
# st.set_page_config DEVE SER A PRIMEIRA CHAMADA STREAMLIT
st.set_page_config(page_title="Disaster Monitor Dashboard", layout="wide")


# Add src directory to Python path to import config
# This assumes frontend_interface.py is run from the project root (e.g., streamlit run frontend/frontend_interface.py)
# or that intelligent_disaster_monitor/ is in PYTHONPATH


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')

_db_path_warning_message = None # Para armazenar a mensagem de aviso

if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from src.config import DATABASE_PATH
except ImportError:
    db_file_name = 'disaster_monitor.db'
    _project_root_from_frontend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_PATH = os.path.join(_project_root_from_frontend, 'data', db_file_name)
    if not os.path.exists(os.path.dirname(DATABASE_PATH)):
         os.makedirs(os.path.dirname(DATABASE_PATH))
    # Armazena a mensagem de aviso para exibir depois
    _db_path_warning_message = f"Could not import DATABASE_PATH from src.config. Using fallback: {DATABASE_PATH}. Ensure this is correct."


# === UI Title and other elements AFTER set_page_config ===
st.title("🌎 Intelligent Disaster Monitor Dashboard")
st.caption("Utilizando Google Gemini para análise e recomendações.")

# Exibe o aviso sobre o DB_PATH aqui, se houver
if _db_path_warning_message:
    st.warning(_db_path_warning_message)


# === Load DB ===
def load_scenarios():
    if not os.path.exists(DATABASE_PATH):
        st.error(f"Database file not found at {DATABASE_PATH}. Ensure the backend agent system has run and created it.")
        return pd.DataFrame()
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        df = pd.read_sql_query("SELECT id, timestamp, summary, recommendation, agent_inputs FROM scenarios ORDER BY timestamp DESC", conn)
        return df
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# === Simulated Strategy Engine ===
# Idealmente, esta função viria de src.strategy_engine conforme discutimos
# Mas para manter este arquivo autocontido por enquanto (ou se a importação falhar):
try:
    from src.strategy_engine import generate_simulated_strategy as generate_strategy
    # Se a importação acima funcionar, a função generate_strategy abaixo não será usada.
except ImportError:
    st.error("Falha ao importar 'generate_simulated_strategy' de src.strategy_engine. Usando fallback interno.")
    def generate_strategy(recommendation_text, capital_available):
        short_assets = ['PETR4.SA', 'VALE3.SA'] 
        long_assets = ['GOLD', 'AGRO3.SA']    

        if recommendation_text:
            lower_rec = recommendation_text.lower()
            if "inflation" in lower_rec or "interest rates rising" in lower_rec:
                long_assets.append('USDBRL') 
                long_assets = list(set(long_assets)) 
            if "recession" in lower_rec or "economic contraction" in lower_rec:
                short_assets.extend(['IBOV', 'SPY']) 
                short_assets = list(set(short_assets))
            if "supply chain disruption" in lower_rec:
                long_assets.append('COMMODITIES_INDEX_ETF') 
                long_assets = list(set(long_assets))
        
        if not short_assets: short_assets = ['SPY'] 
        if not long_assets: long_assets = ['GLD'] 

        # Verifica se as listas de ativos não estão vazias para evitar divisão por zero
        num_short = len(short_assets) if short_assets else 1
        num_long = len(long_assets) if long_assets else 1

        short_alloc_ratio = 0.30
        long_alloc_ratio = 0.70

        if not short_assets and long_assets:
            short_alloc_ratio = 0.0
            long_alloc_ratio = 1.0
        elif short_assets and not long_assets:
            short_alloc_ratio = 1.0
            long_alloc_ratio = 0.0
        elif not short_assets and not long_assets:
             return {'short': {}, 'long': {}} # Retorna vazio se não houver ativos

        allocation = {'short': {}, 'long': {}}
        if short_assets:
            allocation['short'] = {asset: capital_available * short_alloc_ratio / num_short for asset in short_assets}
        if long_assets:
            allocation['long'] = {asset: capital_available * long_alloc_ratio / num_long for asset in long_assets}
        
        return allocation

# === Main UI Logic ===
scenarios_df = load_scenarios()

if not scenarios_df.empty:
    latest = scenarios_df.iloc[0]
    st.subheader(f"🧠 Último Cenário Registrado (ID: {latest['id']})")
    st.markdown(f"**Data/Hora (UTC):** {latest['timestamp']}")
    
    st.markdown("### 📜 Recomendação Econômica Principal")
    st.text_area("Recomendação", latest['recommendation'], height=200, key="rec_main")

    with st.expander("Ver Análise Completa dos Agentes (Sumário)"):
        st.text_area("Sumário Detalhado", latest['summary'], height=400, key="sum_detail")
    
    if 'agent_inputs' in latest and latest['agent_inputs']:
        with st.expander("Ver Dados Brutos dos Agentes (JSON)"):
            try:
                # Garante que é uma string antes de tentar carregar como JSON
                agent_inputs_data = latest['agent_inputs']
                if isinstance(agent_inputs_data, str):
                    agent_data = pd.io.json.loads(agent_inputs_data)
                    st.json(agent_data)
                elif isinstance(agent_inputs_data, dict): # Se já for um dict (improvável do DB)
                    st.json(agent_inputs_data)
                else:
                    st.text(str(agent_inputs_data))
            except Exception as e:
                st.text(str(latest['agent_inputs'])) 
                st.warning(f"Could not parse agent_inputs as JSON: {e}")


    st.markdown("---")
    st.subheader("♟️ Gerador de Estratégia de Ativos (Simulado)")
    capital = st.number_input("💰 Capital disponível para estratégia (R$)", min_value=1000.0, value=10000.0, step=1000.0)
    
    if st.button("📈 Gerar Estratégia de Ativos"):
        if latest['recommendation']:
            strategy = generate_strategy(latest['recommendation'], capital)
            st.success("Estratégia gerada com sucesso!")
            
            st.subheader("Posições Sugeridas")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📉 Short (Venda)")
                if strategy.get('short'): # Use .get() para segurança
                    for asset, value in strategy['short'].items():
                        st.write(f"{asset}: R$ {value:,.2f}")
                else:
                    st.write("Nenhuma posição short sugerida.")
            with col2:
                st.markdown("#### 📈 Long (Compra)")
                if strategy.get('long'): # Use .get() para segurança
                    for asset, value in strategy['long'].items():
                        st.write(f"{asset}: R$ {value:,.2f}")
                else:
                    st.write("Nenhuma posição long sugerida.")
        else:
            st.warning("Não há recomendação econômica no último cenário para basear a estratégia.")
else:
    st.warning("Nenhum cenário disponível ainda. Aguarde o ciclo de monitoramento do sistema de agentes ou verifique os logs.")

st.sidebar.markdown("---")
st.sidebar.info(f"Caminho do Banco de Dados: {DATABASE_PATH}")
if _db_path_warning_message: # Adiciona o aviso na sidebar também
    st.sidebar.warning(_db_path_warning_message)

if st.sidebar.button("Recarregar Dados"):
    st.rerun() # <<< CORREÇÃO AQUI
st.warning("DISCLAIMER -> Dados apenas educativos sem validade para compra ou venda dentro do mercado financeiro. Consulte sua corretora ou banco.")
