import logging
from flask import Blueprint, Flask, render_template, request, redirect, url_for
import utils
import logging
app = Flask(__name__)
logger = app.logger
logger.setLevel(logging.INFO)
MAX_GAMES = 500

@app.route("/", methods=["POST", "GET"])
def home():

    # POST
    if request.method == "POST":

        # get field values from the form
        lichess_name = request.form["lichess_name"]
        lichess_name = lichess_name if lichess_name else " "
        num_games = request.form["num_games"]

        # return the correct template, depending on user-input.
        if num_games=="":
            return render_template("index.html", error_num_games="_")
        elif int(num_games)<=0:
            return render_template("index.html", error_num_games="_")
        elif not utils.is_lichess_user(lichess_name):
            return render_template("index.html", error_name=lichess_name)
        else:
            return redirect(url_for("user", lichess_name=lichess_name, num_games=num_games))

    # normal index
    else:
        return render_template("index.html")

@app.route("/<lichess_name>/<num_games>")
def user(lichess_name, num_games):
    if int(num_games) > MAX_GAMES:
        redirect(url_for("user", lichess_name=lichess_name, num_games=MAX_GAMES))
    opening_stats_struct = utils.get_user_opening_stats(lichess_name, num_games)
    return render_template('user.html',
                           lichess_name=lichess_name,
                           opening_stats_struct=opening_stats_struct)

if __name__ == "__main__":
    app.run(debug=True)