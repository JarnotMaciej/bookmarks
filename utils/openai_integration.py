from bson.codec_options import CodecOptions, DatetimeConversion
from dotenv import load_dotenv
import os
import openai
from pymongo import MongoClient
import re
from datetime import datetime
import pytz

load_dotenv()

# Get environment variables
mongodb_host = os.getenv("MONGODB_HOST")
mongodb_port = os.getenv("MONGODB_PORT")
database = os.getenv("MONGODB_DB")
bookmarks_collection = os.getenv("BOOKMARKS_COLLECTION")
tags_collection = os.getenv("TAGS_COLLECTION")
topics_collection = os.getenv("TOPICS_COLLECTION")
app_port = os.getenv("BOOKMARKS_PORT")
topics_method = os.getenv("TOPICS_METHOD")
env_timezone = os.getenv("TZ")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to MongoDB
client = MongoClient(mongodb_host, int(mongodb_port))
db = client[database]
bookmarks = db[bookmarks_collection]
tags = db[tags_collection]
my_timezone = pytz.timezone(env_timezone)
topics = db[topics_collection].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=my_timezone, datetime_conversion=DatetimeConversion.DATETIME_MS))

def get_16_latest():
    ''' Get 16 latest bookmark names'''
    latest = bookmarks.find({}, {"_id": 0, "name": 1}).sort("date", -1).limit(16)
    return [bookmark["name"] for bookmark in latest]

def get_16_random():
    ''' Get 16 random bookmark names'''
    random = bookmarks.aggregate([{"$sample": {"size": 16}}])
    return [bookmark["name"] for bookmark in random]

def generate_text(prompt):
    messages = [
        {
            "role": "system",
            "content": "You’re a kind helpful assistant. Based on the bookmarks provided below, suggest me 12 different, NEW topics (in ordered list) which might be interesting for me.\n\n"
        }    
    ]
    messages.append({"role": "user", "content": prompt})
    completion = openai.ChatCompletion.create(
        engine="gpt-3.5-turbo",
        messages=messages,
        temperature=0.85,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0.3,
        presence_penalty=0.7,
    )
    return completion

def get_topics(method):
    ''' Get topics from OpenAI API, based on method'''
    bookmarks = []
    if method == "latest":
        bookmarks = get_16_latest()
    elif method == "random":
        bookmarks = get_16_random()
    bookmarksStringWithNewLines = "\n".join(bookmarks)
    topics = generate_text(bookmarks)
    topics = topics.split("\n") # split by new line
    topics = [topic for topic in topics if topic != ""] # remove empty strings
    # delete numbers at the beginning of the string using regex
    topics = [re.sub(r"^\d+\.\s", "", topic) for topic in topics]
    return topics

def put_topics():
    ''' Put topics to MongoDB'''
    my_topics = get_topics(topics_method)
    # put topic names with date to MongoDB
    # topicsToPut = [{"name": topic, "date": datetime.now(tz=my_timezone)} for topic in topics]
    for t in my_topics:
        topics.insert_one({"name": t, "date": datetime.now(tz=my_timezone)})
    
    print("Topics inserted!")

# put_topics()

latest = get_16_latest()
bookmarksStringWithNewLines = "\n".join(latest)
print(bookmarksStringWithNewLines)
print('-'*50)
genText = generate_text(latest)
print(genText)
print('-'*50)

