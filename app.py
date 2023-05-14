import pymysql
from flask import Flask, Response, render_template, jsonify
from flask_restx import Api, Resource, reqparse
from flask_restful import Resource
from flask_restful import reqparse
import DTO_set
import cv2
import os
import json
from config import mydb

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello Opensource"

api = Api(app, version='1.0', title='SLS API', description='Sagger API', doc="/api-docs")

def execute_sql(sql, params=None):
    with mydb.cursor() as cursor:
        cursor.execute(sql, params)
        result = cursor.fetchall()
    return result

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
@app.route('/stream')
def stream():
    # 스트리밍할 비디오 경로
    video_path = '/Users/parksangcheol/Desktop/flask_test/video.mp4'
    return Response(gen(video_path), mimetype='multipart/x-mixed-replace; boundary=frame')'''

# 스트리밍 API 테스터 -> mp4 스트리밍 방식
@app.route('/stream')
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

@app.route('/stream/livestock', methods=['GET'])
def returnLivestockInfo():
    # 가축 정보를 담은 딕셔너리 객체 생성
    livestock_dict = {
        'name': 'Harry',
        'Position': 'first stock',
        'type': 'cow'
    }
    
    # JSON 형식으로 변환하여 리턴
    return jsonify(livestock_dict)

# 캠 등록 API
@app.route('/cam', methods=['post'])
def addCam():
    sql = "INSERT INTO raspi_cam (uid, livestock_type, num) SELECT %s, %s,IFNULL(MAX(num), 0)+1 FROM raspi_cam WHERE uid = %s AND livestock_type = %s"
    parser = reqparse.RequestParser()
    parser.add_argument('uid',type=str)
    parser.add_argument('livestock_type',type=str)
    
    args = parser.parse_args()
    with mydb:
        with mydb.cursor() as cur:
            cur.execute(sql, (args['uid'],args['livestock_type'],args['uid'],args['livestock_type']))
            mydb.commit()
    cam = DTO_set.cam(args['uid'],args['livestock_type'])
    return cam

#캠 조회 쿼리 함수
def queryCamByUidAndlivestockType(uid, livestock_type):
    sql = "SELECT * FROM raspi_cam WHERE UID = (%s) AND livestock_type = (%s)"
    temp = execute_sql(sql, (uid, livestock_type,))
    result = []
    for i in temp:
        result.append(DTO_set.cam(i[0],i[1],i[2]))
    return result

#캠 조회(uid + livestock_type) API
@app.route('/cam/<string:uid>/<string:livestock_type>', methods=['get'])
def getCamByUidAndlivestockType(uid,livestock_type):
    result = queryCamByUidAndlivestockType(uid, livestock_type)
    return jsonify([x.__json__() for x in result])

#캠 조회 쿼리 함수
def queryCamByUid(uid):
    sql = "SELECT * FROM raspi_cam WHERE UID = (%s)"
    temp = execute_sql(sql, (uid,))
    result  = []
    for i in temp:
        result.append(DTO_set.cam(i[0],i[1],i[2]))
    return result

#캠 조회(uid) API
@app.route('/cam/<string:uid>', methods=['get'])
def getCamByUid(uid):
    result = queryCamByUid(uid)
    return jsonify([x.__json__() for x in result])

# 가축 등록 API
@app.route('/livestock', methods=['post'])
def addLivestock():
    sql = "INSERT INTO livestock (uid,name,cattle,type,is_pregnant) VALUES (%s, %s, %s, %s, %s)"
    parser = reqparse.RequestParser()
    parser.add_argument('uid',type=str)
    parser.add_argument('name',type=str)
    parser.add_argument('cattle',type=str)
    parser.add_argument('type',type=str)
    parser.add_argument('is_pregnant',type=bool)
    
    args = parser.parse_args()
    with mydb:
        with mydb.cursor() as cur:
            cur.execute(sql, (args['uid'],args['name'],args['cattle'],args['type'],args['is_pregnant']))
            mydb.commit()
    ret = 'uid : ' + args['uid'] + ' name : ' + args['name']
    return ret

#가축 조회 쿼리 함수
def queryLivestockListByUidAndType(uid, livestock_type):
    sql = "SELECT * FROM livestock WHERE UID = (%s) AND livestock_type = (%s)"
    temp = execute_sql(sql, (uid,livestock_type,))
    result = []
    for i in temp:
        result.append(DTO_set.livestock(i[0],i[1],i[3],i[4],i[5],i[2]));
    return result

#가축 조회(uid + livestock_type) API
@app.route('/livestockList/<string:uid>/<string:livestock_type>', methods=['get'])
def getLivestockListByUidAndType(uid,livestock_type):
    result = queryLivestockListByUidAndType(uid,livestock_type)
    return jsonify([x.__json__() for x in result])

#가축 조회 쿼리 함수
def queryLivestockListByUid(uid):
    sql = "SELECT * FROM livestock WHERE UID = (%s)"
    temp = execute_sql(sql, (uid,))
    result = []
    for i in temp:
        result.append(DTO_set.livestock(i[0],i[1],i[3],i[4],i[5],i[2]));
    return result

#가축 조회(uid) API
@app.route('/livestockList/<string:uid>', methods=['get'])
def getLivestockListByUid(uid):
    result = queryLivestockListByUid(uid)
    return jsonify([x.__json__() for x in result])

#회원 등록 API
@app.route('/member', methods=['post'])
def addMember():
    sql = "INSERT INTO member (uid,name,birth) VALUES (%s, %s, %s)"
    parser = reqparse.RequestParser()
    parser.add_argument('uid',type=str)
    parser.add_argument('name',type=str)
    parser.add_argument('birth',type=str)
        
    args = parser.parse_args()

    with mydb:
        with mydb.cursor() as cur:
            cur.execute(sql, (args['uid'], args['name'], args['birth']))
            mydb.commit()
    ret = 'uid : ' + args['uid'] + ' name : ' + args['name']
    return ret

#회원 조회 쿼리 함수
def queryMemberData(uid):
    sql = "SELECT * FROM member WHERE UID = (%s)"
    result = execute_sql(sql, (uid,))
    return result

#캠 조회(uid) API
@app.route('/member/<string:uid>', methods=['get'])
def getMember(uid):
    tempMember = queryMemberData(uid)
    if not tempMember:
        return {'message': 'uid does not exist'}, 404
    member = DTO_set.Member(tempMember[0][0],tempMember[0][1],tempMember[0][2])
    return jsonify(member.__dict__)

'''memberNS = api.namespace('member',description='회원 조회,가입')

@memberNS.route('/')
class MemberPostManager(Resource):
    def post(self):
        sql = "INSERT INTO member (uid,name,birth) VALUES (%s, %s, %s)"
        parser = reqparse.RequestParser()
        parser.add_argument('uid',type=str)
        parser.add_argument('name',type=str)
        parser.add_argument('birth',type=str)
        
        args = parser.parse_args()

        with mydb:
            with mydb.cursor() as cur:
                cur.execute(sql, (args['uid'], args['name'], args['birth']))
                mydb.commit()
        ret = 'uid : ' + args['uid'] + ' name : ' + args['name']
        return ret

@memberNS.route('/<string:uid>')
@memberNS.response(404, 'uid does not exist')
@memberNS.param('uid', 'put uid in the URL')
class MemberGetManager(Resource):
    def get(self, uid):
        tempMember = queryMemberData(uid)
        if not tempMember:
            return {'message': 'uid does not exist'}, 404
        member = DTO_set.Member(tempMember[0][0],tempMember[0][1],tempMember[0][2])
        return jsonify(member.__dict__)'''
    
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)