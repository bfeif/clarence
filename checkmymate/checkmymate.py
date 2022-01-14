import logging
from flask import Blueprint, Flask, render_template, request, redirect, url_for
from . import utils
import logging
app = Flask(__name__)
logger = app.logger
logger.setLevel(logging.DEBUG)
bp = Blueprint('checkmymate', __name__)

@bp.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@bp.route('/data/', methods=['POST'])
def data():
    lichess_name = request.form.get("lichess_name")
    num_games = request.form.get("num_games")
    if not utils.is_user(lichess_name):
        return redirect("/")
    opening_stats_struct = utils.get_lichess_user_opening_stats(lichess_name, num_games)
    return render_template('data.html',
                           lichess_name=lichess_name,
                           opening_stats_struct=opening_stats_struct)
