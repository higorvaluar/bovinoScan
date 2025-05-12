#include <HX711.h>

#define DT 3
#define SCK 2
HX711 balanca;

float pesoAnterior = 0;
bool boiPresente = false;
unsigned long tempoUltimaLeitura = 0;

const float TOLERANCIA = 0.05;
const float PESO_MINIMO = 0.06;
const int INTERVALO_TARA = 5000;

void setup() {
  Serial.begin(9600);
  balanca.begin(DT, SCK);
  delay(1000);
  balanca.set_scale(81588.57f);
  balanca.tare();
  Serial.println("⚙️ Sistema pronto. Aguardando boi...");
}

void loop() {
  float peso = balanca.get_units(10);
  unsigned long agora = millis();

  if (peso < 0.1 && !boiPresente && (agora - tempoUltimaLeitura > INTERVALO_TARA)) {
    balanca.tare();
    Serial.println("⚖️ Balança zerada automaticamente.");
    tempoUltimaLeitura = agora;
  }

  if (!boiPresente && peso > PESO_MINIMO && abs(peso - pesoAnterior) < TOLERANCIA) {
    int idBoi = random(1000, 9999);
    Serial.print("ID simulado do boi: ");
    Serial.println(idBoi);
    Serial.print("Peso (kg): ");
    Serial.println(peso, 3);
    Serial.println("-------------------------");
    boiPresente = true;
    tempoUltimaLeitura = agora;
  }

  if (boiPresente && peso < 0.1) {
    boiPresente = false;
    tempoUltimaLeitura = agora;
  }

  pesoAnterior = peso;
  delay(200);
}
