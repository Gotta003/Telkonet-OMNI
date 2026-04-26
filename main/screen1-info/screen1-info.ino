#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2); 

int lastState = -1; 

void setup() {
  lcd.init();
  lcd.backlight();
}

void loop() {
  int currentState = (millis() / 10000) % 4;

  if (currentState != lastState) {
    lcd.clear();
    
    switch (currentState) {
      case 0: // SCREEN 1: welcome
        lcd.setCursor(0, 0);
        lcd.print("--- WELCOME! ---");
        lcd.setCursor(0, 1);
        lcd.print("STATUS: IDLE... ");
        break;

      case 1: // SCREEN 2: data modified
        lcd.setCursor(0, 0);
        lcd.print("LAST MODIFIED:");
        lcd.setCursor(0, 1);
        lcd.print("  15/04/2026   ");
        break;

      case 2: // SCREEN 3: istruction
        lcd.setCursor(0, 0);
        lcd.print("ARROW: MOVE      ");
        lcd.setCursor(0, 1);
        lcd.print("ENTER: CONFIRM   ");
        break;

      case 3: // SCREEN 4: menu
        lcd.setCursor(0, 0);
        lcd.print("EMERGENCY SERV.");
        lcd.setCursor(0, 1);
        lcd.print(" SETTINGS|RESET ");
        break;
    }
    lastState = currentState;
  }
}