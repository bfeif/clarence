from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
# app = Flask(__name__)


bp = Blueprint('checkmymate', __name__)

@bp.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('action1') == 'VALUE1':
            pass # do something
        elif  request.form.get('action2') == 'VALUE2':
            pass # do something else
        else:
            pass # unknown
    elif request.method == 'GET':
        return render_template('index.html')#, form=form)
    
    return render_template("index.html")