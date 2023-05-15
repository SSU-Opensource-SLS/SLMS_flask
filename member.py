import pymysql
from flask import Blueprint, Flask, Response, render_template, jsonify
from flask_restx import Api, Resource, reqparse, fields
from flask_restful import Resource, reqparse
import json
from config import mydb

#app = Flask(__name__)
#api = Api(app, version='1.0', title='SLS API', description='Sagger API', doc="/api-docs")
member_blueprint = Blueprint('member', __name__)

class Member:
    def __init__(self,uid,name,birth):
        self.uid = uid
        self.name = name
        self.birth = birth
        
    def __json__(self):
        return {
            'uid' : self.uid,
            'name' : self.name,
            'birth' : self.birth,
        }
        
def execute_sql(sql, params=None):
    with mydb.cursor() as cursor:
        cursor.execute(sql, params)
        result = cursor.fetchall()
    return result

#회원 등록 API
@member_blueprint.route('/member', methods=['post'])
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
@member_blueprint.route('/member/<string:uid>', methods=['get'])
def getMember(uid):
    tempMember = queryMemberData(uid)
    if not tempMember:
        return {'message': 'uid does not exist'}, 404
    member = Member(tempMember[0][0],tempMember[0][1],tempMember[0][2])
    return jsonify(member.__dict__)