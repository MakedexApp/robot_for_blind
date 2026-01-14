#!/usr/bin/env python
import rospy
import tf
import math

if __name__ == '__main__':
    rospy.init_node('dynamic_tf_broadcaster')

    br = tf.TransformBroadcaster()
    rate = rospy.Rate(10.0)

    t = 0.0

    while not rospy.is_shutdown():
        x = 0.05 * math.sin(t)
        y = 0.05 * math.cos(t)
        br.sendTransform((x, y, 0),
                         tf.transformations.quaternion_from_euler(0, 0, 0),
                         rospy.Time.now(),
                         "base_footprint",
                         "odom")
        t += 0.05
        rate.sleep()

