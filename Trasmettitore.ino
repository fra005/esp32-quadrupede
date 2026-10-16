// TRASMETTITORE: ESP32 collegato al joystick
#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <esp_arduino_version.h>

const int PIN_JOYSTICK_X = 34;

// SOSTITUISCI con il MAC del tuo ESP32 ricevitore.
uint8_t macRicevitore[] = {0xA4, 0xF0, 0x0F, 0x61, 0xBC, 0x2C};

// Deve essere identica alla struttura del ricevitore.
typedef struct {
  int xValue;
} DatiJoystick;

DatiJoystick datiDaInviare;

#if ESP_ARDUINO_VERSION_MAJOR >= 3
void allaTrasmissione(const wifi_tx_info_t *informazioni, esp_now_send_status_t stato) {
#else
void allaTrasmissione(const uint8_t *mac, esp_now_send_status_t stato) {
#endif
  Serial.print("Invio: ");
  Serial.println(stato == ESP_NOW_SEND_SUCCESS ? "riuscito" : "non riuscito");
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_JOYSTICK_X, INPUT);
  analogReadResolution(12);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

  if (esp_now_init() != ESP_OK) {
    Serial.println("Errore: impossibile inizializzare ESP-NOW");
    return;
  }
  esp_now_register_send_cb(allaTrasmissione);

  esp_now_peer_info_t destinatario = {};
  memcpy(destinatario.peer_addr, macRicevitore, 6);
  destinatario.channel = 0;
  destinatario.encrypt = false;

  if (esp_now_add_peer(&destinatario) != ESP_OK) {
    Serial.println("Errore: impossibile associare il ricevitore");
    return;
  }
  Serial.println("Trasmettitore pronto");
}

void loop() {
  datiDaInviare.xValue = analogRead(PIN_JOYSTICK_X);
  esp_err_t risultato = esp_now_send(macRicevitore,
                                    (const uint8_t *)&datiDaInviare,
                                    sizeof(datiDaInviare));
  if (risultato != ESP_OK) Serial.println("Errore durante l'invio");

  Serial.print("Valore X inviato: ");
  Serial.println(datiDaInviare.xValue);
  delay(50);
}
