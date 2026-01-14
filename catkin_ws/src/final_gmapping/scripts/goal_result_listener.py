#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from move_base_msgs.msg import MoveBaseActionResult
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from gtts_module import speak
from stt import listen
from gptapi import extract_destination_from_text
import time

class GoalResultHandler:
    def __init__(self):
        rospy.init_node('goal_result_listener', anonymous=True)

        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.dest_pub = rospy.Publisher('/destination', String, queue_size=1)

        rospy.Subscriber('/move_base/result', MoveBaseActionResult, self.goal_result_callback)
        rospy.loginfo("📡 목적지 도착 감지 노드 실행 중...")

        self.valid_places = ["안내 데스크", "화장실", "엘리베이터", "출입구", "식당", "라운지", "의무실"]
        self.default_destination = "안내 데스크"

    def goal_result_callback(self, msg):
        if msg.status.status == 3:  # SUCCEEDED
            rospy.loginfo("✅ 목적지 도착 완료")

            # 1. 정지
            stop = Twist()
            self.cmd_pub.publish(stop)

            # 2. 안내
            speak("목적지에 도착했습니다. 다음 목적지를 말씀해주세요.")

            # 3. 명령 대기 (최대 60초)
            start_time = time.time()
            while not rospy.is_shutdown():
                if time.time() - start_time > 60:
                    # 1분 이상 응답 없으면 복귀
                    speak("응답이 없어 안내 데스크로 돌아갑니다.")
                    self.dest_pub.publish(self.default_destination)
                    return

                user_input = listen()
                if user_input:
                    if "종료" in user_input:
                        speak("안내를 종료합니다.")
                        rospy.signal_shutdown("종료 명령 수신")
                        return

                    dest = extract_destination_from_text(user_input)
                    rospy.loginfo("🧭 추론된 목적지: %s", dest)

                    if dest in self.valid_places:
                        speak(f"{dest}로 안내를 시작합니다.")
                        self.dest_pub.publish(dest)
                        return
                    else:
                        speak("현재 위치 내의 장소만 안내할 수 있습니다.")
                    # 다시 대기시간 초기화
                    start_time = time.time()
                else:
                    speak("다시 말씀해 주세요.")

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    handler = GoalResultHandler()
    handler.run()

