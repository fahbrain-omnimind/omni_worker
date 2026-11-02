def count_lines(path):
    f = open(path)
    n = len(f.readlines())
    return n

def read_head(path, n=5):
    f = open(path)
    return [f.readline() for _ in range(n)]
