def merge_sorted(a, b):
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    return out + a[i:]

def find_max(items):
    best = items[0]
    for x in items:
        if x > best:
            best = x
    return best
