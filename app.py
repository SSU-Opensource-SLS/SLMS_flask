from flask import Flask
from flask_restx import Api
from member import member_blueprint, member_ns
from livestock import livestock_blueprint, livestock_ns
from cam import cam_blueprint, cam_ns
from stream import stream_blueprint
from notify import notify_blueprint

app = Flask(__name__)

app.register_blueprint(member_blueprint, url_prefix='/member')
app.register_blueprint(livestock_blueprint, url_prefix='/livestock')
app.register_blueprint(cam_blueprint, url_prefix='/cam')
app.register_blueprint(stream_blueprint)
app.register_blueprint(notify_blueprint)

@app.route('/')
def index():
    return "Welcome to SLS API"
    
api = Api(app, version='1.0', title='SLS API', description='Sagger API', doc="/api-docs")

api.add_namespace(member_ns, path='/member')
api.add_namespace(livestock_ns, path='/livestock')
api.add_namespace(cam_ns, path='/cam')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)