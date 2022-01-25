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
        chess_username = request.form["chess_username"]
        chess_username = chess_username if chess_username else " "
        num_games = request.form["num_games"]
        num_lookback_days = request.form["num_lookback_days"]
        platform = request.form["platform"]
        logger.info(f"platform: {platform}")

        # return the correct template, depending on user-input.
        if num_games=="":
            return render_template("index.html", error_num_games="_")
        elif int(num_games)<=0:
            return render_template("index.html", error_num_games="_")
        elif not utils.is_lichess_user(chess_username):
            return render_template("index.html", error_name=chess_username)
        else:
            return redirect(url_for("user",
                                    chess_username=chess_username,
                                    num_games=num_games,
                                    num_lookback_days=num_lookback_days,
                                    platform=platform))

    # normal index
    else:
        return render_template("index.html")

@app.route("/<chess_username>_<num_games>_<num_lookback_days>_<platform>")
def user(chess_username, num_games, num_lookback_days, platform):
    if int(num_games) > MAX_GAMES:
        redirect(url_for("user",
                         chess_username=chess_username,
                         num_games=MAX_GAMES,
                         num_lookback_days=num_lookback_days,
                         platform=platform))
    opening_stats_struct = utils.get_user_opening_stats(chess_username=chess_username,
                                                        num_games=int(num_games), 
                                                        num_lookback_days=int(num_lookback_days),
                                                        platform=platform)
    return render_template('user.html',
                           lichess_name=chess_username,
                           opening_stats_struct=opening_stats_struct)

if __name__ == "__main__":
    app.run(debug=True)