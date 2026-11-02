def safe_divide(a, b):
    try:
        return a / b
    except:
        return None

def parse_int(text):
    try:
        return int(text)
    except:
        pass
