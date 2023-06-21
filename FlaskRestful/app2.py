# ################################################# FLASK RESTFULL ##############################################

from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
app = Flask(__name__)
api = Api(app)
list1 = []
class Register(Resource):
    def post(self):
        # global list1
        userinfo = request.get_json()
        username = userinfo.get("username")
        password = userinfo.get("password")
        if username and password:
            b = {"username": username, "password": password}
            list1.append(b)
            # print(list1)
            for i in list1:
                print(i)
        return make_response(jsonify({"message": "User created successfully"}))
# class login(Resource):
#     def post(self):
#         dt = request.get_json()
#         username = dt.get("username")
#         password = dt.get("password")
#
#         for i in list1:
#             print(i)
#
#         if username and password:
#             print({"username": username, "password": password})
#         return make_response(jsonify({"Message": "Lgin "}))
api.add_resource(Register, '/')
# api.add_resource(login, '/login')
print(list1)
if __name__ == '__main__':
    app.run(debug=True)

