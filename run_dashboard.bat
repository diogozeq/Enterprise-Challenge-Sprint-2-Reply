@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
echo.
echo ========================================
echo    🚀 HERMES REPLY IoT ANALYTICS
echo    Sistema Completo de Simulacao e BI
echo ========================================
echo.

:: Configuracao de diretorios
set "PROJECT_DIR=%~dp0"
set "ARDUINO_DIR=%PROJECT_DIR%arduino"
set "DADOS_DIR=%PROJECT_DIR%dados_simulacao"
set "ANALISE_DIR=%PROJECT_DIR%analise_dados"

:: Criar diretorios se nao existirem
if not exist "%DADOS_DIR%" mkdir "%DADOS_DIR%"
if not exist "%ANALISE_DIR%" mkdir "%ANALISE_DIR%"

echo 📁 Diretorios configurados:
echo    - Projeto: %PROJECT_DIR%
echo    - Arduino: %ARDUINO_DIR%
echo    - Dados: %DADOS_DIR%
echo    - Analise: %ANALISE_DIR%
echo.

:: ETAPA 1: Verificar Python
echo ⚙️  ETAPA 1: Verificando Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python nao encontrado! Instale Python 3.8+ para continuar
    pause
    exit /b 1
)
echo ✅ Python encontrado

:: ETAPA 2: Instalar dependencias Python
echo 📦 ETAPA 2: Instalando dependencias Python...
python -m pip install pandas numpy plotly streamlit scikit-learn --upgrade --quiet
if %ERRORLEVEL% EQU 0 (
    echo ✅ Dependencias instaladas com sucesso
) else (
    echo ⚠️  Aviso: Algumas dependencias podem nao ter sido instaladas
)

:: ETAPA 3: Gerar dados simulados
echo 🔄 ETAPA 3: Gerando dados simulados...
cd /d "%ANALISE_DIR%"

:: Limpar log anterior
if exist "%DADOS_DIR%\serial_output.log" del "%DADOS_DIR%\serial_output.log"

:: Gerar dados simulados estruturados com maior diversidade para ML
(
echo JSON_DATA: {"timestamp":1734123456000,"deviceId":"HERMES_ESP32_001","readingId":1,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":23.5,"movingAverage":23.2,"status":"NORMAL"},"humidity":{"value":65.2,"movingAverage":64.8,"status":"NORMAL"},"lightLevel":{"value":450,"status":"NORMAL"},"vibration":{"value":0.15,"status":"NORMAL"}},"analysis":{"systemStatus":"NORMAL","riskLevel":0.1,"nextMaintenance":"2024-12-20T10:00:00Z","statusDetail":"Todos os parametros dentro da normalidade"},"operationalStats":{"uptime":15000,"totalReadings":1,"avgTemperature":23.5,"avgHumidity":65.2}}
echo JSON_DATA: {"timestamp":1734123461000,"deviceId":"HERMES_ESP32_001","readingId":2,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":24.1,"movingAverage":23.8,"status":"NORMAL"},"humidity":{"value":67.5,"movingAverage":66.4,"status":"NORMAL"},"lightLevel":{"value":420,"status":"NORMAL"},"vibration":{"value":0.18,"status":"NORMAL"}},"analysis":{"systemStatus":"NORMAL","riskLevel":0.15,"nextMaintenance":"2024-12-20T10:00:00Z","statusDetail":"Operacao normal"},"operationalStats":{"uptime":20000,"totalReadings":2,"avgTemperature":23.8,"avgHumidity":66.4}}
echo JSON_DATA: {"timestamp":1734123466000,"deviceId":"HERMES_ESP32_001","readingId":3,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":22.8,"movingAverage":23.5,"status":"NORMAL"},"humidity":{"value":63.1,"movingAverage":65.3,"status":"NORMAL"},"lightLevel":{"value":480,"status":"NORMAL"},"vibration":{"value":0.12,"status":"NORMAL"}},"analysis":{"systemStatus":"NORMAL","riskLevel":0.08,"nextMaintenance":"2024-12-20T10:00:00Z","statusDetail":"Sistema operando normalmente"},"operationalStats":{"uptime":25000,"totalReadings":3,"avgTemperature":23.5,"avgHumidity":65.3}}
echo JSON_DATA: {"timestamp":1734123471000,"deviceId":"HERMES_ESP32_001","readingId":4,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":26.8,"movingAverage":24.3,"status":"ATENCAO"},"humidity":{"value":72.1,"movingAverage":67.0,"status":"NORMAL"},"lightLevel":{"value":380,"status":"NORMAL"},"vibration":{"value":0.25,"status":"ATENCAO"}},"analysis":{"systemStatus":"ATENCAO","riskLevel":0.35,"nextMaintenance":"2024-12-19T14:00:00Z","statusDetail":"Temperatura elevada detectada"},"operationalStats":{"uptime":30000,"totalReadings":4,"avgTemperature":24.3,"avgHumidity":67.0}}
echo JSON_DATA: {"timestamp":1734123476000,"deviceId":"HERMES_ESP32_001","readingId":5,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":28.2,"movingAverage":25.1,"status":"ATENCAO"},"humidity":{"value":75.2,"movingAverage":68.6,"status":"ATENCAO"},"lightLevel":{"value":350,"status":"BAIXO"},"vibration":{"value":0.32,"status":"ATENCAO"}},"analysis":{"systemStatus":"ATENCAO","riskLevel":0.45,"nextMaintenance":"2024-12-19T12:00:00Z","statusDetail":"Multiplos sensores em atencao"},"operationalStats":{"uptime":35000,"totalReadings":5,"avgTemperature":25.1,"avgHumidity":68.6}}
echo JSON_DATA: {"timestamp":1734123481000,"deviceId":"HERMES_ESP32_001","readingId":6,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":31.2,"movingAverage":26.1,"status":"CRITICO"},"humidity":{"value":82.5,"movingAverage":71.1,"status":"CRITICO"},"lightLevel":{"value":280,"status":"BAIXO"},"vibration":{"value":0.48,"status":"CRITICO"}},"analysis":{"systemStatus":"CRITICO","riskLevel":0.85,"nextMaintenance":"2024-12-18T08:00:00Z","statusDetail":"Sistema em estado critico - intervencao necessaria"},"operationalStats":{"uptime":40000,"totalReadings":6,"avgTemperature":26.1,"avgHumidity":71.1}}
echo JSON_DATA: {"timestamp":1734123486000,"deviceId":"HERMES_ESP32_001","readingId":7,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":29.8,"movingAverage":26.6,"status":"ATENCAO"},"humidity":{"value":78.5,"movingAverage":72.3,"status":"ATENCAO"},"lightLevel":{"value":320,"status":"BAIXO"},"vibration":{"value":0.42,"status":"ATENCAO"}},"analysis":{"systemStatus":"ATENCAO","riskLevel":0.65,"nextMaintenance":"2024-12-19T10:00:00Z","statusDetail":"Condicoes melhorando gradualmente"},"operationalStats":{"uptime":45000,"totalReadings":7,"avgTemperature":26.6,"avgHumidity":72.3}}
echo JSON_DATA: {"timestamp":1734123491000,"deviceId":"HERMES_ESP32_001","readingId":8,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":27.1,"movingAverage":26.4,"status":"ATENCAO"},"humidity":{"value":74.2,"movingAverage":72.4,"status":"ATENCAO"},"lightLevel":{"value":360,"status":"NORMAL"},"vibration":{"value":0.35,"status":"ATENCAO"}},"analysis":{"systemStatus":"ATENCAO","riskLevel":0.55,"nextMaintenance":"2024-12-19T12:00:00Z","statusDetail":"Sistema ainda em atencao"},"operationalStats":{"uptime":50000,"totalReadings":8,"avgTemperature":26.4,"avgHumidity":72.4}}
echo JSON_DATA: {"timestamp":1734123496000,"deviceId":"HERMES_ESP32_001","readingId":9,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":25.1,"movingAverage":26.0,"status":"NORMAL"},"humidity":{"value":69.8,"movingAverage":71.8,"status":"NORMAL"},"lightLevel":{"value":410,"status":"NORMAL"},"vibration":{"value":0.22,"status":"NORMAL"}},"analysis":{"systemStatus":"NORMAL","riskLevel":0.25,"nextMaintenance":"2024-12-20T09:00:00Z","statusDetail":"Sistema retornando a normalidade"},"operationalStats":{"uptime":55000,"totalReadings":9,"avgTemperature":26.0,"avgHumidity":71.8}}
echo JSON_DATA: {"timestamp":1734123501000,"deviceId":"HERMES_ESP32_001","readingId":10,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":24.3,"movingAverage":25.7,"status":"NORMAL"},"humidity":{"value":66.5,"movingAverage":70.9,"status":"NORMAL"},"lightLevel":{"value":440,"status":"NORMAL"},"vibration":{"value":0.18,"status":"NORMAL"}},"analysis":{"systemStatus":"NORMAL","riskLevel":0.15,"nextMaintenance":"2024-12-20T10:00:00Z","statusDetail":"Operacao estavel"},"operationalStats":{"uptime":60000,"totalReadings":10,"avgTemperature":25.7,"avgHumidity":70.9}}
echo JSON_DATA: {"timestamp":1734123506000,"deviceId":"HERMES_ESP32_001","readingId":11,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":23.8,"movingAverage":25.3,"status":"NORMAL"},"humidity":{"value":64.2,"movingAverage":69.6,"status":"NORMAL"},"lightLevel":{"value":460,"status":"NORMAL"},"vibration":{"value":0.16,"status":"NORMAL"}},"analysis":{"systemStatus":"NORMAL","riskLevel":0.1,"nextMaintenance":"2024-12-20T10:00:00Z","statusDetail":"Todos os sistemas operacionais"},"operationalStats":{"uptime":65000,"totalReadings":11,"avgTemperature":25.3,"avgHumidity":69.6}}
echo JSON_DATA: {"timestamp":1734123511000,"deviceId":"HERMES_ESP32_001","readingId":12,"firmwareVersion":"v2.1.0","sensors":{"temperature":{"value":33.5,"movingAverage":26.2,"status":"CRITICO"},"humidity":{"value":85.2,"movingAverage":71.8,"status":"CRITICO"},"lightLevel":{"value":250,"status":"CRITICO"},"vibration":{"value":0.65,"status":"CRITICO"}},"analysis":{"systemStatus":"CRITICO","riskLevel":0.95,"nextMaintenance":"2024-12-17T06:00:00Z","statusDetail":"Alerta maximo - parada de emergencia recomendada"},"operationalStats":{"uptime":70000,"totalReadings":12,"avgTemperature":26.2,"avgHumidity":71.8}}
) > "%DADOS_DIR%\serial_output.log"

echo ✅ Dados simulados gerados com sucesso

:: ETAPA 4: Processar dados
echo 📊 ETAPA 4: Processando dados da simulacao...
if exist "processar_dados_simulacao.py" (
    python processar_dados_simulacao.py
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Dados processados com sucesso
    ) else (
        echo ⚠️  Aviso: Erro no processamento, mas continuando...
    )
) else (
    echo ⚠️  Arquivo processar_dados_simulacao.py nao encontrado, pulando processamento
)

:: ETAPA 5: Verificar dados
echo 🔍 ETAPA 5: Verificando dados estruturados...
if exist "%DADOS_DIR%\serial_output.log" (
    echo ✅ Arquivo de dados encontrado: serial_output.log
    
    findstr "JSON_DATA" "%DADOS_DIR%\serial_output.log" >nul
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Dados JSON validos detectados
    ) else (
        echo ⚠️  Dados JSON nao encontrados no log
    )
) else (
    echo ❌ Arquivo de dados nao encontrado!
)

:: ETAPA 6: Iniciar Dashboard
echo.
echo 🚀 ETAPA 6: Iniciando Dashboard BI...
echo 🌐 Dashboard sera aberto em: http://localhost:8501
echo.
echo ⚠️  Para parar o servidor, pressione Ctrl+C
echo.

:: Verificar se app.py existe
if exist "app.py" (
    echo ✅ Arquivo app.py encontrado
    echo 🚀 Iniciando Streamlit...
    python -m streamlit run app.py --server.port 8501 --server.headless false
) else (
    echo ❌ Arquivo app.py nao encontrado no diretorio analise_dados!
    echo 📁 Conteudo do diretorio atual:
    dir /b
    pause
)

echo.
echo 🏁 Execucao finalizada.
pause 