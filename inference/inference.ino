#include "DHT.h"
#include <Adafruit_NeoPixel.h>
#include <Stepper.h>
//Temperature and Humidity Pin
#define DHTPIN 2
#define DHTTYPE DHT11
//Light Pin
#define LIGHTPIN A0
//Buttons
#define BUTTON_PIN A1
//8 RGB LED
#define LED_PIN 6
#define LED_COUNT 8
//Ultrasonic Sensor
#define TRIG_PIN 12
#define ECHO_PIN 13
//Motor Stepper
#define IN1_PIN 11
#define IN2_PIN 10
#define IN3_PIN 9
#define IN4_PIN 8
//Buzzer
#define BUZZER_PIN 3

DHT dht(DHTPIN, DHTTYPE);
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB+NEO_KHZ800);
const int stepsPerRevolution=2048;
Stepper myStepper(stepsPerRevolution, IN1_PIN, IN3_PIN, IN2_PIN, IN4_PIN);

bool isGreen[LED_COUNT];
unsigned long lastSensorRead=0;
unsigned long lastButtonRead=0;
bool lastButtonState=false;

void playFeedback() {
  tone(BUZZER_PIN, 4000, 50);
}

void setup() {
  Serial.begin(9600);
  //DHT Init
  dht.begin();
  //Setup Ultrasonic
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  //Setup Motor
  myStepper.setSpeed(12);
  //Buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  //Shift registers 8 LED RGB
  strip.begin();
  strip.setBrightness(50);
  for(int i=0; i<LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(50, 0, 0));
    isGreen[i]=false;
  }
  strip.show();
  Serial.println("STATUS:READY");
}

void loop() {
  //SENSORS
  if(millis()-lastSensorRead>=2000) {
    lastSensorRead=millis();
    float humidity=dht.readHumidity();
    float tempC=dht.readTemperature();
    int lightVal=analogRead(LIGHTPIN);
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    long duration=pulseIn(ECHO_PIN, HIGH);
    int distance=duration*0.034/2;
    Serial.print("DATA");
    Serial.print("|temperature:"); Serial.print(isnan(tempC)?"--":String(tempC, 1));
    Serial.print("|humidity:"); Serial.print(isnan(humidity)?"--":String(humidity, 1));
    Serial.print("|light:"); Serial.print(lightVal);
    Serial.print("|distance:"); Serial.println(distance);
  }
  //BUTTONS
  if(millis()-lastButtonRead>=50) {
    lastButtonRead=millis();
    int btnVal=analogRead(BUTTON_PIN);
    bool pressed=(btnVal>50);
    if(pressed && !lastButtonState) {
      //Rising Edge
      playFeedback();
      Serial.print("EVENT|button:");
      Serial.println(btnVal);
    }
    lastButtonState=pressed;
  }
  //Serial command Handler
  if(Serial.available()>0) {
    String cmd=Serial.readStringUntil('\n');
    cmd.trim();
    playFeedback();
    if(cmd=="OPEN") {
      myStepper.step(1024);
      Serial.println("ACK|OPEN|Opening curtains");
    }
    else if (cmd=="CLOSE") {
      myStepper.step(-1024);
      Serial.println("ACK|CLOSE|Closing curtains");
    }
    else if(cmd=="H"){//ALL ON
      for(int i=0; i<LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(0, 255, 0));
      }
      Serial.println("ACK|H|All lights on");
    }
    else if(cmd=="L") {//ALL OFF
      for(int i=0; i<LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(50, 0, 0));
      }
      Serial.println("ACK|L|All lights off");
    }
    else if(cmd=="N") {//NIGHT MODE
      for(int i=0; i<LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(0, 0, 50));
      }
      Serial.println("ACK|N|Night mode");
    }
    else if (cmd.startsWith("D")) {//TOGLLE LED 0-7
      int idx=cmd.substring(1).toInt();
      if(idx>=0 && idx<LED_COUNT) {
        isGreen[idx]=!isGreen[idx];
        strip.setPixelColor(idx, isGreen[idx] ? strip.Color(0, 255, 0) : strip.Color(50, 0, 0));
        Serial.print("ACK|D");
        Serial.print(idx);
        Serial.print("|");
        Serial.println(isGreen[idx] ? "on" : "off");
      }
    }
    else {
      Serial.print("ERR|unknown: ");
      Serial.println(cmd);
    }
    strip.show();
  }
}