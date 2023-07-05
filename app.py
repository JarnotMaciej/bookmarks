from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Connection to MongoDB
client = MongoClient('192.168.21.8', 32769)
db = client['mydb']
bookmarks = db['bookmarks']
tags = db['tags']

# Set the current page
current_page = 'home'

@app.route('/')
def index():
    # Set the current page
    current_page = 'home'
    # Fetch data from MongoDB
    data = bookmarks.find()

    # Pass the data to the template and render it
    return render_template('index.html', data=data, current_page=current_page)

@app.route('/tags')
def tags():
    # Set the current page
    current_page = 'tags'
    # Fetch data from MongoDB
    data = tags.find()

    # Pass the data to the template and render it
    return render_template('tags.html', data=data, current_page=current_page)

if __name__ == '__main__':
    app.run()