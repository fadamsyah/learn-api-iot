/*
  DHT unit:
    - Humidity    : %
    - Temperature : C
  DHT Status Code:
    - 200 : Success
    - 400 : Gagal baca temperature dan humidity
    - 401 : Berhasil baca temperatur tapi humidity gagal
    - 402 : Gagal baca temperature tapi humidity berhasil
 */

#include "DHT.h"
#define DHTPIN 2 
#define DHTTYPE DHT11   // DHT 11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(57600);

  dht.begin();
}

void loop() {
  String msg = "empty";
  if (Serial.available() > 0) {
    msg = Serial.readStringUntil('\n');
    msg.toLowerCase();
    msg.trim();
  }

  if (msg == "get dht"){
    float h = dht.readHumidity();
    float t = dht.readTemperature(); // Default-nya Celcius
  
    int status_code = 200;
    if (isnan(h) && isnan(t)) {
      int status_code = 400;
      h = -1;
      t = -1;
    }
    else if (isnan(h)) {
      int status_code = 401;
      h = -1;
    }
    else if (isnan(t)){
      int status_code = 402;
      t = -1;
    }
  
    Serial.print(status_code);
    Serial.print("|");
    Serial.print(h);
    Serial.print("|");
    Serial.println(t);
  }
}
