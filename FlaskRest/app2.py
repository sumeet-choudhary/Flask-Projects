####################################################### FLASK REST ########################################################

# # INTEGRATING HTML WITH FLASK
# # HTTP verb GET and POST
#
#
# from flask import Flask, redirect, url_for, render_template, request
# app = Flask(__name__)
#
# @app.route('/')
# def welcome():
#     return render_template('index.html')
#
# @app.route('/success/<int:score>')
# def success(score):
#     res=""
#     if score>=50:
#         res='PASS'
#     else:
#         res='FAIL'
#     return render_template('result.html',result=res)
#
# @app.route('/fail/<int:score>')
# def fail(score):
#     return "The Person is fail and the score is: "+str(score)
#
# # Result checker
# @app.route('/result/<int:marks>')
# def result(marks):
#     result=""
#     if marks>50:
#         result='success'
#     else:
#         result='fail'
#     return redirect(url_for(result,score=marks))
#
# #Result checker submit html page
# @app.route('/submit',methods=['POST','GET'])
# def submit():
#     total_score=0
#     if request.method=='POST':
#         science = float(request.form['science'])
#         maths = float(request.form['maths'])
#         history =float(request.form['history'])
#         english =float(request.form['english'])
#         total_score=(science+maths+history+english)/4
#     res=""
#     return redirect(url_for('success',score=total_score))
#
# if __name__ == '__main__':
#     app.run(debug=True)