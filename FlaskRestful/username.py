from flask import Flask, request
from flask_restful import Resource, Api, abort

app = Flask(__name__)
api = Api(app)


AllUser = {
    "user1": "Sumeet",
    "user2": "Amit",
    "user3": "Anjali"
}


class Users(Resource):
    def get(self, user_id):
        try:
            if user_id not in AllUser:
                abort(409, message="ID doesnt exist cant get it")
            return AllUser[user_id]
        except Exception as e:
            print(e)

    def delete(self, user_id):
        try:
            if user_id not in AllUser:
                abort(409, message="This ID doesn't exist, cant delete it")
            del AllUser[user_id]
            return AllUser
        except Exception as e:
            print(e)

    def post(self, user_id):
        try:
            if user_id in AllUser:
                abort(409, message="This ID is already taken, try putting other")
            new_dict = request.get_json()
            new_key = new_dict.get('key')
            new_value = new_dict.get('value')
            AllUser[new_key] = new_value
            response = {'message': 'New User with both key and value has been added successfully'}
            return response
        except Exception as e:
            print(e)

    def put(self, user_id):
        try:
            if user_id not in AllUser:
                abort(409, message="This ID doesn't exist, cant update it")
            new_dict = request.get_json()
            AllUser[user_id] = new_dict['value']
            response = {'message': 'New changes has been added successfully'}
            return response
        except Exception as e:
            print(e)


class OnlyGet(Resource):
    def get(self):
        return AllUser


api.add_resource(Users, '/<user_id>')
api.add_resource(OnlyGet, '/')

if __name__ == '__main__':
    app.run(debug=True)

