#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import Int32
from flask import Flask, request, jsonify, render_template_string
import threading
import serial
import io

# Flask 앱 정의
app = Flask(__name__)

# === ROS 노드 및 퍼블리셔 클래스 ===
class EncoderPublisher:
    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        # ROS 노드 초기화
        rospy.init_node("encoder_uart_listener", anonymous=True)

        # 퍼블리셔 생성
        self.pub_left = rospy.Publisher("/encoder/left", Int32, queue_size=10)
        self.pub_right = rospy.Publisher("/encoder/right", Int32, queue_size=10)

        # 시리얼 포트 연결
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        #self.sio = io.TextIOWrapper(io.BufferedReader(self.ser), encoding='utf-8')

        # 수신 스레드 시작
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.daemon = True
        self.thread.start()

    def read_loop(self):
        #rate = rospy.Rate(1)
        buffer = ""
        while not rospy.is_shutdown():
            try:
                byte_chunk = self.ser.read(64).decode('utf-8')
                buffer += byte_chunk
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.parse_line(line)
            except Exception as e:
                rospy.logwarn(f"[UART READ] {e}")
            
    def parse_line(self, line):
        if line.startswith("ENC_L:"):
            try:
                val = int(line.split(":")[1])
                self.pub_left.publish(val)
                rospy.loginfo(f"[ENC_L] {val}")
            except:
                pass
        elif line.startswith("ENC_R:"):
            try:
                val = int(line.split(":")[1])
                self.pub_right.publish(val)
                rospy.loginfo(f"[ENC_R] {val}")
            except:
                pass

    def send_pwm(self, data):
        # 시리얼로 PWM 명령 전송
        try:
            self.ser.write((data + "\n").encode())
            rospy.loginfo(f"Sent PWM: {data}")
        except Exception as e:
            rospy.logwarn(f"Failed to send PWM: {e}")


# HTML 페이지
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>STM32 모터 제어</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: sans-serif;
            text-align: center;
            margin-top: 50px;
            -webkit-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }
        button {
            font-size: 24px;
            padding: 20px 40px;
            margin: 20px;
            width: 200px;
            -webkit-user-select: none;
            user-select: none;
        }
    </style>
</head>
<body oncontextmenu="return false;" onselectstart="return false;" ondragstart="return false;">
    <h2>🛞 STM32 모터 제어</h2>
    <button onmousedown="sendCommand('forward')" onmouseup="stop()" ontouchstart="handleTouch(event, 'forward')" ontouchend="stop()">직진</button><br>
    <button onmousedown="sendCommand('left')" onmouseup="stop()" ontouchstart="handleTouch(event, 'left')" ontouchend="stop()">좌회전</button>
    <button onmousedown="sendCommand('right')" onmouseup="stop()" ontouchstart="handleTouch(event, 'right')" ontouchend="stop()">우회전</button><br>
    <button onmousedown="sendCommand('backward')" onmouseup="stop()" ontouchstart="handleTouch(event, 'backward')" ontouchend="stop()">후진</button>

    <script>
        function sendCommand(cmd) {
            let pwm = '';
            if (cmd === 'forward') pwm = 'L90,R90';
            else if (cmd === 'backward') pwm = 'L-90,R-90';
            else if (cmd === 'left') pwm = 'L70,R90';
            else if (cmd === 'right') pwm = 'L90,R70';

            fetch('/send_pwm', {
                method: 'POST',
                headers: { 'Content-Type': 'text/plain' },
                body: pwm
            });
        }

        function stop() {
            fetch('/send_pwm', {
                method: 'POST',
                headers: { 'Content-Type': 'text/plain' },
                body: 'L0,R0'
            });
        }

        function handleTouch(e, cmd) {
            e.preventDefault();
            sendCommand(cmd);
        }
    </script>
</body>
</html>
"""

# === Flask 라우팅 ===
@app.route("/")
def index():
    return render_template_string(html_page)

@app.route("/send_pwm", methods=["POST"])
def send_pwm():
    try:
        data = request.data.decode("utf-8")
        encoder_node.send_pwm(data)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# === 메인 ===
if __name__ == "__main__":
    encoder_node = EncoderPublisher(port='/dev/ttyACM0')  # 포트는 상황에 맞게 수정
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8000))
    flask_thread.daemon = True
    flask_thread.start()
    rospy.spin()

