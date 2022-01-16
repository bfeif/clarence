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
        user = request.form["nm"]
        if user=="ben":
            return render_template("index.html", err="sorry ben")
        return redirect(url_for("user", usr=user))
    else:
        return render_template("index.html")

@app.route("/<usr>")
def user(usr):
    return f"<h1>{usr}</h1>"

if __name__ == "__main__":
    app.run(debug=True)