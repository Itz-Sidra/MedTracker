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
const int irSensorPin = 5;

// Store up to 5 medication times
const int MAX_SCHEDULES = 5;
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
    
    // Look for time format (HH:MM) or enhanced format (HH:MM:NAME)
    if (data.length() >= 5 && data.charAt(2) == ':') {
      if (scheduleCount < MAX_SCHEDULES) {
        // Check if it contains medication name
        int nameIndex = data.indexOf(':', 3);
        if (nameIndex != -1) {
          // Enhanced format with name
          scheduledTimes[scheduleCount] = data.substring(0, nameIndex);
          medNames[scheduleCount] = data.substring(nameIndex + 1);
        } else {
          // Simple time format
          scheduledTimes[scheduleCount] = data;
          medNames[scheduleCount] = "Medication";  // Default name
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
  
  // Activate dispenser
  digitalWrite(ledYellow, HIGH);
  servo.write(90);
  delay(1000);
  servo.write(0);
  delay(1000);
  digitalWrite(ledYellow, LOW);
  
  // Check if pill was dispensed
  if (digitalRead(irSensorPin) == LOW) {
    digitalWrite(ledGreen, HIGH);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Pill Dispensed!");
    delay(3000);
    digitalWrite(ledGreen, LOW);
    
    // Notify Flet app
    Serial.print("DISPENSED:");
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