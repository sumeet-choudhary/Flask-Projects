################################################# FLASK RESTFULL ##############################################


from flask import Flask, make_response, jsonify
from flask_restful import Resource, Api, reqparse, abort

app = Flask(__name__)   #creates a flask application instance and assign it to app variable which can be used to define routes, etc
api = Api(app)          #Integrates the flask restful extension with flask application to define n handle restful api

todos = {
    1: {"task": "Write Hello World", "summary": "write it in python."},
    2: {"task": "Hi Sumeet", "summary": "Hi computer."},                # Dictionary because it is close to JSON format
    3: {"task": "Bye Sumeet", "summary": "Bye computer."}
}

task_post = reqparse.RequestParser()
task_post.add_argument("task", type=str, help="Task is required.", required=True)
task_post.add_argument("summary", type=str, help="Summary is required.", required=True)

task_put = reqparse.RequestParser()
task_put.add_argument("task", type=str)
task_put.add_argument("summary", type=str)

class ToDo(Resource):
    def get(self, todo_id):               # this is how we have our
        return todos[todo_id]            # get api for our to do list

    def post(self,todo_id):
        args = task_post.parse_args()
        if todo_id in todos:
            abort(409, message="Task id already taken.")
        todos[todo_id] = {"task": args["task"], "summary": args["summary"]}
        return make_response(jsonify({"message": "Your response is entered perfectly"}))

    def put(self, todo_id):
        args = task_put.parse_args()
        if todo_id not in todos:
            abort(404, message="Task doesnt exist, cannot update")
        if args['task']:
            todos[todo_id]['task'] = args['task']
        if args['summary']:
            todos[todo_id]['summary'] = args['summary']
        return todos

    def delete(self, todo_id):
        del todos[todo_id]
        return todos


class ToDoList(Resource):
    def get(self):
        return todos


api.add_resource(ToDo,'/todos/<int:todo_id>')  # This is how we add our api, and each url endpoint has to be class in itself.
api.add_resource(ToDoList,'/todos')

if __name__ == '__main__':
    app.run(debug=True)