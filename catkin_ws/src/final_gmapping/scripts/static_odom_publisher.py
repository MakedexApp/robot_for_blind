#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
import tf
from nav_msgs.msg import Odometry
import math

rospy.init_node('fake_odom')
odom_pub = rospy.Publisher('/odom', Odometry, queue_size=10)
odom_broadcaster = tf.TransformBroadcaster()
rate = rospy.Rate(10)

x, y, theta = 0.0, 0.0, 0.0
linear_speed = 0.05      # m/s (전진 속도)
angular_speed = 0.05     # rad/s (회전 속도)
dt = 0.1                 # 10Hz 주기

while not rospy.is_shutdown():
    now = rospy.Time.now()

    # 위치 업데이트 (x, y, theta)
    dx = linear_speed * math.cos(theta) * dt
    dy = linear_speed * math.sin(theta) * dt
    dtheta = angular_speed * dt

    x += dx
    y += dy
    theta += dtheta

    quaternion = tf.transformations.quaternion_from_euler(0, 0, theta)

    # TF 퍼블리시
    odom_broadcaster.sendTransform(
        (x, y, 0.0),
        quaternion,
        now,
        "base_footprint",
        "odom"
    )

    # 메시지 퍼블리시
    odom = Odometry()
    odom.header.stamp = now
    odom.header.frame_id = "odom"
    odom.child_frame_id = "base_footprint"
    odom.pose.pose.position.x = x
    odom.pose.pose.position.y = y
    odom.pose.pose.position.z = 0.0
    odom.pose.pose.orientation.x = quaternion[0]
    odom.pose.pose.orientation.y = quaternion[1]
    odom.pose.pose.orientation.z = quaternion[2]
    odom.pose.pose.orientation.w = quaternion[3]
    odom_pub.publish(odom)

    rate.sleep()

