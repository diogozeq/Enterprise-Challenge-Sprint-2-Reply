#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard BI - Hermes Reply IoT Analytics
Sistema de análise de dados IoT com Machine Learning e visualizações interativas
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import re
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import warnings
warnings.filterwarnings('ignore')

# === CONFIGURAÇÃO DA PÁGINA ===
st.set_page_config(
    page_title="Hermes Reply IoT Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === TEMA E CORES PERSONALIZADAS ===
CORES_TEMA = {
    'primaria': '#1f77b4',
    'secundaria': '#ff7f0e', 
    'sucesso': '#2ca02c',
    'alerta': '#d62728',
    'info': '#17becf',
    'fundo': '#f8f9fa',
    'texto': '#2c3e50'
}

# === CSS PERSONALIZADO PARA UX/UI OTIMIZADA PARA VIESES COGNITIVOS ===
st.markdown("""
<style>
    /* === REDUÇÃO DE CARGA COGNITIVA === */
    .main > div {
        padding-top: 1rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* === HIERARQUIA VISUAL CLARA === */
    .titulo-gradiente {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1.5rem;
        letter-spacing: -0.02em;
    }
    
    /* === CARDS COM AFFORDANCES VISUAIS === */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.8rem 1.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
        margin-bottom: 1.2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: rgba(255,255,255,0.3);
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 48px rgba(102, 126, 234, 0.4);
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0.8rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        font-size: 1.1rem;
        opacity: 0.95;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    /* === BOTÕES COM FEEDBACK VISUAL CLARO === */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 28px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* === SIDEBAR COM NAVEGAÇÃO INTUITIVA === */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 0 16px 16px 0;
    }
    
    /* === STATUS COM SEMÂNTICA VISUAL === */
    .status-normal {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(46, 204, 113, 0.3);
        display: inline-block;
        margin: 0.2rem;
    }
    
    .status-atencao {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(243, 156, 18, 0.3);
        display: inline-block;
        margin: 0.2rem;
    }
    
    .status-critico {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
        display: inline-block;
        margin: 0.2rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3); }
        50% { box-shadow: 0 4px 16px rgba(231, 76, 60, 0.6); }
        100% { box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3); }
    }
    
    /* === REDUÇÃO DE FADIGA VISUAL === */
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    /* === AGRUPAMENTO VISUAL === */
    .section-container {
        background: rgba(255,255,255,0.8);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    /* === FEEDBACK DE PROGRESSO === */
    .progress-indicator {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 4px;
        border-radius: 2px;
        margin: 1rem 0;
        animation: loading 2s ease-in-out infinite;
    }
    
    @keyframes loading {
        0% { transform: scaleX(0); }
        50% { transform: scaleX(1); }
        100% { transform: scaleX(0); }
    }
    
    /* === MICROINTERAÇÕES === */
    .element-container {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* === CONTRASTE E LEGIBILIDADE === */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .stMarkdown h2 {
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    /* === ALERTAS VISUAIS === */
    .alert-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #b8dacc;
        border-left: 5px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffeaa7;
        border-left: 5px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #f5c6cb;
        border-left: 5px solid #dc3545;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* === RESPONSIVIDADE === */
    @media (max-width: 768px) {
        .metric-card {
            padding: 1.2rem 1rem;
        }
        
        .metric-value {
            font-size: 2.2rem;
        }
        
        .titulo-gradiente {
            font-size: 2.2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

class HermesAnalytics:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.dados_path = os.path.normpath(os.path.join(self.base_path, '..', 'dados_simulacao'))
        
        # Inicializar session state para ML
        if 'modelo_treinado' not in st.session_state:
            st.session_state.modelo_treinado = False
        if 'modelo' not in st.session_state:
            st.session_state.modelo = None
        if 'label_encoder' not in st.session_state:
            st.session_state.label_encoder = None
        if 'metricas_modelo' not in st.session_state:
            st.session_state.metricas_modelo = None
        
    def carregar_dados_historicos(self):
        """Carrega dados históricos de todas as execuções"""
        arquivo_historico = os.path.join(self.dados_path, 'hermes_historico_completo.csv')
        
        if os.path.exists(arquivo_historico):
            try:
                df = pd.read_csv(arquivo_historico)
                df['timestamp_simulacao'] = pd.to_datetime(df['timestamp_simulacao'], unit='ms')
                df['timestamp_processamento'] = pd.to_datetime(df['timestamp_processamento'])
                return df
            except Exception as e:
                st.error(f"❌ Erro ao carregar dados históricos: {e}")
                return None
        else:
            st.warning("⚠️ Arquivo de dados históricos não encontrado. Execute uma simulação primeiro.")
            return None
    
    def listar_execucoes_disponiveis(self):
        """Lista todas as execuções disponíveis"""
        execucoes = []
        
        if os.path.exists(self.dados_path):
            for arquivo in os.listdir(self.dados_path):
                if arquivo.startswith('hermes_data_') and arquivo.endswith('.csv'):
                    execucao_id = arquivo.replace('hermes_data_', '').replace('.csv', '')
                    execucoes.append(execucao_id)
        
        return sorted(execucoes, reverse=True)
    
    def carregar_execucao_especifica(self, execucao_id):
        """Carrega dados de uma execução específica"""
        arquivo = os.path.join(self.dados_path, f'hermes_data_{execucao_id}.csv')
        
        if os.path.exists(arquivo):
            try:
                df = pd.read_csv(arquivo)
                df['timestamp_simulacao'] = pd.to_datetime(df['timestamp_simulacao'], unit='ms')
                df['timestamp_processamento'] = pd.to_datetime(df['timestamp_processamento'])
                return df
            except Exception as e:
                st.error(f"❌ Erro ao carregar execução {execucao_id}: {e}")
                return None
        return None
    
    def carregar_resumos_estatisticos(self):
        """Carrega resumos estatísticos de todas as execuções"""
        resumos = []
        
        if os.path.exists(self.dados_path):
            for arquivo in os.listdir(self.dados_path):
                if arquivo.startswith('hermes_resumo_') and arquivo.endswith('.csv'):
                    try:
                        df_resumo = pd.read_csv(os.path.join(self.dados_path, arquivo))
                        resumos.append(df_resumo.iloc[0].to_dict())
                    except Exception as e:
                        continue
        
        return pd.DataFrame(resumos) if resumos else None
    
    def criar_modelo_ml(self, df):
        """Cria e treina modelo de Machine Learning com validação robusta"""
        if df is None or len(df) < 10:
            st.error("❌ Dados insuficientes para treinar o modelo (mínimo 10 registros)")
            return False
            
        try:
            # Preparar features
            features = ['temperatura', 'umidade', 'luminosidade', 'vibracao']
            X = df[features].fillna(df[features].mean())
            
            # Verificar se há variabilidade nos dados
            if X.std().min() == 0:
                st.warning("⚠️ Alguns sensores têm valores constantes. Isso pode afetar a performance do modelo.")
            
            # Preparar target
            le = LabelEncoder()
            y = le.fit_transform(df['system_status'])
            
            # Verificar distribuição de classes
            unique_classes, class_counts = np.unique(y, return_counts=True)
            min_class_count = class_counts.min()
            
            if len(unique_classes) < 2:
                st.error("❌ É necessário pelo menos 2 classes diferentes de status para treinar o modelo")
                return False
            
            # Verificar se há classes com apenas 1 amostra
            if min_class_count < 2:
                st.warning("⚠️ Algumas classes têm poucas amostras. Usando split simples sem estratificação.")
                # Split sem estratificação para evitar erro
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.3, random_state=42
                )
            else:
                # Split com estratificação quando possível
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.3, random_state=42, stratify=y
                )
            
            # Treinar modelo
            modelo = RandomForestClassifier(
                n_estimators=100, 
                random_state=42,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2
            )
            modelo.fit(X_train, y_train)
            
            # Avaliar modelo
            y_pred = modelo.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            feature_importance = dict(zip(features, modelo.feature_importances_))
            
            # Salvar modelo
            modelo_path = os.path.join(self.dados_path, 'modelo_randomforest.joblib')
            joblib.dump(modelo, modelo_path)
            
            # Armazenar no session state
            st.session_state.modelo = modelo
            st.session_state.label_encoder = le
            st.session_state.metricas_modelo = {
                'accuracy': accuracy,
                'feature_importance': feature_importance,
                'classification_report': classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True),
                'n_samples': len(df),
                'n_features': len(features)
            }
            st.session_state.modelo_treinado = True
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro no treinamento do modelo: {e}")
            return False

    def criar_grafico_moderno(self, df, x, y, tipo='line', titulo='', cor=None):
        """Cria gráficos com design moderno e consistente"""
        if tipo == 'line':
            fig = px.line(df, x=x, y=y, title=titulo)
        elif tipo == 'bar':
            fig = px.bar(df, x=x, y=y, title=titulo)
        elif tipo == 'scatter':
            fig = px.scatter(df, x=x, y=y, title=titulo, color=cor)
        elif tipo == 'pie':
            fig = px.pie(df, values=y, names=x, title=titulo)
        
        # Aplicar tema moderno
        fig.update_layout(
            title_font_size=20,
            title_font_color=CORES_TEMA['texto'],
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial, sans-serif", size=12, color=CORES_TEMA['texto']),
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Estilizar eixos
        fig.update_xaxes(
            gridcolor='rgba(128,128,128,0.2)',
            showgrid=True,
            zeroline=False,
            tickangle=45
        )
        fig.update_yaxes(
            gridcolor='rgba(128,128,128,0.2)',
            showgrid=True,
            zeroline=False
        )
        
        return fig

def exibir_alerta_cognitivo(tipo, titulo, mensagem):
    """Exibe alertas otimizados para reduzir vieses cognitivos"""
    if tipo == "success":
        st.markdown(f"""
        <div class="alert-success">
            <strong>✅ {titulo}</strong><br>
            {mensagem}
        </div>
        """, unsafe_allow_html=True)
    elif tipo == "warning":
        st.markdown(f"""
        <div class="alert-warning">
            <strong>⚠️ {titulo}</strong><br>
            {mensagem}
        </div>
        """, unsafe_allow_html=True)
    elif tipo == "error":
        st.markdown(f"""
        <div class="alert-error">
            <strong>❌ {titulo}</strong><br>
            {mensagem}
        </div>
        """, unsafe_allow_html=True)

def exibir_metricas_principais(df):
    """Exibe métricas principais com cards otimizados para cognição"""
    # Calcular métricas com contexto
    total_registros = len(df)
    execucoes = df['execucao_id'].nunique() if 'execucao_id' in df.columns else 1
    temp_media = df['temperatura'].mean()
    umidade_media = df['umidade'].mean()
    
    # Determinar status das métricas para feedback visual
    temp_status = "🟢" if 20 <= temp_media <= 30 else "🟡" if 15 <= temp_media <= 35 else "🔴"
    umidade_status = "🟢" if 40 <= umidade_media <= 70 else "🟡" if 30 <= umidade_media <= 80 else "🔴"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📊 Total de Registros</div>
            <div class="metric-value">{total_registros:,}</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">
                {execucoes} execução{'ões' if execucoes > 1 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        duracao_estimada = total_registros * 5 / 60  # 5s por registro
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏱️ Duração Total</div>
            <div class="metric-value">{duracao_estimada:.1f}min</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">
                ~{total_registros * 5}s de dados
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🌡️ Temperatura {temp_status}</div>
            <div class="metric-value">{temp_media:.1f}°C</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">
                Faixa: {df['temperatura'].min():.1f}° - {df['temperatura'].max():.1f}°
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💧 Umidade {umidade_status}</div>
            <div class="metric-value">{umidade_media:.1f}%</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">
                Faixa: {df['umidade'].min():.1f}% - {df['umidade'].max():.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

def exibir_indicador_progresso():
    """Exibe indicador de progresso para reduzir ansiedade"""
    st.markdown('<div class="progress-indicator"></div>', unsafe_allow_html=True)

def exibir_resumo_inteligente(df):
    """Exibe resumo inteligente para reduzir carga cognitiva"""
    status_counts = df['system_status'].value_counts()
    status_dominante = status_counts.index[0]
    porcentagem_dominante = (status_counts.iloc[0] / len(df)) * 100
    
    # Análise de tendência
    if 'timestamp_simulacao' in df.columns:
        df_sorted = df.sort_values('timestamp_simulacao')
        temp_inicial = df_sorted['temperatura'].iloc[:3].mean()
        temp_final = df_sorted['temperatura'].iloc[-3:].mean()
        tendencia_temp = "📈 Subindo" if temp_final > temp_inicial + 1 else "📉 Descendo" if temp_final < temp_inicial - 1 else "➡️ Estável"
    else:
        tendencia_temp = "➡️ Estável"
    
    st.markdown(f"""
    <div class="section-container">
        <h3>🧠 Resumo Inteligente</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
                <strong>Status Predominante:</strong><br>
                <span class="status-{status_dominante.lower()}">{status_dominante}</span>
                <small style="color: #666;"> ({porcentagem_dominante:.1f}% dos dados)</small>
            </div>
            <div>
                <strong>Tendência de Temperatura:</strong><br>
                {tendencia_temp}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    analytics = HermesAnalytics()
    
    # Título principal com gradiente
    st.markdown('<h1 class="titulo-gradiente">🚀 Hermes Reply IoT Analytics</h1>', unsafe_allow_html=True)
    st.markdown("**Sistema de Análise de Dados IoT com Machine Learning e Predição Inteligente**")
    
    # Sidebar com design moderno
    st.sidebar.markdown("## 📊 Painel de Controle")
    
    modo_visualizacao = st.sidebar.selectbox(
        "🎯 Modo de Visualização",
        ["📈 Dados Históricos Completos", "🔍 Execução Específica", "📋 Resumos Estatísticos"],
        help="Selecione o tipo de análise que deseja realizar"
    )
    
    # === MODO: DADOS HISTÓRICOS COMPLETOS ===
    if modo_visualizacao == "📈 Dados Históricos Completos":
        df = analytics.carregar_dados_historicos()
        
        if df is not None:
            exibir_alerta_cognitivo("success", "Dados Carregados", 
                f"Sistema carregou {len(df):,} registros de {df['execucao_id'].nunique()} execuções com sucesso")
            
            # Resumo inteligente para reduzir carga cognitiva
            exibir_resumo_inteligente(df)
            
            # Filtros avançados
            with st.sidebar.expander("🔧 Filtros Avançados", expanded=True):
                execucoes_disponiveis = df['execucao_id'].unique()
                execucoes_selecionadas = st.multiselect(
                    "📅 Execuções",
                    execucoes_disponiveis,
                    default=execucoes_disponiveis[-3:] if len(execucoes_disponiveis) > 3 else execucoes_disponiveis,
                    help="Selecione as execuções para análise"
                )
                
                status_selecionados = st.multiselect(
                    "🚨 Status do Sistema",
                    df['system_status'].unique(),
                    default=df['system_status'].unique(),
                    help="Filtre por status específicos"
                )
                
                # Filtro de data
                data_min = df['timestamp_simulacao'].min().date()
                data_max = df['timestamp_simulacao'].max().date()
                data_range = st.date_input(
                    "📅 Período",
                    value=(data_min, data_max),
                    min_value=data_min,
                    max_value=data_max,
                    help="Selecione o período para análise"
                )
            
            # Aplicar filtros
            if execucoes_selecionadas:
                df_filtrado = df[df['execucao_id'].isin(execucoes_selecionadas)]
            else:
                df_filtrado = df
            
            df_filtrado = df_filtrado[df_filtrado['system_status'].isin(status_selecionados)]
            
            if len(data_range) == 2:
                df_filtrado = df_filtrado[
                    (df_filtrado['timestamp_simulacao'].dt.date >= data_range[0]) &
                    (df_filtrado['timestamp_simulacao'].dt.date <= data_range[1])
                ]
            
            # Métricas principais
            exibir_metricas_principais(df_filtrado)
            
            # Análise temporal
            st.markdown("## 📈 Análise Temporal dos Sensores")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_temp = analytics.criar_grafico_moderno(
                    df_filtrado, 
                    'timestamp_simulacao', 
                    'temperatura',
                    tipo='line',
                    titulo="🌡️ Temperatura ao Longo do Tempo"
                )
                if 'execucao_id' in df_filtrado.columns:
                    fig_temp.update_traces(line=dict(color=CORES_TEMA['primaria']))
                st.plotly_chart(fig_temp, use_container_width=True)
            
            with col2:
                fig_umidade = analytics.criar_grafico_moderno(
                    df_filtrado, 
                    'timestamp_simulacao', 
                    'umidade',
                    tipo='line',
                    titulo="💧 Umidade ao Longo do Tempo"
                )
                if 'execucao_id' in df_filtrado.columns:
                    fig_umidade.update_traces(line=dict(color=CORES_TEMA['secundaria']))
                st.plotly_chart(fig_umidade, use_container_width=True)
            
            # Análise de status
            st.markdown("## 🚨 Análise de Status do Sistema")
            
            col1, col2 = st.columns(2)
            
            with col1:
                status_counts = df_filtrado['system_status'].value_counts()
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="📊 Distribuição de Status",
                    color_discrete_sequence=['#2ecc71', '#f39c12', '#e74c3c']
                )
                fig_status.update_layout(
                    title_font_size=20,
                    font=dict(family="Arial, sans-serif", size=12),
                    showlegend=True
                )
                st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                numeric_cols = ['temperatura', 'umidade', 'luminosidade', 'vibracao']
                corr_matrix = df_filtrado[numeric_cols].corr()
                
                fig_corr = px.imshow(
                    corr_matrix,
                    title="🔗 Matriz de Correlação dos Sensores",
                    color_continuous_scale="RdBu",
                    aspect="auto"
                )
                fig_corr.update_layout(
                    title_font_size=20,
                    font=dict(family="Arial, sans-serif", size=12)
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            
            # Machine Learning Section
            st.markdown("## 🤖 Análise de Machine Learning")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.button("🚀 Treinar Modelo de Predição", help="Treina um modelo RandomForest para predição de status"):
                    exibir_indicador_progresso()
                    with st.spinner("🔄 Treinando modelo de Machine Learning..."):
                        sucesso = analytics.criar_modelo_ml(df_filtrado)
                        
                        if sucesso:
                            exibir_alerta_cognitivo("success", "Modelo Treinado", 
                                "Modelo RandomForest treinado com sucesso e pronto para predições!")
                            st.balloons()
                        else:
                            exibir_alerta_cognitivo("error", "Falha no Treinamento", 
                                "Não foi possível treinar o modelo. Verifique se há dados suficientes e classes balanceadas.")
            
            with col2:
                if st.session_state.modelo_treinado and st.session_state.metricas_modelo:
                    st.info("ℹ️ Modelo treinado e pronto para uso!")
            
            # Exibir resultados do modelo se disponível
            if st.session_state.modelo_treinado and st.session_state.metricas_modelo:
                st.markdown("### 📊 Resultados do Modelo")
                
                metricas = st.session_state.metricas_modelo
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "🎯 Acurácia do Modelo", 
                        f"{metricas['accuracy']:.2%}",
                        help="Percentual de predições corretas"
                    )
                
                with col2:
                    st.metric(
                        "📊 Amostras de Treino", 
                        f"{metricas['n_samples']:,}",
                        help="Número total de amostras utilizadas"
                    )
                
                with col3:
                    st.metric(
                        "🔧 Features Utilizadas", 
                        metricas['n_features'],
                        help="Número de características dos sensores"
                    )
                
                # Gráfico de importância das features
                col1, col2 = st.columns(2)
                
                with col1:
                    importance_df = pd.DataFrame(
                        list(metricas['feature_importance'].items()),
                        columns=['Sensor', 'Importância']
                    ).sort_values('Importância', ascending=True)
                    
                    fig_importance = px.bar(
                        importance_df,
                        x='Importância',
                        y='Sensor',
                        orientation='h',
                        title="🎯 Importância dos Sensores",
                        color='Importância',
                        color_continuous_scale='viridis'
                    )
                    fig_importance.update_layout(
                        title_font_size=18,
                        font=dict(family="Arial, sans-serif", size=12),
                        showlegend=False
                    )
                    st.plotly_chart(fig_importance, use_container_width=True)
                
                with col2:
                    st.markdown("#### 📈 Relatório de Classificação")
                    
                    for classe, metricas_classe in metricas['classification_report'].items():
                        if isinstance(metricas_classe, dict) and classe not in ['accuracy', 'macro avg', 'weighted avg']:
                            with st.expander(f"📋 Classe: {classe}"):
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("Precisão", f"{metricas_classe.get('precision', 0):.2%}")
                                with col_b:
                                    st.metric("Recall", f"{metricas_classe.get('recall', 0):.2%}")
                                with col_c:
                                    st.metric("F1-Score", f"{metricas_classe.get('f1-score', 0):.2%}")
            
            # Dados detalhados
            with st.expander("📋 Dados Detalhados", expanded=False):
                st.dataframe(
                    df_filtrado.sort_values('timestamp_simulacao', ascending=False),
                    use_container_width=True
                )
    
    # === MODO: EXECUÇÃO ESPECÍFICA ===
    elif modo_visualizacao == "🔍 Execução Específica":
        execucoes = analytics.listar_execucoes_disponiveis()
        
        if execucoes:
            execucao_selecionada = st.sidebar.selectbox(
                "📅 Selecionar Execução", 
                execucoes,
                help="Escolha uma execução específica para análise detalhada"
            )
            
            df = analytics.carregar_execucao_especifica(execucao_selecionada)
            
            if df is not None:
                st.success(f"✅ Execução {execucao_selecionada} carregada: {len(df):,} registros")
                
                # Métricas da execução
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Registros", f"{len(df):,}")
                with col2:
                    duracao = (df['timestamp_simulacao'].max() - df['timestamp_simulacao'].min()).total_seconds()
                    st.metric("⏱️ Duração", f"{duracao:.1f}s")
                with col3:
                    st.metric("🌡️ Temp. Média", f"{df['temperatura'].mean():.1f}°C")
                with col4:
                    st.metric("💧 Umidade Média", f"{df['umidade'].mean():.1f}%")
                
                # Análise da execução
                st.markdown("## 📈 Análise da Execução")
                
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('🌡️ Temperatura', '💧 Umidade', '💡 Luminosidade', '📳 Vibração'),
                    vertical_spacing=0.1,
                    horizontal_spacing=0.1
                )
                
                # Cores modernas para cada sensor
                cores = [CORES_TEMA['primaria'], CORES_TEMA['secundaria'], CORES_TEMA['sucesso'], CORES_TEMA['alerta']]
                
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp_simulacao'], 
                        y=df['temperatura'], 
                        name='Temperatura',
                        line=dict(color=cores[0], width=3)
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp_simulacao'], 
                        y=df['umidade'], 
                        name='Umidade',
                        line=dict(color=cores[1], width=3)
                    ),
                    row=1, col=2
                )
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp_simulacao'], 
                        y=df['luminosidade'], 
                        name='Luminosidade',
                        line=dict(color=cores[2], width=3)
                    ),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp_simulacao'], 
                        y=df['vibracao'], 
                        name='Vibração',
                        line=dict(color=cores[3], width=3)
                    ),
                    row=2, col=2
                )
                
                fig.update_layout(
                    height=600, 
                    title_text="📊 Sensores ao Longo da Execução",
                    title_font_size=20,
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                # Atualizar eixos X para todas as subplots
                for i in range(1, 3):
                    for j in range(1, 3):
                        fig.update_xaxes(
                            gridcolor='rgba(128,128,128,0.2)',
                            showgrid=True,
                            row=i, col=j
                        )
                        fig.update_yaxes(
                            gridcolor='rgba(128,128,128,0.2)',
                            showgrid=True,
                            row=i, col=j
                        )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Timeline de status
                st.markdown("## 🚨 Timeline de Status")
                fig_status = px.scatter(
                    df, 
                    x='timestamp_simulacao', 
                    y='system_status',
                    color='system_status',
                    title="📈 Evolução do Status do Sistema",
                    color_discrete_map={
                        'NORMAL': '#2ecc71',
                        'ATENÇÃO': '#f39c12', 
                        'ATENCAO': '#f39c12',
                        'CRÍTICO': '#e74c3c',
                        'CRITICO': '#e74c3c'
                    }
                )
                fig_status.update_layout(
                    title_font_size=20,
                    font=dict(family="Arial, sans-serif", size=12),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                fig_status.update_xaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)
                fig_status.update_yaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)
                st.plotly_chart(fig_status, use_container_width=True)
                
                # Dados da execução
                with st.expander("📋 Dados da Execução", expanded=False):
                    st.dataframe(df, use_container_width=True)
        else:
            st.warning("⚠️ Nenhuma execução encontrada. Execute uma simulação primeiro.")
    
    # === MODO: RESUMOS ESTATÍSTICOS ===
    elif modo_visualizacao == "📋 Resumos Estatísticos":
        df_resumos = analytics.carregar_resumos_estatisticos()
        
        if df_resumos is not None:
            st.success(f"✅ {len(df_resumos):,} resumos estatísticos carregados")
            
            # Métricas gerais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🔄 Total de Execuções", f"{len(df_resumos):,}")
            with col2:
                st.metric("📊 Total de Registros", f"{df_resumos['total_registros'].sum():,}")
            with col3:
                st.metric("🌡️ Temp. Média Geral", f"{df_resumos['temp_media'].mean():.1f}°C")
            with col4:
                st.metric("💧 Umidade Média Geral", f"{df_resumos['umidade_media'].mean():.1f}%")
            
            # Evolução das execuções
            st.markdown("## 📈 Evolução das Execuções")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_temp_evolucao = px.line(
                    df_resumos,
                    x='execucao_id',
                    y='temp_media',
                    title="🌡️ Evolução da Temperatura Média",
                    markers=True
                )
                fig_temp_evolucao.update_layout(
                    title_font_size=18,
                    font=dict(family="Arial, sans-serif", size=12),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_tickangle=45
                )
                fig_temp_evolucao.update_traces(line=dict(color=CORES_TEMA['primaria'], width=3))
                fig_temp_evolucao.update_xaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)
                fig_temp_evolucao.update_yaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)
                st.plotly_chart(fig_temp_evolucao, use_container_width=True)
            
            with col2:
                # Verificar se as colunas existem
                status_cols = []
                for col in ['status_normal', 'status_atencao', 'status_critico']:
                    if col in df_resumos.columns:
                        status_cols.append(col)
                
                if status_cols:
                    fig_status_evolucao = px.bar(
                        df_resumos,
                        x='execucao_id',
                        y=status_cols,
                        title="📊 Distribuição de Status por Execução",
                        color_discrete_sequence=['#2ecc71', '#f39c12', '#e74c3c']
                    )
                    fig_status_evolucao.update_layout(
                        title_font_size=18,
                        font=dict(family="Arial, sans-serif", size=12),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_tickangle=45
                    )
                    fig_status_evolucao.update_xaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)
                    fig_status_evolucao.update_yaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)
                    st.plotly_chart(fig_status_evolucao, use_container_width=True)
                else:
                    st.info("ℹ️ Dados de status não disponíveis nos resumos")
            
            # Resumos detalhados
            with st.expander("📋 Resumos Detalhados", expanded=False):
                st.dataframe(
                    df_resumos.sort_values('execucao_id', ascending=False),
                    use_container_width=True
                )
        else:
            st.warning("⚠️ Nenhum resumo estatístico encontrado. Execute uma simulação primeiro.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #7f8c8d; padding: 20px;'>
            🚀 <strong>Hermes Reply IoT Analytics</strong> | 
            Desenvolvido com ❤️ usando Streamlit & Plotly | 
            © 2024 FIAP Challenge
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 