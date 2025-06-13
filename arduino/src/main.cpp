// Autor: Diogo L. Zequini Pinto
// Projeto: Hermes Reply - Challenge Sprint 2 - Firmware ESP32

#include <Arduino.h>
#include <DHT.h>
#include <ArduinoJson.h>

// === CONFIGURAÇÕES DO SISTEMA HERMES REPLY ===
#define DEVICE_ID "HR-PRED-MAINT-01"
#define FIRMWARE_VERSION "1.0.0"

// === MAPEAMENTO DE PINOS ===
#define DHT_PIN 27
#define DHT_TYPE DHT22
#define LDR_PIN 34          // Sensor de luminosidade (LDR)
#define VIBRATION_PIN 35    // Sensor de vibração simulado
#define LED_STATUS_PIN 2    // LED interno ESP32

// === CONFIGURAÇÕES DOS SENSORES ===
DHT dht(DHT_PIN, DHT_TYPE);

// === VARIÁVEIS GLOBAIS ===
JsonDocument telemetryData;
unsigned long lastReading = 0;
const unsigned long READING_INTERVAL = 5000; // 5 segundos entre leituras
int readingCount = 0;

// === LIMITES PARA ANÁLISE PREDITIVA ===
const float TEMP_MIN_NORMAL = 15.0;
const float TEMP_MAX_NORMAL = 35.0;
const float HUMIDITY_MIN_NORMAL = 30.0;
const float HUMIDITY_MAX_NORMAL = 70.0;
const int LIGHT_MIN_NORMAL = 200;
const int LIGHT_MAX_NORMAL = 800;
const int VIBRATION_MAX_NORMAL = 500;

// === CAPA-FW-002: OTIMIZAÇÃO DA MÉDIA MÓVEL ===
const int MOVING_AVG_WINDOW = 12; // 1 minuto (12 leituras x 5s)
float tempWindow[MOVING_AVG_WINDOW] = {0};
float humWindow[MOVING_AVG_WINDOW] = {0};
int windowIndex = 0;
float tempSum = 0.0;  // Soma corrente para temperatura
float humSum = 0.0;   // Soma corrente para umidade
bool windowFilled = false; // Flag para saber se a janela foi preenchida

// === CAPA-FW-003: LED NÃO-BLOQUEANTE ===
unsigned long lastBlinkTime = 0;
bool ledState = false;
int blinkCount = 0;
int maxBlinks = 0;
unsigned long blinkInterval = 0;
char currentLedStatus[10] = "NORMAL";

// === PROTÓTIPOS DAS FUNÇÕES ===
void printSystemInfo();
void analyzeSystemHealth(float temp, float humidity, int light, int vibration, char* statusResult, char* alertsResult);
void buildTelemetryJson(float temp, float humidity, int light, int vibration, const char* status, float movAvgTemp, float movAvgHum);
void sendTelemetryData();
void configureLedPattern(const char* newStatus);
void handleLedBlinking();

void setup() {
  Serial.begin(115200);
  
  // Configuração dos pinos
  pinMode(LED_STATUS_PIN, OUTPUT);
  pinMode(LDR_PIN, INPUT);
  pinMode(VIBRATION_PIN, INPUT);
  
  // Inicialização dos sensores
  dht.begin();
  
  // Sequência de inicialização
  digitalWrite(LED_STATUS_PIN, HIGH);
  delay(1000);
  digitalWrite(LED_STATUS_PIN, LOW);
  
  printSystemInfo();
  
  Serial.println("=== SISTEMA INICIADO - AGUARDANDO PRIMEIRA LEITURA ===");
  Serial.println();
}

void loop() {
  unsigned long currentTime = millis();
  
  if (currentTime - lastReading >= READING_INTERVAL) {
    readingCount++;
    
    // Coleta de dados dos sensores
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    int lightLevel = analogRead(LDR_PIN);
    int vibrationLevel = analogRead(VIBRATION_PIN);
    
    // Simula variações realistas se sensores não conectados
    if (isnan(temperature)) temperature = 20.0 + random(-50, 150) / 10.0;
    if (isnan(humidity)) humidity = 50.0 + random(-200, 300) / 10.0;
    
    // === CAPA-FW-002: MÉDIA MÓVEL OTIMIZADA O(1) ===
    // Remove valor antigo da soma (se janela já foi preenchida)
    if (windowFilled) {
      tempSum -= tempWindow[windowIndex];
      humSum -= humWindow[windowIndex];
    }
    
    // Adiciona novo valor
    tempWindow[windowIndex] = temperature;
    humWindow[windowIndex] = humidity;
    tempSum += temperature;
    humSum += humidity;
    
    // Avança índice
    windowIndex = (windowIndex + 1) % MOVING_AVG_WINDOW;
    if (windowIndex == 0) windowFilled = true;
    
    // Calcula médias móveis
    int validSamples = windowFilled ? MOVING_AVG_WINDOW : (readingCount < MOVING_AVG_WINDOW ? readingCount : MOVING_AVG_WINDOW);
    float movingAvgTemp = tempSum / validSamples;
    float movingAvgHum = humSum / validSamples;
    
    // Adiciona ruído realista aos sensores analógicos
    lightLevel = lightLevel + random(-50, 50);
    vibrationLevel = vibrationLevel + random(-100, 200);
    
    // Limita valores aos ranges sensores reais
    lightLevel = constrain(lightLevel, 0, 1023);
    vibrationLevel = constrain(vibrationLevel, 0, 1023);
    
    // === CAPA-FW-001: ANÁLISE PREDITIVA SEM String ===
    char systemStatus[10];  // Buffer para status
    char alerts[20];        // Buffer para alertas
    analyzeSystemHealth(temperature, humidity, lightLevel, vibrationLevel, systemStatus, alerts);
    
    // Monta JSON de telemetria (inclui médias móveis)
    buildTelemetryJson(temperature, humidity, lightLevel, vibrationLevel, systemStatus, movingAvgTemp, movingAvgHum);
    
    // Envia dados via Serial
    sendTelemetryData();
    
    // Atualiza LED de status (não-bloqueante)
    configureLedPattern(systemStatus);
    
    lastReading = currentTime;
  }
  
  // === CAPA-FW-003: PROCESSA LED NÃO-BLOQUEANTE ===
  handleLedBlinking();
  
  delay(100); // Pequeno delay para estabilidade
}

void printSystemInfo() {
  Serial.println("╔══════════════════════════════════════════════════════════╗");
  Serial.println("║            HERMES REPLY - MANUTENÇÃO PREDITIVA        ║");
  Serial.println("║                 Monitoramento IoT Industrial                ║");
  Serial.println("╠══════════════════════════════════════════════════════════╣");
  Serial.print("║ ID do Dispositivo: ");
  Serial.print(DEVICE_ID);
  Serial.print(" | Firmware: ");
  Serial.print(FIRMWARE_VERSION);
  Serial.println("           ║");
  Serial.println("║ Sensores: DHT22, LDR, Vibração, LED de Status              ║");
  Serial.println("║ Frequência de Leitura: 5s | Formato: JSON | Análise: Preditiva     ║");
  Serial.println("╚══════════════════════════════════════════════════════════╝");
  Serial.println();
}

// === CAPA-FW-001: FUNÇÃO SEM String ===
void analyzeSystemHealth(float temp, float humidity, int light, int vibration, char* statusResult, char* alertsResult) {
  int alertCount = 0;
  alertsResult[0] = '\0'; // Inicializa string vazia
  
  // Análise de temperatura
  if (temp < TEMP_MIN_NORMAL || temp > TEMP_MAX_NORMAL) {
    alertCount++;
    strncat(alertsResult, "TEMP ", 19 - strlen(alertsResult));
  }
  
  // Análise de umidade
  if (humidity < HUMIDITY_MIN_NORMAL || humidity > HUMIDITY_MAX_NORMAL) {
    alertCount++;
    strncat(alertsResult, "UMID ", 19 - strlen(alertsResult));
  }
  
  // Análise de luminosidade
  if (light < LIGHT_MIN_NORMAL || light > LIGHT_MAX_NORMAL) {
    alertCount++;
    strncat(alertsResult, "LUZ ", 19 - strlen(alertsResult));
  }
  
  // Análise de vibração
  if (vibration > VIBRATION_MAX_NORMAL) {
    alertCount++;
    strncat(alertsResult, "VIB ", 19 - strlen(alertsResult));
  }
  
  // Remove espaço final se existir
  int len = strlen(alertsResult);
  if (len > 0 && alertsResult[len-1] == ' ') {
    alertsResult[len-1] = '\0';
  }
  
  // Determina status geral
  if (alertCount == 0) strcpy(statusResult, "NORMAL");
  else if (alertCount <= 2) strcpy(statusResult, "ATENÇÃO");
  else strcpy(statusResult, "CRÍTICO");
}

void buildTelemetryJson(float temp, float humidity, int light, int vibration, const char* status, float movAvgTemp, float movAvgHum) {
  telemetryData.clear();
  
  // Metadados do dispositivo
  telemetryData["deviceId"] = DEVICE_ID;
  telemetryData["timestamp"] = millis();
  telemetryData["readingId"] = readingCount;
  telemetryData["firmwareVersion"] = FIRMWARE_VERSION;
  
  // Dados dos sensores
  JsonObject sensors = telemetryData["sensors"].to<JsonObject>();
  sensors["temperature"]["value"] = round(temp * 100) / 100.0;
  sensors["temperature"]["movingAverage"] = round(movAvgTemp * 100) / 100.0;
  sensors["temperature"]["unit"] = "°C";
  sensors["temperature"]["status"] = (temp >= TEMP_MIN_NORMAL && temp <= TEMP_MAX_NORMAL) ? "OK" : "ALERTA";
  
  sensors["humidity"]["value"] = round(humidity * 100) / 100.0;
  sensors["humidity"]["movingAverage"] = round(movAvgHum * 100) / 100.0;
  sensors["humidity"]["unit"] = "%";
  sensors["humidity"]["status"] = (humidity >= HUMIDITY_MIN_NORMAL && humidity <= HUMIDITY_MAX_NORMAL) ? "OK" : "ALERTA";
  
  sensors["lightLevel"]["value"] = light;
  sensors["lightLevel"]["unit"] = "lux";
  sensors["lightLevel"]["status"] = (light >= LIGHT_MIN_NORMAL && light <= LIGHT_MAX_NORMAL) ? "OK" : "ALERTA";
  
  sensors["vibration"]["value"] = vibration;
  sensors["vibration"]["unit"] = "intensidade";
  sensors["vibration"]["status"] = (vibration <= VIBRATION_MAX_NORMAL) ? "OK" : "ALERTA";
  
  // Análise preditiva
  JsonObject analysis = telemetryData["analysis"].to<JsonObject>();
  analysis["systemStatus"] = status;
  analysis["riskLevel"] = (strcmp(status, "CRÍTICO") == 0) ? "ALTO" : (strcmp(status, "ATENÇÃO") == 0) ? "MÉDIO" : "BAIXO";
  analysis["nextMaintenance"] = (strcmp(status, "CRÍTICO") == 0) ? "IMEDIATA" : (strcmp(status, "ATENÇÃO") == 0) ? "24H" : "AGENDADA";
  
  // === CAPA-FW-001: DETALHE DE STATUS SEM String ===
  char statusDetail[25];
  statusDetail[0] = '\0'; // Inicializa string vazia
  
  if (sensors["temperature"]["status"] == "ALERTA") strncat(statusDetail, "TEMP,", 24 - strlen(statusDetail));
  if (sensors["humidity"]["status"] == "ALERTA") strncat(statusDetail, "HUMID,", 24 - strlen(statusDetail));
  if (sensors["lightLevel"]["status"] == "ALERTA") strncat(statusDetail, "LIGHT,", 24 - strlen(statusDetail));
  if (sensors["vibration"]["status"] == "ALERTA") strncat(statusDetail, "VIB,", 24 - strlen(statusDetail));
  
  // Remove vírgula final se existir
  int len = strlen(statusDetail);
  if (len > 0 && statusDetail[len-1] == ',') {
    statusDetail[len-1] = '\0';
  }
  
  analysis["statusDetail"] = statusDetail;
  
  // Estatísticas operacionais
  JsonObject stats = telemetryData["operationalStats"].to<JsonObject>();
  stats["uptime"] = millis();
  stats["totalReadings"] = readingCount;
  stats["avgTemperature"] = movAvgTemp;
  stats["avgHumidity"] = movAvgHum;
}

void sendTelemetryData() {
  Serial.println("┌─────────────────────────────────────────────────────────────┐");
  Serial.print("│ LEITURA #");
  Serial.print(readingCount);
  Serial.print(" | ");
  Serial.print(millis()/1000);
  Serial.println("s de funcionamento                               │");
  Serial.println("├─────────────────────────────────────────────────────────────┤");
  
  // Saída JSON para análise
  Serial.print("JSON_DATA: ");
  serializeJson(telemetryData, Serial);
  Serial.println();
  
  // Saída humanizada para monitoramento
  Serial.print("│ Temp: ");
  Serial.print(telemetryData["sensors"]["temperature"]["value"].as<float>(), 1);
  Serial.print("°C | Umidade: ");
  Serial.print(telemetryData["sensors"]["humidity"]["value"].as<float>(), 1);
  Serial.print("% | Luz: ");
  Serial.print(telemetryData["sensors"]["lightLevel"]["value"].as<int>());
  Serial.print(" | Vib: ");
  Serial.print(telemetryData["sensors"]["vibration"]["value"].as<int>());
  Serial.println(" │");
  
  Serial.print("│ STATUS: ");
  Serial.print(telemetryData["analysis"]["systemStatus"].as<String>());
  Serial.print(" | RISCO: ");
  Serial.print(telemetryData["analysis"]["riskLevel"].as<String>());
  Serial.print(" | MANUTENÇÃO: ");
  Serial.print(telemetryData["analysis"]["nextMaintenance"].as<String>());
  Serial.println("     │");
  
  Serial.println("└─────────────────────────────────────────────────────────────┘");
  Serial.println();
}

// === CAPA-FW-003: LED NÃO-BLOQUEANTE ===
void configureLedPattern(const char* newStatus) {
  if (strcmp(currentLedStatus, newStatus) != 0) {
    strncpy(currentLedStatus, newStatus, sizeof(currentLedStatus) - 1);
    currentLedStatus[sizeof(currentLedStatus) - 1] = '\0';

    blinkCount = 0; // Reseta a contagem

    if (strcmp(newStatus, "NORMAL") == 0) maxBlinks = 1 * 2;     // 1 ciclo on/off (2 alternâncias)
    else if (strcmp(newStatus, "ATENÇÃO") == 0) maxBlinks = 2 * 2; // 2 ciclos on/off (4 alternâncias)
    else maxBlinks = 5 * 2;                                         // 5 ciclos on/off (10 alternâncias)

    lastBlinkTime = 0; // Força a piscada imediata
  }
}

void handleLedBlinking() {
  if (blinkCount >= maxBlinks) {
    digitalWrite(LED_STATUS_PIN, LOW); // Garante que o LED apague no final
    return;
  }

  unsigned long currentTime = millis();
  unsigned long interval = (strcmp(currentLedStatus, "ATENÇÃO") == 0) ? 150 : 100;

  if (currentTime - lastBlinkTime >= interval) {
    ledState = !ledState;
    digitalWrite(LED_STATUS_PIN, ledState);
    lastBlinkTime = currentTime;
    blinkCount++;
  }
}