# -*- coding: utf-8 -*-
"""
Autor: Diogo L. Zequini Pinto
Projeto: Hermes Reply - Challenge Sprint 2
Dashboard de BI Interativo para análise de dados e modelagem preditiva a partir de logs de telemetria IoT.
"""

import streamlit as st
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report
import joblib

# Configuração da página
st.set_page_config(
    page_title="HERMES Reply - Dashboard de Análise Preditiva",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

class HermesReplyDataAnalyzer:
    """
    Classe para encapsular todo o pipeline de análise de dados,
    desde a ingestão do log até a geração de relatórios e modelos.
    """
    def __init__(self, log_file='dados_simulacao/serial_output.log'):
        self.log_file = log_file
        self.data = []
        self.df = None

    def extract_json_data(self):
        """
        Extrai payloads JSON do arquivo de log serial.
        CAPA-PY-002: Remove st.error() e lança exceção para tratamento na interface.
        """
        if not os.path.exists(self.log_file):
            raise FileNotFoundError(f"Arquivo de log não encontrado: {self.log_file}")
        
        pattern = re.compile(r"JSON_DATA:\s*({.*})")
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    try:
                        data_json = json.loads(match.group(1))
                        # Achata o JSON aninhado
                        flat = {
                            'timestamp': data_json.get('timestamp'),
                            'readingId': data_json.get('readingId'),
                            'temperature': data_json['sensors']['temperature']['value'],
                            'temperatureMA': data_json['sensors']['temperature'].get('movingAverage', data_json['sensors']['temperature']['value']),
                            'humidity': data_json['sensors']['humidity']['value'],
                            'humidityMA': data_json['sensors']['humidity'].get('movingAverage', data_json['sensors']['humidity']['value']),
                            'light': data_json['sensors']['lightLevel']['value'],
                            'vibration': data_json['sensors']['vibration']['value'],
                            'systemStatus': data_json['analysis']['systemStatus']
                        }
                        self.data.append(flat)
                    except Exception as e:
                        # CAPA-PY-002: Não usa st.error(), apenas lança exceção
                        raise ValueError(f"Erro ao parsear JSON: {e}")
        return len(self.data)

    def create_dataframe(self):
        """Cria DataFrame e adiciona features"""
        if not self.data:
            self.extract_json_data()
        self.df = pd.DataFrame(self.data)
        self.df['datetime'] = pd.to_datetime(self.df['timestamp'], unit='ms')
        self.df['time_minutes'] = (self.df['timestamp'] - self.df['timestamp'].min()) / 60000
        
        # === CAPA-PY-001: CORREÇÃO DA FEATURE ENGINEERING ===
        # Janela de 10 minutos com leituras a cada 5 segundos = 120 leituras (10*60/5 = 120)
        self.df['Rolling_Std_Dev_Vibration_10min'] = self.df['vibration'].rolling(window=120, min_periods=1).std()
        self.df['Temp_x_Vibration_Interaction'] = self.df['temperature'] * self.df['vibration']
        
        return self.df

    def generate_comprehensive_analysis(self):
        """Gera análise estatística completa dos dados"""
        if self.df is None:
            self.create_dataframe()
        
        analysis = {
            'total_records': len(self.df),
            'temp_stats': {
                'mean': self.df['temperature'].mean(),
                'std': self.df['temperature'].std(),
                'min': self.df['temperature'].min(),
                'max': self.df['temperature'].max()
            },
            'humidity_stats': {
                'mean': self.df['humidity'].mean(),
                'std': self.df['humidity'].std(),
                'min': self.df['humidity'].min(),
                'max': self.df['humidity'].max()
            },
            'light_stats': {
                'mean': self.df['light'].mean(),
                'std': self.df['light'].std()
            },
            'vibration_stats': {
                'mean': self.df['vibration'].mean(),
                'std': self.df['vibration'].std()
            },
            'status_distribution': self.df['systemStatus'].value_counts().to_dict(),
            'anomalies': {
                'temp_out_of_range': len(self.df[(self.df['temperature'] < 15) | (self.df['temperature'] > 35)]),
                'humidity_out_of_range': len(self.df[(self.df['humidity'] < 30) | (self.df['humidity'] > 70)])
            },
            'correlations': {
                'temp_humidity': self.df['temperature'].corr(self.df['humidity']),
                'vibration_temp': self.df['vibration'].corr(self.df['temperature'])
            }
        }
        
        return analysis

    def plot_sensor_timeline(self):
        """Gráfico temporal dos sensores"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('HERMES REPLY - Monitoramento Temporal de Sensores IoT', fontsize=16, fontweight='bold')
        
        # Temperatura
        axes[0,0].plot(self.df['time_minutes'], self.df['temperature'], 'o-', color='red', alpha=0.7)
        axes[0,0].axhspan(15, 35, alpha=0.2, color='green', label='Range Normal')
        axes[0,0].set_title('Temperatura (°C)')
        axes[0,0].set_ylabel('Temperatura (°C)')
        axes[0,0].grid(True, alpha=0.3)
        axes[0,0].legend()
        
        # Umidade
        axes[0,1].plot(self.df['time_minutes'], self.df['humidity'], 'o-', color='blue', alpha=0.7)
        axes[0,1].axhspan(30, 70, alpha=0.2, color='green', label='Range Normal')
        axes[0,1].set_title('Umidade (%)')
        axes[0,1].set_ylabel('Umidade (%)')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].legend()
        
        # Luminosidade
        axes[1,0].plot(self.df['time_minutes'], self.df['light'], 'o-', color='orange', alpha=0.7)
        axes[1,0].axhspan(200, 800, alpha=0.2, color='green', label='Range Normal')
        axes[1,0].set_title('Luminosidade (lux)')
        axes[1,0].set_ylabel('Luminosidade')
        axes[1,0].set_xlabel('Tempo (minutos)')
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].legend()
        
        # Vibração
        axes[1,1].plot(self.df['time_minutes'], self.df['vibration'], 'o-', color='purple', alpha=0.7)
        axes[1,1].axhline(y=500, color='red', linestyle='--', alpha=0.5, label='Limite Crítico')
        axes[1,1].set_title('Vibração (intensidade)')
        axes[1,1].set_ylabel('Vibração')
        axes[1,1].set_xlabel('Tempo (minutos)')
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].legend()
        
        plt.tight_layout()
        return fig

    def plot_status_analysis(self):
        """Gráfico de análise de status do sistema"""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('HERMES REPLY - Análise de Status do Sistema', fontsize=16, fontweight='bold')
        
        # Distribuição de status
        status_counts = self.df['systemStatus'].value_counts()
        colors = {'NORMAL': 'green', 'ATENÇÃO': 'orange', 'CRÍTICO': 'red'}
        
        # Gráfico de pizza
        axes[0].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', 
                   colors=[colors.get(x, 'gray') for x in status_counts.index])
        axes[0].set_title('Distribuição de Status do Sistema')
        
        # Timeline de status
        status_numeric = self.df['systemStatus'].map({'NORMAL': 0, 'ATENÇÃO': 1, 'CRÍTICO': 2})
        scatter = axes[1].scatter(self.df['time_minutes'], status_numeric, 
                                c=status_numeric, cmap='RdYlGn_r', s=50, alpha=0.7)
        axes[1].set_yticks([0, 1, 2])
        axes[1].set_yticklabels(['NORMAL', 'ATENÇÃO', 'CRÍTICO'])
        axes[1].set_xlabel('Tempo (minutos)')
        axes[1].set_ylabel('Status do Sistema')
        axes[1].set_title('Evolução do Status ao Longo do Tempo')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig

    def plot_correlation_heatmap(self):
        """Mapa de calor das correlações entre sensores"""
        fig, ax = plt.subplots(figsize=(10, 8))
        correlation = self.df[['temperature', 'humidity', 'light', 'vibration']].corr()
        
        sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0, 
                   square=True, fmt='.3f', cbar_kws={'label': 'Correlação'}, ax=ax)
        
        ax.set_title('HERMES REPLY - Mapa de Correlação entre Sensores', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig

    def train_predictive_model(self):
        """Treina modelo de classificação RandomForest para prever systemStatus"""
        if self.df is None:
            self.create_dataframe()
        
        feature_cols = [
            'temperature', 'temperatureMA', 'humidity', 'humidityMA', 'light', 'vibration',
            'Rolling_Std_Dev_Vibration_10min', 'Temp_x_Vibration_Interaction'
        ]
        X = self.df[feature_cols].fillna(0)
        y = self.df['systemStatus']
        y_encoded = y.map({'NORMAL':0, 'ATENÇÃO':1, 'CRÍTICO':2})
        
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
        clf = RandomForestClassifier(n_estimators=200, random_state=42)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        
        # Definir todos os rótulos de classe possíveis
        all_class_labels = [0, 1, 2] # NORMAL, ATENÇÃO, CRÍTICO
        display_names = ['NORMAL', 'ATENÇÃO', 'CRÍTICO']

        cm = confusion_matrix(y_test, y_pred, labels=all_class_labels)
        
        # Matriz de Confusão
        fig_cm, ax_cm = plt.subplots(figsize=(8, 6))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=display_names)
        disp.plot(cmap='Blues', ax=ax_cm)
        ax_cm.set_title('Matriz de Confusão - Modelo Preditivo')
        
        # Feature importance
        importances = pd.Series(clf.feature_importances_, index=feature_cols).sort_values(ascending=False)
        fig_fi, ax_fi = plt.subplots(figsize=(10,6))
        sns.barplot(x=importances, y=importances.index, ax=ax_fi)
        ax_fi.set_title('Importância das Features')
        ax_fi.set_xlabel('Importância')
        plt.tight_layout()
        
        # Salva modelo
        joblib.dump(clf, 'dados_simulacao/modelo_randomforest.joblib')
        
        return fig_cm, fig_fi, clf, cm

# Interface do usuário Streamlit
def main():
    st.title("🏭 HERMES Reply - Dashboard de Análise Preditiva IoT")
    st.markdown("**Autor:** Diogo Leite Zequini Pinto | **RM:** 565535")
    
    # Sidebar
    st.sidebar.header("🔧 Controles do Dashboard")
    st.sidebar.markdown("---")
    
    # Botão para carregar dados
    if st.sidebar.button("📊 Carregar e Processar Dados", type="primary"):
        with st.spinner("Carregando dados do log serial..."):
            try:
                analyzer = HermesReplyDataAnalyzer()
                records_count = analyzer.extract_json_data()
                
                if records_count > 0:
                    df = analyzer.create_dataframe()
                    analysis = analyzer.generate_comprehensive_analysis()
                    
                    # Armazenar no session_state
                    st.session_state.analyzer = analyzer
                    st.session_state.df = df
                    st.session_state.analysis = analysis
                    st.session_state.data_loaded = True
                    
                    st.sidebar.success(f"✅ {records_count} registros carregados!")
                else:
                    st.sidebar.error("❌ Nenhum dado encontrado no log serial!")
                    
            # === CAPA-PY-002: TRATAMENTO DE ERRO NA INTERFACE ===
            except FileNotFoundError as e:
                st.sidebar.error(f"❌ Arquivo de log não encontrado! Execute a simulação Wokwi primeiro.")
                st.error(f"**Erro de Arquivo:** {e}")
            except ValueError as e:
                st.sidebar.error(f"❌ Erro ao processar dados JSON!")
                st.error(f"**Erro de Processamento:** {e}")
            except Exception as e:
                st.sidebar.error(f"❌ Erro inesperado ao carregar dados!")
                st.error(f"**Erro Geral:** {e}")
    
    # Verificar se os dados foram carregados
    if 'data_loaded' not in st.session_state:
        st.info("👈 Use o botão na barra lateral para carregar os dados da simulação IoT.")
        st.markdown("""
        ### 📋 Instruções:
        1. **Execute a simulação Wokwi** para gerar o arquivo `dados_simulacao/serial_output.log`
        2. **Clique em \"Carregar e Processar Dados\"** na barra lateral
        3. **Explore as abas** para visualizar as análises interativas
        """)
        return
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Visão Geral", "🔍 Análise de Sensores", "🤖 Análise Preditiva", "📊 Dados Brutos"])
    
    analyzer = st.session_state.analyzer
    df = st.session_state.df
    analysis = st.session_state.analysis
    
    with tab1:
        st.header("📈 Visão Geral do Sistema")
        
        # KPIs principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Total de Registros",
                value=analysis['total_records']
            )
        
        with col2:
            st.metric(
                label="🌡️ Temperatura Média",
                value=f"{analysis['temp_stats']['mean']:.1f}°C",
                delta=f"±{analysis['temp_stats']['std']:.1f}"
            )
        
        with col3:
            st.metric(
                label="💧 Umidade Média", 
                value=f"{analysis['humidity_stats']['mean']:.1f}%",
                delta=f"±{analysis['humidity_stats']['std']:.1f}"
            )
        
        with col4:
            status_critico = analysis['status_distribution'].get('CRÍTICO', 0)
            st.metric(
                label="⚠️ Alertas Críticos",
                value=status_critico,
                delta=f"{(status_critico/analysis['total_records']*100):.1f}% do total"
            )
        
        st.markdown("---")
        
        # Distribuição de Status
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚨 Distribuição de Status")
            status_df = pd.DataFrame(list(analysis['status_distribution'].items()), 
                                   columns=['Status', 'Quantidade'])
            st.dataframe(status_df, use_container_width=True)
        
        with col2:
            st.subheader("🔗 Correlações Principais")
            if not np.isnan(analysis['correlations']['temp_humidity']):
                st.info(f"**Temperatura x Umidade:** {analysis['correlations']['temp_humidity']:.3f}")
            else:
                st.info("**Temperatura x Umidade:** Dados insuficientes para correlação.")

            if not np.isnan(analysis['correlations']['vibration_temp']):
                st.info(f"**Vibração x Temperatura:** {analysis['correlations']['vibration_temp']:.3f}")
            else:
                st.info("**Vibração x Temperatura:** Dados insuficientes para correlação.")
        
        # Anomalias
        st.subheader("🚨 Detecção de Anomalias")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="🌡️ Temperatura Fora do Range (15-35°C)",
                value=analysis['anomalies']['temp_out_of_range']
            )
        
        with col2:
            st.metric(
                label="💧 Umidade Fora do Range (30-70%)",
                value=analysis['anomalies']['humidity_out_of_range']
            )
    
    with tab2:
        st.header("🔍 Análise Detalhada de Sensores")
        
        # Gráfico temporal
        st.subheader("📈 Monitoramento Temporal")
        fig_timeline = analyzer.plot_sensor_timeline()
        st.pyplot(fig_timeline)
        
        # Análise de status
        st.subheader("📊 Análise de Status do Sistema")
        fig_status = analyzer.plot_status_analysis()
        st.pyplot(fig_status)
        
        # Correlações
        st.subheader("🔗 Mapa de Correlações")
        fig_corr = analyzer.plot_correlation_heatmap()
        st.pyplot(fig_corr)
    
    with tab3:
        st.header("🤖 Análise Preditiva com Machine Learning")
        
        st.info("**CAPA-PY-001 Implementado:** A feature 'Rolling_Std_Dev_Vibration_10min' agora usa uma janela de 120 leituras (10 minutos reais).")
        
        if st.button("🚀 Treinar Modelo Preditivo", type="primary"):
            with st.spinner("Treinando modelo RandomForest..."):
                fig_cm, fig_fi, model, cm = analyzer.train_predictive_model()

                # Armazena resultados no session_state para persistir entre reruns
                st.session_state.model_trained = True
                st.session_state.fig_cm = fig_cm
                st.session_state.fig_fi = fig_fi
                st.session_state.model_path = "dados_simulacao/modelo_randomforest.joblib"

        # Exibe resultados se o modelo já foi treinado anteriormente
        if 'model_trained' in st.session_state and st.session_state.model_trained:
            st.success("✅ Modelo treinado com sucesso!")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Matriz de Confusão")
                st.pyplot(st.session_state.fig_cm)

            with col2:
                st.subheader("🎯 Importância das Features")
                st.pyplot(st.session_state.fig_fi)

            st.info(f"💾 Modelo salvo em: `{st.session_state.model_path}`")
    
    with tab4:
        st.header("📊 Dados Brutos")
        st.subheader("🔍 DataFrame Completo")
        st.dataframe(df, use_container_width=True)
        
        st.subheader("📈 Estatísticas Descritivas")
        st.dataframe(df.describe(), use_container_width=True)

if __name__ == "__main__":
    main() 