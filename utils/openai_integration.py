# -*- coding: utf-8 -*-

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

def who_bookmarked(bookmarks):
    ''' Define who bookmarked stuff'''
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    default_prompt = 'Based on the bookmarks provided below, please define and the person. Examples of some definitions of the person: "passionate researcher", "tech enthusiast". The definition should be very short (5 words at most). Bookmarks:\n\n'

    bookmarks_str = ""
    for bookmark in bookmarks:
        bookmarks_str += bookmark.encode("utf-8").decode("utf-8")
        bookmarks_str += "\n"
    default_prompt += bookmarks_str + "\n"
    default_prompt += "You should answer only with definition of the user.\n"
    
    messages.append({"role": "user", "content": default_prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1.2,
        max_tokens=20,
        top_p=0.5,
        frequency_penalty=0.3,
        presence_penalty=0.3,
    )

    return response.choices[0].message.content

def generate_topics(prompt, user_definition):
    ''' Generate topics based on prompt'''
    messages = []
    if user_definition != "":
        system_role_string = "You are a helpful assistant. Imagine you are assisting " + user_definition
        messages.append({"role": "system", "content": system_role_string})
    else:
        messages.append({"role": "system", "content": "You are a helpful assistant."})
        

    messages.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8,
        max_tokens=256,
        frequency_penalty=0.3,
        presence_penalty=0.9,
    )
    return response.choices[0].message.content

def prompt_creator(bookmarks):
    default_prompt = "Based on the bookmark names provided below, I want you to assume that the person who bookmarked these is an avid learner with diverse interests. Please suggest 12 different, NEW topics and subjects that align with their curiosity and passion for learning. Think outside the box and provide unique ideas based on the bookmark names. Here are the bookmarks:\n\n"

    bookmarks_str = ""

    for bookmark in bookmarks:
        bookmarks_str += bookmark.encode("utf-8").decode("utf-8")
        bookmarks_str += "\n"

    default_prompt += bookmarks_str + "\n"
    default_prompt += "Remember not to be generic, you need to think out of the box and provide NEW and FRESH topics. Provide ONLY the topics in ordered list. All of the topics should be short and concise (one topic should have at most 5 words.\n"

    return default_prompt

def get_topics(method):
    ''' Get topics from OpenAI API, based on method'''
    bookmarks = []
    if method == "latest":
        bookmarks = get_16_latest()
    elif method == "random":
        bookmarks = get_16_random()
    bookmarksStringWithNewLines = "\n".join(bookmarks)
    user_definition = who_bookmarked(bookmarks)
    prompt = prompt_creator(bookmarks)
    generated_topics = generate_topics(prompt, user_definition)
    topics = generated_topics.replace(bookmarksStringWithNewLines, "")
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

# testin
# random_bm = get_16_random()
# my_prompt = prompt_creator(random_bm)
# # print(my_prompt)
# generated_topics = generate_topics(my_prompt)
# print(generated_topics)

asjfns = get_topics(topics_method)
print(asjfns)
