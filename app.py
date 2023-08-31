from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from flask import Flask, json, render_template, request, jsonify, redirect, Response
from pymongo import MongoClient
import pytz
from bson.datetime_ms import DatetimeMS
from bson.codec_options import CodecOptions, DatetimeConversion

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
topics_collection = os.getenv("TOPICS_COLLECTION")
app_port = os.getenv("APP_PORT")
if app_port == None:
    app_port = 4999
env_timezone = os.getenv("TZ")
if env_timezone == None:
    env_timezone = 'UTC'

app = Flask(__name__)

my_timezone = pytz.timezone(env_timezone)
client = MongoClient(mongodb_host, int(mongodb_port))
db = client[database]
bookmarks_collection = db[bookmarks_collection].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=my_timezone, datetime_conversion=DatetimeConversion.DATETIME_MS))
tags_collection = db[tags_collection]
topics_collection = db[topics_collection].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=my_timezone, datetime_conversion=DatetimeConversion.DATETIME_MS))

sorting = [
    {'name': 'Bookmark name (A-Z)', 'value': 'nameAsc'},
    {'name': 'Bookmark name (Z-A)', 'value': 'nameDesc'},
    {'name': 'Date added (oldest first)', 'value': 'dateAsc'},
    {'name': 'Date added (newest first)', 'value': 'dateDesc'}
]

### Functions ###
def importFromJson(jsonInput):
    """Takes a JSON input and imports it into the database."""
    if validation.validateImport(jsonInput):
        bookmarks_collection.delete_many({})
        tags_collection.delete_many({})
        for tag in jsonInput['tags']:
            tags_collection.insert_one(tag)
        for bookmark in jsonInput['bookmarks']:
            bookmark['date'] = datetime.fromtimestamp(bookmark['date'] / 1000.0)
            bookmarks_collection.insert_one(bookmark)
        return True
    return False

def insert_tag(name, color):
    """Inserts a tag into the database"""
    tags_collection.insert_one({'name': name, 'color': color})

def insert_bookmark(name, url, tags):
    """Inserts a bookmark into the database"""
    bookmarks_collection.insert_one({
        'name': name,
        'url': url,
        'tags': tags,
        'visited': False,
        'date': datetime.now(tz=my_timezone)
    })

def assign_tag_colors_and_transform_dates(bookmarks, tags):
    """Assigns a color to each tag and transforms the dates to a more readable format."""
    tag_colors = {}
    for tag in tags:
        tag_colors[tag['name']] = tag['color']

    modified_bookmarks = []
    for bookmark in bookmarks:
        modified_tags = []

        if 'date' in bookmark:
            date = bookmark['date']
            # Convert DatetimeMS to Python datetime object
            datetime_obj = date.as_datetime()

            # Convert the datetime object to the desired format
            formatted_date = datetime_obj.strftime("%d.%m.%Y")
            bookmark['date'] = formatted_date

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
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        activeSorting = data.get('activeSorting')
        tagsToFilter = data.get('activeTags')
        print(activeSorting)
        print(tagsToFilter)
        # Query builder
        query = {}
        if tagsToFilter:
            query['tags'] = {'$all': tagsToFilter}
        if activeSorting == 'nameAsc':
            bookmarks = bookmarks_collection.find(query).sort('name', 1)
        elif activeSorting == 'nameDesc':
            bookmarks = bookmarks_collection.find(query).sort('name', -1)
        elif activeSorting == 'dateAsc':
            bookmarks = bookmarks_collection.find(query).sort('date', 1)
        elif activeSorting == 'dateDesc':
            bookmarks = bookmarks_collection.find(query).sort('date', -1)
        else:
            bookmarks = bookmarks_collection.find(query)  # Default sorting (if no activeSorting provided)
        modified_bookmarks = assign_tag_colors_and_transform_dates(bookmarks, tags_collection.find())

        for bookmark in modified_bookmarks:
            bookmark['_id'] = str(bookmark['_id'])

        return jsonify(modified_bookmarks)
    
    # This is the GET request handling
    bookmarks = bookmarks_collection.find().sort('name', 1)
    # how many bookmarks are there in total
    total_bookmarks = bookmarks_collection.count_documents({})
    tags = tags_collection.find().sort('name', 1)
    modified_bookmarks = assign_tag_colors_and_transform_dates(bookmarks, tags_collection.find())
    return render_template('index.html', bookmarks=modified_bookmarks, editTags=tags, sorting=sorting, total_bookmarks=total_bookmarks)

@app.route('/tags')
def tags():
    # Fetch data from MongoDB
    tags = tags_collection.find().sort('name', 1)

    return render_template('tags.html', tags=tags)

@app.route('/add-bookmark')
def add_bookmark():
    tags = tags_collection.find().sort('name', 1)

    return render_template('add-bookmark.html', tags=tags)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/suggestions')
def suggestions():
    # Fetch data from MongoDB topics collection
    generated_suggestions = topics_collection.find().sort('date', -1).limit(1)
    # get topics array from the document
    topic_suggestions = generated_suggestions[0]['topics']
    chosen_bookmarks = generated_suggestions[0]['chosen-bookmarks']
    user_definition = generated_suggestions[0]['user-definition'].title()
    generation_date = generated_suggestions[0]['date']
    # change DatetimeMS(1691573948364) into format DD.MM.YYYY
    generation_date = generation_date.as_datetime().strftime("%d.%m.%Y")

    return render_template('suggestions.html', suggestions=topic_suggestions, chosen_bookmarks=chosen_bookmarks, user_definition=user_definition, generation_date=generation_date)

##################

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
    bookmarks = bookmarks_collection.find({}, {"_id": 0, "name": 1, "tags": 1, "url": 1, "visited": 1, "date": 1}).sort('name', 1)
    tags = tags_collection.find({}, {"_id": 0, "name": 1, "color": 1}).sort('name', 1)
    
    # Convert bookmarks to a list of dictionaries
    bookmarks_list = list(bookmarks)

    # Assign current date to bookmarks without a date
    for bookmark in bookmarks_list:
        if 'date' in bookmark:
            date = int(bookmark['date'])
            bookmark['date'] = date
        else:
            date = int(datetime.now(tz=my_timezone).timestamp() * 1000)
            bookmark['date'] = date

    # Export JSON data
    json_file = migration.exportToJson(bookmarks_list, tags)  # Pass the 'tags' argument here

    response = jsonify(json_file)
    # Put date and time in the filename
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

@app.errorhandler(500)
def page_not_found(error):
    # Custom error page template
    return render_template('error.html', error_code=500), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app_port)