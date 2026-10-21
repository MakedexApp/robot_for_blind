#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

SAFE_DISTANCE = 0.8  # 사람과 최소 거리 (m)

class SafetyFilter:
    def __init__(self):
        self.cmd_sub = rospy.Subscriber('/cmd_vel_raw', Twist, self.cmd_callback)
        self.scan_sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.obstacle_close = False
        self.last_cmd = Twist()

    def scan_callback(self, scan):
        front_ranges = scan.ranges[len(scan.ranges)//2 - 10 : len(scan.ranges)//2 + 10]
        # invalid_range_is_inf=false 라서 무효 측정값이 0.0으로 들어온다.
        # 0.0을 그대로 두면 항상 "장애물 있음"으로 판정돼 로봇이 못 움직인다.
        valid_ranges = [r for r in front_ranges if r > 0.0]
        if not valid_ranges:
            return
        front_min = min(valid_ranges)

        self.obstacle_close = front_min < SAFE_DISTANCE

    def cmd_callback(self, msg):
        if self.obstacle_close:
            self.cmd_pub.publish(Twist())  # 정지
        else:
            self.cmd_pub.publish(msg)  # 통과
            self.last_cmd = msg

if __name__ == '__main__':
    rospy.init_node('safety_filter')
    SafetyFilter()
    rospy.spin()
