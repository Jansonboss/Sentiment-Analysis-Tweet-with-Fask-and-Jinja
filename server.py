"""
A server that responds with two pages, one showing the most recent
100 tweets for given user and the other showing the people that follow
that given user (sorted by the number of followers those users have).

For authentication purposes, the server takes a commandline argument
that indicates the file containing Twitter data in a CSV file format:

    consumer_key, consumer_secret, access_token, access_token_secret

For example, I pass in my secrets via file name:

    /Users/parrt/Dropbox/licenses/twitter.csv

Please keep in mind the limits imposed by the twitter API:

    https://dev.twitter.com/rest/public/rate-limits

For example, you can only do 15 follower list fetches per
15 minute window, but you can do 900 user timeline fetches.
"""
import sys
import os
import datetime
import numpy as np
from tweetie import *
from colour import Color
from numpy import median
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)


def add_color(tweets):
    """
    Given a list of tweets, one dictionary per tweet, add
    a "color" key to each tweets dictionary with a value
    containing a color graded from red to green. Pure red
    would be for -1.0 sentiment score and pure green would be for
    sentiment score 1.0.

    Use colour.Color to get 100 color values in the range
    from red to green. Then convert the sentiment score from -1..1
    to an index from 0..100. That index gives you the color increment
    from the 100 gradients.

    This function modifies the dictionary of each tweet. It lives in
    the server script because it has to do with display not collecting
    tweets.
    """
    colors = list(Color("red").range_to(Color("green"), 100))
    np_index = np.linspace(-1, 1, 100)

    for t in tweets:
        score = t['score']
        # getting true false list and sum them up to get color index
        color_index = np.sum( score > np_index ) - 1
        senti_color = colors[color_index]
        # adding color key value pair and convert <Color #c0be00> to #c0be00
        t['color'] = str(senti_color).replace('<Color ', "").replace(">", "")
    
    return tweets


@app.route("/favicon.ico")
def favicon():
    """
    Open and return a 16x16 or 32x32 .png or other image file in binary mode.
    This is the icon shown in the browser tab next to the title.
    """
    return send_from_directory(os.path.join(app.root_path, 'static'),'scon.ico')

@app.route("/<name>")
def tweets(name):
    "Display the tweets for a screen name color-coded by sentiment score"
    # tweets is samething in the render_template's tweets
    record = fetch_tweets(api=api, name=name)
    add_color(tweets=record['tweets']) 
    return render_template('tweets.html', record=record)


@app.route("/following/<name>")
def following(name):
    """
    Display the list of users followed by a screen name, sorted in
    reverse order by the number of followers of those users.
    """
    follow_record = fetch_following(api, name)
    return render_template('following.html', name=name, follow_record=follow_record)


# @app.route("/test")
# def tweets():
#     "Display the tweets for a screen name color-coded by sentiment score"
#     # tweets is samething in the render_template's tweets
#     # record = fetch_tweets(api=api, name=name)
#     # add_color(tweets=record['tweets'])
    
#     record = {'user': 'realDonaldTrump',
#         'count': 58836,
#         'median_score': 0.234,
#         'tweets': 
#         [{'id': 1333857049294344194,
#         'created': datetime.datetime(2020, 12, 1, 19, 34, 37),
#         'retweeted': 133,
#         'text': 'Michigan voter fraud hearing going on now!',
#         'hashtags': [],
#         'urls': 'https://twitter.com/twitter/statuses/1333857049294344194',
#         'mentions': [],
#         'score': -0.6239,
#         'color': '#e85400'},
#         {'id': 1333856259662077954,
#         'created': datetime.datetime(2020, 12, 1, 19, 31, 28),
#         'retweeted': 3928,
#         'text': 'Hope everybody is watching @OANN right now. Other media afraid to show. People are coming forward like never before. Large truck carrying hundreds of thousands of fraudulent (FAKE) ballots to a voting center? TERRIBLE - SAVE AMERICA!',
#         'hashtags': [],
#         'urls': 'https://twitter.com/twitter/statuses/1333856259662077954',
#         'mentions': ['OANN'],
#         'score': -0.4263,
#         'color': '#db7c00'},
#         {'id': 1333846507993374726,
#         'created': datetime.datetime(2020, 12, 1, 18, 52, 43),
#         'retweeted': 11506,
#         'text': 'https://t.co/QjmZqNeJdt',
#         'hashtags': [],
#         'urls': 'https://twitter.com/twitter/statuses/1333846507993374726',
#         'mentions': [],
#         'score': 0.0,
#         'color': '#c0be00'},
#         {'id': 1333846469007335426,
#         'created': datetime.datetime(2020, 12, 1, 18, 52, 34),
#         'retweeted': 7144,
#         'text': 'https://t.co/IKBaWI68af',
#         'hashtags': [],
#         'urls': 'https://twitter.com/twitter/statuses/1333846469007335426',
#         'mentions': [],
#         'score': 0.0,
#         'color': '#c0be00'},
#         {'id': 1333846439194189826,
#         'created': datetime.datetime(2020, 12, 1, 18, 52, 27),
#         'retweeted': 7260,
#         'text': 'https://t.co/PypQRFKuWt',
#         'hashtags': [],
#         'urls': 'https://twitter.com/twitter/statuses/1333846439194189826',
#         'mentions': [],
#         'score': 0.0,
#         'color': '#c0be00'},
#         {'id': 1333846411985739776,
#         'created': datetime.datetime(2020, 12, 1, 18, 52, 20),
#         'retweeted': 7141,
#         'text': 'https://t.co/hhxUHKxwlE',
#         'hashtags': [],
#         'urls': 'https://twitter.com/twitter/statuses/1333846411985739776',
#         'mentions': [],
#         'score': 0.0,
#         'color': '#c0be00'},
#         {'id': 1333846348345602051,
#         'created': datetime.datetime(2020, 12, 1, 18, 52, 5),
#         'retweeted': 5953,
#         'text': 'https://t.co/hTRI4vYbY5',
#         'hashtags': [],
#         'urls': 'https://twitter.com/twitter/statuses/1333846348345602051',
#         'mentions': [],
#         'score': 0.0,
#         'color': '#c0be00'},
#         {'id': 1333846314766004224,
#         'created': datetime.datetime(2020, 12, 1, 18, 51, 57),
#         'retweeted': 5977,
#         'text': 'https://t.co/x2kNO9LYEO',
#         'hashtags': [],
#         'urls': 'https://twitter.com/twitter/statuses/1333846314766004224',
#         'mentions': [],
#         'score': 0.0,
#         'color': '#c0be00'},
#         {'id': 1333846286341185542,
#         'created': datetime.datetime(2020, 12, 1, 18, 51, 50),
#         'retweeted': 6296,
#         'text': 'https://t.co/a1kQRp7EzG',
#         'hashtags': [],
#         'urls': 'https://twitter.com/twitter/statuses/1333846286341185542',
#         'mentions': [],
#         'score': 0.0,
#         'color': '#c0be00'},
#         {'id': 1333846259866742790,
#         'created': datetime.datetime(2020, 12, 1, 18, 51, 44),
#         'retweeted': 5943,
#         'text': 'https://t.co/MLUbZv1OpN',
#         'hashtags': [],
#         'urls': 'https://twitter.com/twitter/statuses/1333846259866742790',
#         'mentions': [],
#         'score': 0.0,
#         'color': '#c0be00'}
#         ]
#     }
        
#     return render_template('tweets.html', record=record)



# @app.route("/following/")
# def following():
#     """
#     Display the list of users followed by a screen name, sorted in
#     reverse order by the number of followers of those users.
#     """
#     follow_record = [
#     {'name': 'The White House',
#     'screen_name': 'WhiteHouse',
#     'followers': 25891570,
#     'created': datetime.datetime(2017, 1, 19, 22, 54, 27),
#     'image': 'http://pbs.twimg.com/profile_images/1059888693945630720/yex0Gcbi_normal.jpg'},
#     {'name': 'Vice President Mike Pence',
#     'screen_name': 'VP',
#     'followers': 10241417,
#     'created': datetime.datetime(2017, 1, 10, 20, 2, 44),
#     'image': 'http://pbs.twimg.com/profile_images/951600999902281728/s-3S8iBE_normal.jpg'},
#     {'name': 'Ivanka Trump',
#     'screen_name': 'IvankaTrump',
#     'followers': 10239716,
#     'created': datetime.datetime(2009, 6, 30, 22, 32, 3),
#     'image': 'http://pbs.twimg.com/profile_images/1054179226100908032/i5ZXfFdE_normal.jpg'},
#     {'name': 'Donald Trump Jr.',
#     'screen_name': 'DonaldJTrumpJr',
#     'followers': 6457705,
#     'created': datetime.datetime(2009, 5, 11, 21, 18, 33),
#     'image': 'http://pbs.twimg.com/profile_images/766652495858896897/LjrJJB9a_normal.jpg'},
#     {'name': 'Kayleigh McEnany',
#     'screen_name': 'PressSec',
#     'followers': 6237390,
#     'created': datetime.datetime(2017, 1, 10, 21, 6, 57),
#     'image': 'http://pbs.twimg.com/profile_images/1250415895383506944/EttGxOru_normal.jpg'},
#     {'name': 'Mike Pence',
#     'screen_name': 'Mike_Pence',
#     'followers': 5941000,
#     'created': datetime.datetime(2009, 2, 27, 23, 4, 51),
#     'image': 'http://pbs.twimg.com/profile_images/1320890359505915910/o9n6k6x1_normal.jpg'},
#     {'name': 'Sean Hannity',
#     'screen_name': 'seanhannity',
#     'followers': 5582170,
#     'created': datetime.datetime(2009, 5, 21, 17, 41, 12),
#     'image': 'http://pbs.twimg.com/profile_images/1298273293061853188/5SVIYpyY_normal.jpg'},
#     {'name': 'Tucker Carlson',
#     'screen_name': 'TuckerCarlson',
#     'followers': 4575542,
#     'created': datetime.datetime(2009, 3, 4, 0, 3, 12),
#     'image': 'http://pbs.twimg.com/profile_images/796823622450982912/XYcUsJUI_normal.jpg'},
#     {'name': 'Eric Trump',
#     'screen_name': 'EricTrump',
#     'followers': 4561924,
#     'created': datetime.datetime(2009, 5, 11, 21, 42, 30),
#     'image': 'http://pbs.twimg.com/profile_images/1287159519743807490/A_NzWpYr_normal.jpg'},
#     {'name': 'Laura Ingraham',
#     'screen_name': 'IngrahamAngle',
#     'followers': 3962912,
#     'created': datetime.datetime(2009, 6, 25, 21, 3, 25),
#     'image': 'http://pbs.twimg.com/profile_images/1146349820912660480/CjdAuR5i_normal.jpg'},
#     {'name': 'Kellyanne Conway',
#     'screen_name': 'KellyannePolls',
#     'followers': 3617073,
#     'created': datetime.datetime(2012, 1, 23, 4, 14, 28),
#     'image': 'http://pbs.twimg.com/profile_images/1212176191844757507/ypMvAPHv_normal.jpg'},
#     {'name': "Bill O'Reilly",
#     'screen_name': 'BillOReilly',
#     'followers': 3407150,
#     'created': datetime.datetime(2009, 3, 12, 15, 44, 18),
#     'image': 'http://pbs.twimg.com/profile_images/1124085945530298370/x9EsUs56_normal.png'},
#     {'name': 'Jeanine Pirro',
#     'screen_name': 'JudgeJeanine',
#     'followers': 2521087,
#     'created': datetime.datetime(2009, 4, 7, 14, 27, 6),
#     'image': 'http://pbs.twimg.com/profile_images/850023968484368386/jBcIv7W1_normal.jpg'},
#     {'name': 'Vince McMahon',
#     'screen_name': 'VinceMcMahon',
#     'followers': 2452441,
#     'created': datetime.datetime(2013, 2, 26, 18, 6, 9),
#     'image': 'http://pbs.twimg.com/profile_images/956545058978885632/UURuOqef_normal.jpg'},
#     {'name': 'Team Trump',
#     'screen_name': 'TeamTrump',
#     'followers': 2423362,
#     'created': datetime.datetime(2016, 5, 9, 14, 15, 10),
#     'image': 'http://pbs.twimg.com/profile_images/745768799849308160/KrZhjkpH_normal.jpg'},
#     {'name': 'Lou Dobbs',
#     'screen_name': 'LouDobbs',
#     'followers': 2316975,
#     'created': datetime.datetime(2009, 3, 25, 12, 39, 59),
#     'image': 'http://pbs.twimg.com/profile_images/1291061804982992896/FmNLrPOG_normal.jpg'},
#     {'name': 'Leader McConnell',
#     'screen_name': 'senatemajldr',
#     'followers': 2107656,
#     'created': datetime.datetime(2013, 3, 7, 20, 21, 15),
#     'image': 'http://pbs.twimg.com/profile_images/732596482336002049/JYMrr9_4_normal.jpg'},
#     {'name': 'Rep. Jim Jordan',
#     'screen_name': 'Jim_Jordan',
#     'followers': 1941062,
#     'created': datetime.datetime(2008, 12, 16, 17, 20, 24),
#     'image': 'http://pbs.twimg.com/profile_images/596012379231617025/TtrAXbnA_normal.jpg'},
#     {'name': 'Kimberly Guilfoyle',
#     'screen_name': 'kimguilfoyle',
#     'followers': 1921133,
#     'created': datetime.datetime(2009, 3, 18, 16, 33, 40),
#     'image': 'http://pbs.twimg.com/profile_images/1276508455042527232/qBl4p7P1_normal.jpg'},
#     {'name': 'Jesse Watters',
#     'screen_name': 'JesseBWatters',
#     'followers': 1570038,
#     'created': datetime.datetime(2009, 7, 14, 1, 23, 16),
#     'image': 'http://pbs.twimg.com/profile_images/697123861163192320/6ra0cPIS_normal.jpg'},
#     {'name': 'Diamond and Silk®',
#     'screen_name': 'DiamondandSilk',
#     'followers': 1453784,
#     'created': datetime.datetime(2014, 12, 6, 18, 49, 6),
#     'image': 'http://pbs.twimg.com/profile_images/1257866413571813377/amVKEtcq_normal.jpg'},
#     {'name': 'MELANIA TRUMP',
#     'screen_name': 'MELANIATRUMP',
#     'followers': 1347968,
#     'created': datetime.datetime(2010, 1, 26, 1, 48, 43),
#     'image': 'http://pbs.twimg.com/profile_images/726781589192069126/zg456hZZ_normal.jpg'},
#     {'name': 'FOX & friends',
#     'screen_name': 'foxandfriends',
#     'followers': 1344719,
#     'created': datetime.datetime(2008, 7, 21, 10, 50, 9),
#     'image': 'http://pbs.twimg.com/profile_images/952249840884383744/8Xp95_Ip_normal.jpg'},
#     {'name': 'Lara Trump',
#     'screen_name': 'LaraLeaTrump',
#     'followers': 1220116,
#     'created': datetime.datetime(2009, 9, 19, 12, 49, 26),
#     'image': 'http://pbs.twimg.com/profile_images/1299885652897673217/7y3TYuC0_normal.jpg'},
#     {'name': 'Greta Van Susteren',
#     'screen_name': 'greta',
#     'followers': 1216985,
#     'created': datetime.datetime(2008, 8, 28, 20, 4, 54),
#     'image': 'http://pbs.twimg.com/profile_images/793843822065246208/aoQehI29_normal.jpg'},
#     {'name': '🇺🇸ERIC BOLLING🇺🇸',
#     'screen_name': 'ericbolling',
#     'followers': 1208667,
#     'created': datetime.datetime(2008, 5, 19, 23, 36, 4),
#     'image': 'http://pbs.twimg.com/profile_images/1321466776719425537/zAwsvNzu_normal.jpg'}
#     ]
#     return render_template('following.html', name='fuckyou', follow_record=follow_record)


i = sys.argv.index('server:app')
twitter_auth_filename = sys.argv[i+1] # e.g., "/Users/parrt/Dropbox/licenses/twitter.csv"
api = authenticate(twitter_auth_filename)


if __name__ == '__main__':
    app.run('0.0.0.0')
