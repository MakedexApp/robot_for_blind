#!/usr/bin/env python3
import rospy
from std_msgs.msg import Int32
import time

class SpeedTester:
    def __init__(self):
        rospy.init_node("pwm_speed_tester")
        self.left_tick = 0
        self.right_tick = 0

        rospy.Subscriber("/encoder/left", Int32, self.left_callback)
        rospy.Subscriber("/encoder/right", Int32, self.right_callback)

        self.last_left = 0
        self.last_right = 0

        # 로봇 파라미터 (너가 쓰던 값 기준)
        self.wheel_radius = 0.065  # 바퀴 반지름 (m)
        self.ticks_per_rev = 3952 / 104  # encoder ticks per wheel revolution

        time.sleep(2)  # 시작 대기
        self.measure_speed()

    def left_callback(self, msg):
        self.left_tick = msg.data

    def right_callback(self, msg):
        self.right_tick = msg.data

    def ticks_to_distance(self, delta_tick):
        # 엔코더 tick → 거리 (m)
        return delta_tick * (2.0 * 3.14159 * self.wheel_radius / self.ticks_per_rev)

    def measure_speed(self):
        pwm_input = input("🛞 측정할 PWM (예: L90,R90): ")
        print("STM32에 이 명령을 수동으로 보내고 [Enter]를 누르세요.")
        input("▶ 명령 전송 후 [Enter]")

        print("⏱ 3초 동안 속도 측정 중...")
        self.last_left = self.left_tick
        self.last_right = self.right_tick
        start_time = time.time()
        time.sleep(3)
        end_time = time.time()

        delta_left = self.left_tick - self.last_left
        delta_right = self.right_tick - self.last_right
        dt = end_time - start_time

        d_left = self.ticks_to_distance(delta_left)
        d_right = self.ticks_to_distance(delta_right)

        v_left = d_left / dt
        v_right = d_right / dt
        v_avg = (v_left + v_right) / 2.0

        print("\n📊 === 측정 결과 ===")
        print(f"⏱ 측정 시간: {dt:.2f}초")
        print(f"⬅️ 왼쪽 바퀴 거리: {d_left:.3f} m, 속도: {v_left:.3f} m/s")
        print(f"➡️ 오른쪽 바퀴 거리: {d_right:.3f} m, 속도: {v_right:.3f} m/s")
        print(f"🔁 평균 속도: {v_avg:.3f} m/s")
        print("=======================================")

if __name__ == '__main__':
    try:
        SpeedTester()
    except rospy.ROSInterruptException:
        pass

