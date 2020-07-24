# mini tweet bot

:a python application [DEMO], for twitter automation with Cloud Foundry on IBM Bluemix

### python

  * __language:__ Python 3.6.1
  * __libraries:__ tweepy, time, multiprocessing, opencv-python, numpy, workzeug
  * __web framework:__ flask
  * __style__: PEP 8: https://www.python.org/dev/peps/pep-0008/

### cloud:

  * __infrastructure:__ IBM Bluemix, https://www.ibm.com/cloud-computing/bluemix/
  * __platform:__ Cloud Foundry, https://www.cloudfoundry.org/

### examples:

  * __working app:__ https://bootcamp-mtb.mybluemix.net/
  * __original app:__ https://mtb.mybluemix.net/
  * __blog:__ http://www.davidjohncoleman.com/2017/mini-tweet-bot/

## description

Demo of how a company could customize mini tweet bot to use for their lobby, an
event, a promotion, or other public relations campaign.  For the original tweet
bot, check out the link to the 'original' above.  <strong>Note:</strong> This
demo is designed to function on an ipad tablet, and therefore does not format
properly on all devices.

## documentation

For integration with IBM Bluemix, cloudfoundry apps, see the 
[README.md](https://github.com/IBM-bluemix/get-started-python) 
from the below referenced repository.  Or read the blog post referenced above,
or check out the original mini tweet bot referenced above.

## file list

* for complete file list see file: `./FILELIST.md`

## usage

* from local machine:

  ```
  $ python3 app.py
  ```

* with cloudfoundry CLI:

  ```
  $ cf login -a api.[my-cloudfoundry].com
  $ cd [my-app-directory]
  $ cf push -b https://github.com/heroku/heroku-buildpack-python.git
  ```
  Note: use latest heroku python buildpack for most updated python & pip
  versions

## build your own bot

   * fork or clone the github repository.
   * get your own twitter app from twitter dev tools linked above.
   * change the `mycredentials.py` file name to `credentials.py`
   * change the strings from the credentials file to contain your personal
   	 twitter information.
   * change the twitter feed link in the <aside> HTML tag to instead link to
   	 your twitter feed.
   * change the link of the twitter handle in the nav HTML tag to link instead
   	 to your linked twitter account.
   * change the icon/ logos to your preference
   * find the cloud to host the app.  Mini tweet bot is already setup with
   	 Cloud Foundry for IBM Bluemix, but other cloud services will work as well.

__NOTE:__ The mini tweet bot functions most successfully when hosted on a
cloud.  However, if you would like to run the app on your own machine, you can
run it, and it will be loaded on a local host port IP address such as:
http://0.0.0.0:8080/.  If you do not want the user interface, you should then
use only the tweet functions, and run them on an as needed basis.  Here is an
example of how to run a single function from the `singletweet.py` file in the
`./support` directory:

```
$ cat singletweet.py
import tweepy
from credentials import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def tweet_text(tweetvar):
    """ tweets text from input variable """
    try:
        api.update_status(tweetvar)
    except:
        print("error")
        pass

tweet_text("this tweet is an example of running a tweet function in python")
$ python singletweet.py
```

### Authors

* David John Coleman II, [davidjohncoleman.com](http://www.davidjohncoleman.com/)
* Carrie Ybay, [@hicarrie](https://github.com/hicarrie)

### License

MIT License
