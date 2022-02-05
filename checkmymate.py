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
        chess_username = chess_username.strip() if chess_username else " "  # Clean the string input with .strip().
        num_lookback_days = request.form["num_lookback_days"]
        platform = request.form["platform"]
        logger.debug(f"platform: {platform}")

        # return the correct template, depending on user-input.
        if (platform=="lichess" or platform=="both") and utils.is_lichess_user(chess_username)==False:
            return render_template("index.html", error_name=chess_username, error_platform="lichess")
        elif (platform=="chessdotcom" or platform=="both") and utils.is_chessdotcom_user(chess_username)==False:
            return render_template("index.html", error_name=chess_username, error_platform="chess.com")
        else:
            return redirect(url_for("user",
                                    chess_username=chess_username,
                                    num_lookback_days=num_lookback_days,
                                    platform=platform))

    # normal index
    else:
        return render_template("index.html")

@app.route("/<chess_username>/since_<num_lookback_days>daysago/platform_<platform>")
def user(chess_username, num_lookback_days, platform):
    opening_stats_struct = utils.get_user_opening_stats(chess_username=chess_username,
                                                        num_lookback_days=int(num_lookback_days),
                                                        platform=platform)
    return render_template('user.html',
                           chess_username=chess_username,
                           opening_stats_struct=opening_stats_struct)

if __name__ == "__main__":
    app.run(debug=True)