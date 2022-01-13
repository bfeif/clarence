from flask import Blueprint, Flask, render_template, request
bp = Blueprint('checkmymate', __name__)

@bp.route("/", methods=['GET', 'POST'])
def index():
    # if request.method == 'POST':
    #     if request.form.get('username_entry')=='VALUE1':
    #         pass # do something
    #     else:
    #         pass # unknown
    # elif request.method == 'GET':
    #     return render_template('index.html')#, form=form)
    
    return render_template("index.html")

@bp.route('/data/', methods = ['POST', 'GET'])
def data():
    lichess_name = request.args.get('lichess_name')
    return render_template('data.html', lichess_name=lichess_name)
    # if request.method == 'GET':
    #     return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    # if request.method == 'POST':
    #     form_data = request.form
    #     return render_template('data.html')
 