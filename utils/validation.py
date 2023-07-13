import re

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
    pattern = r"^[0-9a-zA-Z\s]{1,64}$"
    return bool(name) and re.match(pattern, name) is not None

def validate_bookmark_name(name):
    '''Validates the bookmark name'''
    pattern = r"^[0-9a-zA-Z\s]{1,128}$"
    return bool(name) and re.match(pattern, name) is not None

def validate_url(url):
    '''Validates the url'''
    pattern = r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,63}(:[0-9]{1,5})?(\/.*)?$"
    return bool(url) and re.match(pattern, url) is not None

def validate_tags(tags):
    '''Validates the tags'''
    for tag in tags:
        if not validate_tag_name(tag):
            return False
    return True

def validateImport(jsonInput):
    '''Takes a JSON input and validates it.'''
    # Check if the JSON has the right keys
    if 'bookmarks' not in jsonInput.keys() or 'tags' not in jsonInput.keys():
        return False
    
    # Check if the JSON has the right types
    if not isinstance(jsonInput['bookmarks'], list) or not isinstance(jsonInput['tags'], list):
        return False
    
    # Check if the JSON has the right length
    if len(jsonInput['bookmarks']) < 1:
        return False
    
    # Check if the JSON has the right values
    for bookmark in jsonInput['bookmarks']:
        if not isinstance(bookmark, dict) or 'name' not in bookmark or 'url' not in bookmark or 'tags' not in bookmark:
            return False
        if not isinstance(bookmark['name'], str) or not isinstance(bookmark['url'], str) or not isinstance(bookmark['tags'], list):
            return False
        if len(bookmark['name']) < 1 or len(bookmark['url']) < 1:
            return False

    for tag in jsonInput['tags']:
        if not isinstance(tag, dict) or 'name' not in tag or 'color' not in tag:
            return False
        if not isinstance(tag['name'], str) or not isinstance(tag['color'], str):
            return False
        if len(tag['name']) < 1 or len(tag['color']) < 1:
            return False
        
    return True