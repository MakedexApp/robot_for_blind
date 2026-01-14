#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import message_filters
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry

# 라이다와 오도메트리 데이터 동기화 처리 함수
def callback(lidar_data, odom_data):
    rospy.loginfo("LIDAR and Odometry synchronized")

def listener():
    # ROS 노드 초기화
    rospy.init_node('sync_listener', anonymous=True)

    # 라이다와 오도메트리 데이터 구독
    lidar_sub = message_filters.Subscriber("/scan", LaserScan)
    odom_sub = message_filters.Subscriber("/odom", Odometry)

    # 0.1초 차이 이내로 동기화 설정
    ts = message_filters.ApproximateTimeSynchronizer([lidar_sub, odom_sub], queue_size=10, slop=0.1)
    ts.registerCallback(callback)

    # ROS 스핀을 실행하여 콜백 대기
    rospy.spin()

if __name__ == '__main__':
    listener()

