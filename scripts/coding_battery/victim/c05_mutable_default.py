def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags

class Registry:
    def __init__(self, entries={}):
        self.entries = entries
