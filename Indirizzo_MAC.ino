// UTILITY: mostra l'indirizzo MAC dell'ESP32 ricevitore
#include <Arduino.h>
#include <WiFi.h>

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  delay(300);
  Serial.print("Indirizzo MAC di questo ESP32: ");
  Serial.println(WiFi.macAddress());
}

void loop() {
  // Non serve eseguire altre operazioni.
}
