from flask import Flask, request
from flask_restful import Api, Resource, abort

app = Flask(__name__)
api = Api(app)

todos = {
    "task1": "Write Hello World",
    "task2": "Hi Sumeet",
    "task3": "Bye Sumeet"
}


class AllFunc(Resource):
    def get(self, todo_id):
        global todos
        return todos[todo_id]

    def delete(self, todo_id):
        del todos[todo_id]
        return todos

    def post(self, todo_id):
        global todos
        if todo_id in todos:
            abort(409, message="Task id already taken.")
        dict1 = request.get_json()
        new_key = dict1.get('key')
        new_value = dict1.get('value')
        todos[new_key] = new_value
        response = {'message': 'New key and values added successfully'}
        return response

    def put(self, todo_id):
        global todos
        if todo_id not in todos:
            abort(404, message="Task doesnt exist, cannot update")
        dict1 = request.get_json()
        todos[todo_id] = dict1["value"]
        response = {'message': 'updated successfully'}
        return response


class OnlyGet(Resource):
    def get(self):
        return todos


api.add_resource(AllFunc, '/<todo_id>')
api.add_resource(OnlyGet, '/')


if __name__ == '__main__':
    app.run(debug=True)
