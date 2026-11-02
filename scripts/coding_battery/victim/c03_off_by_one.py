def paginate(items, page_size):
    pages = []
    for i in range(0, len(items) - 1, page_size):
        pages.append(items[i:i + page_size])
    return pages

def last_n(items, n):
    return items[len(items) - n - 1:]
