import pymysql
from flask import Blueprint, jsonify
from flask_restx import Namespace, Api, Resource, reqparse, fields
from config import create_db_connection

member_blueprint = Blueprint('member', __name__)
member_ns = Namespace('member', description='회원 등록 및 조회')
api = Api(namespace=member_ns, version='1.0', title='SLS API', description='Sagger API', doc="/api-docs")

class Member:
    def __init__(self,uid,email,name,birth):
        self.uid = uid
        self.email = email
        self.name = name
        self.birth = birth
        
    def __json__(self):
        return {
            'uid' : self.uid,
            'email' : self.email,
            'name' : self.name,
            'birth' : self.birth,
        }

class Token:
    def __init__(self,uid,token):
        self.uid = uid
        self.token = token
        
    def __json__(self):
        return {
            'uid' : self.uid,
            'token' : self.token
        }
        
def execute_sql(sql, params=None):
    mydb = create_db_connection()
    with mydb.cursor() as cursor:
        cursor.execute(sql, params)
        result = cursor.fetchall()
    return result

member_fields = member_ns.model('Member', {
    'uid': fields.String(),
    'email': fields.String(),
    'token': fields.String(),
    'name': fields.String(),
    'birth': fields.String(),
})

token_fields = member_ns.model('Token', {
    'uid': fields.String(),
    'token': fields.String(),
})

# 회원 등록 API
@member_ns.route('/')
class MemberRegistration(Resource):
    @member_ns.expect(member_fields)
    def post(self):
        mydb = create_db_connection()
        sql = "INSERT INTO member (uid,email,name,birth) VALUES (%s, %s, %s, %s)"
        parser = reqparse.RequestParser()
        parser.add_argument('uid',type=str)
        parser.add_argument('email',type=str)
        parser.add_argument('name',type=str)
        parser.add_argument('birth',type=str)
        
        args = parser.parse_args()

        with mydb:
            with mydb.cursor() as cur:
                cur.execute(sql, (args['uid'], args['email'], args['name'], args['birth']))
                mydb.commit()
                
        ret = args['uid']
        # 연결 유지를 위해 Ping을 수행
        mydb.ping(reconnect=True)
        return ret
    
# 토큰 등록 API
@member_ns.route('/token')
class MemberAddToken(Resource):
    @member_ns.expect(token_fields)
    def post(self):
        mydb = create_db_connection()
        sql = "INSERT INTO fcm_token (uid, token) VALUES (%s, %s)"
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=str)
        parser.add_argument('token', type=str)
        args = parser.parse_args()

        with mydb:
            with mydb.cursor() as cur:
                try:
                    cur.execute(sql, (args['uid'], args['token']))
                    mydb.commit()
                    ret = args['uid']
                except:
                    ret = {'message': 'Duplicate uid and token'}
                finally:
                    # 연결 유지를 위해 Ping을 수행
                    mydb.ping(reconnect=True)
        return ret

# 회원 탈퇴
@member_ns.route('/<string:uid>')
class MemberDeletion(Resource):
    def delete(self, uid):
        mydb = create_db_connection()
        sql = "DELETE FROM member WHERE uid = %s"
        with mydb:
            with mydb.cursor() as cur:
                cur.execute(sql, (uid,))
                mydb.commit()
        ret = 'Deleted member with uid: ' + uid
        mydb.ping(reconnect=True)
        return ret
    
# 회원 조회 API
@member_ns.route('/<string:uid>')
class MemberManager(Resource):
    @member_ns.response(404, 'uid does not exist')
    def get(self, uid):
        tempMember = queryMemberData(uid)
        if not tempMember:
            return {'message': 'uid does not exist'}, 404
        member = Member(tempMember[0][0], tempMember[0][1], tempMember[0][2], tempMember[0][3])
        return jsonify(member.__dict__)

#회원 조회 쿼리 함수
def queryMemberData(uid):
    sql = "SELECT * FROM member WHERE UID = (%s)"
    result = execute_sql(sql, (uid,))
    return result

# 토큰 조회 API
@member_ns.route('/token/<string:uid>')
class TokenManager(Resource):
    @member_ns.response(404, 'uid does not exist')
    def get(self, uid):
        token = queryMemberData(uid)
        if not token:
            return {'message': 'uid does not exist'}, 404
        return jsonify([x.__json__() for x in token])

#회원 조회 쿼리 함수
def queryMemberData(uid):
    sql = "SELECT * FROM fcm_token WHERE UID = (%s)"
    temp = execute_sql(sql, (uid,))
    result = []
    for i in temp:
        result.append(Token(i[1],i[2]))
    return result

api.add_resource(MemberRegistration, '/')
api.add_resource(MemberAddToken, '/token')
api.add_resource(MemberDeletion, '/<string:uid>')
api.add_resource(MemberManager, '/<string:uid>')
api.add_resource(TokenManager, '/token/<string:uid>')