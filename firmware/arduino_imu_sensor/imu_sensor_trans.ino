#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

#define BNO055_SAMPLERATE_DELAY_MS (500)

Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29, &Wire);  // 주소는 0x28 또는 0x29 확인

void setup() {
  Serial.begin(115200);
  while (!Serial);  // Wait for serial

  if (!bno.begin()) {
    Serial.println("No BNO055 detected. Check wiring or I2C address!");
    while (1);
  }

  delay(1000);
  bno.setExtCrystalUse(true);
}

void loop() {
  sensors_event_t event;
  bno.getEvent(&event);

  uint8_t sys, gyro, accel, mag;
  bno.getCalibration(&sys, &gyro, &accel, &mag);

  // 모든 보정값이 3일 때만 전송 (방향각이 0이 아닌지로는 보정 완료를 판단할 수 없음 -
  // 로봇이 실제로 그 방향을 보고 있으면 보정 전에도 0이 아닌 값이 나오고,
  // 반대로 보정이 끝나도 방향이 0 근처면 전송이 누락됨)
  if (sys == 3 && gyro == 3 && accel == 3 && mag == 3)
  {
    Serial.print("YPR:");
    Serial.print(event.orientation.z, 1); Serial.print(",");  // Yaw
    Serial.print(event.orientation.y, 1); Serial.print(",");  // Pitch
    Serial.println(event.orientation.x, 1);                   // Roll
  }
  delay(BNO055_SAMPLERATE_DELAY_MS);
}
