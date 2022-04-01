import tweepy
import networkx

f = open("token.txt", "r")
bearer_token=f.read()

client = tweepy.Client(bearer_token)

screen_name = "barackobama"
user = client.get_user(username=screen_name)
ID = user.data.id

public_tweets = client.get_users_tweets(ID)
for tweet in public_tweets.data:
    print(tweet)
    print("-------------------")
