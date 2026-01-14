#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32
import serial
import threading

class EncoderListener:
    def __init__(self):
        rospy.init_node('encoder_uart_listener')

        self.left_pub = rospy.Publisher('/encoder/left', Int32, queue_size=10)
        self.right_pub = rospy.Publisher('/encoder/right', Int32, queue_size=10)

        # 시리얼 포트 설정
        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)

        # 데이터 수신 스레드 시작
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.daemon = True
        self.thread.start()

    def read_loop(self):
        buffer = ""
        while not rospy.is_shutdown():
            if self.ser.in_waiting:
                buffer += self.ser.read(self.ser.in_waiting).decode(errors='ignore')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.parse_line(line.strip())

    def parse_line(self, line):
        if line.startswith("ENC_L:"):
            try:
                val = int(line.split(":")[1])
                self.left_pub.publish(val)
            except:
                pass
        elif line.startswith("ENC_R:"):
            try:
                val = int(line.split(":")[1])
                self.right_pub.publish(val)
            except:
                pass

    def spin(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        node = EncoderListener()
        node.spin()
    except rospy.ROSInterruptException:
        pass

