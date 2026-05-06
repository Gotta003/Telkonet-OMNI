#include "DHT.h"
#include <Adafruit_NeoPixel.h>
//Temperature and Humidity Pin
#define DHTPIN 2
#define DHTTYPE DHT11
//Light Pin
#define LIGHTPIN A0
//8 RGB LED
#define LED_PIN 6
#define LED_COUNT 8

const int serPin=11;
const int rclkPin=8;
const int srclkPin=12;
const int sensorPin=LIGHTPIN;
DHT dht(DHTPIN, DHTTYPE);
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB+NEO_KHZ800);
int sensorValue=0;
bool isGreen[LED_COUNT];
unsigned long lastSensorRead=0;

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(serPin, OUTPUT);
  pinMode(rclkPin, OUTPUT);
  pinMode(srclkPin, OUTPUT);
  strip.begin();
  strip.setBrightness(50);
  for(int i=0; i<LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(50, 0, 0));
    isGreen[i]=false;
  }
  strip.show();
  Serial.print("Setup Correct!");
}

void loop() {
  if(millis()-lastSensorRead>=2000) {
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
    lastSensorRead=millis();
  }
  if(Serial.available()>0) {
    String cmd=Serial.readStringUntil("\n");
    if(cmd=="H"){//ALL ON
      for(int i=0; i<LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(0, 255, 0));
      }
    }
    else if(cmd=="L") {//ALL OFF
      for(int i=0; i<LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(50, 0, 0));
      }
    }
    else if(cmd=="N") {//NIGHT MODE
      for(int i=0; i<LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(0, 0, 50));
      }
    }
    else if (cmd.startsWith("D")) {//TOGLLE LED 0-7
      int ledIndex=cmd.substring(1).toInt();
      if(!isGreen[ledIndex]) {
        strip.setPixelColor(ledIndex, strip.Color(0, 255, 0));
        isGreen[ledIndex]=true;
      }
      else {
        strip.setPixelColor(ledIndex, strip.Color(50, 0, 0));
        isGreen[ledIndex]=false;
      }
    }
    strip.show();
  }
}