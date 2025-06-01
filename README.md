# ATENÇÃO O PROJETO AINDA NÃO ESTÁ PRONTO E POSSUI ERROS

# 🌎 Intelligent Disaster Monitor (Google Gemini Edition)

### 🔍 Inteligência Artificial multiagente para monitoramento em tempo real de riscos naturais e impactos econômicos, utilizando Google Gemini.

Este projeto utiliza agentes especializados (climatologista, sismólogo, economista, especialista solar, analista de seguros) que se retroalimentam por meio da API Google Generative AI (Gemini) para interpretar dados em tempo real de desastres naturais e antecipar impactos econômicos. Baseado em web scraping (Selenium headless para JS, Requests para estático), análise assíncrona e integração com APIs como FRED (St. Louis Fed), USGS, NOAA, e alertas por Telegram.

---

## 🧠 Componentes principais

- 🌐 **Web Scraping Híbrido**: Selenium (headless Chrome) para sites com JavaScript e `requests` para sites estáticos.
- 🧬 **Agentes com Inteligência Artificial via Google Generative AI (Gemini API)**.
- 📊 **Banco de dados SQLite3** para armazenamento histórico de cenários e análises.
- 🔔 **Alertas automáticos via Telegram** para novos cenários e recomendações.
- 🔄 **Execução em Ciclos**: O sistema opera em ciclos, coletando dados, analisando e gerando insights periodicamente.
- 🧱 **Frontend Interativo com Streamlit**: Visualização de dados, cenários e simulação de estratégias de trading.
- 📦 **Container Docker Leve e Portátil**: Para fácil deploy e execução consistente.
- ☁️ **Compatível com Google Colab (com ajustes), desktop ou nuvem**.

---

## 📦 Tecnologias e Bibliotecas

| Componente             | Versão/Tecnologia        |
|------------------------|--------------------------|
| Python                 | >= 3.10                  |
| Google Generative AI   | `google-generativeai`    |
| Web Scraping           | `selenium`, `beautifulsoup4`, `requests` |
| HTTP Client (Async)    | `aiohttp` (opcional, para futuras otimizações) |
| Environment Variables  | `python-dotenv`          |
| Database               | `sqlite3` (nativo)       |
| Logging                | `logging` (nativo)       |
| Frontend               | `streamlit`, `pandas`    |
| Telegram Integration   | `requests`               |
| Containerization       | `Docker`                 |

---

## 📂 Estrutura do Projeto


---

## 🚀 Como executar

### 🔧 Requisitos
- Python >= 3.10
- Google Chrome e ChromeDriver (se não usar Docker, e ChromeDriver deve estar no PATH ou especificado)
- API Keys (Google AI, FRED, Telegram)

### 📝 Configuração Inicial
1.  Clone o repositório:
    ```bash
    git clone <repository_url>
    cd intelligent_disaster_monitor
    ```
2.  Crie um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate    # Windows
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Crie o arquivo `.env` na raiz do projeto (copie de `.env.example` se existir, ou crie manualmente) e preencha suas chaves de API:
    ```ini
    # .env
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    FRED_API_KEY="YOUR_FRED_API_KEY"
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID"
    ```

### 🏃 Executando o Sistema de Agentes (Backend)

Diretamente com Python:
```bash
python -m src.agent_system

streamlit run frontend/frontend_interface.py

docker build -t intelligent-disaster-monitor .

Isso iniciará o ciclo de monitoramento contínuo.
🖥️ Executando o Frontend (Streamlit)
Em um novo terminal (com o ambiente virtual ativado):
streamlit run frontend/frontend_interface.py
Use code with caution.
Bash
Acesse o dashboard no navegador, geralmente em http://localhost:8501.
🐳 Com Docker
Construa a imagem Docker:
Certifique-se de que o Docker Desktop (ou Docker Engine no Linux) está em execução.
No diretório raiz do projeto (onde o Dockerfile está localizado):
docker build -t intelligent-disaster-monitor .
Use code with caution.
Bash
Execute o container Docker (Sistema de Agentes):
Você precisará passar suas variáveis de ambiente para o container. A forma mais fácil é usando um arquivo .env.
docker run -d --name disaster-monitor-agent --env-file .env intelligent-disaster-monitor
Use code with caution.
Bash
-d: Executa em modo detached (background).
--name disaster-monitor-agent: Nomeia o container.
--env-file .env: Carrega variáveis de ambiente do arquivo .env.
intelligent-disaster-monitor: Nome da imagem que você construiu.
Para ver os logs do container do agente:
docker logs -f disaster-monitor-agent
Use code with caution.
Bash
Execute o container Docker (Frontend - Opcional, se quiser rodar o frontend em Docker também):
Se você quiser rodar o frontend em Docker, você precisaria de um CMD diferente no Dockerfile ou uma imagem separada.
Para este exemplo, rodar o frontend localmente (como descrito acima) enquanto o backend roda em Docker é mais simples se eles compartilham o arquivo de banco de dados via volume.
Se o banco de dados data/disaster_monitor.db é criado pelo container do agente, o frontend (rodando localmente ou em outro container) precisa acessar esse arquivo.
Para compartilhar o data diretório com o container do agente:
docker run -d --name disaster-monitor-agent \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  intelligent-disaster-monitor
Use code with caution.
Bash
Assim, o data/disaster_monitor.db criado pelo container estará disponível no seu host no diretório data/, e o Streamlit (rodando localmente) poderá acessá-lo.
🛠️ Considerações sobre Scraping Avançado (Ex: Toro Investimentos)
A infraestrutura de scraping atual com Selenium é um ponto de partida. Para plataformas financeiras complexas como a Toro Investimentos, seriam necessárias técnicas mais avançadas:
Login e Gerenciamento de Sessão:
Automatizar o login de forma segura (evitar hardcoding de credenciais).
Manter e reutilizar cookies de sessão.
Navegação Dinâmica e Waits Explícitos:
Uso intensivo de WebDriverWait para esperar por elementos específicos (gráficos, tabelas de cotações, feeds de notícias) antes de tentar interagir ou extrair dados.
Identificar XHR/Fetch requests que carregam dados dinamicamente e potencialmente interceptá-los ou simular sua lógica.
Tratamento de CAPTCHAs:
Muito desafiador. Pode envolver serviços de terceiros para resolução de CAPTCHAs (ex: Anti-CAPTCHA, 2Captcha) ou técnicas para minimizar sua aparição.
Estrutura do Site Alvo:
Análise detalhada da estrutura HTML/CSS/JS do site para identificar seletores robustos.
Adaptação a mudanças frequentes na interface do usuário do site.
Evasão de Detecção:
Rotação de User-Agents.
Uso de proxies (residenciais ou de datacenters) para evitar bloqueios de IP.
Simulação de comportamento humano (movimentos de mouse, delays aleatórios).
Robustez e Tratamento de Erros Específicos:
Mecanismos de retry mais sofisticados para falhas de rede ou elementos não encontrados.
Logging detalhado de cada etapa do scraping para depuração.
A implementação dessas técnicas requer um esforço considerável e customização para cada site alvo. O framework atual provê a base para integrar tais módulos de scraping avançado.
---

**Final Checks and How to Run:**

1.  **Install Dependencies:** `pip install -r requirements.txt`
2.  **Set up `.env`:** Create and populate your `.env` file in the project root.
3.  **Run the Agent System (Backend):**
    ```bash
    python -m src.agent_system
    ```
    This will start logging to console, create/use `data/disaster_monitor.db`, and send Telegram alerts if configured.
4.  **Run the Frontend:**
    In a *new terminal*:
    ```bash
    streamlit run frontend/frontend_interface.py
    ```
    Open your browser to the URL Streamlit provides (usually `http://localhost:8501`).

**Docker Execution:**
1. Build: `docker build -t intelligent-disaster-monitor .`
2. Run Agent System: `docker run -d --name disaster-monitor-agent --env-file .env -v "$(pwd)/data:/app/data" intelligent-disaster-monitor`
   The `-v "$(pwd)/data:/app/data"` mounts the local `data` directory into the container's `/app/data` directory. This way, the SQLite database created by the agent system inside the Docker container will be persistent on your host machine in the `data` folder. The Streamlit app (run locally) can then access this same database file.

This comprehensive refactor provides a much more robust, maintainable, and extensible system using Google Gemini for its AI capabilities. The scraping part is still foundational but allows for plugging in more advanced techniques as needed.
