import re
import time
from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient

app = Flask(__name__)

# Connection to MongoDB
client = MongoClient('192.168.21.8', 32769)
db = client['mydb']
bookmarks_collection = db['bookmarks']
tags_collection = db['tags']

# Set the current page
current_page = 'home'


### Functions ###

def insert_tag(name, color):
    '''Inserts a tag into the database'''
    tags_collection.insert_one({'name': name, 'color': color})

def insert_bookmark(title, url, tags):
    '''Inserts a bookmark into the database'''
    bookmarks_collection.insert_one({'title': title, 'url': url, 'tags': tags, 'viewed': False})

def validate_color(color):
    '''Validates the color'''
    if len(color) != 6:
        return False
    try:
        int(color, 16)
        return True
    except ValueError:
        return False
    
def validate_tag_name(name):
    '''Validates the tag name'''
    pattern = r"^[0-9a-zA-Z\s]{1,128}$"
    return re.match(pattern, name) is not None

def assign_tag_colors(bookmarks_collection, tags_collection):
    '''Assigns a color to each tag'''
    # Fuck CSS
    tag_colors = {}
    for tag in tags_collection:
        tag_colors[tag['name']] = tag['color']

    modified_bookmarks = []
    for bookmark in bookmarks_collection:
        modified_tags = []
        for tag in bookmark['tags']:
            modified_tag = {
                'name': tag,
                'color': tag_colors.get(tag, '9E2A2A')
            }
            modified_tags.append(modified_tag)
        bookmark['tags'] = modified_tags
        modified_bookmarks.append(bookmark)

    return modified_bookmarks

### Routes ###
@app.route('/')
def index():
    current_page = 'home'
    # Fetch data from MongoDB
    bookmarks = bookmarks_collection.find().sort('name', 1)
    tags = tags_collection.find()

    modified_bookmarks = assign_tag_colors(bookmarks, tags)

    return render_template('index.html', bookmarks=modified_bookmarks, page=current_page)

@app.route('/tags', methods=['GET', 'POST'])
def tags():
    current_page = 'tags'

    # Fetch data from MongoDB
    tags = tags_collection.find().sort('name', 1)

    return render_template('tags.html', tags=tags, page=current_page)

@app.route('/add-tag', methods=['POST'])
def add_tag():
    name = request.form.get('tagName')
    color = request.form.get('tagColor') 
    if color[0] == '#':
        color = color[1:]
    if validate_tag_name(name) and validate_color(color):
        insert_tag(name, color)

    return redirect('/tags')

@app.route('/delete-tag', methods=['DELETE'])
def delete_tag():
    tag_name = request.get_json().get('tagName')
    tags_collection.delete_one({'name': tag_name})
    # update bookmarks
    for bookmark in bookmarks_collection.find():
        if tag_name in bookmark['tags']:
            bookmark['tags'].remove(tag_name)
            bookmarks_collection.update_one({'name': bookmark['name']}, {'$set': {'tags': bookmark['tags']}})

    return jsonify({'message': 'Tag deleted successfully'})

# edit tag
@app.route('/edit-tag', methods=['POST'])
def edit_tag():
    tag_name = request.form.get('tagName')
    new_name = request.form.get('newTagName')
    new_color = request.form.get('newTagColor')
    if new_color[0] == '#':
        new_color = new_color[1:]
    if validate_tag_name(new_name) and validate_color(new_color):

        tags_collection.update_one({'name': tag_name}, {'$set': {'name': new_name, 'color': new_color}})
        # update bookmarks
        for bookmark in bookmarks_collection.find():
            if tag_name in bookmark['tags']:
                bookmark['tags'].remove(tag_name)
                bookmark['tags'].append(new_name)
                bookmarks_collection.update_one({'name': bookmark['name']}, {'$set': {'tags': bookmark['tags']}})

    return jsonify({'message': 'Tag edited successfully'})


@app.errorhandler(404)
def page_not_found(error):
    # Custom error page template
    return render_template('error.html', error_code=404), 404

if __name__ == '__main__':
    app.run()