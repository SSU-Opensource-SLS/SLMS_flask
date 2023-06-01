from flask import Blueprint, Response, render_template, url_for, send_file
from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, messaging

notify_blueprint = Blueprint('notify', __name__)

# Firebase Admin SDK 초기화
cred = credentials.Certificate('./serviceAccountKey.json')
firebase_admin.initialize_app(cred)

@notify_blueprint.route('/send_notification', methods=['POST'])
def send_notification():
    user_id = request.json['user_id']  # 사용자 식별자 토큰을 JSON 데이터에서 가져옵니다.
    title = request.json['title']  # 알림 제목을 요청의 JSON 데이터에서 가져옵니다.
    body = request.json['body']  # 알림 내용을 요청의 JSON 데이터에서 가져옵니다.

    # FCM 메시지 생성
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=user_id  # 사용자 식별자를 FCM 메시지의 대상으로 지정합니다.
    )

    # FCM 메시지 전송
    response = messaging.send(message)
    return 'Notification sent successfully'