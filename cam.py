import pymysql
from flask import Blueprint, Flask, Response, render_template, jsonify
from flask_restx import Api, Resource, reqparse, fields
from flask_restful import Resource, reqparse
import json
from config import mydb

cam_blueprint = Blueprint('cam', __name__)

class Cam:
    def __init__(self,uid,livestock_type,num = None):
        self.uid = uid
        self.livestock_type = livestock_type
        self.num = num
        
    def __json__(self):
        return {
            'uid': self.uid,
            'livestock_type': self.livestock_type,
            'num': self.num
        }
 
def execute_sql(sql, params=None):
    with mydb.cursor() as cursor:
        cursor.execute(sql, params)
        result = cursor.fetchall()
    return result
       
# 캠 등록 API
@cam_blueprint.route('/cam', methods=['post'])
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
    cam = Cam(args['uid'],args['livestock_type'])
    return cam

#캠 조회 쿼리 함수
def queryCamByUidAndlivestockType(uid, livestock_type):
    sql = "SELECT * FROM raspi_cam WHERE UID = (%s) AND livestock_type = (%s)"
    temp = execute_sql(sql, (uid, livestock_type,))
    result = []
    for i in temp:
        result.append(Cam(i[0],i[1],i[2]))
    return result

#캠 조회(uid + livestock_type) API
@cam_blueprint.route('/cam/<string:uid>/<string:livestock_type>', methods=['get'])
def getCamByUidAndlivestockType(uid,livestock_type):
    result = queryCamByUidAndlivestockType(uid, livestock_type)
    return jsonify([x.__json__() for x in result])

#캠 조회 쿼리 함수
def queryCamByUid(uid):
    sql = "SELECT * FROM raspi_cam WHERE UID = (%s)"
    temp = execute_sql(sql, (uid,))
    result  = []
    for i in temp:
        result.append(Cam(i[0],i[1],i[2]))
    return result

#캠 조회(uid) API
@cam_blueprint.route('/cam/<string:uid>', methods=['get'])
def getCamByUid(uid):
    result = queryCamByUid(uid)
    return jsonify([x.__json__() for x in result])