####################################################### FLASK REST ########################################################

# # BUILDING DYNAMIC URL
#
# from flask import Flask, redirect, url_for
# app= Flask(__name__)
#
# @app.route('/')
# def welcome():
#     return 'Welcome to my site'
#
# @app.route('/success/<int:score>')
# def success(score):
#     return "The Person is success and the score is: "+str(score)
#
# @app.route('/fail/<int:score>')
# def fail(score):
#     return "The Person is fail and the score is: "+str(score)
#
# @app.route('/result/<int:marks>')
# def result(marks):
#     result=""
#     if marks>50:
#         result='success'
#     else:
#         result='fail'
#     return redirect(url_for(result,score=marks))
#
# if __name__ == '__main__':
#     app.run(debug=True)