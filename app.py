from flask import Flask
from flask_restx import Api
from member import member_blueprint, member_ns
from livestock import livestock_blueprint, livestock_ns
from cam import cam_blueprint, cam_ns
#from stream import stream_blueprint

app = Flask(__name__)
app.register_blueprint(member_blueprint)
app.register_blueprint(livestock_blueprint)
app.register_blueprint(cam_blueprint)
#app.register_blueprint(stream_blueprint)

api = Api(app, version='1.0', title='SLS API', description='Sagger API', doc="/api-docs")

api.add_namespace(member_ns)
api.add_namespace(livestock_ns)
api.add_namespace(cam_ns)

@app.route('/')
def index():
    return "Hello Opensource"
    
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)