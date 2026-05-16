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

const int serPin=11;
const int rclkPin=8;
const int srclkPin=7;
//Init Variables
const int sensorPin=LIGHTPIN;
DHT dht(DHTPIN, DHTTYPE);
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB+NEO_KHZ800);
int sensorValue=0;
bool isGreen[LED_COUNT];
unsigned long lastSensorRead=0;
//Motor
const int stepsPerRevolution=2048;
Stepper myStepper(stepsPerRevolution, IN1_PIN, IN3_PIN, IN2_PIN, IN4_PIN);

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
  //SENSORS
  if(millis()-lastSensorRead>=2000) {
    lastSensorRead=millis();
    float humidity=dht.readHumidity();
    float tempC=dht.readTemperature();
    if (isnan(humidity) || isnan(tempC)) {
      Serial.println("Failed to read from DHT sensor!");
      return;
    }
    sensorValue=analogRead(sensorPin);
    long duration;
    int distance;
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    duration=pulseIn(ECHO_PIN, HIGH);
    distance=duration*0.034/2;
    Serial.print("DATA");
    Serial.print("|temperature:");
    if (!isnan(tempC)) {
      Serial.print(tempC, 1);
    }
    else {
      Serial.print("--");
    }
    Serial.print("|humidity:"); 
    if (!isnan(humidity)) {
      Serial.print(humidity, 1);
    }
    else {
      Serial.print("--");
    }
    Serial.print("light:"); 
    Serial.print(sensorValue);
    Serial.print("|distance:");
    Serial.print(distance);
  }
  //BUTTONS
  if(millis()-lastButtonRead>=50) {
    lastButtonRead=millis();
    int btnVal=analogRead(BUTTON_PIN);
    bool pressed=(btnVal>100);
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
      Serial.println("ACK|OPEN|Opening curtains");
      myStepper.step(1024);
    }
    else if (cmd=="CLOSE") {
      Serial.println("ACK|CLOSE|Closing curtains");
      myStepper.step(-1024);
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
      int ledIndex=cmd.substring(1).toInt();
      if(ledIndex>=0 && ledIndex<LED_COUNT) {
        if(!isGreen[ledIndex]) {
          strip.setPixelColor(ledIndex, strip.Color(0, 255, 0));
          isGreen[ledIndex]=true;
        }
        else {
          strip.setPixelColor(ledIndex, strip.Color(50, 0, 0));
          isGreen[ledIndex]=false;
        }
        Serial.print("ACK|D");
        Serial.print(ledIndex);
        Serial.print("|");
        Serial.println(isGreen[ledIndex] ? "on" : "off");
      }
    }
    else {
      Serial.print("ERR|unknown command: ");
      Serial.println(cmd);
    }
    strip.show();
  }
}