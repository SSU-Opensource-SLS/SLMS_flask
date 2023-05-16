import pymysql
from flask import Blueprint, jsonify
from flask_restx import Namespace, Api, Resource, reqparse, fields
from config import mydb

member_blueprint = Blueprint('member', __name__)
member_ns = Namespace('member', description='회원 등록 및 조회')
api = Api(namespace=member_ns, version='1.0', title='SLS API', description='Sagger API', doc="/api-docs")

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

member_fields = member_ns.model('Member', {
    'uid': fields.String(),
    'name': fields.String(),
    'birth': fields.String(),
})

# 회원 등록 API
@member_ns.route('/')
class MemberRegistration(Resource):
    @member_ns.expect(member_fields)
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
    
# 회원 조회 API
@member_ns.route('/<string:uid>')
class MemberManager(Resource):
    @member_ns.response(404, 'uid does not exist')
    def get(self, uid):
        tempMember = queryMemberData(uid)
        if not tempMember:
            return {'message': 'uid does not exist'}, 404
        member = Member(tempMember[0][0], tempMember[0][1], tempMember[0][2])
        return jsonify(member.__dict__)

#회원 조회 쿼리 함수
def queryMemberData(uid):
    sql = "SELECT * FROM member WHERE UID = (%s)"
    result = execute_sql(sql, (uid,))
    return result

api.add_resource(MemberRegistration, '/')
api.add_resource(MemberManager, '/<string:uid>')