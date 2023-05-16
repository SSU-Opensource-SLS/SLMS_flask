from flask import Flask, Blueprint, Response, render_template, jsonify
from flask_restful import Resource, reqparse
import cv2
import os
import json

stream_blueprint = Blueprint('stream', __name__)

# 스트리밍 API 테스터 -> mp4 스트리밍 방식
@stream_blueprint.route('/stream')
def stream():
    # mp4 파일 경로 설정
    path = '/Users/parksangcheol/Desktop/flask_test/video.mp4'

    # 비디오 스트리밍 생성기 함수
    def generate():
        with open(path, 'rb') as video:
            while True:
                data = video.read(1024*8) # 적절한 데이터 크기로 설정
                if not data:
                    break
                yield (b'--frame\r\n'
                       b'Content-Type: video/mp4\r\n\r\n' + data + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

'''# 비디오 스트리밍 함수 -> jpeg 스트리밍 방식
def gen(video_path):
    cap = cv2.VideoCapture(video_path)
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # MJPEG로 인코딩하여 바이트 스트림으로 변환
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        # HTTP 프로토콜용 MJPEG 스트림 생성
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# 스트리밍 API 테스터 -> jpeg 스트리밍 방식
@stream_blueprint.route('/stream')
def stream():
    # 스트리밍할 비디오 경로
    video_path = '/Users/parksangcheol/Desktop/flask_test/video.mp4'
    return Response(gen(video_path), mimetype='multipart/x-mixed-replace; boundary=frame')'''
