// Pilot Wnet Rev A (Radio Wnet) — wariant Meshtastic dla własnej płytki ESP32-S3-WROOM-1-N16R8 + Ebyte E22-900M22S.
//
// Pochodzenie: kopia pliku variants/esp32s3/t-eth-elite/variant.h z repozytorium meshtastic/firmware,
// gałąź develop, pobrany 18.10.2026 z
//   https://raw.githubusercontent.com/meshtastic/firmware/develop/variants/esp32s3/t-eth-elite/variant.h
// ostatni commit pliku 2361776992adff08b623e2f3b110ffe98978342e (5.02.2026), SHA-256 oryginału
// 572f59966c5ec9988ca7ee38b650c2b8ce8345656c8856439387208991af8b88.
// Licencja: GPL-3.0 (jak całe Meshtastic firmware). Ten plik jest utworem zależnym i podlega GPL-3.0;
// wolno go rozpowszechniać tylko na tych samych warunkach, razem z informacją o zmianach poniżej.
//
// Zmiany względem t-eth-elite (Pilot Wnet, 18.10.2026; źródło pinów: pcb/obwod.py, R3 rozdz. 6.2–6.3):
//  1. LORA_RESET 46 → 2 (NRESET radia przeniesiony z pinu strapping GPIO46; R3 rozdz. 6.4).
//  2. Bez GPS: usunięte GPS_RX_PIN 39 / GPS_TX_PIN 42 (+ MESHTASTIC_EXCLUDE_GPS w platformio.ini).
//     GPIO39 = PLAY, GPIO42 = START (DECYZJE D9) — wejścia przycisków, nie wolno ich sterować jako UART.
//  3. Wyłączone wykrywanie RF95 (USE_RF95), SX1280 (USE_SX1280) i LR1121 (USE_LR1121) wraz z ich pinami:
//     wariant t-eth-elite ma dla SX1280 DIO2 = 33 i DIO3 = 34, a przy PSRAM Octal GPIO33–37 to linie pamięci
//     (R5 S13). Firmware próbuje radii kolejno — bez SX1262 sięgnąłby po te piny. Zostaje tylko SX1262.
//  4. Bez karty SD (HAS_SDCARD, SDCARD_USE_SPI1): Rev A nie ma gniazda; domyślne piny SPI płytki esp32s3box
//     w arduino-esp32 (SCK 12, MISO 13) to SPRAWDŹ i EXP_IO13 [DO WERYFIKACJI, skąd FSCommon bierze SPI_SCK].
//  5. Bez zmian: LoRa SCK 10 / MISO 9 / MOSI 11 / CS 40 / DIO1 8 / BUSY 16, DIO2 jako przełącznik RF,
//     TCXO z DIO3, I2C 17/18, LED 38 (stan wysoki = świeci), BUTTON_PIN 0 (przycisk BOOT na płytce),
//     Ethernet W5500 jak w t-eth-elite (MISO 47, MOSI 21, SCLK 48, CS 45, INT 14, bez RST).
// Szkic nieprzetestowany: nie budowany na komputerze studyjnym; budowa w CI (firmware/ci/build-mesh.yml)
// albo na maszynie roboczej.

#define I2C_SDA 17 // I2C: OLED J17, Qwiic J18, złącze J19
#define I2C_SCL 18

#define HAS_SCREEN 1 // OLED SSD1306/SH1106 (0x3C) na złączu J17

#define LED_POWER 38 // zielona dioda SMD D2 przez 1 kΩ, stan wysoki = świeci
#define BUTTON_PIN 0 // BOOT (SW2) — START jest na GPIO42 i Meshtastic go nie używa

#define BUTTON_NEED_PULLUP // na płytce jest też zewnętrzne 10 kΩ (R9)

// Tylko SX1262 (E22-900M22S). RF95, SX1280 i LR1121 celowo NIE są zdefiniowane (zmiana 3).
#define USE_SX1262

#define LORA_SCK 10
#define LORA_MISO 9
#define LORA_MOSI 11
#define LORA_CS 40
#define LORA_RESET 2 // Rev A: GPIO2 (t-eth-elite: 46); zworka R77 (DNP) przywraca GPIO46

// per SX1276_Receive_Interrupt/utilities.h — zostawione jak w t-eth-elite (te same piny co SX1262)
#define LORA_DIO0 8
#define LORA_DIO1 16
#define LORA_DIO2 RADIOLIB_NC

// per SX1262_Receive_Interrupt/utilities.h
#ifdef USE_SX1262
#define SX126X_CS LORA_CS
#define SX126X_DIO1 8
#define SX126X_BUSY 16
#define SX126X_RESET LORA_RESET
#define SX126X_DIO2_AS_RF_SWITCH // DIO2 → TXEN, NOT DIO2 (74LVC1G04) → RXEN
// TCXO: 1,8 V jak w t-eth-elite i wszystkich wariantach z R3 rozdz. 6.1; Ebyte V1.5 podaje 2,2 V.
// [DO WERYFIKACJI w karcie kupionej partii E22-900M22S] — przy 2,2 V zmienić na 2.2.
#define SX126X_DIO3_TCXO_VOLTAGE 1.8
#endif

#define HAS_ETHERNET 1
#define USE_WS5500 1 // this driver uses the same stack as the ESP32 Wifi driver

#define ETH_MISO_PIN 47
#define ETH_MOSI_PIN 21
#define ETH_SCLK_PIN 48
#define ETH_CS_PIN 45
#define ETH_INT_PIN 14
#define ETH_RST_PIN -1 // reset W5500 tylko RC
#define ETH_ADDR 1

// Napięcie VSYS (5 V przez dzielnik 1:2 na GPIO1) celowo nie jest podane jako BATTERY_PIN: Rev A nie ma
// akumulatora (DECYZJE D2), a Meshtastic interpretowałby 5 V jako stan baterii.
