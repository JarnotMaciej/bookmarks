def exportToMarkdown(jsonInput):
    '''Takes a JSON input and returns a string of Markdown text.'''
    markdownOutput = '# Bookmarks\n\n'
    for bookmark in jsonInput:
        markdownOutput += ' * [' + bookmark['name'] + '](https://' + bookmark['url'] + ')\n'
    return markdownOutput

def exportToJson(bookmarks, tags):
    '''Takes a JSON input from bookmarks and tags and returns merged JSON text.'''
    output = {}
    tags = list(tags)
    bookmarks = list(bookmarks)
    output['tags'] = tags
    output['bookmarks'] = bookmarks
    return output
