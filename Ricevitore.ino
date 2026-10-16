// RICEVITORE: ESP32 montato sul robot quadrupede
#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <ESP32Servo.h>
#include <esp_arduino_version.h>

Servo anterioreSinistro, anterioreDestro, posterioreSinistro, posterioreDestro;

// Collegamenti dei servomotori
const int PIN_ANT_SX = 17;
const int PIN_ANT_DX = 18;
const int PIN_POST_SX = 25;
const int PIN_POST_DX = 33;

// Soglie del joystick (ESP32: intervallo analogico 0-4095)
const int SOGLIA_AVANTI = 4000;
const int SOGLIA_INDIETRO = 100;

// Parametri dei movimenti
const int CENTRO = 90;
const int AMPIEZZA = 30;
const int PAUSA_PASSO_MS = 12;
const unsigned long TEMPO_SICUREZZA_MS = 1000;

// Inversioni per compensare l'orientamento dei servomotori
const bool INVERTI_ANT_SX = false;
const bool INVERTI_ANT_DX = false;
const bool INVERTI_POST_SX = true;
const bool INVERTI_POST_DX = true;

// La struttura deve essere identica a quella del trasmettitore.
typedef struct {
  int xValue;
} DatiJoystick;

volatile int valoreJoystick = 2048;
volatile unsigned long ultimoMessaggioMs = 0;

void elaboraDati(const uint8_t *dati, int lunghezza) {
  if (lunghezza != sizeof(DatiJoystick)) return;
  DatiJoystick ricevuti;
  memcpy(&ricevuti, dati, sizeof(ricevuti));
  valoreJoystick = constrain(ricevuti.xValue, 0, 4095);
  ultimoMessaggioMs = millis();
}

// Compatibile con ESP32 Arduino Core 2.x e 3.x
#if ESP_ARDUINO_VERSION_MAJOR >= 3
void allaRicezione(const esp_now_recv_info_t *info, const uint8_t *dati, int lunghezza) {
  elaboraDati(dati, lunghezza);
}
#else
void allaRicezione(const uint8_t *mac, const uint8_t *dati, int lunghezza) {
  elaboraDati(dati, lunghezza);
}
#endif

void impostaAngolo(Servo &servo, int angolo, bool inverti) {
  angolo = constrain(angolo, 0, 180);
  servo.write(inverti ? 180 - angolo : angolo);
}

void impostaSinistra(int angoloAnteriore, int angoloPosteriore) {
  impostaAngolo(anterioreSinistro, angoloAnteriore, INVERTI_ANT_SX);
  impostaAngolo(posterioreSinistro, angoloPosteriore, INVERTI_POST_SX);
}

void impostaDestra(int angoloAnteriore, int angoloPosteriore) {
  impostaAngolo(anterioreDestro, angoloAnteriore, INVERTI_ANT_DX);
  impostaAngolo(posterioreDestro, angoloPosteriore, INVERTI_POST_DX);
}

void posizioneNeutra() {
  impostaSinistra(CENTRO, CENTRO);
  impostaDestra(CENTRO, CENTRO);
}

void muoviLato(bool sinistra, bool avanti) {
  if (sinistra) impostaDestra(CENTRO, CENTRO);
  else impostaSinistra(CENTRO, CENTRO);

  for (int passo = 0; passo <= 20; passo++) {
    // Se la comunicazione si interrompe, interrompe il movimento.
    if (millis() - ultimoMessaggioMs > TEMPO_SICUREZZA_MS) break;
    float frazione = float(passo) / 20.0f;
    int angolo = CENTRO + (avanti ? 1 : -1) * int(AMPIEZZA * frazione);
    if (sinistra) impostaSinistra(angolo, angolo);
    else impostaDestra(angolo, angolo);
    delay(PAUSA_PASSO_MS);
  }
  posizioneNeutra();
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

  if (esp_now_init() != ESP_OK) {
    Serial.println("Errore: impossibile inizializzare ESP-NOW");
    return;
  }
  esp_now_register_recv_cb(allaRicezione);

  ESP32PWM::allocateTimer(0);
  anterioreSinistro.attach(PIN_ANT_SX, 500, 2400);
  anterioreDestro.attach(PIN_ANT_DX, 500, 2400);
  posterioreSinistro.attach(PIN_POST_SX, 500, 2400);
  posterioreDestro.attach(PIN_POST_DX, 500, 2400);
  posizioneNeutra();
  Serial.println("Ricevitore pronto");
}

void loop() {
  // Nessun dato recente: torna alla posizione neutra.
  if (millis() - ultimoMessaggioMs > TEMPO_SICUREZZA_MS) {
    posizioneNeutra();
    delay(20);
    return;
  }

  int x = valoreJoystick;
  Serial.print("Joystick ricevuto: ");
  Serial.println(x);

  if (x > SOGLIA_AVANTI) {
    muoviLato(true, true);
    if (valoreJoystick > SOGLIA_AVANTI) muoviLato(false, true);
  } else if (x < SOGLIA_INDIETRO) {
    muoviLato(true, false);
    if (valoreJoystick < SOGLIA_INDIETRO) muoviLato(false, false);
  } else {
    posizioneNeutra();
    delay(20);
  }
}
