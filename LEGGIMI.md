# Robot quadrupede ESP32 con ESP-NOW

Questo archivio contiene **tre sketch Arduino separati**, con commenti e nomi in italiano.

## File
- `Indirizzo_MAC/Indirizzo_MAC.ino`: legge il MAC dell'ESP32 ricevitore.
- `Ricevitore/Ricevitore.ino`: riceve i comandi wireless e pilota quattro servomotori.
- `Trasmettitore/Trasmettitore.ino`: legge l'asse X del joystick e invia il valore al ricevitore.

## Istruzioni
1. Apri `Indirizzo_MAC.ino` nell'IDE Arduino, caricalo sull'ESP32 del robot e leggi il MAC sul Monitor Seriale a **115200 baud**.
2. Nel file `Trasmettitore.ino`, sostituisci `macRicevitore` con il MAC ottenuto (esempio: `AA:BB:CC:DD:EE:FF` diventa `{0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF}`).
3. Carica `Ricevitore.ino` sull'ESP32 del robot.
4. Carica `Trasmettitore.ino` sull'ESP32 con il joystick.
5. Alimenta entrambi e muovi il joystick sull'asse X.

## Collegamenti
- Ricevitore: anteriore sinistro GPIO 17, anteriore destro GPIO 18, posteriore sinistro GPIO 25, posteriore destro GPIO 33.
- Trasmettitore: uscita analogica X del joystick su GPIO 34; alimenta il joystick a **3,3 V** e collega GND.
- I servomotori devono usare un'alimentazione adeguata **esterna** alla scheda ESP32, con **GND in comune** all'ESP32. Non alimentare quattro servomotori dal pin 3,3 V della scheda.

## Requisiti
- Arduino IDE con supporto ESP32.
- Libreria `ESP32Servo` installata.
- `WiFi.h`, `esp_now.h` e `Arduino.h` incluse con il core ESP32.

## Note
- I valori delle soglie (4000 e 100) sono molto vicini agli estremi della lettura 0–4095: se il joystick non attiva il movimento, calibra `SOGLIA_AVANTI` e `SOGLIA_INDIETRO` usando i valori mostrati nel Monitor Seriale.
- I movimenti sono quelli del codice fornito: semplici oscillazioni alternate dei due lati; non costituiscono una camminata tridimensionale con sollevamento delle zampe.
- Aggiunto un controllo della dimensione del messaggio e un arresto in posizione neutra se non arrivano comandi per un secondo.
- Il codice include callback diverse per Arduino ESP32 Core 2.x e 3.x; i nomi delle API possono variare con gli aggiornamenti del core.
