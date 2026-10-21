# Firmware

Jetson(`catkin_ws/src/final_gmapping`)과 UART로 묶이는 하드웨어 쪽 코드 모음.

## stm32_motor_control/

STM32CubeIDE 프로젝트 (`motor_control_for_mapping.ioc`로 STM32CubeIDE에서 열기).

- USART2, 115200bps, Jetson의 `/dev/ttyACM0`와 연결
- 수신: `"L%d,R%d\n"` → `set_motor_pwm()` / `smooth_motor_pwm()`으로 모터 PWM·방향 제어
  - 송신 측: `catkin_ws/src/final_gmapping/scripts/cmdvel_to_uart.py`
- 송신: 1초마다 `"ENC_L:%d\nENC_R:%d\n"` (엔코더 누적값)
  - 수신 측: 같은 `cmdvel_to_uart.py`의 `read_loop()` / `parse_line()`

## arduino_imu_sensor/

Arduino + BNO055(IMU) 스케치. STM32와는 별개의 보드.

- Serial 115200bps, Jetson의 `/dev/ttyACM1`과 연결
- 송신: 500ms마다 `"YPR:yaw,pitch,roll\n"` (보정 완료 시에만)
  - 수신 측: `catkin_ws/src/final_gmapping/scripts/imu_uart_publisher.py`
