@echo off

echo.
echo [HERMES] Garantindo que todas as dependencias estao atualizadas...
pip install -r analise_dados/requirements.txt
echo.
echo [HERMES] Iniciando o Dashboard de Analise Preditiva...
echo [HERMES] A aplicacao sera aberta em seu navegador.
echo.
python -m streamlit run analise_dados/app.py 