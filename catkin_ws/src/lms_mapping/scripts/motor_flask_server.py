#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#flask 서버로 모터 제어만 하는 코드임.
import rospy
from flask import Flask, request, jsonify, render_template_string
import serial
import threading

app = Flask(__name__)
rospy.init_node("motor_flask_server", anonymous=True)

# UART 설정
ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=0.1)  # 실제 포트 확인 필요

# HTML 페이지
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>STM32 모터 제어</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; user-select: none; }
        button { font-size: 24px; padding: 20px 40px; margin: 20px; width: 200px; }
    </style>
</head>
<body oncontextmenu="return false;" onselectstart="return false;" ondragstart="return false;">
    <h2> STM32 모터 제어</h2>
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

@app.route("/")
def index():
    return render_template_string(html_page)

@app.route("/send_pwm", methods=["POST"])
def send_pwm():
    try:
        data = request.data.decode("utf-8")
        rospy.loginfo(f"PWM command: {data}")
        ser.write((data + "\n").encode())
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
