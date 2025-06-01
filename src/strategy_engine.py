# src/strategy_engine.py
import logging

logger = logging.getLogger(__name__)

DEFAULT_CAPITAL_FOR_ALERTS = 10000.0 # Capital padrão para alertas do Telegram

def generate_simulated_strategy(recommendation_text: str, capital_available: float = DEFAULT_CAPITAL_FOR_ALERTS):
    """
    Simula uma estratégia de alocação de ativos baseada em uma recomendação textual.
    Esta função é um placeholder e deve ser substituída por um modelo mais inteligente.
    """
    if not recommendation_text:
        logger.warning("generate_simulated_strategy: Recommendation text is empty. Cannot generate strategy.")
        return {'short': {}, 'long': {}, 'message': "Nenhuma recomendação para basear a estratégia."}

    short_assets = ['PETR4.SA', 'VALE3.SA'] # Default short
    long_assets = ['GOLD', 'AGRO3.SA']    # Default long

    lower_rec = recommendation_text.lower()
    if "inflation" in lower_rec or "interest rates rising" in lower_rec or "juros subindo" in lower_rec:
        long_assets.append('USDBRL') # Hedge contra desvalorização da moeda local
        long_assets.append('IMA-B') # Títulos atrelados à inflação (exemplo Brasil)
    if "recession" in lower_rec or "economic contraction" in lower_rec or "contração econômica" in lower_rec:
        short_assets.extend(['IBOV', 'SPY']) # Short em índices amplos
        long_assets.append('USD') # Dólar como refúgio
    if "supply chain disruption" in lower_rec or "quebra na cadeia" in lower_rec:
        # Isso é complexo, pode ser long em algumas commodities, short em outras
        long_assets.append('COMMODITIES_INDEX_ETF') # Placeholder para ETF de commodities
    if "tecnologia em alta" in lower_rec or "tech boom" in lower_rec:
        long_assets.append('QQQ') # ETF de tecnologia (Nasdaq 100)
    if "mercados emergentes" in lower_rec and ("oportunidade" in lower_rec or "crescimento" in lower_rec):
        long_assets.append('EEM') # ETF de Mercados Emergentes

    # Garante que as listas não fiquem vazias e sejam únicas
    long_assets = list(set(long_assets))
    short_assets = list(set(short_assets))

    if not short_assets and not long_assets:
        # Se nenhuma regra específica for acionada, estratégia neutra ou de erro
        return {'short': {}, 'long': {}, 'message': "Nenhuma regra de estratégia acionada pela recomendação."}
    
    # Evita divisão por zero se uma das listas estiver vazia após as regras
    num_short = len(short_assets) if short_assets else 1
    num_long = len(long_assets) if long_assets else 1

    # Ajuste de alocação: se apenas um lado tiver ativos, aloca 100% para ele
    short_alloc_ratio = 0.30
    long_alloc_ratio = 0.70

    if not short_assets and long_assets:
        short_alloc_ratio = 0.0
        long_alloc_ratio = 1.0
    elif short_assets and not long_assets:
        short_alloc_ratio = 1.0
        long_alloc_ratio = 0.0
    elif not short_assets and not long_assets: # Deve ser pego pelo check anterior, mas por segurança
        short_alloc_ratio = 0.0
        long_alloc_ratio = 0.0


    allocation = {
        'short': {},
        'long': {},
        'message': "Estratégia gerada."
    }

    if short_assets:
        allocation['short'] = {asset: capital_available * short_alloc_ratio / num_short for asset in short_assets}
    
    if long_assets:
        allocation['long'] = {asset: capital_available * long_alloc_ratio / num_long for asset in long_assets}
        
    return allocation

if __name__ == '__main__':
    # Testes rápidos
    rec1 = "Previsão de alta da inflação e juros subindo. Contração econômica à vista."
    strat1 = generate_simulated_strategy(rec1, 50000)
    print(f"Recomendação: {rec1}\nEstratégia: {strat1}\n")

    rec2 = "Oportunidades em mercados emergentes e tecnologia em alta."
    strat2 = generate_simulated_strategy(rec2) # Usa capital padrão
    print(f"Recomendação: {rec2}\nEstratégia: {strat2}\n")

    rec3 = "Nada de muito novo no horizonte."
    strat3 = generate_simulated_strategy(rec3)
    print(f"Recomendação: {rec3}\nEstratégia: {strat3}\n")
