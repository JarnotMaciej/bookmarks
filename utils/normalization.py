def url_normalization(url):
    '''Normalizes the url'''
    # deleting http:// or https://
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
    # deleting www.
    if url.startswith('www.'):
        url = url[4:]
    # deleting / at the end
    if url.endswith('/'):
        url = url[:-1]
    return url