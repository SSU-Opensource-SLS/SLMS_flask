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
    try:
        user_id = request.json['user_id']
        title = request.json['title']
        body = request.json['body']

        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=user_id
        )
        
        response = messaging.send(message)
        return 'Notification sent successfully'
    except Exception as e:
        return str(e), 500
