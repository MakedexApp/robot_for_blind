#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from geometry_msgs.msg import PoseWithCovarianceStamped

def publish_initial_pose():
    rospy.init_node('set_initial_pose')
    pub = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size=1)
    rospy.sleep(1.0)  # 퍼블리셔 안정화 대기

    msg = PoseWithCovarianceStamped()
    msg.header.frame_id = "map"
    msg.header.stamp = rospy.Time.now()

    # 출발 위치 지정 (예: x=0.5, y=0.5)
    msg.pose.pose.position.x = 0.0
    msg.pose.pose.position.y = 0.0
    msg.pose.pose.position.z = 0.0
    msg.pose.pose.orientation.w = 1.0

    # 위치/자세에 대한 추정 오차 (작게 줘야 빠르게 수렴함)
    msg.pose.covariance = [0.25, 0, 0, 0, 0, 0,
                           0, 0.25, 0, 0, 0, 0,
                           0, 0, 0.0, 0, 0, 0,
                           0, 0, 0, 0.0, 0, 0,
                           0, 0, 0, 0, 0.0, 0,
                           0, 0, 0, 0, 0, 0.068]

    rospy.loginfo(" 2D Pose Estimate 자동 퍼블리시 완료")
    pub.publish(msg)

if __name__ == '__main__':
    try:
        publish_initial_pose()
    except rospy.ROSInterruptException:
        pass

