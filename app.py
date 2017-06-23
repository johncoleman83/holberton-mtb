"""
app python mini tweet bot application
takes user input and tweets to designated account
"""
import tweepy
import os
import time
from flask import Flask, render_template, request, Markup, redirect, url_for
from werkzeug import secure_filename
from time import sleep
from credentials import (consumer_key, consumer_secret, access_token,
                         access_token_secret)
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
TWEET_APPEND_TEXT = " hello from @holbertonschool!"
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


#globals to keep track of user experiences
def verify_tweet():
    global TWEET
    if TWEET[0] and TWEET[1]:
        return True
    else:
        return False


def reset_tweet():
    global TWEET
    TWEET = [False, False]


# begin flask template rendering
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
            return redirect(url_for('failure', message='fprofanity'))
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
            return redirect(url_for('failure', message='ftweepy'))
        else:
            return redirect(url_for('confirmfeature', status='success'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        reset_tweet()
        return render_template('index.html')
    if request.method == 'POST':
        try:
            if request.files['file']:
                file = request.files['file']
                if allowed_file(file.filename):
                    global imagefile
                    imagefile = secure_filename(file.filename)
                    imagefile = os.path.join(UPLOAD_FOLDER, imagefile)
                    imagefile = add_date(imagefile)
                    file.save(imagefile)
                    global TWEET
                    TWEET[0] = True
                    imagemarkup =  Markup("<img id='tweet-image' src='{:}' />"
                                          .format(imagefile[1:]))
            return render_template('status.html', image=imagemarkup)
        except:
            reset_tweet()
            return render_template('index.html')


@app.route('/status', methods=['GET', 'POST'])
def status():
    if request.method == 'GET':
        reset_tweet()
        return render_template('status.html', image=None)
    if request.method == 'POST':
        global TWEET, imagefile, tweetvar
        if request.form['tweet']:
            tweetvar = request.form['tweet'] + TWEET_APPEND_TEXT
            if not censor(tweetvar):
                reset_tweet()
                return redirect(url_for('failure', message='fprofanity'))
        else:
            tweetvar = TWEET_APPEND_TEXT
            if verify_tweet == False:
                return redirect(url_for('failure', message='fprocedure'))
        TWEET[1] = True
        if verify_tweet():
            reset_tweet()
            if tweet_image(imagefile, tweetvar):
                return redirect(url_for('loader'))
            else:
                return redirect(url_for('failure', message='ftweepy'))
        else:
            reset_tweet()
            return redirect(url_for('failure', message='fprocedure'))


@app.route('/confirmfeature/<status>', methods=['GET'])
def confirmfeature(status):
    return render_template('confirmfeature.html', status=status)


@app.route('/failure/<message>', methods=['GET'])
def failure(message):
    reset_tweet()
    return render_template('failure.html', message=message)


@app.route('/loader', methods=['GET'])
def loader():
    return render_template('loader.html')


@app.route('/confirm', methods=['GET'])
def confirm():
    return render_template('confirm.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
