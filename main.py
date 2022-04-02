import tweepy
import networkx
from collections import defaultdict
import re
import time

#open the Twitter Client
f = open("token.txt", "r")
bearer_token=f.read()
client = tweepy.Client(bearer_token,wait_on_rate_limit=True)

#global variables
requests=0 #number of tweets that have been alayzed
requests_max=5000 #number of requests before quitting
keywords=["onepiece","one piece","luffy","ワンピース"] 
accounts_checked=set() #accounts that have already been analyzed
pages=2 # 1 page = 100 tweets
min_keywords=10 #smallest number of keywords for an account to be valid
min_rts=2 #smallest number of retweets for a link
sleep_time=3 #sleep time between requests
sleep_count=0 #how many times it slept, for debugging purposes

def sleep():
    global sleep_count
    #time.sleep(sleep_time)
    sleep_count+=1
    print(sleep_count)

def get_id_from_username(name):
    user = client.get_user(username=name)
    sleep()
    return user.data.id

def get_user_id_from_tweet(x):
    sleep()
    return client.get_tweet(x["id"],expansions=["author_id"]).includes["users"][0]["id"]

def get_accounts_rted(ID,recursion_level=0):
    global requests
    if requests>=requests_max:
        return
    if recursion_level>100:
        return
    if ID in accounts_checked:
        return

    accounts_checked.add(ID)
    keywords_found=0
    
    print("\n")
    print("user ID",ID)

    accounts_found=defaultdict(int)
    public_tweets = tweepy.Paginator(
                        client.get_users_tweets,
                        ID,
                        max_results=100,
                        tweet_fields=["referenced_tweets"],
                        limit=pages)
    k=0
    for page in public_tweets:
        sleep()
        for tweet in page.data:
            tweet_text=tweet["text"]
            k+=1
            #find keywords
            for key in keywords:
                if re.search(key, tweet_text, re.IGNORECASE):
                    keywords_found+=1
            
            requests+=1
            referenced_tweets=tweet["referenced_tweets"]
            if referenced_tweets:
                for x in referenced_tweets:
                    type_interaction=x["type"]
                    if type_interaction=="retweeted":
                        user_id=get_user_id_from_tweet(x)
                        if user_id!=ID:
                            accounts_found[user_id]+=1
    print("tweets analyzed:",k)
    if keywords_found>min_keywords:
        print("keywords found:",keywords_found)
        print("accounts found:")
        for k,v in accounts_found.items():
            if v>=min_rts:
                print("ID:",k)
                print("times:",v)
        for k,v in accounts_found.items():
            if v>=min_rts:
                get_accounts_rted(k,recursion_level+1)
    else:
        print("false alarm!")
        
get_accounts_rted(get_id_from_username("Koishi_D_Sama"))
