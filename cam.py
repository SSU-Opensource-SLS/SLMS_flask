import pymysql
from flask import Blueprint, jsonify
from flask_restx import Namespace, Api, Resource, reqparse, fields
from config import mydb

cam_blueprint = Blueprint('cam', __name__)
cam_ns = Namespace('cam', description='캠 등록 및 조회')
api = Api(namespace=cam_ns, version='1.0', title='SLS API', description='Sagger API', doc="/api-docs")

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

cam_fields = cam_ns.model('Cam', {
    'uid' : fields.String(),
    'livestock_type' : fields.String(),
    'num' : fields.Integer(),
})

# 캠 등록 API
@cam_ns.route('/')
class CamRegistration(Resource):
    @cam_ns.expect(cam_fields)
    def post(self):
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

#캠 조회(uid) 쿼리 함수
def queryCamByUid(uid):
    sql = "SELECT * FROM raspi_cam WHERE UID = (%s)"
    temp = execute_sql(sql, (uid,))
    result  = []
    for i in temp:
        result.append(Cam(i[0],i[1],i[2]))
    return result

#캠 조회(uid) API    
@cam_ns.route("/<string:uid>")
class CamManagerByUid(Resource):
    @cam_ns.response(404, 'uid does not exist')
    def get(self, uid):
        result = queryCamByUid(uid)
        return jsonify([x.__json__() for x in result])
        
#캠 조회 쿼리 함수
def queryCamByUidAndlivestockType(uid, livestock_type):
    sql = "SELECT * FROM raspi_cam WHERE UID = (%s) AND livestock_type = (%s)"
    temp = execute_sql(sql, (uid, livestock_type,))
    result = []
    for i in temp:
        result.append(Cam(i[0],i[1],i[2]))
    return result

#캠 조회(uid + livestock_type) API  
@cam_ns.route("/<string:uid>/<string:livestock_type>")
class CamManagerByUidAndType(Resource):
    @cam_ns.response(404, 'uid does not exist')
    def get(self, uid, livestock_type):
        result = queryCamByUidAndlivestockType(uid, livestock_type)
        return jsonify([x.__json__() for x in result])
    
api.add_resource(CamRegistration, '/')
api.add_resource(CamManagerByUid, '/<string:uid>')
api.add_resource(CamManagerByUidAndType, '/<string:uid>/<string:livestock_type>')