from requests_oauthlib import OAuth1Session
from datetime import datetime
import requests
import os
import json
import time

# To set your environment variables in your terminal run the following lines:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# export 'CONSUMER_KEY'='<your_consumer_key>'
# export 'CONSUMER_SECRET'='<your_consumer_secret>'
# export 'ACCESS_TOKEN'='<your_access_token>'
# export 'ACCESS_SECRET'='<your_access_secret>'
bearer_token = os.environ.get("BEARER_TOKEN")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_secret = os.environ.get("ACCESS_SECRET")

# According to https://developer.twitter.com/en/docs/twitter-api/rate-limits, only 50 deletes in 15 min
DELETE_RATE_LIMIT = 50
RATE_LIMIT_TIMEOUT_MIN = 15

##############################################################################
# **********************************
# ********** CHANGE ME!!! **********
# **********************************
#
# All tweets BEFORE this date will be deleted. Set to whatever you like.
#
##############################################################################
DATE_CUTOFF = datetime(2015, 7, 1)


def get_oauth():
    """
    Get the authenticated OAuth1Session object. This will be used to make 
    requests to get the user id, and to delete the user's tweets.
    """

    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_secret,
    )

    return oauth


def get_user(oauth):
    """
    Get the current authenticated user. We mostly need the user id.
    """

    response = oauth.get("https://api.twitter.com/2/users/me",
                         params={"user.fields": "id,username"})

    if response.status_code != 200:
        raise Exception(
            "Error getting current user: {} {}".format(
                response.status_code, response.text)
        )

    user = response.json()['data']

    print("\nCurrent user:")
    print(json.dumps(user, indent=4, sort_keys=True))

    return user


def fetch_all_tweets(user_id):
    """
    Fetch all the tweets for the given user id, by paginating through the 
    GET /tweets endpoint, with a page size of 100.

    Returns an array of all the tweets.
    """

    def bearer_oauth(r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2UserTweetsPython"
        return r

    def fetch_tweets(pagination_token):
        """
        Fetch one page of tweets for a user. Page size is 100.
        """

        url = "https://api.twitter.com/2/users/%s/tweets?max_results=100" % user_id

        if (pagination_token is not None):
            url = url + '&pagination_token=' + pagination_token

        response = requests.request("GET", url, auth=bearer_oauth, params={
                                    "tweet.fields": "created_at"})

        if response.status_code != 200:
            raise Exception(
                "Error fetching tweets for userId={}: {} {}".format(
                    user_id, response.status_code, response.text
                )
            )

        return response.json()

    tweets = []
    page = 1
    pagination_token = None

    print("\nFetching tweets...")

    while (True):
        result = fetch_tweets(pagination_token)
        tweets.extend(result['data'])

        print("\tFetched page " + str(page))

        if ('next_token' not in result['meta']):
            break

        pagination_token = result['meta']['next_token']
        page = page + 1

    print('\nFetched %d total tweets' % len(tweets))

    return tweets


def delete_tweets(oauth, tweets):
    """
    Goes through the list of tweets and deletes the ones that were created 
    before the given cutoff date. Due to Twitter API rate limits:
    https://developer.twitter.com/en/docs/twitter-api/rate-limits, 
    this function sleeps for 15 min, every 50 tweets it deletes.
    """

    def delete_tweet(tweet, num_deleted, num_errored):
        """
        Do the request to delete a tweet by id. Print and increment success / error counts.
        """

        response = oauth.delete(
            "https://api.twitter.com/2/tweets/{}".format(tweet['id']))

        if response.status_code != 200:
            print("\t[ERROR] Could not delete tweetId=%s. Reason: %s" %
                  (tweet['id'], response.text))
            num_errored = num_errored + 1
        else:
            print("\t[SUCCESS] Deleted tweetId=%s" % tweet['id'])
            num_deleted = num_deleted + 1

    print("\nDeleting tweets before: %s" % DATE_CUTOFF)

    num_deleted = 0
    num_errored = 0

    rate_limit = 0

    for tweet in tweets:
        tweet_date = datetime.strptime(
            tweet['created_at'], "%Y-%m-%dT%H:%M:%S.000Z")

        if (tweet_date >= DATE_CUTOFF):
            # If the tweet came AFTER the DATE_CUTOFF, ignore
            continue

        # Otherwise, the tweet came BEFORE the DATE_CUTOFF, delete
        delete_tweet(tweet, num_deleted, num_errored)

        rate_limit = rate_limit + 1

        if (rate_limit == DELETE_RATE_LIMIT):
            rate_limit = 0
            print("\n*** RATE LIMIT REACHED. SLEEPING FOR 15 MIN. ***")
            for i in range(1, RATE_LIMIT_TIMEOUT_MIN + 1):
                time.sleep(60)
                print('\t%d minutes left...' % RATE_LIMIT_TIMEOUT_MIN - 1)
            print('\n')

    print("\nSuccessfully deleted %d tweets, with %d errors" %
          (num_deleted, num_errored))


def main():
    oauth = get_oauth()
    user = get_user(oauth)
    all_tweets = fetch_all_tweets(user['id'])
    delete_tweets(oauth, all_tweets)
    print("\nDone!")


if __name__ == "__main__":
    main()
