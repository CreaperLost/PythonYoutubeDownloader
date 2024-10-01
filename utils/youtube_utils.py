import re


# Fixing PyTube.
def sanitize_filename(filename):
    # Remove any non-ASCII characters
    filename = filename.encode('ascii', 'ignore').decode('ascii')

    # Replace spaces with underscores
    filename = filename.replace(' ', '_')

    # Remove any characters that aren't alphanumeric, underscore, hyphen, or period
    filename = re.sub(r'[^\w\-.]', '', filename)

    # Remove any leading or trailing periods or spaces
    filename = filename.strip('. ')

    # Limit the length of the filename (optional, adjust as needed)
    max_length = 255  # Maximum filename length for most file systems
    if len(filename) > max_length:
        filename = filename[:max_length]

    # If the filename is empty after sanitization, provide a default
    if not filename:
        filename = "untitled"

    return filename


def get_throttling_function_name(js: str) -> str:
    """Extract the name of the function that computes the throttling parameter.

    :param str js:
        The contents of the base.js asset file.
    :rtype: str
    :returns:
        The name of the function used to compute the throttling parameter.
    """
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    # logger.debug('Finding throttling function name')
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            # logger.debug("finished regex search, matched: %s", pattern)
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise re.RegexMatchError(
        caller="get_throttling_function_name", pattern="multiple"
    )


def is_valid_youtube_url(url):
    # Basic regex pattern for YouTube URLs
    pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$'
    return re.match(pattern, url) is not None
