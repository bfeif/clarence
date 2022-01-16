import logging
from flask import Blueprint, Flask, render_template, request, redirect, url_for
import utils
import logging
app = Flask(__name__)
logger = app.logger
logger.setLevel(logging.INFO)

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        lichess_name = request.form["lichess_name"]
        lichess_name = lichess_name if lichess_name else " "
        num_games = request.form["num_games"]
        if not utils.is_user(lichess_name):
            return render_template("index.html", error_name=lichess_name)
        return redirect(url_for("user", lichess_name=lichess_name, num_games=num_games))
    else:
        return render_template("index.html")

@app.route("/<lichess_name>/<num_games>")
def user(lichess_name, num_games):
    opening_stats_struct = utils.get_lichess_user_opening_stats(lichess_name, num_games)
    return render_template('user.html',
                           lichess_name=lichess_name,
                           opening_stats_struct=opening_stats_struct)

if __name__ == "__main__":
    app.run(debug=True)