#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador de Dados de Simulação Hermes Reply
Processa dados JSON da simulação Wokwi e salva em formato estruturado para BI
"""

import json
import pandas as pd
import re
import os
from datetime import datetime
import time

class ProcessadorDadosSimulacao:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.dados_simulacao_dir = os.path.normpath(os.path.join(self.base_path, '..', 'dados_simulacao'))
        self.log_file = os.path.join(self.dados_simulacao_dir, 'serial_output.log')
        self.timestamp_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def extrair_dados_json(self):
        """Extrai e processa dados JSON do log da simulação"""
        dados_processados = []
        
        # Espera um pouco para garantir que o arquivo seja gravado
        time.sleep(2)
        
        if not os.path.exists(self.log_file):
            print(f"[ERRO] Arquivo de log não encontrado: {self.log_file}")
            return dados_processados
            
        pattern = re.compile(r"JSON_DATA:\s*({.*})")
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for linha in f:
                match = pattern.search(linha)
                if match:
                    try:
                        data_json = json.loads(match.group(1))
                        
                        # Estrutura dados para análise
                        registro = {
                            'timestamp_simulacao': data_json.get('timestamp'),
                            'timestamp_processamento': datetime.now().isoformat(),
                            'execucao_id': self.timestamp_execucao,
                            'device_id': data_json.get('deviceId'),
                            'reading_id': data_json.get('readingId'),
                            'firmware_version': data_json.get('firmwareVersion'),
                            
                            # Dados dos sensores
                            'temperatura': data_json['sensors']['temperature']['value'],
                            'temperatura_media_movel': data_json['sensors']['temperature'].get('movingAverage'),
                            'temperatura_status': data_json['sensors']['temperature']['status'],
                            
                            'umidade': data_json['sensors']['humidity']['value'],
                            'umidade_media_movel': data_json['sensors']['humidity'].get('movingAverage'),
                            'umidade_status': data_json['sensors']['humidity']['status'],
                            
                            'luminosidade': data_json['sensors']['lightLevel']['value'],
                            'luminosidade_status': data_json['sensors']['lightLevel']['status'],
                            
                            'vibracao': data_json['sensors']['vibration']['value'],
                            'vibracao_status': data_json['sensors']['vibration']['status'],
                            
                            # Análise preditiva
                            'system_status': data_json['analysis']['systemStatus'],
                            'risk_level': data_json['analysis']['riskLevel'],
                            'next_maintenance': data_json['analysis']['nextMaintenance'],
                            'status_detail': data_json['analysis'].get('statusDetail', ''),
                            
                            # Estatísticas operacionais
                            'uptime': data_json['operationalStats']['uptime'],
                            'total_readings': data_json['operationalStats']['totalReadings'],
                            'avg_temperature': data_json['operationalStats']['avgTemperature'],
                            'avg_humidity': data_json['operationalStats']['avgHumidity']
                        }
                        
                        dados_processados.append(registro)
                        
                    except Exception as e:
                        print(f"[AVISO] Erro ao processar JSON: {e} na linha: {linha.strip()}")
                        continue
        
        return dados_processados
    
    def salvar_dados_estruturados(self, dados):
        """Salva dados em CSV estruturado e datado"""
        if not dados:
            print("[AVISO] Nenhum dado para salvar")
            return None
            
        df = pd.DataFrame(dados)
        
        # Arquivo específico desta execução
        arquivo_execucao = os.path.join(self.dados_simulacao_dir, f"hermes_data_{self.timestamp_execucao}.csv")
        df.to_csv(arquivo_execucao, index=False, encoding='utf-8')
        print(f"[SUCESSO] Dados salvos em: {arquivo_execucao}")
        
        # Arquivo histórico cumulativo
        arquivo_historico = os.path.join(self.dados_simulacao_dir, "hermes_historico_completo.csv")
        if os.path.exists(arquivo_historico):
            # Anexa aos dados existentes
            df_existente = pd.read_csv(arquivo_historico)
            df_completo = pd.concat([df_existente, df], ignore_index=True)
        else:
            df_completo = df
            
        df_completo.to_csv(arquivo_historico, index=False, encoding='utf-8')
        print(f"[SUCESSO] Histórico atualizado: {arquivo_historico}")
        
        # Gera resumo estatístico
        self.gerar_resumo_estatistico(df)
        
        return arquivo_execucao
    
    def gerar_resumo_estatistico(self, df):
        """Gera resumo estatístico da execução"""
        resumo = {
            'execucao_id': self.timestamp_execucao,
            'timestamp_processamento': datetime.now().isoformat(),
            'total_registros': len(df),
            'duracao_simulacao_ms': df['timestamp_simulacao'].max() - df['timestamp_simulacao'].min() if len(df) > 1 else 0,
            'temp_media': df['temperatura'].mean(),
            'temp_min': df['temperatura'].min(),
            'temp_max': df['temperatura'].max(),
            'umidade_media': df['umidade'].mean(),
            'umidade_min': df['umidade'].min(),
            'umidade_max': df['umidade'].max(),
            'status_normal': len(df[df['system_status'] == 'NORMAL']),
            'status_atencao': len(df[df['system_status'] == 'ATENÇÃO']),
            'status_critico': len(df[df['system_status'] == 'CRÍTICO']),
            'alertas_temperatura': len(df[df['temperatura_status'] == 'ALERTA']),
            'alertas_umidade': len(df[df['umidade_status'] == 'ALERTA']),
            'alertas_vibracao': len(df[df['vibracao_status'] == 'ALERTA'])
        }
        
        # Salva resumo
        arquivo_resumo = os.path.join(self.dados_simulacao_dir, f"hermes_resumo_{self.timestamp_execucao}.csv")
        pd.DataFrame([resumo]).to_csv(arquivo_resumo, index=False, encoding='utf-8')
        print(f"[SUCESSO] Resumo estatístico salvo: {arquivo_resumo}")
        
        # Exibe resumo no terminal
        print("\n" + "="*60)
        print(f"RESUMO DA SIMULAÇÃO - {self.timestamp_execucao}")
        print("="*60)
        print(f"📊 Total de registros: {resumo['total_registros']}")
        print(f"⏱️  Duração da simulação: {resumo['duracao_simulacao_ms']/1000:.1f}s")
        print(f"🌡️  Temperatura: {resumo['temp_min']:.1f}°C - {resumo['temp_max']:.1f}°C (média: {resumo['temp_media']:.1f}°C)")
        print(f"💧 Umidade: {resumo['umidade_min']:.1f}% - {resumo['umidade_max']:.1f}% (média: {resumo['umidade_media']:.1f}%)")
        print(f"✅ Status NORMAL: {resumo['status_normal']} registros")
        print(f"⚠️  Status ATENÇÃO: {resumo['status_atencao']} registros")
        print(f"🚨 Status CRÍTICO: {resumo['status_critico']} registros")
        print("="*60)
    
    def processar_simulacao(self):
        """Método principal para processar dados da simulação"""
        print(f"\n[HERMES] Processando dados da simulação - {self.timestamp_execucao}")
        
        # Extrai dados JSON
        dados = self.extrair_dados_json()
        
        if not dados:
            print("[ERRO] Nenhum dado JSON válido encontrado no log!")
            return False
            
        # Salva dados estruturados
        arquivo_salvo = self.salvar_dados_estruturados(dados)
        
        if arquivo_salvo:
            print(f"[HERMES] Processamento concluído com sucesso!")
            return True
        else:
            print("[ERRO] Falha no processamento dos dados!")
            return False

if __name__ == "__main__":
    processador = ProcessadorDadosSimulacao()
    processador.processar_simulacao() 