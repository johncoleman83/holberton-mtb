"""
app python mini tweet bot application
takes user input and tweets to designated account
"""
import tweepy
import multiprocessing
import os
import cv2
import time
from flask import Flask, render_template, request, jsonify, Markup
from werkzeug import secure_filename
from time import sleep
from credentials import (consumer_key, consumer_secret, access_token,
                         access_token_secret)
from camera import take_picture
# custom imports
import censorship
from aldict import ascii_dict, leet_dict

# custom variable names from imports
remove_whitespace = censorship.remove_whitespace
censor = censorship.censor

# tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
TWEET_APPEND_TEXT = " -tweeted at @holbertonschool"
TWEET = [False, False]

# flask integrations
app = Flask(__name__)
port = int(os.getenv('PORT', 8080))
UPLOAD_FOLDER = './static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


# flask support function to verify file import type
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# adds date to input image file
def add_date(filename):
    extension = filename[-4:]
    prefix = filename[:-4]
    thedate = time.strftime("%d-%m-%y--%H:%M:%S")
    return "{:}{:}{:}".format(prefix, thedate, extension)

# translation to ascii or leet


def translate(tweetvar, c):
    if c == 'a':
        tweetvar = tweetvar.lower()
        for key in ascii_dict:
            if key in tweetvar:
                tweetvar = tweetvar.replace(key, ascii_dict[key])
    else:
        for key in leet_dict:
            if key in tweetvar:
                tweetvar = tweetvar.replace(key, leet_dict[key])
    return tweetvar


# begin tweet functions here


def tweet_text(tweetvar):
    """ tweets text from input variable """
    try:
        api.update_status(tweetvar)
    except:
        return False
    return True


def tweet_image(filename, tweetvar):
    """ tweets image with status """
    try:
        api.update_with_media(filename, tweetvar)
        return True
    except tweepy.TweepError as e:
            print(e.reason)
            pass
    return False


def retweet_follow(searchterms):
    """searches tweets with searchterms, retweets, then follows"""
    for tweet in tweepy.Cursor(api.search, q=searchterms).items(60):
        try:
            tweet.retweet()
            if not tweet.user.following:
                tweet.user.follow()
            return True
        except tweepy.TweepError as e:
            print(e.reason)
            pass
    return False


def follow_x(searchterms, xfollowers):
    """follow ten new followers based on given searchterms"""
    retval = False
    for x in range(xfollowers):
        for tweet in tweepy.Cursor(api.search, q=searchterms).items(60):
            try:
                if not tweet.user.following:
                    tweet.user.follow()
                    retval = True
                    break
            except tweepy.TweepError as e:
                print(e.reason)
                pass
    return retval


def follow_followers():
    """ follow all your followers """
    for follower in tweepy.Cursor(api.followers).items():
        try:
            follower.follow()
        except tweepy.TweepError as e:
                print(e.reason)
                pass


def reset_tweet():
    global TWEET
    TWEET = [False, False]


# begin flask template rendering


@app.route('/')
def index():
    reset_tweet()
    return render_template('index.html', newstring="none")


@app.route('/features', methods=['GET', 'POST'])
def features():
    if request.method == 'GET':
        return render_template('features.html')
    if request.method == 'POST':
        failcount = 0
        searchterms = (request.form['searchterms']
                       if request.form['searchterms'] else '#opensource')
        xfollowers = int(request.form['xfollowers']
                         if request.form['xfollowers'] else 3)
        if not censor(searchterms):
            return render_template('failure.html', message='fprofanity')
        try:
            if request.form['retweet']:
                if retweet_follow(searchterms) is not True:
                    failcount += 1
        except:
            failcount += 1
        try:
            if request.form['followfollowers']:
                follow_followers()
        except:
            failcount += 1
        try:
            if request.form['followx']:
                if follow_x(searchterms, xfollowers) is False:
                    failcount += 1
        except:
            failcount += 1
        if failcount >= 3:
            return render_template('failure.html', message='ftweepy')
        else:
            return render_template('confirmfeature.html', status='success')


@app.route('/selfie', methods=['GET', 'POST'])
def selfie():
    if request.method == 'GET':
        reset_tweet()
        return render_template('selfie.html')
    if request.method == 'POST':
        try:
            if request.files['file']:
                file = request.files['file']
                if allowed_file(file.filename):
                    global filename
                    filename = secure_filename(file.filename)
                    filename = os.path.join(UPLOAD_FOLDER, filename)
                    filename = add_date(filename)
                    file.save(filename)
                    global TWEET
                    TWEET[0] = True
            return render_template('status.html')
        except:
            return render_template('selfie.html')


@app.route('/status', methods=['GET', 'POST'])
def status():
    if request.method == 'GET':
        return render_template('status.html')
    if request.method == 'POST':
        global TWEET
        if TWEET[0] == False:
            reset_tweet()
            return render_template('failure.html', message='fprocedure')
        global tweetvar
        tweetvar = request.form['tweet']
        if not censor(tweetvar):
            reset_tweet()
            return render_template('failure.html', message='fprofanity')
        if request.form['translate'] == "ascii":
            tweetvar = translate(tweetvar, 'a')
        elif request.form['translate'] == "leet":
            tweetvar = translate(tweetvar, 'l')
        imagemarkup =  Markup("<img id='tweet-image' src='{:}' />"
                              .format(filename[1:]))
        TWEET[1] = True
        return render_template('tweet.html', tweetvar=tweetvar,
                               image=imagemarkup)


@app.route('/confirmfeature')
def confirmfeatures():
    return render_template('confirmfeature.html')


@app.route('/failure')
def failure():
    reset_tweet()
    return render_template('failure.html')


@app.route('/tweet', methods=['GET', 'POST'])
def tweet():
    if request.method == 'GET':
        return render_template('tweet.html')
    if request.method == 'POST':
        if TWEET[0] and TWEET[1]:
            global tweetvar
            tweetvar = tweetvar + TWEET_APPEND_TEXT
            try:
                if tweet_image(filename, tweetvar):
                    sleep(5)
                    return render_template('confirm.html')
                else:
                    reset_tweet()
                    return render_template('failure.html', message='ftweepy')
            except:
                reset_tweet()
                return render_template('failure.html', message='ftweepy')
        else:
            reset_tweet()
            return render_template('failure.html', message='fprocedure')


@app.route('/confirm')
def confirm():
    return render_template('confirm.html')


@app.route('/are-no-one')
def easteregg():
    return render_template('easteregg.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
