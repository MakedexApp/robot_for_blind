#!/usr/bin/env python
import rospy
import tf2_ros
import geometry_msgs.msg

if __name__ == '__main__':
    rospy.init_node('map_to_odom_broadcaster')

    br = tf2_ros.TransformBroadcaster()
    rate = rospy.Rate(30.0)  # 30Hz

    while not rospy.is_shutdown():
        t = geometry_msgs.msg.TransformStamped()
        t.header.stamp = rospy.Time.now()
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

