from flask import Flask, render_template, request
import test, youtube_comment_analyzer
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import os
import main_nltk

OUTPUT_FOLDER = os.path.join('static', 'output_img')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = OUTPUT_FOLDER


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/scrap', methods=['POST'])
def scrap_comments():
    url = request.form.get('youtube url')
    # output = request.form.get('user mail id')

    file_and_detail = test.scrapfyt(url)
    # pos_comments_csv = pd.read_csv('Full Comments.csv')
    # list_file_and_detail = list(file_and_detail)
    # video_title, video_owner, video_comment_with_replies, video_comment_without_replies = list_file_and_detail[1:]

    sentiment = youtube_comment_analyzer.sepposnegcom("Full Comments.csv")
    emotions = main_nltk.emotions("Full Comments.csv")

    list_file_and_detail = list(file_and_detail)
    list_sentiment = list(sentiment)
    list_emotions = list(emotions)
    print(list_file_and_detail)
    video_title, video_owner, video_comment_with_replies, video_comment_without_replies = list_file_and_detail[1:]
    pos_comments_csv, neg_comments_csv, neu_comments_csv, video_positive_comments, video_negative_comments, \
    video_neutral_comments= list_sentiment
    figname = list_emotions
    pos_comments_csv = pd.read_csv('Positive Comments.csv')
    neg_comments_csv = pd.read_csv('Negative Comments.csv')
    neu_comments_csv = pd.read_csv('Neutral Comments.csv')
    # filename = os.path.join(app.config['UPLOAD_FOLDER'], 'analysis.png')
    # figname = os.path.join(app.config['UPLOAD_FOLDER'], 'graph.png')
    # filename_bar = os.path.join(app.config['UPLOAD_FOLDER'], 'analysis_bar.jpg')

    after_complete_message = "Your data is ready"

    return render_template("index.html", after_complete_message=after_complete_message, title=video_title,
                           owner=video_owner, comment_w_replies=video_comment_with_replies,
                           comment_wo_replies=video_comment_without_replies,
                           positive_comment=video_positive_comments, negative_comment=video_negative_comments,
                           neutral_comment=video_neutral_comments,
                           pos_comments_csv=[pos_comments_csv.to_html()], neg_comments_csv=[neg_comments_csv.to_html()],
                           neu_comments_csv=[neu_comments_csv.to_html()])


if __name__ == "__main__":
    app.debug = True
    app.run()
