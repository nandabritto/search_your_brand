# python code goes here
import os
import tweepy as tw
import pandas as pd
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import argparse
import gspread as gs
import gspread_dataframe as gd

load_dotenv()


"""
Twitter API keys
"""
consumer_key = os.environ.get('API_KEY')
consumer_secret = os.environ.get('API_SECRET_KEY')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]


gc = gs.service_account(filename="creds.json")
"""
Get arguments and assign inputs if arguments are empty and
run all the functions
"""


def get_args():
    # add description of task
    parser = argparse.ArgumentParser(
        description='search for tweets by location and \
                     keyword')
    # add city argument
    parser.add_argument(
        '--city', type=str, help='Your city')
    # add country argument
    parser.add_argument(
        '--country', type=str, help='Your country')
    # add keyword argument
    parser.add_argument(
        '--keyword', type=str, help='Your keyword')
    # add language argument
    parser.add_argument(
        '--language', type=str, help='Your prefered language')
    # array for all arguments passed to script
    args = parser.parse_args()
    # assign inputs if arguments are empty
    if not args.city:
        args.city = input("Insert your city \n")
    if not args.country:
        args.country = input("Insert your country \n")
    if not args.keyword:
        args.keyword = input("Insert your keyword for searching \n")
    if not args.language:
        args.language = input("Insert your prefered language \n")

    return(args)


def main():
    parsed_args = get_args()
    # assign variable to geo_location function
    loc = geo_location(parsed_args)
    print(loc)
    # call function with geolocation and args argument
    search_result = search_tweet(loc, parsed_args)
    update_worksheet(search_result)


def geo_location(args):
    """
    Get user location (by city and country)
    """

    geolocator = Nominatim(user_agent="my_user_agent")
    # assign the args to variables with geolocator and geocode
    loc = geolocator.geocode(args.city + ',' + args.country)
    return loc


def search_tweet(loc, args):
    """
    Gets user's latitude and longitude and search tweets
    on Twitter in max range of 100km, enable user to add
    search keyword, preferred language and outputs tweet
    text, tweet username, and outputs tweet location,
    tweet coordenation and if geolocaton is enable.
    """

    new_search = args.keyword + "-filter:retweets"

    max_range = 100
    tweets = tw.Cursor(
                  api.search,
                  q=new_search,
                  count=10,
                  lang=args.language,
                  geocode="%f,%f,%dkm" %
                  (float(loc.latitude), float(loc.longitude), max_range),
                  tweet_mode='extended')
    # maxCount = 5
    # count = 0

    json_data = [r._json for r in tweets.items() if r.user.geo_enabled]
    df = pd.json_normalize(json_data)
    new_df = (df[['user.screen_name', 'full_text', 'user.location']])
    print(new_df[:5])
    return (new_df[:5])
    # for index, tweet in new_df.iterrows():
    #         # if tweet.user.geo_enabled:
    #     print()
    #     print("Tweet Information")
    #     print("================================")
    #     print(tweet['full_text'])
    #     print()

    #     print("User Information")
    #     print("================================")
    #     print("Username:", user.screen_name)
    #     print("Location: ", user.location)
    #     count = count + 1
    #     if count == maxCount:
    #         break
    # df = pd.DataFrame({'username': [tweet.user.screen_name], 'Tweet': [tweet.full_text]})
    # print(df)
    # df = pd.json_normalize(json_data)
    # new_df = (df[['user.screen_name','full_text', 'user.location']])
    # print(new_df[:5]



def update_worksheet(p_search_result):
    """
    Update sales worksheet, add new row with the dataframe created
    """
    ws = gc.open("search_your_brand").worksheet("tweets")
    existing = gd.get_as_dataframe(ws)
    updated = existing.append(p_search_result)
    gd.set_with_dataframe(ws, updated)


main()
