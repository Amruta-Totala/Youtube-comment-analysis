from flask import Flask, render_template, request
from youtube_comment_scraper_python import *
import pandas as pd

app = Flask(__name__)


@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")


@app.route("/", methods=['POST'])
def getvalue():
    name = request.form['nm']
    output = request.form['output']
    youtube.open(name)

    response = youtube.video_comments()
    data = response['body']

    df = pd.DataFrame(data)
    df.to_csv(output)
    return data


if __name__ == "__main__":
    app.run(debug=True)
