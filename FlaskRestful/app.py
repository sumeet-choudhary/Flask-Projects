####################################################### FLASK RESTFULL ########################################################

from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'data': 'HELLO WORLD'}

class HelloName(Resource):
    def get(self,name):
        return {'data': 'HELLO, {}'.format(name)}

api.add_resource(HelloWorld, '/helloworld')
api.add_resource(HelloName, '/helloworld/<string:name>')

if __name__ == '__main__':
    app.run(debug=True)