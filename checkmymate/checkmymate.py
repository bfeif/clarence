from flask import Blueprint, Flask, render_template, request, redirect, url_for
bp = Blueprint('checkmymate', __name__)

@bp.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        lichess_name = request.form['lichess_name']
        return redirect(url_for('data', lichess_name=lichess_name))
    return render_template("index.html")

@bp.route('/data/', methods=['POST'])
def data():
    lichess_name = request.form.get("lichess_name")
    games = [1,2,3]
    return render_template('data.html', lichess_name=lichess_name, games=games)
