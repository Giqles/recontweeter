import tweepy
import logging
from config import create_api
from random import random
from heapq import nlargest
from math import log
from statistics import mean
from datetime import date, timedelta

logging.basicConfig(level="INFO")

logger = logging.getLogger()

def make_weights(tweets):
    numer = [x["fav_count"] + x["rt_count"] for x in tweets]
    weights = [(x + mean(numer)) / (sum(numer) * 2) for x in numer]
    return(weights)

def weighted_sample(weights, m):
    n_to_choose = min([len(weights), m])
    elt = [(log(random()) / weights[i], i) for i in range(len(weights))]
    return ([x[1] for x in nlargest(n_to_choose, elt)])

def find_tweets(api, ndays=1, res_type="mixed"):
    # find original tweets (ie, not replies, not retweets, but quote tweets ok)
    # sent since yesterday
    # including the #econtwitter tag
    yd = date.today() - timedelta(days=ndays)
    search_args = {
        "q": f"#econtwitter -filter:replies -filter:retweets since:{yd.strftime('%Y-%m-%d')}",
        "rpp": 100,
        "lang": "en",
        "tweet_mode": "extended",
        "result_type": res_type
    }
    results = []
    for page in tweepy.Cursor(api.search, **search_args).pages():
        results.extend(page)
    logger.info(f"Found {len(results)} tweets")
    return(results)

def choose_tweets(results, n_tweets=1, max_hashtags=3):
    # get the important info
    # and let's not try to retweet things we've already retweeted
    eligible = [{"id": x.id,
                 "rt_count": x.retweet_count,
                 "fav_count": x.favorite_count,
                 "n_hashtags": len(x.entities["hashtags"])} for x in results if x.retweeted==False]
    # the "retweeted" flag seems unreliable or slow to update...
    logger.info(f"Found {len(eligible)} unretweeted tweets")
    # and dodge some hashtag spamming
    filtered = [x for x in eligible if x["n_hashtags"] <= max_hashtags]
    logger.info(f"Found {len(filtered)} tweets that weren't hashtag spam")
    # weighted random sample
    weights = make_weights(filtered)
    # try not to be spammy, limit of 1 rt per run
    selected = weighted_sample(weights, n_tweets)
    return([filtered[x]["id"] for x in selected])

def most_popular(results, max_hashtags=3):
    # get the important info
    # don't filter for things we've already retweeted
    eligible = [{"id": x.id,
                 "score": x.retweet_count + x.favorite_count,
                 "user": x.user.screen_name}
                for x in results if len(x.entities["hashtags"]) <= max_hashtags]
    logger.info(f"Found {len(eligible)} tweets to draw from")
    top_tweet = max(eligible, key=lambda x:x["score"])
    return(top_tweet)

def retweet_random(event, context):
    api = create_api()
    res = find_tweets(api, ndays=1, res_type="mixed")
    to_retweet = choose_tweets(res)
    for tweet in to_retweet:
        logger.info(f"Trying to retweet {tweet}")
        try:
            api.retweet(tweet)
            logger.info("Success!")
        except Exception:
            logger.error("Error retweeting: %s", exc_info=True)

def retweet_most_popular(event, context):
    api = create_api()
    res = find_tweets(api, ndays=7, res_type="mixed")
    tweet = most_popular(res)
    logger.info(f"Trying to retweet {tweet['id']}")
    try:
        api.update_status(
            status=f"The most popular #econtwitter content this week was this from @{tweet['user']}:",
            attachment_url=f"https://twitter.com/{tweet['user']}/status/{tweet['id']}"
        )
    except Exception:
        logger.error("Error retweeting: %s", exc_info=True)
