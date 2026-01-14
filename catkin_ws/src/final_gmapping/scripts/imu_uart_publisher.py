#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import serial
import threading
import math
from sensor_msgs.msg import Imu
from tf.transformations import quaternion_from_euler

class IMUUARTPublisher:
    def __init__(self, port="/dev/ttyACM1", baudrate=115200):
        rospy.init_node("imu_uart_publisher", anonymous=True)
        self.pub_imu = rospy.Publisher("/imu/data_raw", Imu, queue_size=10)
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        self.buffer = ""
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.daemon = True
        self.thread.start()

    def read_loop(self):
        while not rospy.is_shutdown():
            try:
                data = self.ser.read(64).decode("utf-8", errors="ignore")
                self.buffer += data
                while '\n' in self.buffer:
                    line, self.buffer = self.buffer.split('\n', 1)
                    self.parse_line(line.strip())
            except Exception as e:
                rospy.logwarn("[IMU UART READ ERROR] %s" % str(e))

    def parse_line(self, line):
        if line.startswith("YPR:"):
            try:
                ypr = line.replace("YPR:", "").split(",")
                if len(ypr) != 3:
                    return

                yaw_deg = float(ypr[0])
                pitch_deg = float(ypr[1])
                roll_deg = float(ypr[2])

                yaw = math.radians(yaw_deg)
                pitch = math.radians(pitch_deg)
                roll = math.radians(roll_deg)

                q = quaternion_from_euler(roll, pitch, yaw)

                imu_msg = Imu()
                imu_msg.header.stamp = rospy.Time.now()
                imu_msg.header.frame_id = "imu_link"
                imu_msg.orientation.x = q[0]
                imu_msg.orientation.y = q[1]
                imu_msg.orientation.z = q[2]
                imu_msg.orientation.w = q[3]
                imu_msg.orientation_covariance[0] = -1

                imu_msg.angular_velocity.x = 0.0
                imu_msg.angular_velocity.y = 0.0
                imu_msg.angular_velocity.z = 0.0
                imu_msg.angular_velocity_covariance[0] = -1

                imu_msg.linear_acceleration.x = 0.0
                imu_msg.linear_acceleration.y = 0.0
                imu_msg.linear_acceleration.z = 0.0
                imu_msg.linear_acceleration_covariance[0] = -1

                self.pub_imu.publish(imu_msg)
                rospy.loginfo("[IMU] YPR(deg): Y=%.1f, P=%.1f, R=%.1f" % (yaw_deg, pitch_deg, roll_deg))
            except Exception as e:
                rospy.logwarn("[IMU PARSE ERROR] %s" % str(e))

if __name__ == "__main__":
    try:
        IMUUARTPublisher(port="/dev/ttyACM1")
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

