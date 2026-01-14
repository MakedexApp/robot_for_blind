#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import LaserScan

class LaserScanMirror:
    def __init__(self):
        rospy.init_node('laser_scan_mirror_node')

        self.sub = rospy.Subscriber('/scan', LaserScan, self.callback)
        self.pub = rospy.Publisher('/scan_flipped', LaserScan, queue_size=10)

        rospy.loginfo("🪞 LaserScan 좌우 반전 노드 실행 중 (/scan → /scan_flipped)")
        rospy.spin()

    def callback(self, msg):
        flipped = LaserScan()
        flipped.header = msg.header

        # 좌우 반전을 위한 각도 정보 반전
        flipped.angle_min = -msg.angle_max
        flipped.angle_max = -msg.angle_min
        flipped.angle_increment = -msg.angle_increment

        flipped.time_increment = msg.time_increment
        flipped.scan_time = msg.scan_time
        flipped.range_min = msg.range_min
        flipped.range_max = msg.range_max

        # ranges/intensities 반전
        flipped.ranges = list(reversed(msg.ranges))
        if msg.intensities:
            flipped.intensities = list(reversed(msg.intensities))
        else:
            flipped.intensities = []

        self.pub.publish(flipped)

if __name__ == '__main__':
    try:
        LaserScanMirror()
    except rospy.ROSInterruptException:
        pass

