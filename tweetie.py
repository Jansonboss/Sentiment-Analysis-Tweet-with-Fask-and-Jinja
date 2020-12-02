import sys
from numpy.lib.function_base import median
import tweepy
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def loadkeys(filename):
    """
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(',')
    return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    api_items = loadkeys(filename=twitter_auth_filename)
    consumer_key, consumer_secret = api_items[0], api_items[1]
    access_token, access_token_secret = api_items[2], api_items[3]
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    
    return api



def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """
    
    tweets_obj = api.user_timeline(
        screen_name=name, # realDonaldTrump
        # 100 is the maximum allowed count
        count=200,
        # filter out retweets
        include_rts = False,
        # Necessary to keep full_text 
        # otherwise only the first 140 words are extracted
        tweet_mode = 'extended')
    
    # intialize an empty list for tweet
    tweets_list = list()
    for fetch_tweets in tweets_obj:
        # sntimental analysis 
        analyzer = SentimentIntensityAnalyzer()
        text = fetch_tweets.full_text
        score = analyzer.polarity_scores(text)['compound']
        
        entity = fetch_tweets.entities    
        tweet_dict = {
            'id':fetch_tweets.id,
            'created':fetch_tweets.created_at,
            'retweeted':fetch_tweets.retweet_count, 
            'text':text,
            'hashtags':entity['hashtags'],
            'urls':'https://twitter.com/twitter/statuses/' + str(fetch_tweets.id),
            'mentions': [ i['screen_name'] for i in entity['user_mentions'] ],
            'score': score
            }
        tweets_list.append(tweet_dict)
    
    final_dict = {
    'user': fetch_tweets.author.screen_name,
    'count': fetch_tweets.author.statuses_count,
    'tweets': tweets_list,
    'median_score': np.median( [i['score'] for i in tweets_list] )
    } 
    
    return final_dict


def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image

    To collect data: get the list of User objects back from friends();
    get a maximum of 100 results. Pull the appropriate values from
    the User objects and put them into a dictionary for each friend.
    """
    
    friends = api.friends(screen_name = name, count=200)
    friends_list = list()
    for f in friends:
        f_dict = {
            "name": f.name,
            "screen_name": f.screen_name,
            "created": f.created_at,
            "followers":f.followers_count,
            "image" : f.profile_image_url
            }
        friends_list.append(f_dict)
        
    friends_list = sorted(friends_list, key = lambda x: x['followers'], reverse = True)
    return friends_list