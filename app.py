from dotenv import load_dotenv
import os
from datetime import datetime
from flask import Flask, json, render_template, request, jsonify, redirect, Response
from pymongo import MongoClient
import utils.validation as validation
import utils.normalization as normalization
import utils.migration as migration

load_dotenv()
# Access the variables
mongodb_host = os.getenv("MONGODB_HOST")
mongodb_port = os.getenv("MONGODB_PORT")
database = os.getenv("MONGODB_DB")
bookmarks_collection = os.getenv("BOOKMARKS_COLLECTION")
tags_collection = os.getenv("TAGS_COLLECTION")
app_port = os.getenv("BOOKMARKS_PORT")
if app_port == None:
    app_port = 4999

app = Flask(__name__)

client = MongoClient(mongodb_host, int(mongodb_port))
db = client[database]
bookmarks_collection = db[bookmarks_collection]
tags_collection = db[tags_collection]


current_page = 'home'
sorting = [
    {
        'name': 'Bookmark name (A-Z)', 
        'value': 'nameAsc'
    },
    {
        'name': 'Bookmark name (Z-A)',
        'value': 'nameDesc'
    },
    {
        'name': 'Date added (oldest first)',
        'value': 'dateAsc'
    },
    {
        'name': 'Date added (newest first)',
        'value': 'dateDesc'
    }
]

### Functions ###
def importFromJson(jsonInput):
    '''Takes a JSON input and imports it into the database.'''
    # it is already connected to the database
    if validation.validateImport(jsonInput):
        # delete all bookmarks
        bookmarks_collection.delete_many({})
        # delete all tags
        tags_collection.delete_many({})
        # insert all tags
        for tag in jsonInput['tags']:
            tags_collection.insert_one(tag)
        # insert all bookmarks
        for bookmark in jsonInput['bookmarks']:
            bookmarks_collection.insert_one(bookmark)
        return True
    
    return False

def insert_tag(name, color):
    '''Inserts a tag into the database'''
    tags_collection.insert_one({'name': name, 'color': color})

def insert_bookmark(name, url, tags):
    '''Inserts a bookmark into the database'''
    bookmarks_collection.insert_one({'name': name, 'url': url, 'tags': tags, 'visited': False})

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
    tags = tags_collection.find().sort('name', 1)

    modified_bookmarks = assign_tag_colors(bookmarks, tags_collection.find())

    return render_template('index.html', bookmarks=modified_bookmarks, page=current_page, editTags=tags, sorting=sorting)

@app.route('/tags', methods=['GET', 'POST'])
def tags():
    current_page = 'tags'

    # Fetch data from MongoDB
    tags = tags_collection.find().sort('name', 1)

    return render_template('tags.html', tags=tags, page=current_page)

@app.route('/add-bookmark')
def add_bookmark():
    tags = tags_collection.find().sort('name', 1)
    current_page = 'tags'

    return render_template('add-bookmark.html', page=current_page, tags=tags)

@app.route('/settings')
def settings():
    current_page = 'settings'

    return render_template('settings.html', page=current_page)

@app.route('/add-bookmark-execute', methods=['POST'])
def add_bookmark_execute():
    name = request.get_json().get('name')
    url = normalization.url_normalization(request.get_json().get('url'))
    tags = request.get_json().get('tags')
    
    if validation.validate_bookmark_name(name) and validation.validate_url(url) and validation.validate_tags(tags):
        # check if bookmark already exists
        for bookmark in bookmarks_collection.find():
            if bookmark['name'] == name:
                return jsonify({'message': 'Bookmark already exists'})
            if bookmark['url'] == url:
                return jsonify({'message': 'Bookmark already exists'})
        insert_bookmark(name, url, tags)
    
    return jsonify({'message': 'Bookmark added successfully'})

@app.route('/delete-bookmark', methods=['DELETE'])
def delete_bookmark():
    name = request.get_json().get('name')
    bookmarks_collection.delete_one({'name': name})

    return jsonify({'message': 'Bookmark deleted successfully'})

@app.route('/update-bookmark', methods=['POST'])
def update_bookmark():
    name = request.get_json().get('name')
    name_to_update = request.get_json().get('nameToUpdate')
    url = normalization.url_normalization(request.get_json().get('url'))
    tags = request.get_json().get('tags')
    old_url = bookmarks_collection.find_one({'name': name})['url']

    if validation.validate_bookmark_name(name) and validation.validate_url(url) and validation.validate_tags(tags):
        # check if bookmark already exists
        if name != name_to_update:
            for bookmark in bookmarks_collection.find():
                if bookmark['name'] == name_to_update:
                    return jsonify({'message': 'Bookmark already exists'})
        if url != old_url:
            for bookmark in bookmarks_collection.find():
                if bookmark['url'] == url:
                    return jsonify({'message': 'Bookmark already exists'})
        # delete all the tags from the bookmark
        bookmarks_collection.update_one({'name': name}, {'$unset': {'tags': 1}})

        bookmarks_collection.update_one({'name': name}, {'$set': {'name': name_to_update,'url': url, 'tags': tags}})

    return jsonify({'message': 'Bookmark updated successfully'})

@app.route('/visit-bookmark', methods=['POST'])
def visit_bookmark():
    name = request.get_json().get('name')
    bookmarks_collection.update_one({'name': name}, {'$set': {'visited': True}})

    return jsonify({'message': 'Bookmark visited successfully'})

####################

@app.route('/add-tag', methods=['POST'])
def add_tag():
    name = request.form.get('tagName')
    color = request.form.get('tagColor') 
    if color[0] == '#':
        color = color[1:]
    if validation.validate_tag_name(name) and validation.validate_color(color):
        # check if tag already exists
        for tag in tags_collection.find():
            if tag['name'] == name:
                return redirect('/tags')
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

@app.route('/edit-tag', methods=['POST'])
def edit_tag():
    tag_name = request.form.get('tagName')
    new_name = request.form.get('newTagName')
    new_color = request.form.get('newTagColor')

    if new_color[0] == '#':
        new_color = new_color[1:]
    if validation.validate_tag_name(new_name) and validation.validate_color(new_color):
        if tag_name == new_name:
            tags_collection.update_one({'name': tag_name}, {'$set': {'color': new_color}})
        else:
            # check if new name already exists
            for tag in tags_collection.find():
                if tag['name'] == new_name:
                    return jsonify({'message': 'Tag already exists'})
            tags_collection.update_one({'name': tag_name}, {'$set': {'name': new_name, 'color': new_color}})

        # update bookmarks
        for bookmark in bookmarks_collection.find():
            if tag_name in bookmark['tags']:
                bookmark['tags'].remove(tag_name)
                bookmark['tags'].append(new_name)
                bookmarks_collection.update_one({'name': bookmark['name']}, {'$set': {'tags': bookmark['tags']}})

    return jsonify({'message': 'Tag edited successfully'})

# Return exports
@app.route('/bookmarks-markdown')
def bookmarks_markdown():
    bookmarks = bookmarks_collection.find({}, {"_id": 0, "name": 1, "url": 1}).sort('name', 1)
    markdownFile = migration.exportToMarkdown(bookmarks)
    response = Response(markdownFile)
    # put date and time in the filename
    response.headers['Content-Disposition'] = 'attachment; filename=bookmarks-' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.md'
    return response

@app.route('/bookmarks-json-export')
def bookmarks_json_export():
    bookmarks = bookmarks_collection.find({}, {"_id": 0, "name": 1, "tags": 1, "url": 1, "visited": 1}).sort('name', 1)
    tags = tags_collection.find({}, {"_id": 0, "name": 1, "color": 1}).sort('name', 1)
    jsonFile = migration.exportToJson(bookmarks, tags)
    response = jsonify(jsonFile)
    # put date and time in the filename
    response.headers['Content-Disposition'] = 'attachment; filename=bookmarks-' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.json'
    return response

@app.route('/bookmarks-json-import', methods=['POST'])
def bookmarks_json_import():
    # check if the post request has the file part and if it is blank
    if 'fileToImport' not in request.files or request.files['fileToImport'].filename == '':
        return redirect('/settings')
    jsonFile = request.files['fileToImport']
    # check if the file is a json file
    if not jsonFile.filename.endswith('.json'):
        return redirect('/settings')
    jsonData = json.load(jsonFile)  # Parse JSON data from file object
    importFromJson(jsonData)
    return redirect('/')

@app.errorhandler(404)
def page_not_found(error):
    # Custom error page template
    return render_template('error.html', error_code=404), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app_port)