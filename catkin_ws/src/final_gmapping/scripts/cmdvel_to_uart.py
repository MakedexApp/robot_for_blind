#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import rospy
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
from move_base_msgs.msg import MoveBaseActionResult
import serial

class CmdVelToUART:
    def __init__(self):
        # ROS 노드 초기화
        rospy.init_node("cmdvel_to_uart")

        # UART 포트 열기 (이 노드가 단독으로 소유 -- jetson_uart_flask.py와 동시 실행 금지,
        # 같은 /dev/ttyACM0를 두 프로세스가 열면 "device busy"로 한쪽이 죽는다)
        self.serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
        self.write_lock = threading.Lock()

        # 로봇 파라미터
        self.max_speed = 0.42       # 최대 속도 (m/s)
        self.max_pwm = 90           # 최대 PWM
        self.wheel_base = 0.45      # 바퀴 간 거리 (m)

        self.goal_reached = False   # 목표 도달 상태 플래그

        # 엔코더 퍼블리셔 (기존 jetson_uart_flask.py가 하던 역할을 이 노드가 같은 UART로 흡수)
        self.pub_left = rospy.Publisher("/encoder/left", Int32, queue_size=10)
        self.pub_right = rospy.Publisher("/encoder/right", Int32, queue_size=10)
        self.read_thread = threading.Thread(target=self.read_loop)
        self.read_thread.daemon = True
        self.read_thread.start()

        # /cmd_vel 강제 정지를 위한 publisher
        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=1)

        # ROS 구독자
        rospy.Subscriber("/cmd_vel", Twist, self.cmd_callback)
        rospy.Subscriber("/move_base/result", MoveBaseActionResult, self.result_callback)

        rospy.loginfo("/cmd_vel → UART 변환 노드 시작됨 (엔코더 수신 겸용)")
        rospy.spin()

    def read_loop(self):
        buffer = ""
        while not rospy.is_shutdown():
            try:
                chunk = self.serial_port.read(64).decode("utf-8", errors="ignore")
                if not chunk:
                    continue
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.parse_line(line.strip())
            except Exception as e:
                rospy.logwarn("[UART READ] {}".format(e))

    def parse_line(self, line):
        if line.startswith("ENC_L:"):
            try:
                self.pub_left.publish(int(line.split(":")[1]))
            except ValueError:
                pass
        elif line.startswith("ENC_R:"):
            try:
                self.pub_right.publish(int(line.split(":")[1]))
            except ValueError:
                pass

    def speed_to_pwm(self, v):
        pwm = int((v / self.max_speed) * self.max_pwm)
        return max(-self.max_pwm, min(self.max_pwm, pwm))  # PWM 범위 제한

    def cmd_callback(self, msg):
        if self.goal_reached:
            rospy.loginfo("목표 도달 상태: /cmd_vel 무시됨")
            return

        v = msg.linear.x
        omega = msg.angular.z

        # 🔒 속도 0 근처면 강제 정지
        if abs(v) < 0.01 and abs(omega) < 0.01:
            pwm_left = 0
            pwm_right = 0
        else:
            v_left = v - (omega * self.wheel_base / 2.0)
            v_right = v + (omega * self.wheel_base / 2.0)

            pwm_left = self.speed_to_pwm(v_left)
            pwm_right = self.speed_to_pwm(v_right)

        cmd_str = "L{},R{}\n".format(pwm_left, pwm_right)
        self._write(cmd_str)
        rospy.loginfo("TX → {}".format(cmd_str.strip()))

    def result_callback(self, msg):
        if msg.status.status == 3:  # SUCCEEDED
            self.goal_reached = True  # 이후 /cmd_vel 무시

            # 정지 명령 3회 반복 전송
            for _ in range(3):
                self._write("L0,R0\n")
                rospy.sleep(0.05)

            rospy.loginfo("목표 도달: 모터 정지 명령 전송됨 (L0,R0 x3)")

            # /cmd_vel 강제 정지
            self.cmd_pub.publish(Twist())
            rospy.loginfo("/cmd_vel 0 메시지 강제 발행됨")

    def _write(self, data):
        try:
            with self.write_lock:
                self.serial_port.write(data.encode())
        except Exception as e:
            rospy.logwarn("UART 전송 실패: {}".format(e))


if __name__ == '__main__':
    try:
        CmdVelToUART()
    except rospy.ROSInterruptException:
        pass
