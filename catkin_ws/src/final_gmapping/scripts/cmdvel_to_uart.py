#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
from move_base_msgs.msg import MoveBaseActionResult
import serial

class CmdVelToUART:
    def __init__(self):
        # /cmd_vel 강제 정지를 위한 publisher
        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=1)

        # ROS 노드 초기화
        rospy.init_node("cmdvel_to_uart")

        # UART 포트 열기
        self.serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)

        # 로봇 파라미터
        self.max_speed = 0.42       # 최대 속도 (m/s)
        self.max_pwm = 90           # 최대 PWM
        self.wheel_base = 0.45      # 바퀴 간 거리 (m)

        self.goal_reached = False   # 목표 도달 상태 플래그

        # ROS 구독자
        rospy.Subscriber("/cmd_vel", Twist, self.cmd_callback)
        rospy.Subscriber("/move_base/result", MoveBaseActionResult, self.result_callback)

        rospy.loginfo("/cmd_vel → UART 변환 노드 시작됨")
        rospy.spin()

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

        try:
            self.serial_port.write(cmd_str.encode())
            rospy.loginfo("TX → {}".format(cmd_str.strip()))
        except Exception as e:
            rospy.logwarn("UART 전송 실패: {}".format(e))

    def result_callback(self, msg):
        if msg.status.status == 3:  # SUCCEEDED
            self.goal_reached = True  # 이후 /cmd_vel 무시

            try:
                # 정지 명령 3회 반복 전송
                for _ in range(3):
                    self.serial_port.write(b"L0,R0\n")
                    rospy.sleep(0.05)

                rospy.loginfo("목표 도달: 모터 정지 명령 전송됨 (L0,R0 x3)")

                # /cmd_vel 강제 정지
                stop_msg = Twist()
                self.cmd_pub.publish(stop_msg)
                rospy.loginfo("/cmd_vel 0 메시지 강제 발행됨")

            except Exception as e:
                rospy.logwarn("정지 처리 실패: {}".format(e))


if __name__ == '__main__':
    try:
        CmdVelToUART()
    except rospy.ROSInterruptException:
        pass
