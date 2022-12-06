from flask import Flask, render_template, request, redirect, session, url_for, flash
import test, youtube_comment_analyzer
import pandas as pd
import mysql.connector
from matplotlib import pyplot as plt
import numpy as np
import os
import main_nltk
from flask_fontawesome import FontAwesome
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import base64
from PIL import Image
from werkzeug.utils import secure_filename

OUTPUT_FOLDER = os.path.join('static', 'output_img')

app = Flask(__name__)
# app.secret_key = os.urandom(24)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
fa = FontAwesome(app)

# initializing the user cookie


try:
    conn = mysql.connector.connect(
        host="localhost", user="root", password="", database="users")
    cursor = conn.cursor()
except:
    print("An exception occurred")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[2]
            session['image'] = account[4]
            msg = 'Logged in successfully !'
            return render_template('index1.html', msg=msg)
        else:
            msg = 'Incorrect email / password !'
    return render_template('login.html', msg=msg)


@app.route('/add_account', methods=['GET', 'POST'])
def add_account():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form \
            and 'password' in request.form and 'input-file' in request.files:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        image = request.files['input-file']
        print(type(image))
        print(username)
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """SELECT * from `accounts` WHERE `username` = '{}'""".format(username))
        account = cursor.fetchone()
        cursor.execute(
            """SELECT * from `accounts` WHERE `email` = '{}'""".format(email))
        # cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))

        account1 = cursor.fetchone()
        if account or account1:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', str(email)):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', str(username)):
            msg = 'Username must contain only characters and numbers !'
        elif not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', str(password)):
            msg = 'Password must contain minimum eight characters, at least one uppercase letter, one lowercase ' \
                  'letter and one number: ! '
        else:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor.execute("INSERT INTO accounts (username,email,password,image) VALUES (%s,%s,%s,%s)",
                           (username, email, password, filename))

            conn.commit()
            msg = 'You have successfully registered !'
            return render_template("register.html", msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template('register.html', msg=msg)


# @app.route('/display/<filename>')
# def display_image(filename):
#     if 'loggedin' in session:
#         print('display_image filename: ' + filename)
#         return redirect(url_for('static', filename='output_img/' + filename), code=301)

def get_image():
    if 'loggedin' in session:
        # file1 = cursor.execute("""SELECT `image` from `accounts` where `id`='{}'""".format(session['id']))
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        file = cursor.fetchone()
        name = file[1]
        file1 = file[4]
        file2 = file1.decode()
        final = url_for('static', filename='output_img/' + file2)
    return final, name


@app.route("/update", methods=['GET', 'POST'])
def update():
    msg = ''
    final, name = get_image()
    if 'loggedin' in session:
        if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'input-file' in request.files:
            username = request.form.get('username')
            email = request.form.get('email')
            image = request.files['input-file']
            print(username)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            print(account)
            if account:
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'name must contain only characters and numbers !'

            else:
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                cursor.execute("""UPDATE `accounts` SET  `username` = '{}',`email` = '{}',`image` = '{}' where
                `id`='{}'""".format(username, email, filename, session['id']))

                conn.commit()
                msg = 'You have successfully updated !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("user-profile.html", msg=msg, filename=final, username=name)
    return redirect(url_for('login'))


@app.route("/update_password", methods=['GET', 'POST'])
def update_password():
    msg1 = ''
    if 'loggedin' in session:
        if request.method == 'POST' and 'current' in request.form and 'new' in request.form and 'confirm' in request.form:
            current = request.form.get('current')
            new = request.form.get('new')
            confirm = request.form.get('confirm')
            cursor.execute('SELECT password FROM accounts WHERE password = %s', (current,))
            account = cursor.fetchone()
            if account is None:
                msg1 = 'Account does not exists!'
            return render_template("user-profile.html", msg1=msg1)

            if account[0] != new:
                if new == confirm:
                    cursor.execute("""UPDATE `accounts` SET  `password` = '{}' where
                                   `id`='{}'""".format(new, session['id']))
                    conn.commit()
                    msg1 = 'Password is updated!'
                else:
                    msg1 = 'New and confirmed password should be same!'
            else:
                msg1 = 'New password should not matched with previous!'

        elif request.method == 'POST':
            msg1 = 'Please fill out the form !'
        return render_template("user-profile.html", msg1=msg1)
    return redirect(url_for('login'))


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/index1')
def index1():
    if 'loggedin' in session:
        return render_template('index1.html')
    else:
        return redirect('/')


@app.route('/category')
def category():
    if 'loggedin' in session:
        return render_template('category.html')


@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        final, name = get_image()
        return render_template('dashboard.html',filename=final,username=name)


@app.route('/single')
def single():
    if 'loggedin' in session:
        return render_template('single.html')


@app.route('/single-blog')
def single_blog():
    if 'loggedin' in session:
        return render_template('single-blog.html')


@app.route('/sad')
def sad():
    if 'loggedin' in session:
        return render_template('sad.html')


@app.route('/angry')
def angry():
    if 'loggedin' in session:
        return render_template('angry.html')


@app.route('/surprise')
def surprise():
    if 'loggedin' in session:
        return render_template('surprise.html')


@app.route('/laugh')
def laugh():
    if 'loggedin' in session:
        return render_template('laugh.html')


@app.route('/tear')
def tear():
    if 'loggedin' in session:
        return render_template('tear.html')


@app.route('/hearts')
def hearts():
    if 'loggedin' in session:
        return render_template('hearts.html')


@app.route('/flushed')
def flushed():
    if 'loggedin' in session:
        return render_template('flushed.html')


@app.route('/user-profile')
def user_profile():
    if 'loggedin' in session:
        filename, name = get_image()
        return render_template('user-profile.html', filename=filename, username=name)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/scrap', methods=['POST'])
def scrap_comments():
    if 'loggedin' in session:
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
        video_neutral_comments, filename = list_sentiment
        figname = list_emotions
        pos_comments_csv = pd.read_csv('Positive Comments.csv')
        neg_comments_csv = pd.read_csv('Negative Comments.csv')
        neu_comments_csv = pd.read_csv('Neutral Comments.csv')
        filename = os.path.join(app.config['UPLOAD_FOLDER'], 'analysis.png')
        figname = os.path.join(app.config['UPLOAD_FOLDER'], 'graph.png')
        # filename_bar = os.path.join(app.config['UPLOAD_FOLDER'], 'analysis_bar.jpg')

        after_complete_message = "Your data is ready"


        return render_template("dashboard.html", after_complete_message=after_complete_message, title=video_title,
                               owner=video_owner, comment_w_replies=video_comment_with_replies,
                               comment_wo_replies=video_comment_without_replies,
                               positive_comment=video_positive_comments, negative_comment=video_negative_comments,
                               neutral_comment=video_neutral_comments, user_image_bar=filename,
                               user_emotion_bar=figname,
                               pos_comments_csv=[pos_comments_csv.to_html()],
                               neg_comments_csv=[neg_comments_csv.to_html()],
                               neu_comments_csv=[neu_comments_csv.to_html()])


if __name__ == "__main__":
    app.debug = True
    app.run()
