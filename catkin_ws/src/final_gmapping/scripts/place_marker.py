#!/usr/bin/env python
import rospy
from visualization_msgs.msg import Marker

rospy.init_node("place_label_publisher")
pub = rospy.Publisher("visualization_marker", Marker, queue_size=10)

marker = Marker()
marker.header.frame_id = "map"
marker.header.stamp = rospy.Time.now()
marker.ns = "place_names"
marker.id = 0
marker.type = Marker.TEXT_VIEW_FACING
marker.action = Marker.ADD
marker.pose.position.x = 6.717
marker.pose.position.y = 1.209
marker.pose.position.z = 0.0
marker.scale.z = 0.5
marker.color.a = 1.0
marker.color.r = 1.0
marker.color.g = 1.0
marker.color.b = 1.0
marker.text = "Kitchen"

rate = rospy.Rate(1)
while not rospy.is_shutdown():
    pub.publish(marker)
    rate.sleep()

