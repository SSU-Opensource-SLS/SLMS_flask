import pymysql
from flask import Blueprint, jsonify
from flask_restx import Namespace, Api, Resource, reqparse, fields
from config import mydb

livestock_blueprint = Blueprint('livestock', __name__)
livestock_ns = Namespace('livestock', description='가축 등록 및 조회')
api = Api(namespace=livestock_ns, version='1.0', title='SLS API', description='Sagger API', doc="/api-docs")

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

livestock_fields = livestock_ns.model('Livestock', {
    'uid' : fields.String(),
    'livestock_type' : fields.String(),
    'num' : fields.Integer(),
    'name' : fields.String(),
    'cattle' : fields.String(),
    'is_pregnancy' : fields.Boolean(),
})

# 가축 등록 API
@livestock_ns.route('/')
class LivestockRegistration(Resource):
    @livestock_ns.expect(livestock_fields)
    def post(self):
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
def queryLivestockListByUid(uid):
    sql = "SELECT * FROM livestock WHERE UID = (%s)"
    temp = execute_sql(sql, (uid,))
    result = []
    for i in temp:
        result.append(Livestock(i[0],i[1],i[3],i[4],i[5],i[2]));
    return result

#가축 조회(uid) API    
@livestock_ns.route("/<string:uid>")
class LivestockManagerByUid(Resource):
    @livestock_ns.response(404, 'uid does not exist')
    def get(self, uid):
        result = queryLivestockListByUid(uid)
        return jsonify([x.__json__() for x in result])

#가축 조회 쿼리 함수
def queryLivestockListByUidAndType(uid, livestock_type):
    sql = "SELECT * FROM livestock WHERE UID = (%s) AND livestock_type = (%s)"
    temp = execute_sql(sql, (uid,livestock_type,))
    result = []
    for i in temp:
        result.append(Livestock(i[0],i[1],i[3],i[4],i[5],i[2]));
    return result

#가축 조회(uid + livestock_type) API  
@livestock_ns.route("/<string:uid>/<string:livestock_type>")
class LivestockManagerByUidAndType(Resource):
    @livestock_ns.response(404, 'uid does not exist')
    def get(self, uid, livestock_type):
        result = queryLivestockListByUidAndType(uid,livestock_type)
        return jsonify([x.__json__() for x in result])

api.add_resource(LivestockRegistration, '/')
api.add_resource(LivestockManagerByUid, '/<string:uid>')
api.add_resource(LivestockManagerByUidAndType, '/<string:uid>/<string:livestock_type>')