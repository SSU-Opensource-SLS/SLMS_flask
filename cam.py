import pymysql
from flask import Blueprint, jsonify
from flask_restx import Namespace, Api, Resource, reqparse, fields
from config import create_db_connection
import time

cam_blueprint = Blueprint('cam', __name__)
cam_ns = Namespace('cam', description='캠 등록 및 조회')
api = Api(namespace=cam_ns, version='1.0', title='SLS API', description='Sagger API', doc="/api-docs")

class Cam:
    def __init__(self,uid,livestock_type,livestock_name,url,num = None):
        self.uid = uid
        self.livestock_type = livestock_type
        self.num = num
        self.livestock_name = livestock_name
        self.url = url
        
    def __json__(self):
        return {
            'uid': self.uid,
            'livestock_type': self.livestock_type,
            'num': self.num,
            'livestock_name': self.livestock_name,
            'url': self.url
        }
 
def execute_sql(sql, params=None):
    mydb = create_db_connection()
    with mydb.cursor() as cursor:
        cursor.execute(sql, params)
        result = cursor.fetchall()
    return result

cam_fields = cam_ns.model('Cam', {
    'uid' : fields.String(),
    'livestock_type' : fields.String(),
    'num' : fields.Integer(),
    'livestock_name' : fields.String(),
    'url' : fields.String()
})
    
# 캠 등록 API
@cam_ns.route('/')
class CamRegistration(Resource):
    @cam_ns.expect(cam_fields)
    @cam_ns.response(200, 'Success')
    @cam_ns.response(400, 'Bad Request')
    @cam_ns.response(500, 'Server error')
    @cam_ns.doc(description='캠 등록 API')
    def post(self):
        try:
            mydb = create_db_connection()
            sql = "INSERT INTO raspi_cam (uid, livestock_type, livestock_name, url ,num) SELECT %s, %s, %s, %s, IFNULL(MAX(num), 0) + 1 FROM raspi_cam WHERE uid = %s AND livestock_type = %s"
            parser = reqparse.RequestParser()
            parser.add_argument('uid', type=str)
            parser.add_argument('livestock_type', type=str)
            parser.add_argument('livestock_name', type=str)
            parser.add_argument('url', type=str)

            args = parser.parse_args()
            with mydb:
                with mydb.cursor() as cur:
                    cur.execute(sql, (args['uid'], args['livestock_type'], args['livestock_name'], args['url'], args['uid'], args['livestock_type']))
                    mydb.commit()
                    result = queryCamByUidAndlivestockType(args['uid'], args['livestock_type'])
                    if not result:
                        return {'message': 'Failed to register cam'}, 400
            mydb.ping(reconnect=True)
            cam = result[-1]
            return jsonify(cam.__dict__)
        except Exception as e:
            return str(e), 500

#캠 삭제 api
@cam_ns.route('/<string:uid>/<string:livestock_type>/<int:num>')
class CamDeletion(Resource):
    @cam_ns.response(200, 'Success')
    @cam_ns.response(400, 'Bad Request')
    @cam_ns.doc(description='캠 삭제 API')
    def delete(self, uid, livestock_type, num):
        try:
            mydb = create_db_connection()
            sql = "DELETE FROM raspi_cam WHERE uid = %s AND livestock_type = %s AND num = %s"
            with mydb:
                with mydb.cursor() as cur:
                    cur.execute(sql, (uid, livestock_type, num))
                    mydb.commit()
            ret = 'Deleted cam with uid: {}, livestock_type: {}, num: {}'.format(uid, livestock_type, num)
            mydb.ping(reconnect=True)
            return ret
        except Exception as e:
            return str(e), 500


#캠 조회(uid) 쿼리 함수
def queryCamByUid(uid):
    sql = "SELECT * FROM raspi_cam WHERE UID = (%s)"
    temp = execute_sql(sql, (uid,))
    result  = []
    for i in temp:
        result.append(Cam(i[0],i[1],i[3],i[4],i[2]))
    return result

#캠 조회(uid) API    
@cam_ns.route("/<string:uid>")
class CamManagerByUid(Resource):
    @cam_ns.response(404, 'uid does not exist')
    @cam_ns.doc(description='캠 조회 API(uid)')
    def get(self, uid):
        try:
            result = queryCamByUid(uid)
            if not result:
                return {'message': 'uid does not exist'}, 404
            return jsonify([x.__json__() for x in result])
        except Exception as e:
            return str(e), 500
        
#캠 조회 쿼리 함수
def queryCamByUidAndlivestockType(uid, livestock_type):
    sql = "SELECT * FROM raspi_cam WHERE UID = (%s) AND livestock_type = (%s)"
    temp = execute_sql(sql, (uid, livestock_type,))
    result = []
    for i in temp:
        result.append(Cam(i[0],i[1],i[3],i[4],i[2]))
    return result

#캠 조회(uid + livestock_type) API  
@cam_ns.route("/<string:uid>/<string:livestock_type>")
class CamManagerByUidAndType(Resource):
    @cam_ns.response(404, 'uid does not exist')
    @cam_ns.doc(description='캠 조회 API(uid, livestock_stock)')
    def get(self, uid, livestock_type):
        try:
            result = queryCamByUidAndlivestockType(uid, livestock_type)
            if not result:
                return {'message': 'uid does not exist'}, 404
            return jsonify([x.__json__() for x in result])
        except Exception as e:
            return str(e), 500

    
#캠 조회 쿼리 함수
def queryCamByUidAndlivestockTypeAndNum(uid, livestock_type, num):
    sql = "SELECT * FROM raspi_cam WHERE UID = (%s) AND livestock_type = (%s) AND num = (%s)"
    temp = execute_sql(sql, (uid, livestock_type, num,))
    result = []
    for i in temp:
        result.append(Cam(i[0],i[1],i[3],i[4],i[2]))
    return result

#캠 조회(uid + livestock_type) API  
@cam_ns.route("/<string:uid>/<string:livestock_type>/<int:num>")
class CamManagerByUidAndTypeAndNum(Resource):
    @cam_ns.response(404, 'uid does not exist')
    @cam_ns.doc(description='마지막 캠 조회 API')
    def get(self, uid, livestock_type, num):
        try:
            result = queryCamByUidAndlivestockTypeAndNum(uid, livestock_type, num)
            if not result:
                return {'message': 'uid does not exist'}, 404
            return jsonify([x.__json__() for x in result])
        except Exception as e:
            return str(e), 500
    
api.add_resource(CamRegistration, '/')
api.add_resource(CamDeletion, '/<string:uid>/<string:livestock_type>/<int:num>')
api.add_resource(CamManagerByUid, '/<string:uid>')
api.add_resource(CamManagerByUidAndType, '/<string:uid>/<string:livestock_type>')
api.add_resource(CamManagerByUidAndTypeAndNum, '/<string:uid>/<string:livestock_type>/<int:num>')