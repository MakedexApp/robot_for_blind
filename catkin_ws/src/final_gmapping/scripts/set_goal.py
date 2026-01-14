#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
import json
import os
from geometry_msgs.msg import PoseStamped

# 목적지 이름으로부터 좌표를 가져오는 함수
def load_destination_coordinates(dest_name):
    with open("/home/jetson/Desktop/destinations.json", "r") as f:
        data = json.load(f)
        if dest_name in data:
            return data[dest_name]
        else:
            return None

def read_goal_name():
    if not os.path.exists("/home/jetson/goal.json"):
        return None
    with open("/home/jetson/goal.json", "r") as f:
        try:
            goal_data = json.load(f)
            return goal_data.get("destination")
        except:
            return None

def send_goal():
    rospy.init_node('goal_sender', anonymous=True)
    pub = rospy.Publisher('/move_base/goal', PoseStamped, queue_size=1)

    rate = rospy.Rate(1)  # 1Hz
    last_goal = None

    while not rospy.is_shutdown():
        current_goal = read_goal_name()

        # 새 목적지 요청이 들어왔을 때만 실행
        if current_goal and current_goal != last_goal:
            coords = load_destination_coordinates(current_goal)
            if coords is None:
                rospy.logwarn("❌ destination.json에 '{}'에 해당하는 좌표가 없습니다.".format(current_goal))
                last_goal = current_goal
                continue

            goal = PoseStamped()
            goal.header.frame_id = "map"
            goal.header.stamp = rospy.Time.now()

            goal.pose.position.x = coords["x"]
            goal.pose.position.y = coords["y"]
            goal.pose.position.z = 0.0

            # yaw → quaternion 변환 (기본은 yaw=0 → z=0, w=1)
            goal.pose.orientation.x = 0.0
            goal.pose.orientation.y = 0.0
            goal.pose.orientation.z = coords.get("z", 0.0)
            goal.pose.orientation.w = coords.get("w", 1.0)

            pub.publish(goal)
            rospy.loginfo("📍 목적지 '{}' (x: {}, y: {})로 이동합니다.".format(
                current_goal, coords["x"], coords["y"]))

            last_goal = current_goal

        rate.sleep()

if __name__ == '__main__':
    try:
        send_goal()
    except rospy.ROSInterruptException:
        pass
