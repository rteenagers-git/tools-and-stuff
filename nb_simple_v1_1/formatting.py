import re

def format_string(string):
    return re.sub(r"([\\~!#^*\(\)_+\[\]>])", r"\\\1", string)


def format_block(string):
    return re.sub(r'(^|\n)', r'\1>', format_string(string))
