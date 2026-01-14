#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from sensor_msgs.msg import LaserScan
import math

class FlipFrontBack:
    def __init__(self):
        rospy.init_node("laser_frontback_flip")

        rospy.Subscriber("/scan", LaserScan, self.callback)
        self.pub = rospy.Publisher("/scan_flipped", LaserScan, queue_size=10)

        rospy.loginfo("🔁 LaserScan 앞뒤 반전 노드 실행됨")
        rospy.spin()

    def callback(self, msg):
        n = len(msg.ranges)
        shift = n // 2

        flipped = LaserScan()
        flipped.header = msg.header
        flipped.angle_min = msg.angle_min + math.pi
        flipped.angle_max = msg.angle_max + math.pi
        flipped.angle_increment = msg.angle_increment
        flipped.time_increment = msg.time_increment
        flipped.scan_time = msg.scan_time
        flipped.range_min = msg.range_min
        flipped.range_max = msg.range_max

        flipped.ranges = msg.ranges[shift:] + msg.ranges[:shift]

        if msg.intensities:
            flipped.intensities = msg.intensities[shift:] + msg.intensities[:shift]
        else:
            flipped.intensities = []

        self.pub.publish(flipped)

if __name__ == '__main__':
    try:
        FlipFrontBack()
    except rospy.ROSInterruptException:
        pass

