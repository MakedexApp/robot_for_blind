#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import rospy
import serial
from std_msgs.msg import Int32
from sensor_msgs.msg import Imu
import tf
import math

# UART 포트 설정
PORT = '/dev/ttyTHS1'
BAUD = 115200

# ROS 노드 초기화
rospy.init_node("stm32_uart_parser", anonymous=True)

# 퍼블리셔 생성
pub_left = rospy.Publisher("/encoder/left", Int32, queue_size=10)
pub_right = rospy.Publisher("/encoder/right", Int32, queue_size=10)
pub_imu = rospy.Publisher("/imu/data_raw", Imu, queue_size=10)

# TF broadcaster
br = tf.TransformBroadcaster()

# 시리얼 포트 열기
try:
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    rospy.loginfo("Serial port opened on {}".format(PORT))
except Exception as e:
    rospy.logerr("Serial port error: {}".format(e))
    exit()

rate = rospy.Rate(50)
buffer = ""

while not rospy.is_shutdown():
    try:
        if ser.in_waiting:
            buffer += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')

            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()

                if line.startswith("ENC_L:"):
                    try:
                        val = int(line.split(":")[1])
                        pub_left.publish(val)
                        rospy.loginfo("Left encoder: {}".format(val))
                    except:
                        pass

                elif line.startswith("ENC_R:"):
                    try:
                        val = int(line.split(":")[1])
                        pub_right.publish(val)
                        rospy.loginfo("Right encoder: {}".format(val))
                    except:
                        pass

                elif line.startswith("IMU_YAW:"):
                    try:
                        yaw_deg = float(line.split(":")[1])
                        yaw_rad = math.radians(yaw_deg)

                        imu_msg = Imu()
                        imu_msg.header.stamp = rospy.Time.now()
                        imu_msg.header.frame_id = "imu_link"

                        quaternion = tf.transformations.quaternion_from_euler(0, 0, yaw_rad)
                        imu_msg.orientation.x = quaternion[0]
                        imu_msg.orientation.y = quaternion[1]
                        imu_msg.orientation.z = quaternion[2]
                        imu_msg.orientation.w = quaternion[3]

                        pub_imu.publish(imu_msg)

                        br.sendTransform(
                            (0, 0, 0),
                            quaternion,
                            rospy.Time.now(),
                            "imu_link",
                            "base_footprint"
                        )

                        rospy.loginfo("IMU Yaw: {:.2f} deg".format(yaw_deg))
                    except:
                        pass

    except Exception as e:
        rospy.logerr("UART read error: {}".format(e))

    rate.sleep()

