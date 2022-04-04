import tweepy
from collections import defaultdict
import re
import time

#open the Twitter Client
with open("token.txt", "r") as f:
    bearer_token=f.read()
client = tweepy.Client(bearer_token,wait_on_rate_limit=True)
f.close()

#global variables
tweets_analyzed=0 #number of tweets that have been alayzed
accounts_checked=set() #accounts that have already been analyzed
sleep_count=0 #how many times it slept, for debugging purposes
edges=[]

#parameters
tweets_max=50000 #number of tweets before quitting
keywords=["anti-vax","antivax","vaccinedeath","vaxxdeath","vaxdeath",
          "vaccineinjur","vaccinemandate","sideeffect","vaxmandate"
          "experimentalvaccine","ivermectin","genetherapy","pfizergate",
          "vaccinemandate","medicaltyran","vaers","vaccinegenocide",
          "phizer","vaxinjur","vaxxinjur","vax-injur","vaxx-injur",
          "jabbed","vaccinationregret","#pfizer","bigpharma"] 
pages=4 # 1 page = 100 tweets
min_keywords=5 #smallest number of keywords for an account to be valid
min_rts=2 #smallest number of retweets for a link
sleep_time=1 #sleep time between requests

#sleep after doing a request in order to not get rate limited
def sleep():
    global sleep_count
    #time.sleep(sleep_time)
    sleep_count+=1
    #print("sleep count:",sleep_count)

def get_id_from_username(name):
    user = client.get_user(username=name)
    sleep()
    return user.data.id

def get_user_id_from_referenced_tweet(x):
    sleep()
    return client.get_tweet(x["id"],expansions=["author_id"]).includes["users"][0]["id"]

def get_accounts_rted(ID):
    global tweets_analyzed
    if ID in accounts_checked:
        return
    print("user ID:",ID)
    accounts_checked.add(ID)
    keywords_found=0
    accounts_found=defaultdict(int)
    public_tweets = tweepy.Paginator(
                        client.get_users_tweets,
                        ID,
                        max_results=100,
                        tweet_fields=["referenced_tweets"],
                        expansions=["referenced_tweets.id,referenced_tweets.id.author_id"],
                        limit=pages)
    
    k=0
    for page in public_tweets:
        sleep()
        if page.includes=={}:
            break
        users=page.includes["users"]
        for tweet in page.data:
            tweets_analyzed+=1
            tweet_text=tweet["text"]
            k+=1
            
            #find keywords
            for key in keywords:
                if re.search(key, tweet_text.replace(" ", ""), re.IGNORECASE):
                    keywords_found+=1

            #add to count if RT'ed
            referenced_tweets=tweet["referenced_tweets"]
            if referenced_tweets:
                for x in referenced_tweets:
                    type_interaction=x["type"]
                    if type_interaction=="retweeted":
                        username=tweet.data["text"].split(":")[0][4:] #idk a nicer way
                        user_id_list=[x for x in users if x.username==username]
                        if user_id_list:
                            user_id=user_id_list[0].data["id"]
                        else:
                            user_id=get_user_id_from_referenced_tweet(x) 
                        if user_id!=ID:
                            accounts_found[user_id]+=1
                            
    print("tweets analyzed for this account:",k)
    if keywords_found>=min_keywords:
        print("keywords found:",keywords_found)
        print("edges added:")
        f = open("list.txt", "a")
        for k,v in accounts_found.items():
            if v>=min_rts:
                print(ID,k)
                edges.append((ID,k))
                f.write(f"{ID} {k}\n")
        f.close()
        
    else:
        print("account is irrelevant!")
        print("keywords found:",keywords_found)
        with open("irrelevant.txt","a") as f:
             f.write(f"{ID}\n")
    print("\n")

def write_cursor(cursor):
    with open("cursor.txt", "w") as f:
        f.write(str(cursor))

#read cursor and list
cursor=0
old_cursor=False #do we already have a cursor from a prior run of the program?

try:
    with open("cursor.txt","r") as f:
        cursor=int(f.read())
        old_cursor=True
except FileNotFoundError:
    pass
        
try:
    with open("list.txt","r") as f:
        lines=f.readlines()
        for line in lines:
            xandy=line.strip().split()
            edges.append((xandy[0],xandy[1]))
except FileNotFoundError:
    pass

f=open("start.txt","r")
starting_username=f.read()
f.close()

if old_cursor:
    accounts_checked.add(get_id_from_username(starting_username))
else:
    get_accounts_rted(get_id_from_username(starting_username))
        
k=0
write_cursor(k)
for x,y in edges:
    k+=1
    if old_cursor and k<cursor:
        accounts_checked.add(y)
        print(x,y)
        continue
    write_cursor(k)
    #if tweets_analyzed>=tweets_max:
    #    print("reached tweet limit!")
    #    break
    get_accounts_rted(y)
