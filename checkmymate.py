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
        num_games = request.form["num_games"]
        if not utils.is_user(lichess_name):
            return render_template("index.html", error_name=lichess_name)
        return redirect(url_for("user", lichess_name=lichess_name, num_games=num_games))
    else:
        return render_template("index.html")

@app.route("/<lichess_name>/<num_games>")
def user(lichess_name, num_games):
    return f"<h1>{lichess_name}, {num_games}</h1>"

if __name__ == "__main__":
    app.run(debug=True)