#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import tf2_ros
import geometry_msgs.msg

def publish_map_to_odom():
    rospy.init_node('map_to_odom_broadcaster')
    br = tf2_ros.TransformBroadcaster()
    rate = rospy.Rate(50.0)  # 50Hz

    while not rospy.is_shutdown():
        t = geometry_msgs.msg.TransformStamped()
        t.header.stamp = rospy.Time.now()  # ROS 시간 (로봇의 다른 노드와 동기화되어야 함)
        t.header.frame_id = "map"
        t.child_frame_id = "odom"
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        br.sendTransform(t)
        rate.sleep()

if __name__ == '__main__':
    try:
        publish_map_to_odom()
    except rospy.ROSInterruptException:
        pass

