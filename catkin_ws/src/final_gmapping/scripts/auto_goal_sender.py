#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped

goal_positions = {
    '화장실': (47.956, 2.661),
    '출입구': (5.0, 2.0),
    '라운지': (16.029, 0.939),
    '안내데스크': (1.0, 1.0),  # voice_to_destination.py의 valid_places 표기와 맞춰 공백 제거
    '엘리베이터': (3.0, 7.0),
    '식당': (20.641, 1.617),
    '의무실': (3.0, 7.0),
}

def destination_callback(msg):
    dest = msg.data.strip()
    if dest in goal_positions:
        x, y = goal_positions[dest]

        goal = PoseStamped()
        goal.header.frame_id = "map"
        goal.header.stamp = rospy.Time.now()
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.position.z = 0.0
        goal.pose.orientation.z = 0.0
        goal.pose.orientation.w = 1.0

        goal_pub.publish(goal)
        rospy.loginfo("🎯 목적지 '%s'로 주행 시작: x=%.2f, y=%.2f", dest, x, y)
    else:
        rospy.logwarn("❗알 수 없는 목적지: '%s'", dest)

if __name__ == '__main__':
    rospy.init_node('destination_listener', anonymous=True)
    goal_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=1)
    rospy.Subscriber('/destination', String, destination_callback)
    print(String)
    rospy.loginfo("📡 '/destination' 토픽 구독 중...")
    rospy.spin()
