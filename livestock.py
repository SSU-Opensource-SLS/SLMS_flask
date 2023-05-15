import pymysql
from flask import Blueprint, Flask, Response, render_template, jsonify
from flask_restx import Api, Resource, reqparse, fields
from flask_restful import Resource, reqparse
import json
from config import mydb

livestock_blueprint = Blueprint('livestock', __name__)

class Livestock:
    def __init__(self,uid,livestock_type,name,cattle,is_pregnancy = False,num = None):
        self.uid = uid
        self.livestock_type = livestock_type
        self.num = num
        self.name = name
        self.cattle = cattle
        self.is_pregnancy = is_pregnancy
    def __json__(self):
        return {
            'uid' : self.uid,
            'livestock_type' : self.livestock_type,
            'num' : self.num,
            'name' : self.name,
            'cattle' : self.cattle,
            'is_pregnancy' : self.is_pregnancy
        }
        
def execute_sql(sql, params=None):
    with mydb.cursor() as cursor:
        cursor.execute(sql, params)
        result = cursor.fetchall()
    return result
        
# 가축 등록 API
@livestock_blueprint.route('/livestock', methods=['post'])
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
        result.append(Livestock(i[0],i[1],i[3],i[4],i[5],i[2]));
    return result

#가축 조회(uid + livestock_type) API
@livestock_blueprint.route('/livestockList/<string:uid>/<string:livestock_type>', methods=['get'])
def getLivestockListByUidAndType(uid,livestock_type):
    result = queryLivestockListByUidAndType(uid,livestock_type)
    return jsonify([x.__json__() for x in result])

#가축 조회 쿼리 함수
def queryLivestockListByUid(uid):
    sql = "SELECT * FROM livestock WHERE UID = (%s)"
    temp = execute_sql(sql, (uid,))
    result = []
    for i in temp:
        result.append(Livestock(i[0],i[1],i[3],i[4],i[5],i[2]));
    return result

#가축 조회(uid) API
@livestock_blueprint.route('/livestockList/<string:uid>', methods=['get'])
def getLivestockListByUid(uid):
    result = queryLivestockListByUid(uid)
    return jsonify([x.__json__() for x in result])