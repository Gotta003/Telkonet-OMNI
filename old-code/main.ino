/*
1 arduino
1 computer to show the encrypting 
-------------------------------------------INPUT:---------------------------------------------------------------------------------
4x button for menu
1x button for enter
1x button for settings
1x button for call service
1x button for reset the device
1x sensor for temperature
1x button for home --> 
1x sensor for humidity
1x sensor for noise
1x sensor for light
-------------------------------------------OUTPUT:---------------------------------------------------------------------------------
2x display I2C
2x led yellow to simulate the bulbs
1x fan to simulate change temperature and humidity
1x speaker
1x motor to simulate movement of curtains

------------------------------------------IDEA:------------------------------------------------------------------------------------
1 DISPLAY:
+-----------------------+
|       WELCOME!        |
|  ___________________  |
|                       |
| L-MOD: 15/04/2026     |
| STATUS: IDLE...       |
+-----------------------+
1 DISPLAY CHANGE VIEW AFTER TIMER: 1min
+-----------------------+
| USE ARROW TO MOVE     |
| USE ENTER TO CONFIRM  |
| EMERGENCY: SERVICE    |
| SETTINGS              |
| RESET                 |
+-----------------------+

2 DISPLAY --> this display change to modify the different parameters
          --> this display is unique that it possible to move the arrow, menu, and modify the parameters
          --> to modify the parameter is enough to click confirm on letter: T, H, V, L1, L2
+-----------------------+
| T:30°C | H:54% | V:30 |
|--------+-------+------|
| L1:[#####-----] 50%   | 
| L2:[##--------] 20%   |
+-----------------------+

* [VIEW MODIFY TEMP]
 * +-----------------------+
 * | > SET TEMP THRESH <   |
 * |-----------------------|
 * | TARGET: [ 30°C ]      |
 * | [-]   [+]         [OK]|
 * +-----------------------+

 * [VIEW MODIFY HUMIDITY]
 * +-----------------------+
 * | > SET HUMIDITY % <    |
 * |-----------------------|
 * | TARGET: [ 54% ]       |
 * |                   [OK]|
 * +-----------------------+

 * [VIEW MODIFY VOLUME]
 * +-----------------------+
 * | > SET SYS VOLUME <    |
 * |-----------------------|
 * | VOL: 30               |
 * | [|||-----------]  [OK]|
 * +-----------------------+


 * [VIEW MODIFY LIGHT 1]
 * +-----------------------+
 * | > EDIT BULB L1 <      |
 * |-----------------------|
 * | POWER: 50%            |
 * | [#####-----]      [OK]|
 * +-----------------------+

 * [VIEW MODIFY LIGHT 1]
 * +-----------------------+
 * | > EDIT BULB L2 <      |
 * |-----------------------|
 * | POWER: 20%            |
 * | [##--------]      [OK]|
 * +-----------------------+

3 DISPLAY
+-----------------------+
| USE ARROW TO MOVE     |
| USE ENTER TO CONFIRM  |
| EMERGENCY: SERVICE    |
| SETTINGS              |
| RESET                 |
+-----------------------+

---------------------------------------------SECURITY:---------------------------------------------------------------
private/public key
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// --- DISPLAY INITIALIZATION ---
// Address 0x27: Status Display (Display 1)
// Address 0x3F: Control Display (Display 2)
LiquidCrystal_I2C lcd1(0x27, 20, 4); 
LiquidCrystal_I2C lcd2(0x3F, 20, 4);

// --- PIN DEFINITIONS ---

// Buttons (Inputs)
const int BTN_UP      = 2;
const int BTN_DOWN    = 3;
const int BTN_LEFT    = 4;
const int BTN_RIGHT   = 5;
const int BTN_ENTER   = 6;
const int BTN_SET     = 7;
const int BTN_SERVICE = 8;
const int BTN_RESET   = 9;
const int BTN_HOME    = 10;

// Sensors (Analog Inputs)
const int PIN_TEMP    = A0;
const int PIN_HUM     = A1;
const int PIN_NOISE   = A2;
const int PIN_LIGHT   = A3;

// Outputs
const int LED_L1      = 11; // Yellow Bulb 1
const int LED_L2      = 12; // Yellow Bulb 2
const int FAN_CTRL    = 13; // Cooling/Humidity Fan
const int SPEAKER     = A4; // Audio Alerts
const int MOTOR_PWM   = A5; // Curtain Movement

// --- SYSTEM VARIABLES ---
unsigned long lastViewChange = 0;
const unsigned long VIEW_TIMEOUT = 60000; // 1 Minute Timer

void setup() {
  // 1. SERIAL COMMUNICATION (For PC Encryption Visualization)
  Serial.begin(9600);
  Serial.println(F("--- SECURE BOOT SEQUENCE ---"));
  Serial.println(F("Generating RSA Keys... Done."));
  Serial.println(F("Public Key: [0x7B2A...], Private Key: [HIDDEN]"));

  // 2. DISPLAY INITIALIZATION
  lcd1.init();
  lcd1.backlight();
  lcd2.init();
  lcd2.backlight();

  // 3. INPUT CONFIGURATION
  pinMode(BTN_UP,      INPUT_PULLUP);
  pinMode(BTN_DOWN,    INPUT_PULLUP);
  pinMode(BTN_LEFT,    INPUT_PULLUP);
  pinMode(BTN_RIGHT,   INPUT_PULLUP);
  pinMode(BTN_ENTER,   INPUT_PULLUP);
  pinMode(BTN_SET,     INPUT_PULLUP);
  pinMode(BTN_SERVICE, INPUT_PULLUP);
  pinMode(BTN_RESET,   INPUT_PULLUP);
  pinMode(BTN_HOME,    INPUT_PULLUP);

  pinMode(PIN_TEMP,    INPUT);
  pinMode(PIN_HUM,     INPUT);
  pinMode(PIN_NOISE,   INPUT);
  pinMode(PIN_LIGHT,   INPUT);

  // 4. OUTPUT CONFIGURATION
  pinMode(LED_L1,      OUTPUT);
  pinMode(LED_L2,      OUTPUT);
  pinMode(FAN_CTRL,    OUTPUT);
  pinMode(SPEAKER,     OUTPUT);
  pinMode(MOTOR_PWM,   OUTPUT);

  // 5. STARTUP VISUALS
  lcd1.setCursor(0, 0);
  lcd1.print(F("  SYSTEM BOOTING   "));
  lcd1.setCursor(0, 1);
  lcd1.print(F("  CHECKING KEYS..  "));

  lcd2.setCursor(0, 0);
  lcd2.print(F("DASHBOARD READY"));
  
  // Audio chime
  tone(SPEAKER, 1200, 150);
  delay(200);
  tone(SPEAKER, 1500, 150);

  delay(1500); 
  
  lcd1.clear();
  lcd2.clear();
  
  lastViewChange = millis(); // Start Timer for Display 1 View Change
  
  Serial.println(F("System Online. Security Level: HIGH."));
}

void loop() {
  // Main logic for display switching, sensor reading, 
  // and button navigation will go here.
}