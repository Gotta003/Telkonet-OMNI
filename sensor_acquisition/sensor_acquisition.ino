#include "DHT.h"

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  Serial.print("DHT11 Setup Correct!");
  dht.begin();
}

void loop() {
  delay(2000);
  float humidity=dht.readHumidity();
  float tempC=dht.readTemperature();
  if (isnan(humidity) || isnan(tempC)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.print("% | ");
  Serial.print("Temperature: ");
  Serial.print(tempC);
  Serial.println("°C");
}
