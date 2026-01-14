#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import rospy
import tf
from nav_msgs.msg import Odometry
from std_msgs.msg import Int32

class OdomPublisher:
    def __init__(self):
        rospy.init_node('encoder_odometry_publisher')

        self.left_sub = rospy.Subscriber('/encoder/left', Int32, self.left_callback)
        self.right_sub = rospy.Subscriber('/encoder/right', Int32, self.right_callback)
        self.odom_pub = rospy.Publisher('/odom', Odometry, queue_size=10)
        self.odom_broadcaster = tf.TransformBroadcaster()

        self.left_tick = 0
        self.right_tick = 0
        self.last_time = rospy.Time.now()

        # 로봇 파라미터
        self.wheel_radius = 0.065   # 바퀴 반지름 (단위: m)
        self.ticks_per_rev = 3952/104    # 엔코더 해상도 (PPR)
        self.wheel_base = 0.55       # 바퀴 간 거리 (단위: m)

        self.x = 0.0
        self.y = 0.0
        self.th = 0.0

    def left_callback(self, msg):
        self.left_tick = msg.data

    def right_callback(self, msg):
        self.right_tick = msg.data

    def spin(self):
        rate = rospy.Rate(10)
        last_left = self.left_tick
        last_right = self.right_tick

        while not rospy.is_shutdown():
            now = rospy.Time.now()
            dt = (now - self.last_time).to_sec()
            self.last_time = now

            delta_left = self.left_tick - last_left
            delta_right = self.right_tick - last_right
            last_left = self.left_tick
            last_right = self.right_tick

            # 엔코더 tick → 거리 (meter)
            distance_per_tick = 2.0 * 3.14159 * self.wheel_radius / self.ticks_per_rev
            d_left = delta_left * distance_per_tick
            d_right = delta_right * distance_per_tick

            d_center = (d_left + d_right) / 2.0
            d_theta = (d_right - d_left) / self.wheel_base

            self.x += d_center * math.cos(self.th + d_theta / 2.0)
            self.y += d_center * math.sin(self.th + d_theta / 2.0)
            self.th += d_theta

            # Odometry 메시지 생성
            odom = Odometry()
            odom.header.stamp = now
            odom.header.frame_id = "odom"
            odom.child_frame_id = "base_footprint"

            odom.pose.pose.position.x = self.x
            odom.pose.pose.position.y = self.y
            odom.pose.pose.position.z = 0.0
            q = tf.transformations.quaternion_from_euler(0, 0, self.th)
            odom.pose.pose.orientation.x = q[0]
            odom.pose.pose.orientation.y = q[1]
            odom.pose.pose.orientation.z = q[2]
            odom.pose.pose.orientation.w = q[3]

            # 퍼블리시
            self.odom_pub.publish(odom)
            self.odom_broadcaster.sendTransform(
                (self.x, self.y, 0),
                tf.transformations.quaternion_from_euler(0, 0, self.th),
                rospy.Time.now(),
                "base_footprint",
                "odom"
            )

            rate.sleep()

if __name__ == '__main__':
    try:
        node = OdomPublisher()
        node.spin()
    except rospy.ROSInterruptException:
        pass

