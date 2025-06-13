# 🚀 Projeto Hermes: Manutenção Preditiva IoT para o Enterprise Challenge

**Desenvolvedor:** Diogo Leite Zequini Pinto | **RM:** 565535

---

## 💡 1. Visão Geral e Objetivos do Projeto

Este projeto é a minha solução para a segunda etapa do Enterprise Challenge, desenvolvido em parceria com a Hermes Reply. Meu objetivo foi construir um protótipo funcional de um sistema de monitoramento IoT para manutenção preditiva, indo além de uma simples coleta de dados.

A solução abrange todo o ciclo de vida dos dados: desde a simulação de um dispositivo embarcado (ESP32) que coleta e pré-processa informações de sensores, até um pipeline de análise em Python. Este pipeline não apenas visualiza os dados, mas também aplica um modelo de Machine Learning para prever o estado do sistema e ajudar no diagnóstico de falhas. Para tornar a análise mais acessível e poderosa, finalizei o projeto com um dashboard de Business Intelligence (BI) interativo, desenvolvido em Streamlit.

---

## 🛠️ 2. Arquitetura da Solução

Desenvolvi o projeto de forma modular, com cada componente tendo uma responsabilidade clara e otimizada.

### 2.1. Hardware Simulado: Circuito Virtual no Wokwi

Para simular um dispositivo de monitoramento real, montei o circuito no Wokwi. A escolha dos sensores foi baseada na sua relevância para cenários industriais:

*   **DHT22 (Temperatura e Umidade):** Fundamental para monitorar as condições operacionais do equipamento e do ambiente.
*   **LDR (Luminosidade):** Simula um sensor ambiental que pode ser útil para análises de contexto ou segurança.
*   **Potenciômetro (Vibração):** A vibração é um dos indicadores mais críticos de falha mecânica. Utilizei um potenciômetro para simular diferentes níveis de intensidade, essenciais para a análise preditiva.

*O esquema do circuito está disponível em: `documentacao/imagens/hermes_reply_circuito_wokwi.png`*

### 2.2. Firmware: Inteligência na Borda com ESP32

O código para o ESP32 (`arduino/src/main.cpp`) é responsável pela coleta e preparação dos dados na fonte.

*   **Leitura e Estruturação:** A cada 5 segundos, o firmware lê os valores dos sensores e os organiza em um payload JSON estruturado.
*   **Cálculo de Média Móvel:** Implementei um cálculo de média móvel para temperatura e umidade para suavizar ruídos e fornecer uma visão de tendência mais estável, importante para a análise.
*   **Payload de Dados:** Os dados são transmitidos via Serial em um formato JSON completo, incluindo metadados do dispositivo, valores instantâneos, médias móveis e uma análise de status inicial baseada em regras.

**Exemplo da Saída de Dados:**
```json
JSON_DATA: {"deviceId":"HR-PRED-MAINT-01","timestamp":5110,"sensors":{"temperature":{"value":26.6,"movingAverage":25.8},"humidity":{"value":78.4,"movingAverage":65.2}, ...}}
```

### 2.3. Análise de Dados: Pipeline em Python

O script `analise_dados/app.py` centraliza todo o fluxo de processamento e análise dos dados.

1.  **Ingestão Automatizada:** O script lê o arquivo de log (`dados_simulacao/serial_output.log`) e extrai automaticamente os payloads JSON gerados pela simulação.
2.  **Engenharia de Features:** Para aumentar o poder preditivo, criei novas variáveis (features) a partir dos dados brutos. Por exemplo, calculei o desvio padrão da vibração em uma janela de tempo para identificar instabilidades e a interação entre temperatura e vibração para detectar sobrecargas.
3.  **Modelagem Preditiva (Machine Learning):** Utilizei um `RandomForestClassifier` para treinar um modelo que aprende a classificar o estado do sistema (`NORMAL`, `ATENÇÃO`, `CRÍTICO`) com base nos padrões dos dados.
4.  **Diagnóstico de Causa Raiz:** Através da análise de "Feature Importance" do modelo, é possível identificar quais sensores e comportamentos mais influenciaram um alerta, auxiliando no diagnóstico da causa raiz do problema.

### 2.4. Interface de BI: Dashboard Interativo com Streamlit

Para apresentar os resultados de forma clara e interativa, desenvolvi um dashboard web com Streamlit.

*   **Interface Organizada:** O layout utiliza abas para separar as diferentes seções da análise (Visão Geral, Análise de Sensores, Análise Preditiva).
*   **KPIs e Visualizações:** Métricas importantes são exibidas de forma destacada, e todos os gráficos (temporais, de status, correlações) são gerados dinamicamente para a análise do usuário.
*   **Resultados do ML:** A performance do modelo (Matriz de Confusão) e a análise de causa raiz (Importância das Features) são apresentadas de forma visual e de fácil compreensão.
*   **Exploração de Dados:** Há uma seção dedicada para visualizar a tabela de dados completa, permitindo uma análise mais aprofundada.

---

## 🚀 3. Como Executar o Projeto

Preparei um script para simplificar a execução do projeto.

### 3.1. Método Simplificado (Recomendado)

Na raiz do projeto, execute o script `run_dashboard.bat`.

```bash
.\run_dashboard.bat
```

Este script irá:
1.  Verificar e instalar as dependências Python necessárias a partir do `requirements.txt`.
2.  Iniciar o dashboard web com o Streamlit.
3.  Abrir o dashboard automaticamente no seu navegador.

### 3.2. Método Manual

Caso prefira, você pode executar os passos manualmente:

1.  **Simulação do Hardware (Wokwi CLI):**
    *   Execute a simulação do Wokwi para gerar o arquivo de log `dados_simulacao/serial_output.log`.
2.  **Análise de Dados (Python):**
    *   Navegue até a raiz do projeto em um terminal.
    *   Instale as dependências: `pip install -r analise_dados/requirements.txt`
    *   Inicie o dashboard: `streamlit run analise_dados/app.py`

---

## 📦 4. Estrutura do Repositório

A organização das pastas foi pensada para facilitar a navegação e o entendimento do projeto.

```
.
├── arduino/                  # Código-fonte do firmware para o ESP32
├── analise_dados/            # Pipeline de análise e o dashboard de BI
├── dados_simulacao/          # Arquivos gerados pela simulação e análise
├── documentacao/             # Imagens e relatórios
├── simulacao_wokwi/          # Arquivos de configuração da simulação Wokwi
├── RELATORIO_ANALISE.md      # Relatório detalhado gerado pelo pipeline
├── run_dashboard.bat         # Script para execução simplificada
└── README.md                 # Este documento
```

---

## ✅ 5. Conclusão

Este projeto representa minha abordagem para resolver um desafio de engenharia de forma completa. Busquei não apenas cumprir os requisitos, mas construir uma solução de ponta a ponta que fosse funcional, robusta e que demonstrasse o valor prático de tecnologias como IoT e Machine Learning. Desde a otimização na coleta de dados no ESP32 até a criação de um dashboard interativo para análise, cada etapa foi planejada e executada com o objetivo de entregar um resultado de alta qualidade.

Agradeço pela oportunidade de desenvolver e apresentar este trabalho.

---

*Desenvolvido com dedicação e paixão por tecnologia por Diogo Leite Zequini Pinto - RM 565535* 