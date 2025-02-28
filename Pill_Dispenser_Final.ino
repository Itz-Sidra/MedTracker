#include <Wire.h>
#include <Servo.h>
#include <LiquidCrystal_I2C.h>
#include <RTClib.h>

Servo servo;
RTC_DS3231 rtc;
LiquidCrystal_I2C lcd(0x27, 16, 2);

const int servoPin = 9;
const int buzzerPin = 10;
const int ledYellow = 8;
const int ledGreen = 7;
const int ledRed = 6;
const int irSensorPin = 2;

// Modified to store exactly 4 medication times
const int MAX_SCHEDULES = 4;
String scheduledTimes[MAX_SCHEDULES];
String medNames[MAX_SCHEDULES];
int scheduleCount = 0;

void setup() {
  pinMode(servoPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(ledYellow, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  pinMode(ledRed, OUTPUT);
  pinMode(irSensorPin, INPUT);

  Serial.begin(9600);
  
  // Wait for serial connection to establish
  delay(1000);
  
  lcd.init();
  lcd.backlight();
  servo.attach(servoPin);
  servo.write(0);

  if (!rtc.begin()) {
    Serial.println("ERROR:RTC");
    lcd.setCursor(0, 0);
    lcd.print("RTC Error");
    while (1);
  }

  if (rtc.lostPower()) {
    rtc.adjust(DateTime(__DATE__, __TIME__));
  }
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Med Dispenser");
  lcd.setCursor(0, 1);
  lcd.print("Ready");
  
  // Send ready message to Flet app
  Serial.println("ARDUINO:READY");
}

void checkSerial() {
 if (Serial.available() > 0) {
        String data = Serial.readStringUntil('\n');
        data.trim();

        // Check for DELETE command
        if (data.startsWith("DELETE:")) {
            int index = data.substring(7).toInt();
            if (index >= 0 && index < scheduleCount) {
                // Shift all schedules up
                for (int i = index; i < scheduleCount - 1; i++) {
                    scheduledTimes[i] = scheduledTimes[i + 1];
                    medNames[i] = medNames[i + 1];
                }
                scheduleCount--;
                Serial.println("DELETED:SUCCESS");
                return;
            }
            Serial.println("ERROR:INVALID_INDEX");
            return;
        }

        if (data.length() >= 5 && data.charAt(2) == ':') {
            if (scheduleCount < MAX_SCHEDULES) {
                // Check for duplicate schedule
                for (int i = 0; i < scheduleCount; i++) {
                    if (scheduledTimes[i] == data) {
                        Serial.println("ERROR:DUPLICATE_TIME");
                        return;
                    }
                }

                int nameIndex = data.indexOf(':', 3);
                if (nameIndex != -1) {
                    scheduledTimes[scheduleCount] = data.substring(0, nameIndex);
                    medNames[scheduleCount] = data.substring(nameIndex + 1);
                } else {
                    scheduledTimes[scheduleCount] = data;
                    medNames[scheduleCount] = "Medication";
                }

                scheduleCount++;
        
                // Confirm receipt
                Serial.print("ADDED:");
                Serial.println(scheduledTimes[scheduleCount-1]);
        
                lcd.clear();
                lcd.setCursor(0, 0);
                lcd.print("New Schedule:");
                lcd.setCursor(0, 1);
                lcd.print(scheduledTimes[scheduleCount-1]);
                delay(2000);
            } else {
                // Schedule full
                Serial.println("ERROR:SCHEDULE_FULL");
            }
        } else if (data == "LIST") {
            // New command to list all schedules
            Serial.println("SCHEDULE_LIST_BEGIN");
            for (int i = 0; i < scheduleCount; i++) {
                Serial.print(i);
                Serial.print(":");
                Serial.print(scheduledTimes[i]);
                Serial.print(":");
                Serial.println(medNames[i]);
            }
            Serial.println("SCHEDULE_LIST_END");
        }
    }
}

void loop() {
  // Process any incoming commands
  checkSerial();
  
  // Check if it's time to dispense
  checkSchedules();
  
  // Update the display every 2 seconds
  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate > 2000) {
    updateLCD();
    lastUpdate = millis();
  }
}

void checkSchedules() {
  DateTime now = rtc.now();
  String currentTime = formatTime(now.hour(), now.minute());
  
  for (int i = 0; i < scheduleCount; i++) {
    if (scheduledTimes[i] == currentTime) {
      dispensePill(i);
    }
  }
}

void dispensePill(int scheduleIndex) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Time to take:");
  lcd.setCursor(0, 1);
  lcd.print(medNames[scheduleIndex]);
  
  // Beep alert
  for (int i = 0; i < 3; i++) {
    tone(buzzerPin, 1000);
    delay(300);
    noTone(buzzerPin);
    delay(200);
  }
  
  // Activate dispenser - modified to rotate 45 degrees for 4 compartments
  digitalWrite(ledYellow, HIGH);
  
  // Calculate angle based on medication index (0-3) - 45 degrees per compartment
  int angle = 45 * (scheduleIndex + 1);
  
  servo.write(angle);
  delay(1000);
  servo.write(0);
  delay(1000);
  digitalWrite(ledYellow, LOW);
  
  // Check if pill was dispensed
  if (digitalRead(irSensorPin) == LOW) {
    digitalWrite(ledGreen, HIGH);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Pill Dispensed");
    lcd.setCursor(0, 1);
    lcd.print("Take your Medicine!");
    
    // Wait one minute and check if pill was taken
    unsigned long startTime = millis();
    while (millis() - startTime < 60000) {  // 60000ms = 1 minute
      // If pill is taken (IR sensor no longer detecting)
      if (digitalRead(irSensorPin) == HIGH) {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Pill Taken");
        lcd.setCursor(0, 1);
        lcd.print("Successfully!");
        digitalWrite(ledGreen, LOW);
        
        // Notify Flet app
        Serial.print("TAKEN:");
        Serial.println(scheduledTimes[scheduleIndex]);
        return;
      }
      delay(100);  // Small delay to prevent overwhelming the processor
    }
    
    // If we get here, pill wasn't taken within one minute
    if (digitalRead(irSensorPin) == LOW){
      digitalWrite(ledGreen, LOW);
      digitalWrite(ledRed, HIGH);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Warning:");
      lcd.setCursor(0, 1);
      lcd.print("Pill Not Taken!");
    
      // Sound alarm
      for (int i = 0; i < 5; i++) {
        tone(buzzerPin, 2000);
        delay(500);
        noTone(buzzerPin);
        delay(200);
      }
    
      digitalWrite(ledRed, LOW);
    }
    
    // Notify Flet app
    Serial.print("NOT_TAKEN:");
    Serial.println(scheduledTimes[scheduleIndex]);
    
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Dispense Error!");
    flashLED(ledRed, 5, 300);
    
    // Notify Flet app of error
    Serial.print("ERROR:");
    Serial.println(scheduledTimes[scheduleIndex]);
  }
}

void flashLED(int ledPin, int numFlashes, int flashDelay) {
  for (int i = 0; i < numFlashes; i++) {
    digitalWrite(ledPin, HIGH);
    delay(flashDelay);
    digitalWrite(ledPin, LOW);
    delay(flashDelay);
  }
}

void updateLCD() {
  DateTime now = rtc.now();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Time: ");
  lcd.print(formatTime(now.hour(), now.minute()));
  
  if (scheduleCount > 0) {
    lcd.setCursor(0, 1);
    lcd.print("Doses: ");
    lcd.print(scheduleCount);
    lcd.print("/");
    lcd.print(MAX_SCHEDULES);
  } else {
    lcd.setCursor(0, 1);
    lcd.print("No schedules");
  }
}

String formatTime(int hour, int minute) {
  String h = (hour < 10) ? "0" + String(hour) : String(hour);
  String m = (minute < 10) ? "0" + String(minute) : String(minute);
  return h + ":" + m;
}
