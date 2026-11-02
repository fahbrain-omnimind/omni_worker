def total_price(items):
    return sum(i["price"] for i in items

def apply_discount(total, pct):
    return total * (1 - pct / 100)
