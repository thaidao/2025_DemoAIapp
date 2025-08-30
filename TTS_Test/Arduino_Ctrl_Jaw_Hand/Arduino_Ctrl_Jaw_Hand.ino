#include <Servo.h>

Servo jawServo;
Servo handServo;

String inputString = "";
bool readingMessage = false;

void setup() {
  Serial.begin(9600);

  jawServo.attach(9);   // Pin for JAW servo
  handServo.attach(10); // Pin for HAND servo

  jawServo.write(90);   // Initialize neutral position
  handServo.write(90);
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '<') {
      inputString = "";
      readingMessage = true;
    } else if (c == '>') {
      readingMessage = false;
      processMessage(inputString);
    } else if (readingMessage) {
      inputString += c;
    }
  }
}

void processMessage(String msg) {
  // Example: "JAW:45:100|HAND:90:0"
  int jawAngle = 90, jawDur = 0;
  int handAngle = 90, handDur = 0;

  // Split by '|'
  int sep = msg.indexOf('|');
  String jawPart = msg.substring(0, sep);
  String handPart = msg.substring(sep + 1);

  // Parse JAW
  if (jawPart.startsWith("JAW:")) {
    jawPart.remove(0, 4);
    int firstColon = jawPart.indexOf(':');
    jawAngle = jawPart.substring(0, firstColon).toInt();
    jawDur = jawPart.substring(firstColon + 1).toInt();
  }

  // Parse HAND
  if (handPart.startsWith("HAND:")) {
    handPart.remove(0, 5);
    int firstColon = handPart.indexOf(':');
    handAngle = handPart.substring(0, firstColon).toInt();
    handDur = handPart.substring(firstColon + 1).toInt();
  }

  // Move servos
  jawServo.write(jawAngle);
  handServo.write(handAngle);

  if (jawDur > 0 || handDur > 0) {
    delay(max(jawDur, handDur));
    // Return to neutral after movement
    jawServo.write(90);
    handServo.write(90);
  }
}
