int irSensorPin = 2; // IR sensor connected to digital pin D2
bool pillDispensed = false;

void setup() {
    Serial.begin(9600);
    pinMode(irSensorPin, INPUT);
}

void loop() {
    int sensorValue = digitalRead(irSensorPin);

    // Step 1: Detect pill arrival
    if (sensorValue == LOW && !pillDispensed) {
        Serial.println("Pill Dispensed! Please take your medicine.");
        pillDispensed = true;  // Mark pill as dispensed
    }

    // Step 2: Detect if the pill has been picked up
    if (sensorValue == HIGH && pillDispensed) {
        Serial.println("Pill Taken! Ready for the next dose.");
        pillDispensed = false;  // Reset for the next cycle
    }

    delay(500); // Small delay to avoid false triggers
}
