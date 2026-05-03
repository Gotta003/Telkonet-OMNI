#include "DHT.h"

#define DHTPIN 2
#define DHTTYPE DHT11

const int serPin=11;
const int rclkPin=8;
const int srclkPin=12;
const int sensorPin=A0;
DHT dht(DHTPIN, DHTTYPE);
int sensorValue=0;
byte currentPattern=0b00000000;

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(serPin, OUTPUT);
  pinMode(rclkPin, OUTPUT);
  pinMode(srclkPin, OUTPUT);
  refreshLights(currentPattern);
  Serial.print("Setup Correct!");
}

void loop() {
  delay(2000);
  float humidity=dht.readHumidity();
  float tempC=dht.readTemperature();
  if (isnan(humidity) || isnan(tempC)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  sensorValue=analogRead(sensorPin);
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.print("% | ");
  Serial.print("Temperature: ");
  Serial.print(tempC);
  Serial.print("°C | ");
  Serial.print("Light Level Value: ");
  Serial.println(sensorValue);
  if(Serial.available()>0) {
    String command=Serial.readStringUntil("\n");
    command.trim();
    if(command.length()>0) {
      char type=command[0];
      if(type=='H') {
        currentPattern=0b11111111;
      }
      else if (type=='L') {
        currentPattern=0b00000000;
      }
      else if (type=='N') {
        currentPattern=0b00000001;
      }
      else if (type=='D' && command.length()>1) {
        char digitChar=command[1];
        int bitIndex=digitChar-'0';
        if(bitIndex>=0 && bitIndex<=7) {
          currentPattern^=(1<<bitIndex);
        }
      }
      refreshLights(currentPattern);
    }
  }
}

void refreshLights(byte pattern) {
  digitalWrite(rclkPin, LOW);
  shiftOut(serPin, srclkPin, MSBFIRST, pattern);
  digitalWrite(rclkPin, HIGH);
}