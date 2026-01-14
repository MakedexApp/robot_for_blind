#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String
from stt import listen
from gptapi import extract_destination_from_text, ask_gpt
from gtts_module import speak

def main():
    # ROS 노드 초기화 및 퍼블리셔 생성
    rospy.init_node('gpt_voice_destination_publisher', anonymous=True)
    pub = rospy.Publisher('/destination', String, queue_size=1)
    rospy.loginfo("👂 '티노' 호출 대기 중...")

    # 웨이크 워드 대기 (예: "한국")
    while not rospy.is_shutdown():
        wake_word = listen()
        if wake_word and ("아이봇" in wake_word or "eyebot" in wake_word or "아이벗" in wake_word or "아이밧" in wake_word or "eyebut" in wake_word or "eye" in wake_word or "아이" in wake_word or "에이" in wake_word or "aye" in wake_word or "yee" in wake_word or "이" in wake_word or "아이보트" in wake_word or "eyeboat" in wake_word or "eyevote" in wake_word):
            rospy.loginfo("✅ 호출됨: 티노")
            speak("도움이 필요하신가요?")
            break

    # 목적지 안내 명령 대기 및 처리
    while not rospy.is_shutdown():
        user_input = listen()
        if user_input:
            # 종료 명령 처리
            if "종료" in user_input:
                speak("안내를 종료합니다. 좋은 하루 되세요.")
                break

            # 음성 텍스트에서 목적지 추론
            destination = extract_destination_from_text(user_input)
            rospy.loginfo("🔎 목적지 추론 결과: %s", destination)

            # 목적지를 찾지 못했을 때 처리
            if destination == "없음":
                response = ask_gpt(user_input)
                if response == "저는 길안내만 도와드릴 수 있습니다.":
                    speak(response)
                else:
                    speak("현재 위치 내에 있는 장소만 안내 가능합니다.")
                rospy.logwarn("❌ 안내 불가: 목적지 없음")
                continue

            # 유효한 목적지인지 확인 (7개 장소)
            valid_places = ["안내데스크", "화장실", "엘리베이터", "출입구", "식당", "라운지", "의무실"]
            if destination not in valid_places:
                speak("현재 위치 내에 있는 장소만 안내 가능합니다.")
                continue

            # 목적지 안내 시작
            speak(f"{destination}로 안내하겠습니다.")
            rospy.loginfo(f"📍 목적지: {destination}")
            pub.publish(destination)

    rospy.loginfo("노드 종료.")

if __name__ == "__main__":
    main()
