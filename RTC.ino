#include <Wire.h>
#include <RTClib.h>

RTC_DS1307 rtc;

void setup() {
  Serial.begin(9600);

  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }

  // ⚠️ Set the time manually (Year, Month, Day, Hour, Minute, Second)
  rtc.adjust(DateTime(2025, 2, 21, 11, 47, 0)); // Change this to current date & time
  Serial.println("RTC time set!");
}

void loop() {
}

/*
#include <Wire.h>
#include <RTClib.h>

RTC_DS1307 rtc;

void setup() {
  Serial.begin(9600);
  
  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC!");
    while (1);
  }

  if (!rtc.isrunning()) {
    Serial.println("RTC is NOT running!");
  }
}

void loop() {
  DateTime now = rtc.now();
  
  Serial.print("Time: ");
  Serial.print(now.hour());
  Serial.print(":");
  Serial.print(now.minute());
  Serial.print(":");
  Serial.println(now.second());

  delay(1000);
}
*/
